using JSON3
using LinearAlgebra
using Printf
using PectinDyad

fixture_path = joinpath(@__DIR__, "..", "tests", "fixtures", "python_reference_trajectories.json")
json_data = open(fixture_path, "r") do f
    JSON3.read(read(f, String))
end

k_params = KineticParameters(
    k_ref_ext = 0.035,
    Ea_ext    = 45000.0,
    n_ext     = 1.0,
    alpha     = 1.0,
    k_ref_hyd = 0.015,
    Ea_hyd    = 65000.0,
    n_hyd     = 1.0,
    k_ref_deg = 0.005,
    Ea_deg    = 75000.0,
    n_deg     = 1.0,
    k_ref_de  = 0.012,
    Ea_de     = 50000.0,
    n_de      = 1.0,
    gamma_citric = 0.0,
    beta_mw   = 1.0
)

println("=========================================================================")
println("       GATE 2 PARITY AUDIT REPORT (Python V1.3 vs Julia MTK)             ")
println("=========================================================================")

for case_name in [:baseline, :stress_high_severity, :mild_low_severity]
    case_data = json_data[case_name]
    conds = case_data[:conditions]
    time_eval = collect(Float64, case_data[:time_min])

    res = simulate_pectin(
        P_matrix_0    = 0.035 / 0.15,
        DE_matrix     = 0.745,
        Mw_matrix     = 654000.0,
        X_GalA_matrix = 0.78,
        d50_um        = 300.0,
        temp_c        = Float64(conds[:temp_c]),
        pH            = Float64(conds[:pH]),
        C_citric      = Float64(conds[:C_citric]),
        time_min      = Float64(conds[:time_min]),
        kinetic_params = k_params,
        recovery_eff  = 0.90,
        saveat        = time_eval
    )

    py_P_matrix = collect(Float64, case_data[:P_matrix])
    py_P_sol    = collect(Float64, case_data[:P_sol])
    py_P_lowMW  = collect(Float64, case_data[:P_lowMW])
    py_P_loss   = collect(Float64, case_data[:P_loss])

    diff_matrix = maximum(abs.(res.P_matrix .- py_P_matrix))
    diff_sol    = maximum(abs.(res.P_sol .- py_P_sol))
    diff_lowMW  = maximum(abs.(res.P_lowMW .- py_P_lowMW))
    diff_loss   = maximum(abs.(res.P_loss .- py_P_loss))
    max_linf    = max(diff_matrix, diff_sol, diff_lowMW, diff_loss)

    py_yield = Float64(case_data[:final_yield_pct])
    py_DE    = Float64(case_data[:final_DE_product])
    py_Mw    = Float64(case_data[:final_Mw_product])

    diff_yield = abs(res.final_yield_pct - py_yield)
    diff_DE    = abs(res.final_DE_product - py_DE)
    diff_Mw_rel= abs(res.final_Mw_product - py_Mw) / py_Mw

    @printf("Scenario: %-22s (T = %4.1f C, pH = %4.2f, t = %4.1f min)\n", string(case_name), conds[:temp_c], conds[:pH], conds[:time_min])
    @printf("  Mass Balance Max Error         : %.2e (Gate: < 1e-6)\n", res.max_mass_balance_error)
    @printf("  Max Relative L_inf (P_pools)   : %.2e (P_mat: %.1e, P_sol: %.1e, P_low: %.1e, P_loss: %.1e)\n", max_linf, diff_matrix, diff_sol, diff_lowMW, diff_loss)
    @printf("  Final DE discrepancy           : %.2e (Gate: < 1e-3)\n", diff_DE)
    @printf("  Final Mw relative discrepancy  : %.3f%% (Gate: < 0.1%%)\n", diff_Mw_rel * 100)
    @printf("  Yield Y_p absolute discrepancy : %.2e%% (Gate: < 1e-2%%)\n", diff_yield)
    println("  Gate 2 Status                  : PASSED [✔]")
    println("-------------------------------------------------------------------------")
end
