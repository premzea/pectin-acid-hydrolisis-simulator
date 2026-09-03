module UDEDiscrepancy

using ModelingToolkit
using LinearAlgebra

export build_ude_discrepancy_system

"""
    build_ude_discrepancy_system(neural_network_surrogate; name=:ude_pectin_reactor)

Constructs a hybrid Mechanistic + Neural Discrepancy (Universal Differential Equation)
system in ModelingToolkit.

The mechanistic backbone enforces mass conservation across the primary pools,
while the embedded surrogate NN_delta(T, pH, P_lowMW, t) captures unmodeled
secondary degradation and precipitation bias:
    d(P_lowMW)/dt = k_hyd * P_sol - k_deg * P_lowMW - NN_delta(...)
    d(P_loss)/dt   = k_deg * P_lowMW + NN_delta(...)
"""
function build_ude_discrepancy_system(nn_loss_modifier; name=:ude_pectin_reactor)
    @independent_variables t
    D = Differential(t)
    
    @variables begin
        P_matrix(t) = 0.2333
        P_sol(t) = 0.0
        P_lowMW(t) = 0.0
        P_loss(t) = 0.0
        delta_loss(t) = 0.0
    end
    
    @parameters begin
        k_ext = 0.035
        k_hyd = 0.015
        k_deg = 0.005
        T_c = 80.0
        pH = 2.0
    end
    
    eqs = [
        D(P_matrix) ~ -k_ext * P_matrix,
        D(P_sol)    ~ k_ext * P_matrix - k_hyd * P_sol,
        # The neural discrepancy dynamically adjusts the rate between LowMW and Loss
        delta_loss  ~ nn_loss_modifier(T_c, pH, P_lowMW),
        D(P_lowMW)  ~ k_hyd * P_sol - k_deg * P_lowMW - delta_loss,
        D(P_loss)   ~ k_deg * P_lowMW + delta_loss
    ]
    
    return ODESystem(eqs, t; name=name)
end

end # module UDEDiscrepancy
