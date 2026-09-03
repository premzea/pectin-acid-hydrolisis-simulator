module PectinDyad

include("kinetics.jl")
include("components/reaction_network.jl")
include("components/sensors.jl")
include("surrogates/ude_discrepancy.jl")
include("simulator.jl")

using .Kinetics
using .ReactionNetwork
using .Sensors
using .UDEDiscrepancy
using .Simulator

export 
    # Kinetics
    KineticParameters, RateConstants, calculate_rate_constants,
    # MTK Components
    build_pectin_system, PectinFeedstockInput,
    # Sensors & FIM
    ProxyObservationModel, default_synthetic_covariance, compute_fim,
    # UDE
    build_ude_discrepancy_system,
    # Simulator
    DyadSimulationResult, simulate_pectin

end # module PectinDyad
