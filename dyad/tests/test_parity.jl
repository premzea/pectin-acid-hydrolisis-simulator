using Test
using JSON3
using PectinDyad

@testset "Cross-Language Mathematical Parity (Python V1.3 vs. Julia/Dyad)" begin
    fixture_path = joinpath(@__DIR__, "fixtures", "python_reference_trajectories.json")
    @test isfile(fixture_path)
    
    json_data = open(fixture_path, "r") do f
        JSON3.read(read(f, String))
    end
    
    # Standard kinetic parameters matching Python export
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
    
    for case_name in [:baseline, :stress_high_severity, :mild_low_severity]
        @testset "Case: $case_name" begin
            case_data = json_data[case_name]
            conds = case_data[:conditions]
            time_eval = collect(Float64, case_data[:time_min])
            
            # Execute Dyad simulation
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
            
            # Invariant checks
            @test res.max_mass_balance_error < 1e-6
            
            # Trajectory parity checks
            py_P_matrix = collect(Float64, case_data[:P_matrix])
            py_P_sol    = collect(Float64, case_data[:P_sol])
            py_P_lowMW  = collect(Float64, case_data[:P_lowMW])
            py_P_loss   = collect(Float64, case_data[:P_loss])
            
            max_diff_matrix = maximum(abs.(res.P_matrix .- py_P_matrix))
            max_diff_sol    = maximum(abs.(res.P_sol .- py_P_sol))
            max_diff_lowMW  = maximum(abs.(res.P_lowMW .- py_P_lowMW))
            max_diff_loss   = maximum(abs.(res.P_loss .- py_P_loss))
            
            @test max_diff_matrix < 1e-4
            @test max_diff_sol    < 1e-4
            @test max_diff_lowMW  < 1e-4
            @test max_diff_loss   < 1e-4
            
            # End-of-run property parity
            py_yield = Float64(case_data[:final_yield_pct])
            py_DE    = Float64(case_data[:final_DE_product])
            py_Mw    = Float64(case_data[:final_Mw_product])
            
            @test isapprox(res.final_yield_pct, py_yield, atol=1e-2)
            @test isapprox(res.final_DE_product, py_DE, atol=1e-3)
            @test isapprox(res.final_Mw_product, py_Mw, rtol=1e-3)
        end
    end
end
