module Sensors

using LinearAlgebra
using Statistics

export ProxyObservationModel, default_synthetic_covariance, compute_fim

"""
    ProxyObservationModel

Represents the secondary measurement model mapping true/latent physicochemical
states to cheap empirical proxies with an observation error covariance matrix.
"""
struct ProxyObservationModel{T<:Real}
    # Labels: [:Y_p, :DE, :Mw, :X_GalA]
    mean_bias::Vector{T}
    covariance::Matrix{T}
end

"""
    default_synthetic_covariance()

Returns the initial synthetic measurement covariance matrix used before Phase 1 proxy calibration:
- Yield: sigma = 1% (0.01)
- DE: sigma = 2% (0.02)
- Mw: sigma = 15,000 Da
- GalA: sigma = 2.5% (0.025)
"""
function default_synthetic_covariance()
    sigmas = [0.01, 0.02, 15000.0, 0.025]
    return diagm(sigmas .^ 2)
end

"""
    compute_fim(sensitivities::Matrix{<:Real}, cov_proxy::Matrix{<:Real})

Computes the Fisher Information Matrix (FIM) for OED re-targeting:
    F = S^T * inv(Σ_proxy) * S
Where:
- `S` is the sensitivity matrix (d y / d θ) of size (N_measurements x N_parameters)
- `cov_proxy` is the empirical measurement error covariance matrix (Σ_proxy)
"""
function compute_fim(sensitivities::AbstractMatrix{<:Real}, cov_proxy::AbstractMatrix{<:Real})
    inv_cov = inv(cov_proxy)
    return sensitivities' * inv_cov * sensitivities
end

end # module Sensors
