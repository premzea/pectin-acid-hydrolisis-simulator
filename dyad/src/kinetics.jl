module Kinetics

using LinearAlgebra

export KineticParameters, RateConstants, calculate_rate_constants

"""
    KineticParameters

Parameters for the V1.3 4-pool mass cascade using the reference Arrhenius
formulation (T_ref = 353.15 K, pH_ref = 2.0).
"""
Base.@kwdef struct KineticParameters{T<:Real}
    # Extraction / Solubilization
    k_ref_ext::T
    Ea_ext::T
    n_ext::T = 1.0
    alpha::T = 1.0
    
    # Hydrolysis / Depolymerization
    k_ref_hyd::T
    Ea_hyd::T
    n_hyd::T = 1.0
    
    # Degradation / Loss
    k_ref_deg::T
    Ea_deg::T
    n_deg::T = 1.0
    
    # De-esterification
    k_ref_de::T
    Ea_de::T
    n_de::T = 1.0
    gamma_citric::T = 0.0
    
    # Property sensitivities
    beta_mw::T = 1.0
end

"""
    RateConstants

Effective rate constants evaluated at specific process conditions.
"""
struct RateConstants{T<:Real}
    k_ext::T
    k_hyd::T
    k_deg::T
    k_de::T
    beta_mw::T
end

"""
    calculate_rate_constants(T_kelvin, pH, C_citric, d50_um, params)

Calculate effective rate constants matching the Python V1.3 specification.
"""
function calculate_rate_constants(
    T_kelvin::Real, 
    pH::Real, 
    C_citric::Real, 
    d50_um::Real, 
    params::KineticParameters
)
    @assert T_kelvin > 0 "Temperature must be greater than 0 K"
    @assert d50_um > 0 "Particle size (d50) must be greater than 0 um"
    @assert C_citric >= 0 "Citric acid concentration cannot be negative"
    @assert 0 <= pH <= 14 "pH must be between 0 and 14"

    R = 8.314462618 # J/(mol K)
    T_ref = 353.15  # 80 C
    pH_ref = 2.0
    
    # Mass transfer empirical modifier
    d_ref = 300.0 # um
    phi_d = (d_ref / d50_um)^params.alpha
    
    # Reference Arrhenius equation with numerical safety clamp
    function arrhenius_ref(k_ref, Ea, n)
        arrhenius_arg = -Ea / R * (1.0 / T_kelvin - 1.0 / T_ref)
        clamped_arg = clamp(arrhenius_arg, -50.0, 50.0)
        T_term = exp(clamped_arg)
        pH_term = 10.0^(n * (pH_ref - pH))
        return k_ref * T_term * pH_term
    end
    
    k_ext_chem = arrhenius_ref(params.k_ref_ext, params.Ea_ext, params.n_ext)
    k_ext = k_ext_chem * phi_d
    
    k_hyd = arrhenius_ref(params.k_ref_hyd, params.Ea_hyd, params.n_hyd)
    k_deg = arrhenius_ref(params.k_ref_deg, params.Ea_deg, params.n_deg)
    
    k_de_base = arrhenius_ref(params.k_ref_de, params.Ea_de, params.n_de)
    k_de = k_de_base * (1.0 + params.gamma_citric * C_citric)
    
    return RateConstants(k_ext, k_hyd, k_deg, k_de, params.beta_mw)
end

end # module Kinetics
