module ReactionNetwork

using ModelingToolkit
using Symbolics
using ..Kinetics

export build_pectin_system, PectinFeedstockInput

"""
    PectinFeedstockInput

Feedstock initial characteristics for the extraction vessel.
"""
Base.@kwdef struct PectinFeedstockInput{T<:Real}
    P_matrix_0::T      # kg/kg_dry_feed
    DE_matrix::T       # [-]
    Mw_matrix::T       # [Da]
    Mw_min::T = 10000.0# [Da]
    X_GalA_matrix::T   # [-]
    d50_um::T          # [um]
end

"""
    build_pectin_system(; name=:pectin_reactor)

Builds the symbolic ModelingToolkit.jl (MTK) ODESystem for the V1.3 4-pool
pectin acid hydrolysis cascade with mass-weighted property moments.
"""
function build_pectin_system(; name=:pectin_reactor)
    @independent_variables t
    D = Differential(t)
    
    # Dynamic state variables
    @variables begin
        # Normalized 4-Pool Masses [kg / kg_dry_feed]
        P_matrix(t) = 0.2333
        P_sol(t) = 0.0
        P_lowMW(t) = 0.0
        P_loss(t) = 0.0
        
        # De-esterification Moments
        Q_DE_sol(t) = 0.0
        Q_DE_lowMW(t) = 0.0
        
        # Molecular Weight Moments [Da * kg / kg_dry_feed]
        Q_MW_sol(t) = 0.0
        Q_MW_lowMW(t) = 0.0
        
        # Galacturonic Acid Inventories [kg_GalA / kg_dry_feed]
        G_sol(t) = 0.0
        G_lowMW(t) = 0.0
        G_loss(t) = 0.0
        
        # Observables / Algebraic Derived States
        P_tot(t)
        P_product(t)
        DE_sol(t)
        DE_lowMW(t)
        Mw_sol(t)
        Mw_lowMW(t)
        Mw_product(t)
        DE_product(t)
    end
    
    # Process inputs & rate parameters
    @parameters begin
        # Effective rate constants [1/min]
        k_ext = 0.035
        k_hyd = 0.015
        k_deg = 0.005
        k_de = 0.012
        beta_mw = 1.0
        
        # Feedstock constants
        DE_matrix = 0.745
        Mw_matrix = 654000.0
        Mw_min = 10000.0
        X_GalA_matrix = 0.78
        recovery_eff = 0.90
    end
    
    eqs = [
        # 1. Mass Conservation ODEs
        D(P_matrix) ~ -k_ext * P_matrix,
        D(P_sol)    ~ k_ext * P_matrix - k_hyd * P_sol,
        D(P_lowMW)  ~ k_hyd * P_sol - k_deg * P_lowMW,
        D(P_loss)   ~ k_deg * P_lowMW,
        
        # 2. De-esterification Moments
        D(Q_DE_sol)   ~ k_ext * P_matrix * DE_matrix - k_de * Q_DE_sol - k_hyd * Q_DE_sol,
        D(Q_DE_lowMW) ~ k_hyd * Q_DE_sol - k_de * Q_DE_lowMW - k_deg * Q_DE_lowMW,
        
        # 3. Molecular Weight Moments
        D(Q_MW_sol)   ~ k_ext * P_matrix * Mw_matrix - k_hyd * Q_MW_sol - beta_mw * k_hyd * (Q_MW_sol - Mw_min * P_sol),
        D(Q_MW_lowMW) ~ k_hyd * Q_MW_sol - k_deg * Q_MW_lowMW - beta_mw * k_deg * (Q_MW_lowMW - Mw_min * P_lowMW),
        
        # 4. Galacturonic Acid Inventories
        D(G_sol)   ~ k_ext * P_matrix * X_GalA_matrix - k_hyd * G_sol,
        D(G_lowMW) ~ k_hyd * G_sol - k_deg * G_lowMW,
        D(G_loss)  ~ k_deg * G_lowMW,
        
        # 5. Algebraic Invariants & Product Properties
        P_tot ~ P_matrix + P_sol + P_lowMW + P_loss,
        P_product ~ recovery_eff * (P_sol + P_lowMW),
        
        DE_sol ~ ifelse(P_sol > 1e-12, Q_DE_sol / P_sol, DE_matrix),
        DE_lowMW ~ ifelse(P_lowMW > 1e-12, Q_DE_lowMW / P_lowMW, DE_matrix),
        
        Mw_sol ~ ifelse(P_sol > 1e-12, Q_MW_sol / P_sol, Mw_matrix),
        Mw_lowMW ~ ifelse(P_lowMW > 1e-12, Q_MW_lowMW / P_lowMW, Mw_min),
        
        DE_product ~ ifelse((P_sol + P_lowMW) > 1e-12, (Q_DE_sol + Q_DE_lowMW) / (P_sol + P_lowMW), DE_matrix),
        Mw_product ~ ifelse((P_sol + P_lowMW) > 1e-12, (Q_MW_sol + Q_MW_lowMW) / (P_sol + P_lowMW), Mw_matrix)
    ]
    
    return ODESystem(eqs, t; name=name)
end

end # module ReactionNetwork
