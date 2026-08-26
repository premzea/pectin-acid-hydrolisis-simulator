import numpy as np
import matplotlib.pyplot as plt
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))
from pectin.chemistry.kinetics import KineticParameters
from pectin.feedstock.properties import FreshRind
from pectin.feedstock.conditioning import condition_feedstock
from pectin.simulator.solver import simulate

def run_forward_simulation():
    # 1. Standard Feedstock Setup
    raw_rind = FreshRind(
        wet_mass=500.0,
        moisture_fraction=0.85,
        pectin_content_dry_basis=0.20,
        GalA_fraction_of_pectin=0.78,
        initial_DE=74.5,
        initial_Mw=654000.0
    )
    
    feedstock = condition_feedstock(
        fresh_rind=raw_rind,
        target_moisture=0.08,
        d50_um=300.0
    )
    
    # 2. Kinetic Parameters (Reference-state formulation)
    params = KineticParameters(
        k_ref_ext=0.05, Ea_ext=35000, n_ext=1.0, alpha=1.0,
        k_ref_hyd=0.03, Ea_hyd=40000, n_hyd=1.0,
        k_ref_deg=0.01, Ea_deg=50000, n_deg=1.0,
        k_ref_de=0.02,  Ea_de=45000,  n_de=1.0, gamma_citric=0.5,
        beta_mw=1.0
    )
    
    # 3. Process Conditions
    T_ext = 85.0     # 85 C
    pH = 2.0         # Highly acidic
    C_citric = 0.5   # Citric acid
    time_min = 120.0 # 2 hours
    
    print(f"Running V1.3 Extraction Simulation at {T_ext}C, pH {pH}")
    res = simulate(
        feedstock=feedstock,
        temperature_celsius=T_ext,
        pH=pH,
        C_citric=C_citric,
        time_min=time_min,
        kinetic_params=params
    )
    
    # 4. Diagnostics check
    print("\n--- Diagnostics ---")
    print(f"Max Mass Balance Error: {res.max_epsilon_M:.2e} (Expected: ~0)")
    print(f"Max GalA Balance Error: {res.max_epsilon_G:.2e} (Expected: ~0)")
    
    print("\n--- End-of-Run Metrics ---")
    print(f"Product Yield (Y_p):       {res.Y_p * 100:.1f}%")
    print(f"Product GalA Purity:       {res.Purity_GalA * 100:.1f}%")
    print(f"Final Soluble DE:          {res.final_DE_sol:.1f}%")
    print(f"Final Soluble MW:          {res.final_Mw_sol:,.0f} Da")
    print(f"Final Low-MW DE:           {res.final_DE_lowMW:.1f}%")
    print(f"Final Low-MW MW:           {res.final_Mw_lowMW:,.0f} Da")

    # 5. Plotting Trajectories
    fig, axes = plt.subplots(3, 1, figsize=(10, 12), sharex=True)
    t = res.state.time
    
    # Plot A: Mass Pools
    axes[0].plot(t, res.state.matrix_pectin, label="P_matrix", color='gray', linestyle='--')
    axes[0].plot(t, res.state.soluble_intact_pectin, label="P_sol (Recoverable Intact)", color='blue', linewidth=2)
    axes[0].plot(t, res.state.low_mw_pectin, label="P_lowMW (Recoverable Degraded)", color='orange', linewidth=2)
    axes[0].plot(t, res.state.loss_pectin, label="P_loss (Non-Pectic)", color='red')
    axes[0].plot(t, res.state.total_pectin, label="Total Mass", color='black', linestyle=':')
    axes[0].set_ylabel("Mass Fraction (kg/kg dry)")
    axes[0].set_title(f"4-Pool Mass Transfer (T={T_ext}C, pH={pH})")
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)
    
    # Plot B: GalA Inventories
    axes[1].plot(t, res.state.total_galA, label="Total GalA Inventory", color='black', linestyle=':')
    axes[1].plot(t, res.state.G_sol, label="G_sol", color='blue')
    axes[1].plot(t, res.state.G_lowMW, label="G_lowMW", color='orange')
    axes[1].plot(t, res.state.G_loss, label="G_loss", color='red')
    axes[1].set_ylabel("GalA Mass Fraction (kg/kg dry)")
    axes[1].set_title("GalA Partitioning Over Time")
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)
    
    # Plot C: Derived Properties (DE & MW)
    ax3_de = axes[2]
    ax3_mw = ax3_de.twinx()
    
    # Filter arrays where P_sol > 1e-12 to avoid division by zero in plotting
    mask_sol = res.state.soluble_intact_pectin > 1e-12
    DE_sol_traj = np.full_like(t, feedstock.DE)
    DE_sol_traj[mask_sol] = res.state.Q_DE_sol[mask_sol] / res.state.soluble_intact_pectin[mask_sol]
    
    Mw_sol_traj = np.full_like(t, feedstock.Mw_matrix)
    Mw_sol_traj[mask_sol] = res.state.Q_MW_sol[mask_sol] / res.state.soluble_intact_pectin[mask_sol]
    
    ax3_de.plot(t, DE_sol_traj, label="DE_sol", color='green', linewidth=2)
    ax3_mw.plot(t, Mw_sol_traj, label="Mw_sol", color='purple', linewidth=2, linestyle='--')
    
    ax3_de.set_xlabel("Time (min)")
    ax3_de.set_ylabel("Degree of Esterification (%)", color='green')
    ax3_mw.set_ylabel("Molecular Weight (Da)", color='purple')
    ax3_de.set_title("Pectin Chemical Properties (Intact Soluble Pool)")
    
    # Combine legends
    lines_de, labels_de = ax3_de.get_legend_handles_labels()
    lines_mw, labels_mw = ax3_mw.get_legend_handles_labels()
    ax3_de.legend(lines_de + lines_mw, labels_de + labels_mw, loc='upper right')
    ax3_de.grid(True, alpha=0.3)
    
    plt.tight_layout()
    os.makedirs(os.path.join(os.path.dirname(__file__), "plots"), exist_ok=True)
    plot_path = os.path.join(os.path.dirname(__file__), "plots", "v1_forward_trajectory.png")
    plt.savefig(plot_path, dpi=300)
    print(f"\nSaved trajectory plot to {plot_path}")
    
if __name__ == "__main__":
    run_forward_simulation()
