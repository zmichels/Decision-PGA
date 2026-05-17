"""Decision-PGA tools for probability clouds on the categorical simplex."""

from .diagnostics import (
    DecisionAction,
    DecisionPGAConfig,
    DecisionPGADiagnostic,
    DecisionState,
    diagnose_probability_cloud,
)
from .model_adapters import (
    ModelOutputDiagnostic,
    ModelOutputObservation,
    ObservationKind,
    diagnose_model_outputs,
    probability_cloud_from_observations,
)
from .probability_pga import (
    ProbabilityPGAResult,
    intrinsic_mean_sphere,
    normalize_probabilities,
    pga_probability_cloud,
    sphere_exp,
    sphere_log,
    sqrt_embed,
    synthetic_probability_cloud,
)
from .provider_bridges import (
    MissingScorePolicy,
    PathPart,
    observation_from_provider_scores,
    observation_from_token_scores,
    observations_from_provider_scores,
)
from .source_adapters import (
    SampledResponse,
    SourceAdapterDiagnostic,
    TrajectoryStep,
    UnknownPolicy,
    diagnose_sampled_responses,
    diagnose_trajectory_steps,
    probability_cloud_from_sampled_responses,
    probability_cloud_from_trajectory_steps,
)

__all__ = [
    "DecisionAction",
    "DecisionPGAConfig",
    "DecisionPGADiagnostic",
    "DecisionState",
    "ModelOutputDiagnostic",
    "ModelOutputObservation",
    "ObservationKind",
    "MissingScorePolicy",
    "PathPart",
    "diagnose_probability_cloud",
    "diagnose_model_outputs",
    "ProbabilityPGAResult",
    "SampledResponse",
    "SourceAdapterDiagnostic",
    "TrajectoryStep",
    "UnknownPolicy",
    "intrinsic_mean_sphere",
    "normalize_probabilities",
    "observation_from_provider_scores",
    "observation_from_token_scores",
    "observations_from_provider_scores",
    "pga_probability_cloud",
    "probability_cloud_from_sampled_responses",
    "probability_cloud_from_observations",
    "probability_cloud_from_trajectory_steps",
    "diagnose_sampled_responses",
    "diagnose_trajectory_steps",
    "sphere_exp",
    "sphere_log",
    "sqrt_embed",
    "synthetic_probability_cloud",
]
