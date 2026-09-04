import numpy as np
from scipy.optimize import least_squares
import uuid
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from pectin.chemistry.kinetics import KineticParameters
from pectin.inference.model_registry import MODELS
# Import the functions from our adaptive_campaign script, or redefine them if easier.
# It's better to redefine them cleanly inside the class context so we don't depend on the script directly.
from pectin.feedstock.properties import FreshRind
from pectin.feedstock.conditioning import condition_feedstock
from pectin.simulator.solver import simulate

# Proxy Models
def compute_proxy_signals(p_sol, p_low, Mw_sol, Mw_low, DE_sol, C_citric, LSR=20.0):
    C_pectin = (p_sol + p_low) / LSR 
    brix = (C_pectin + C_citric) * 100.0
    
    Mw_avg = np.where(p_sol + p_low > 1e-9, (p_sol * Mw_sol + p_low * Mw_low) / (p_sol + p_low + 1e-12), 1000.0)
    intrinsic_visc = 2e-5 * (Mw_avg ** 0.8)
    C_g_dL = C_pectin * 100.0
    visc_specific = intrinsic_visc * C_g_dL
    viscosity = 1.0 + visc_specific + 0.4 * (visc_specific ** 2)
    
    DE_avg = np.where(p_sol + p_low > 1e-9, DE_sol, 0.745)
    cond_pectin = 150.0 * (1.0 - DE_avg) * C_pectin
    cond_citric = 25.0 * C_citric 
    conductivity = 1.0 + cond_citric + cond_pectin
    
    return brix, viscosity, conductivity

def run_virtual_experiment(T_ext, pH, C_citric, time_min, kinetic_params, d50_um=300.0):
    raw_rind = FreshRind(wet_mass=500.0, moisture_fraction=0.85, pectin_content_dry_basis=0.20, 
                         GalA_fraction_of_pectin=0.78, initial_DE=0.745, initial_Mw=654000.0)
    feedstock = condition_feedstock(raw_rind, target_moisture=0.08, d50_um=d50_um)
    res = simulate(feedstock, temperature_celsius=T_ext, pH=pH, C_citric=C_citric, 
                   time_min=time_min, kinetic_params=kinetic_params)
    return res, feedstock

def extract_trajectories(res, feedstock):
    t = res.state.time
    p_sol = res.state.soluble_intact_pectin
    p_low = res.state.low_mw_pectin
    
    mask_sol = p_sol > 1e-12
    DE_sol = np.full_like(t, feedstock.DE)
    DE_sol[mask_sol] = res.state.Q_DE_sol[mask_sol] / p_sol[mask_sol]
    
    Mw_sol = np.full_like(t, feedstock.Mw_matrix)
    Mw_sol[mask_sol] = res.state.Q_MW_sol[mask_sol] / p_sol[mask_sol]
    
    Mw_low = np.full_like(t, 10000.0)
    return t, p_sol, p_low, DE_sol, Mw_sol, Mw_low

def generate_experiment_data(cond, params, fmu_runner=None):
    if len(cond) == 5:
        T, pH, C_citric, t_end, d50 = cond
    else:
        T, pH, C_citric, t_end = cond
        d50 = 300.0

    if fmu_runner is not None:
        fmu_res = fmu_runner(
            temperature_celsius=float(T),
            pH=float(pH),
            time_min=float(t_end),
            C_citric=float(C_citric),
            output_interval_s=10.0,
            pectin_mass_0=0.2333
        )
        t = np.array(fmu_res["time_points_s"]) / 60.0
        p_sol = np.array(fmu_res["P_sol_trajectory"])
        p_low = np.array(fmu_res["P_lowMW_trajectory"])
        DE_sol = np.array(fmu_res["DE_sol_trajectory"])
        Mw_sol = np.array(fmu_res["Mw_sol_trajectory"])
        Mw_low = np.full_like(t, 10000.0)
    else:
        res, feedstock = run_virtual_experiment(T, pH, C_citric, t_end, params, d50_um=d50)
        t, p_sol, p_low, DE_sol, Mw_sol, Mw_low = extract_trajectories(res, feedstock)
    
    sample_times = np.arange(0, t_end + 1e-3, 1.0)
    p_s_i = np.interp(sample_times, t, p_sol)
    p_l_i = np.interp(sample_times, t, p_low)
    DE_s_i = np.interp(sample_times, t, DE_sol)
    Mw_s_i = np.interp(sample_times, t, Mw_sol)
    Mw_l_i = np.interp(sample_times, t, Mw_low)
    
    _, _, cond_true = compute_proxy_signals(p_s_i, p_l_i, Mw_s_i, Mw_l_i, DE_s_i, C_citric)
    cond_noisy = cond_true + np.random.normal(0, 0.05, size=len(sample_times))
    
    aliquot_times = np.arange(15.0, t_end + 1e-3, 15.0)
    aliquots = []
    for at in aliquot_times:
        idx = np.argmin(np.abs(t - at))
        b_true, v_true, _ = compute_proxy_signals(p_sol[idx], p_low[idx], Mw_sol[idx], Mw_low[idx], DE_sol[idx], C_citric)
        brix_noisy = b_true + np.random.normal(0, 0.1)
        visc_noisy = v_true + np.random.normal(0, 0.5)
        DE_noisy = DE_sol[idx] + np.random.normal(0, 0.02)
        Mw_noisy = Mw_sol[idx] + np.random.normal(0, 10000.0)
        aliquots.append({
            "t": float(at), 
            "brix": float(brix_noisy),
            "viscosity": float(visc_noisy),
            "DE": float(DE_noisy), 
            "Mw": float(Mw_noisy)
        })
        
    return {
        "condition": {"T": float(T), "pH": float(pH), "C_citric": float(C_citric), "t_end": float(t_end), "d50": float(d50)},
        "times": sample_times.tolist(),
        "conductivity": cond_noisy.tolist(),
        "aliquots": aliquots
    }

def residuals(q, history, schema):
    theta = schema.inverse_transform(q)
    params = schema.unpack(theta)
    all_res = []
    
    for obs in history:
        cond = obs["condition"]
        T, pH, C_citric, t_end = cond["T"], cond["pH"], cond["C_citric"], cond["t_end"]
        d50 = cond.get("d50", 300.0)
        try:
            res, feedstock = run_virtual_experiment(T, pH, C_citric, t_end, params, d50_um=d50)
            t, p_sol, p_low, DE_sol, Mw_sol, Mw_low = extract_trajectories(res, feedstock)
            
            p_s_i = np.interp(obs["times"], t, p_sol)
            p_l_i = np.interp(obs["times"], t, p_low)
            DE_s_i = np.interp(obs["times"], t, DE_sol)
            Mw_s_i = np.interp(obs["times"], t, Mw_sol)
            Mw_l_i = np.interp(obs["times"], t, Mw_low)
            
            _, _, cond_pred = compute_proxy_signals(p_s_i, p_l_i, Mw_s_i, Mw_l_i, DE_s_i, C_citric)
            all_res.extend((cond_pred - obs["conductivity"]) / 0.05)
            
            for al in obs["aliquots"]:
                idx = np.argmin(np.abs(t - al["t"]))
                b_pred, v_pred, _ = compute_proxy_signals(p_sol[idx], p_low[idx], Mw_sol[idx], Mw_low[idx], DE_sol[idx], C_citric)
                pred_de = DE_sol[idx]
                pred_mw = Mw_sol[idx]
                all_res.append((b_pred - al["brix"]) / 0.1)
                all_res.append((v_pred - al["viscosity"]) / 0.5)
                all_res.append((pred_de - al["DE"]) / 0.02)
                all_res.append((pred_mw - al["Mw"]) / 10000.0)
                
        except Exception:
            all_res.extend([1e6] * (len(obs["times"]) + len(obs["aliquots"])*4))
            
    return np.array(all_res)

def log_likelihood(q, history, schema):
    res = residuals(q, history, schema)
    # If residuals hit the 1e6 penalty
    if np.any(res > 1e5):
        return -np.inf
    # Assume unit variance since residuals are already divided by sigma in the residuals() function
    return -0.5 * np.sum(res**2)

def log_prior(q):
    # Q parameters are log-transformed versions of theta.
    # We apply a weak Gaussian prior on q centered around our initial guess
    # to keep the sampler somewhat grounded.
    # q ~ N(0, 5.0^2) - very wide prior in log space
    return -0.5 * np.sum((q / 5.0)**2)

def log_posterior(q, history, schema):
    lp = log_prior(q)
    if not np.isfinite(lp):
        return -np.inf
    ll = log_likelihood(q, history, schema)
    return lp + ll

def run_mcmc(history, q_init, schema, sigma_prop=0.05, n_steps=500, burn_in=200):
    # Fast, naive Metropolis-Hastings tuned for real-time pedagogical UI
    # In a real system, we'd use Emcee or PyMC, but this avoids heavy dependencies.
    n_params = len(q_init)
    chain = np.zeros((n_steps, n_params))
    chain[0] = q_init
    current_log_prob = log_posterior(q_init, history, schema)
    
    accepted = 0
    for i in range(1, n_steps):
        q_prop = chain[i-1] + np.random.normal(0, sigma_prop, n_params)
        prop_log_prob = log_posterior(q_prop, history, schema)
        
        # Metropolis acceptance criterion
        if prop_log_prob > current_log_prob or np.log(np.random.rand()) < (prop_log_prob - current_log_prob):
            chain[i] = q_prop
            current_log_prob = prop_log_prob
            accepted += 1
        else:
            chain[i] = chain[i-1]
            
    # Discard burn-in
    valid_chain = chain[burn_in:]
    
    # Transform q back to physical theta space
    theta_chain = np.zeros_like(valid_chain)
    for i in range(len(valid_chain)):
        theta_chain[i] = schema.inverse_transform(valid_chain[i])
        
    return theta_chain, valid_chain, accepted / n_steps

def calculate_error(theta_opt, theta_true):
    return np.mean(np.abs((theta_opt - theta_true) / theta_true)) * 100.0

class CampaignManager:
    def __init__(self, model_id="v1.3-full", fmu_runner=None):
        self.model_id = model_id
        self.fmu_runner = fmu_runner
        self.schema = MODELS[model_id]
        self.truth = KineticParameters(
            k_ref_ext=0.05, Ea_ext=35000.0, alpha=1.0,
            k_ref_hyd=0.03, Ea_hyd=40000.0,
            k_ref_deg=0.01, Ea_deg=50000.0,
            k_ref_de=0.02,  Ea_de=45000.0,
            n_ext=1.0, n_hyd=1.0, n_deg=1.0, n_de=1.0,
            gamma_citric=0.0, beta_mw=1.0
        )
        
        self.param_names = self.schema.param_names
        theta_true_list = []
        for p in self.schema.fitted_parameters:
            name = p["name"]
            if hasattr(self.truth, name):
                theta_true_list.append(getattr(self.truth, name))
            else:
                theta_true_list.append(p["initial"])
        self.theta_true = np.array(theta_true_list, dtype=np.float64)
        
        # 3D Grid of possible experiments for Bayesian Active Learning (T, pH, d50)
        np.random.seed(42)
        T_grid = np.array([40.0, 65.0, 80.0, 95.0, 115.0])
        pH_grid = np.array([1.2, 1.8, 2.4, 3.2])
        d50_grid = np.array([150.0, 300.0, 600.0])
        self.candidate_space = []
        for T in T_grid:
            for pH in pH_grid:
                for d50 in d50_grid:
                    self.candidate_space.append((T, pH, 0.05, 90.0, d50))
        
        self.history = []
        
        # Start with a 50% bad guess
        self.theta_init = self.theta_true * 1.5
        self.q_opt = self.schema.transform(self.theta_init)
        
        # Initial empty posteriors (just wide priors for visualization)
        self.posterior_means = self.theta_init.copy()
        # Initial large variance
        self.posterior_stds = self.theta_init * 0.5 
        
        self.runs_allowed = 10
        self.current_acquisition = "Ready. Press 'Execute Optimal Experiment' to determine the first experimental condition."
        self.current_q_std = 0.05
        
    def _acquisition_function(self):
        # Value of Information (Maximum Variance across 3D state space)
        if not self.history:
            # First run: explore the maximum driving force extreme (T=115°C, pH=1.2, d50=150µm)
            best_idx = 0
            for i, c in enumerate(self.candidate_space):
                if c[0] == 115.0 and c[1] == 1.2 and c[4] == 150.0:
                    best_idx = i
                    break
            best_cond = self.candidate_space.pop(best_idx)
            self.current_acquisition = f"D-Optimality: Exploring extreme edge of state space (T={best_cond[0]:.0f}°C, pH={best_cond[1]:.1f}, d50={best_cond[4]:.0f}µm)"
            return best_cond

        # Draw 5 samples from our current posterior
        q_samples = []
        for _ in range(5):
            q_samples.append(self.q_opt + np.random.normal(0, 0.2, len(self.q_opt)))
            
        best_variance = -1
        best_idx = 0
        best_cond = self.candidate_space[0]
        
        for i, cond in enumerate(self.candidate_space):
            T, pH, C_citric, t_end, d50 = cond
            yield_predictions = []
            try:
                for q in q_samples:
                    theta = self.schema.inverse_transform(q)
                    params = self.schema.unpack(theta)
                    res, _ = run_virtual_experiment(T, pH, C_citric, t_end, params, d50_um=d50)
                    final_yield = res.state.soluble_intact_pectin[-1] + res.state.low_mw_pectin[-1]
                    yield_predictions.append(final_yield)
                    
                var = np.var(yield_predictions)
                if var > best_variance:
                    best_variance = var
                    best_idx = i
                    best_cond = cond
            except Exception:
                continue
                
        self.candidate_space.pop(best_idx)
        self.current_acquisition = f"Max-Variance (Active Learning): Targeted T={best_cond[0]:.0f}°C, pH={best_cond[1]:.1f}, d50={best_cond[4]:.0f}µm to collapse uncertainty."
        return best_cond
        
    def get_status(self):
        # Format chain samples for scatter plots
        samples = []
        if hasattr(self, 'current_chain') and self.current_chain is not None:
            # Take last 150 samples to avoid crushing the UI
            subset = self.current_chain[-150:]
            for row in subset:
                samples.append({name: float(row[i]) for i, name in enumerate(self.param_names)})
                
        # Return all ground truth parameters, not just fitted ones
        true_all = {
            "k_ref_ext": self.truth.k_ref_ext, "Ea_ext": self.truth.Ea_ext, "alpha": self.truth.alpha,
            "k_ref_hyd": self.truth.k_ref_hyd, "Ea_hyd": self.truth.Ea_hyd,
            "k_ref_deg": self.truth.k_ref_deg, "Ea_deg": self.truth.Ea_deg,
            "k_ref_de": self.truth.k_ref_de, "Ea_de": self.truth.Ea_de
        }
        
        # Add the schema aliases (e.g., Ea_degradation) so the MCMC plots can find their "true" markers
        for i, name in enumerate(self.param_names):
            true_all[name] = float(self.theta_true[i])
            
        return {
            "true_params": true_all,
            "posterior_means": {name: float(self.posterior_means[i]) for i, name in enumerate(self.param_names)},
            "posterior_stds": {name: float(self.posterior_stds[i]) for i, name in enumerate(self.param_names)},
            "posterior_samples": samples,
            "mape": float(calculate_error(self.posterior_means, self.theta_true)),
            "runs_completed": len(self.history),
            "runs_remaining": self.runs_allowed - len(self.history),
            "acquisition_rationale": self.current_acquisition
        }
        
    def step(self):
        if len(self.history) >= self.runs_allowed or not self.candidate_space:
            return {"error": "Campaign finished"}
            
        # 1. Optimal Experimental Design (OED)
        cond = self._acquisition_function()
        
        # 2. Run Virtual Experiment (True Physics + Noise via FMU)
        obs = generate_experiment_data(cond, self.schema.unpack(self.theta_true), fmu_runner=self.fmu_runner)
        self.history.append(obs)
        
        # 3. Bayesian Inference (MCMC)
        # Using a fast 300 step chain for UI responsiveness. 
        # In a real lab, this would run for 100k steps overnight.
        theta_chain, valid_chain, acc_rate = run_mcmc(
            self.history, self.q_opt, self.schema, sigma_prop=self.current_q_std, n_steps=300, burn_in=100
        )
        
        # Save chain for UI correlation plots
        self.current_chain = theta_chain
        
        # Adaptive MCMC: update proposal width based on observed standard deviation
        # Scale to ensure optimal acceptance rate, clip to avoid stuck chain
        new_q_std = np.std(valid_chain, axis=0)
        self.current_q_std = np.clip(new_q_std * 0.5, 1e-3, 0.1)
        
        # 4. Update Beliefs
        self.posterior_means = np.mean(theta_chain, axis=0)
        self.posterior_stds = np.std(theta_chain, axis=0)
        
        # Keep track of the MAP/Mean in q-space for the next MCMC initialization
        self.q_opt = self.schema.transform(self.posterior_means)
        
        return {
            "experiment": obs["condition"],
            "status": self.get_status()
        }

    def analyze_identifiability(self, n_steps=8000, burn_in=1000):
        # Run a high-density chain
        theta_chain, valid_chain, acc_rate = run_mcmc(
            self.history, 
            self.q_opt, 
            self.schema,
            sigma_prop=self.current_q_std, 
            n_steps=n_steps, 
            burn_in=burn_in
        )
        
        corr_matrix = np.corrcoef(theta_chain, rowvar=False)
        
        pairs = []
        n_params = len(self.param_names)
        for i in range(n_params):
            for j in range(i+1, n_params):
                pairs.append((np.abs(corr_matrix[i, j]), i, j, corr_matrix[i, j]))
                
        pairs.sort(reverse=True, key=lambda x: x[0])
        top_pairs = pairs[:3]
        
        sns.set_theme(style="darkgrid")
        fig, axes = plt.subplots(1, 3, figsize=(18, 5))
        fig.suptitle(f"Structural Identifiability Analysis (8,000 steps, Acc: {acc_rate*100:.1f}%)", fontsize=16)
        
        for idx, (abs_r, i, j, r) in enumerate(top_pairs):
            ax = axes[idx]
            x_data = theta_chain[:, i]
            y_data = theta_chain[:, j]
            
            sns.kdeplot(x=x_data, y=y_data, cmap="rocket_r", fill=True, ax=ax)
            
            true_x = self.theta_true[i]
            true_y = self.theta_true[j]
            ax.plot(true_x, true_y, marker='*', color='cyan', markersize=12, label='True Value')
            
            ax.set_title(f"r = {r:.3f}")
            ax.set_xlabel(self.param_names[i])
            ax.set_ylabel(self.param_names[j])
            if idx == 0:
                ax.legend()

        plt.tight_layout()
        
        top_pairs_formatted = [
            {
                "param1": self.param_names[i],
                "param2": self.param_names[j],
                "r": float(r)
            }
            for _, i, j, r in top_pairs
        ]
        
        return fig, top_pairs_formatted
