module Simulator

using DifferentialEquations
using ModelingToolkit
using ..Kinetics
using ..ReactionNetwork

export DyadSimulationResult, simulate_pectin

"""
    DyadSimulationResult

Full simulation output matching Python's SimulationResult struct.
"""
struct DyadSimulationResult
    time::Vector{Float64}
    P_matrix::Vector{Float64}
    P_sol::Vector{Float64}
    P_lowMW::Vector{Float64}
    P_loss::Vector{Float64}
    
    Q_DE_sol::Vector{Float64}
    Q_DE_lowMW::Vector{Float64}
    Q_MW_sol::Vector{Float64}
    Q_MW_lowMW::Vector{Float64}
    
    G_sol::Vector{Float64}
    G_lowMW::Vector{Float64}
    G_loss::Vector{Float64}
    
    P_tot::Vector{Float64}
    max_mass_balance_error::Float64
    
    final_yield_pct::Float64
    final_DE_product::Float64
    final_Mw_product::Float64
end

"""
    simulate_pectin(; feedstock, temp_c, pH, C_citric, time_min, kinetic_params, recovery_eff=0.90)

Runs a high-performance simulation of the V1.3 pectin extraction cascade.
"""
function simulate_pectin(;
    P_matrix_0::Float64,
    DE_matrix::Float64,
    Mw_matrix::Float64,
    X_GalA_matrix::Float64,
    d50_um::Float64,
    temp_c::Float64,
    pH::Float64,
    C_citric::Float64,
    time_min::Float64,
    kinetic_params::KineticParameters,
    recovery_eff::Float64 = 0.90,
    Mw_min::Float64 = 10000.0,
    saveat::Union{Nothing, AbstractVector} = nothing
)
    T_kelvin = temp_c + 273.15
    rates = calculate_rate_constants(T_kelvin, pH, C_citric, d50_um, kinetic_params)
    
    # 11 dynamic states in standard canonical order:
    # 1: P_matrix, 2: P_sol, 3: P_lowMW, 4: P_loss,
    # 5: Q_DE_sol, 6: Q_DE_lowMW,
    # 7: Q_MW_sol, 8: Q_MW_lowMW,
    # 9: G_sol, 10: G_lowMW, 11: G_loss
    u0 = zeros(Float64, 11)
    u0[1] = P_matrix_0
    
    p = (
        k_ext = rates.k_ext,
        k_hyd = rates.k_hyd,
        k_deg = rates.k_deg,
        k_de = rates.k_de,
        beta_mw = rates.beta_mw,
        DE_matrix = DE_matrix,
        Mw_matrix = Mw_matrix,
        Mw_min = Mw_min,
        X_GalA_matrix = X_GalA_matrix
    )
    
    function pectin_ode!(du, u, p, t)
        P_matrix, P_sol, P_lowMW, P_loss = u[1], u[2], u[3], u[4]
        Q_DE_sol, Q_DE_lowMW = u[5], u[6]
        Q_MW_sol, Q_MW_lowMW = u[7], u[8]
        G_sol, G_lowMW, G_loss = u[9], u[10], u[11]
        
        # Masses
        du[1] = -p.k_ext * P_matrix
        du[2] = p.k_ext * P_matrix - p.k_hyd * P_sol
        du[3] = p.k_hyd * P_sol - p.k_deg * P_lowMW
        du[4] = p.k_deg * P_lowMW
        
        # DE moments
        du[5] = p.k_ext * P_matrix * p.DE_matrix - p.k_de * Q_DE_sol - p.k_hyd * Q_DE_sol
        du[6] = p.k_hyd * Q_DE_sol - p.k_de * Q_DE_lowMW - p.k_deg * Q_DE_lowMW
        
        # MW moments
        du[7] = p.k_ext * P_matrix * p.Mw_matrix - p.k_hyd * Q_MW_sol - p.beta_mw * p.k_hyd * (Q_MW_sol - p.Mw_min * P_sol)
        du[8] = p.k_hyd * Q_MW_sol - p.k_deg * Q_MW_lowMW - p.beta_mw * p.k_deg * (Q_MW_lowMW - p.Mw_min * P_lowMW)
        
        # GalA inventories
        du[9]  = p.k_ext * P_matrix * p.X_GalA_matrix - p.k_hyd * G_sol
        du[10] = p.k_hyd * G_sol - p.k_deg * G_lowMW
        du[11] = p.k_deg * G_lowMW
        
        return nothing
    end
    
    tspan = (0.0, time_min)
    prob = ODEProblem(pectin_ode!, u0, tspan, p)
    
    kwargs = Dict{Symbol, Any}(
        :reltol => 1e-7,
        :abstol => 1e-10
    )
    if saveat !== nothing
        kwargs[:saveat] = saveat
    end
    
    # Solve with high-order stiff solver
    sol = solve(prob, AutoTsit5(Rosenbrock23()); kwargs...)
    
    t_arr = sol.t
    P_matrix_t = [sol[1, i] for i in 1:length(t_arr)]
    P_sol_t    = [sol[2, i] for i in 1:length(t_arr)]
    P_lowMW_t  = [sol[3, i] for i in 1:length(t_arr)]
    P_loss_t   = [sol[4, i] for i in 1:length(t_arr)]
    
    Q_DE_sol_t   = [sol[5, i] for i in 1:length(t_arr)]
    Q_DE_lowMW_t = [sol[6, i] for i in 1:length(t_arr)]
    Q_MW_sol_t   = [sol[7, i] for i in 1:length(t_arr)]
    Q_MW_lowMW_t = [sol[8, i] for i in 1:length(t_arr)]
    
    G_sol_t  = [sol[9, i] for i in 1:length(t_arr)]
    G_lowMW_t= [sol[10, i] for i in 1:length(t_arr)]
    G_loss_t = [sol[11, i] for i in 1:length(t_arr)]
    
    P_tot_t = P_matrix_t .+ P_sol_t .+ P_lowMW_t .+ P_loss_t
    max_err = maximum(abs.(P_matrix_0 .- P_tot_t))
    
    final_sol = P_sol_t[end]
    final_low = P_lowMW_t[end]
    product_mass = recovery_eff * (final_sol + final_low)
    final_yield = product_mass * 100.0 # [%]
    
    final_DE = (final_sol + final_low) > 1e-12 ? 
        (Q_DE_sol_t[end] + Q_DE_lowMW_t[end]) / (final_sol + final_low) : DE_matrix
        
    final_Mw = (final_sol + final_low) > 1e-12 ? 
        (Q_MW_sol_t[end] + Q_MW_lowMW_t[end]) / (final_sol + final_low) : Mw_matrix
        
    return DyadSimulationResult(
        t_arr,
        P_matrix_t, P_sol_t, P_lowMW_t, P_loss_t,
        Q_DE_sol_t, Q_DE_lowMW_t,
        Q_MW_sol_t, Q_MW_lowMW_t,
        G_sol_t, G_lowMW_t, G_loss_t,
        P_tot_t,
        max_err,
        final_yield,
        final_DE,
        final_Mw
    )
end

end # module Simulator
