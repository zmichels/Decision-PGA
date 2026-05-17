"""Principal geodesic diagnostics for categorical probability clouds.

The v1 geometry maps probabilities ``p`` to the positive unit sphere with
``sqrt(p)``. This is the standard square-root representation associated with
Fisher-Rao geometry for categorical distributions, up to a constant distance
scale. The implementation intentionally depends only on NumPy so it can become
an agent-callable diagnostic later without a heavy model stack.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import numpy as np


NormalizeMode = Literal["none", "n", "n-1"]


@dataclass(frozen=True)
class ProbabilityPGAResult:
    """Decision-PGA summary for a cloud of categorical distributions."""

    mean_probability: np.ndarray
    tangent_vectors: np.ndarray
    tensor: np.ndarray
    eigenvalues: np.ndarray
    eigenvectors: np.ndarray
    total_dispersion: float
    pc1_fraction: float
    anisotropy_ratio: float
    mean_margin: float
    label: str | None = None


def normalize_probabilities(probs: np.ndarray, eps: float = 1e-12) -> np.ndarray:
    """Return strictly positive row-normalized probability vectors."""

    values = np.asarray(probs, dtype=float)
    if values.ndim == 1:
        values = values[None, :]
    if values.ndim != 2:
        raise ValueError("probs must have shape K or N x K.")
    if values.shape[1] < 2:
        raise ValueError("probability vectors must contain at least two classes.")
    if eps <= 0.0:
        raise ValueError("eps must be positive.")
    if not np.all(np.isfinite(values)):
        raise ValueError("probs must contain only finite values.")
    if np.any(values < 0.0):
        raise ValueError("probs cannot contain negative values.")

    clipped = np.maximum(values, float(eps))
    row_sums = np.sum(clipped, axis=1, keepdims=True)
    if np.any(row_sums <= 0.0):
        raise ValueError("each probability row must have positive mass.")
    return clipped / row_sums


def sqrt_embed(probs: np.ndarray) -> np.ndarray:
    """Map probabilities to the positive unit sphere with ``sqrt(p)``."""

    normalized = normalize_probabilities(probs)
    embedded = np.sqrt(normalized)
    return _normalize_rows(embedded)


def intrinsic_mean_sphere(
    points: np.ndarray,
    tol: float = 1e-10,
    max_iter: int = 100,
) -> np.ndarray:
    """Compute the intrinsic mean of localized points on the unit sphere."""

    sphere_points = _as_sphere_points(points)
    if tol <= 0.0:
        raise ValueError("tol must be positive.")
    if max_iter <= 0:
        raise ValueError("max_iter must be positive.")

    mean = _normalize_vector(np.mean(sphere_points, axis=0))
    for _ in range(max_iter):
        update = np.mean(sphere_log(mean, sphere_points), axis=0)
        if np.linalg.norm(update) <= tol:
            return mean
        mean = sphere_exp(mean, update)
    return mean


def sphere_log(mean: np.ndarray, points: np.ndarray) -> np.ndarray:
    """Log-map unit-sphere points into the tangent space at ``mean``."""

    mean_vector = _normalize_vector(np.asarray(mean, dtype=float))
    sphere_points = _as_sphere_points(points)
    dots = np.clip(sphere_points @ mean_vector, -1.0, 1.0)
    angles = np.arccos(dots)
    tangent = sphere_points - dots[:, None] * mean_vector[None, :]
    tangent_norm = np.linalg.norm(tangent, axis=1)

    scale = np.zeros_like(angles)
    mask = tangent_norm > np.finfo(float).eps
    scale[mask] = angles[mask] / tangent_norm[mask]
    return tangent * scale[:, None]


def sphere_exp(mean: np.ndarray, tangent_vectors: np.ndarray) -> np.ndarray:
    """Exponential-map tangent vectors from ``mean`` back to the unit sphere."""

    mean_vector = _normalize_vector(np.asarray(mean, dtype=float))
    tangent = np.asarray(tangent_vectors, dtype=float)
    single = tangent.ndim == 1
    if single:
        tangent = tangent[None, :]
    if tangent.ndim != 2 or tangent.shape[1] != mean_vector.shape[0]:
        raise ValueError("tangent_vectors must have shape K or N x K.")

    tangent = tangent - (tangent @ mean_vector)[:, None] * mean_vector[None, :]
    norms = np.linalg.norm(tangent, axis=1)
    result = np.empty_like(tangent)
    small = norms <= np.finfo(float).eps
    result[small] = mean_vector
    if np.any(~small):
        unit_tangent = tangent[~small] / norms[~small, None]
        theta = norms[~small]
        result[~small] = (
            np.cos(theta)[:, None] * mean_vector[None, :]
            + np.sin(theta)[:, None] * unit_tangent
        )
    result = _normalize_rows(result)
    return result[0] if single else result


def pga_probability_cloud(
    probs: np.ndarray,
    normalize: NormalizeMode = "n",
    label: str | None = None,
) -> ProbabilityPGAResult:
    """Run PGA-style dispersion analysis on categorical probabilities."""

    probabilities = normalize_probabilities(probs)
    embedded = sqrt_embed(probabilities)
    mean = intrinsic_mean_sphere(embedded)
    tangent_vectors = sphere_log(mean, embedded)
    tensor = tangent_vectors.T @ tangent_vectors
    if normalize == "n":
        tensor = tensor / len(tangent_vectors)
    elif normalize == "n-1":
        if len(tangent_vectors) > 1:
            tensor = tensor / (len(tangent_vectors) - 1)
    elif normalize != "none":
        raise ValueError("normalize must be 'none', 'n', or 'n-1'.")

    eigenvalues, eigenvectors = np.linalg.eigh(tensor)
    order = np.argsort(eigenvalues)[::-1]
    eigenvalues = np.maximum(eigenvalues[order], 0.0)
    eigenvectors = eigenvectors[:, order]
    total_dispersion = float(np.sum(eigenvalues))
    pc1_fraction = float(eigenvalues[0] / total_dispersion) if total_dispersion > 0.0 else 0.0
    if eigenvalues.shape[0] > 1 and eigenvalues[1] > np.finfo(float).eps:
        anisotropy_ratio = float(eigenvalues[0] / eigenvalues[1])
    else:
        anisotropy_ratio = float("inf") if eigenvalues[0] > np.finfo(float).eps else 0.0

    mean_probability = normalize_probabilities(mean**2)[0]
    sorted_mean = np.sort(mean_probability)[::-1]
    mean_margin = float(sorted_mean[0] - sorted_mean[1])
    return ProbabilityPGAResult(
        mean_probability=mean_probability,
        tangent_vectors=tangent_vectors,
        tensor=tensor,
        eigenvalues=eigenvalues,
        eigenvectors=eigenvectors,
        total_dispersion=total_dispersion,
        pc1_fraction=pc1_fraction,
        anisotropy_ratio=anisotropy_ratio,
        mean_margin=mean_margin,
        label=label,
    )


def synthetic_probability_cloud(
    kind: str,
    n_samples: int,
    n_classes: int,
    seed: int | None = None,
) -> np.ndarray:
    """Generate synthetic probability clouds for Decision-PGA examples."""

    if n_samples <= 0:
        raise ValueError("n_samples must be positive.")
    if n_classes < 3:
        raise ValueError("n_classes must be at least 3.")
    rng = np.random.default_rng(seed)
    kind = kind.lower()

    if kind == "stable":
        center = _base_distribution(n_classes, top=0.88, second=0.04)
        return rng.dirichlet(160.0 * center, size=n_samples)

    if kind == "binary_ambiguity":
        axis = rng.beta(0.65, 0.65, size=n_samples)
        cloud = np.full((n_samples, n_classes), 0.11 / (n_classes - 2))
        cloud[:, 0] = 0.17 + 0.66 * axis
        cloud[:, 1] = 0.83 - 0.66 * axis
        noise = rng.dirichlet(np.full(n_classes, 12.0), size=n_samples)
        return normalize_probabilities(0.90 * cloud + 0.10 * noise)

    if kind == "diffuse_uncertainty":
        return rng.dirichlet(np.full(n_classes, 1.0), size=n_samples)

    if kind == "boundary":
        axis = np.linspace(0.1, 0.9, n_samples)
        axis = np.clip(axis + rng.normal(0.0, 0.04, size=n_samples), 0.02, 0.98)
        cloud = np.full((n_samples, n_classes), 0.08 / (n_classes - 2))
        cloud[:, 0] = 0.10 + 0.74 * axis
        cloud[:, 1] = 0.84 - 0.74 * axis
        return normalize_probabilities(cloud)

    if kind == "regime_shift":
        half = n_samples // 2
        first = rng.dirichlet(120.0 * _base_distribution(n_classes, top=0.82, second=0.08), size=half)
        second_center = np.roll(_base_distribution(n_classes, top=0.82, second=0.08), 2)
        second = rng.dirichlet(120.0 * second_center, size=n_samples - half)
        return np.vstack([first, second])

    raise ValueError(
        "kind must be one of 'stable', 'binary_ambiguity', "
        "'diffuse_uncertainty', 'boundary', or 'regime_shift'."
    )


def _base_distribution(n_classes: int, *, top: float, second: float) -> np.ndarray:
    values = np.full(n_classes, (1.0 - top - second) / (n_classes - 2))
    values[0] = top
    values[1] = second
    return normalize_probabilities(values)[0]


def _as_sphere_points(points: np.ndarray) -> np.ndarray:
    values = np.asarray(points, dtype=float)
    if values.ndim == 1:
        values = values[None, :]
    if values.ndim != 2 or values.shape[1] < 2:
        raise ValueError("points must have shape K or N x K with K >= 2.")
    if not np.all(np.isfinite(values)):
        raise ValueError("points must contain only finite values.")
    norms = np.linalg.norm(values, axis=1)
    if np.any(norms <= np.finfo(float).eps):
        raise ValueError("sphere points must be nonzero.")
    return values / norms[:, None]


def _normalize_rows(values: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(values, axis=1, keepdims=True)
    if np.any(norms <= np.finfo(float).eps):
        raise ValueError("rows must be nonzero.")
    return values / norms


def _normalize_vector(value: np.ndarray) -> np.ndarray:
    norm = np.linalg.norm(value)
    if norm <= np.finfo(float).eps:
        raise ValueError("vector must be nonzero.")
    return value / norm
