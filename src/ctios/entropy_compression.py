# SPDX-License-Identifier: MIT
"""ctios.entropy_compression — deterministic compression of a noisy
observable into a compact inferential state, verified hard.

The task: take a high-entropy linear series (the realised intervals — a
"biological-like" noisy signal, label only, NOT a biological claim) and
compress it deterministically into a fixed, small inferential state that
still carries the one thing that matters — the hidden regime rupture —
while discarding the noise.

A representation is admitted only if it survives hard verification:

* deterministic     — same input -> byte-identical state, always;
* compressive       — k_out scalars, k_out << n_in, fewer bits out than in;
* task-retaining     — the rupture stays detectable from the state alone;
* noise-rejecting    — a rupture-free series yields a strictly lower change
                       score than a ruptured one (no hallucinated structure);
* honest            — it exposes the entropy it threw away (`residual_std`).

This is representational compression (contract STAGE: representation value
function), not lossless coding: it keeps task-relevant information and
drops the rest, and it says how much it dropped.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

# Number of scalars in a CompressedState — the fixed output dimension.
K_OUT = 6


def shannon_bits(x: np.ndarray, n_bins: int = 64) -> float:
    """Total Shannon content of ``x`` in bits, via a fixed-edge histogram.

    Deterministic: edges span [min, max] in ``n_bins`` equal cells. Returns
    ``N * H`` where ``H`` is the per-symbol entropy in bits. A constant
    series has H = 0 bits.
    """
    a = np.asarray(x, dtype=np.float64).ravel()
    n = a.size
    if n == 0:
        return 0.0
    lo, hi = float(a.min()), float(a.max())
    if hi <= lo:
        return 0.0
    counts, _ = np.histogram(a, bins=n_bins, range=(lo, hi))
    p = counts[counts > 0] / n
    h_per_symbol = float(-np.sum(p * np.log2(p)))
    return h_per_symbol * n


@dataclass(frozen=True)
class CompressedState:
    """A compact, inspectable inferential state. Exactly ``K_OUT`` scalars."""

    n_in: int
    mean: float
    pe_energy: float  # mean squared prediction error (the adaptive signal)
    change_index: int  # argmax split point — the inferred T*
    change_score: float  # standardized two-segment mean shift at the split
    residual_std: float  # the entropy deliberately discarded (honesty term)

    @property
    def k_out(self) -> int:
        return K_OUT

    def as_vector(self) -> np.ndarray:
        return np.array(
            [
                float(self.n_in),
                self.mean,
                self.pe_energy,
                float(self.change_index),
                self.change_score,
                self.residual_std,
            ],
            dtype=np.float64,
        )


def _causal_prediction_error(a: np.ndarray, window: int) -> np.ndarray:
    """Prediction error from a causal rolling mean: predict sample t from the
    mean of the preceding ``window`` samples. Index 0 has no past -> error 0.
    Deterministic, no leakage of the future."""
    n = a.size
    err = np.zeros(n, dtype=np.float64)
    csum = np.concatenate(([0.0], np.cumsum(a)))
    for t in range(1, n):
        lo = max(0, t - window)
        pred = (csum[t] - csum[lo]) / (t - lo)
        err[t] = a[t] - pred
    return err


def _best_split(a: np.ndarray) -> tuple[int, float]:
    """Find the split index maximizing the mean shift standardized by the
    *within-segment* spread. Returns (index, score). Deterministic argmax
    (first on ties).

    Normalizing by within-segment std (not the global std, which the shift
    itself inflates) makes the statistic large for a real rupture and small
    for a rupture-free series — the separation the task needs.
    """
    n = a.size
    if n < 4:
        return 0, 0.0
    csum = np.concatenate(([0.0], np.cumsum(a)))
    csum2 = np.concatenate(([0.0], np.cumsum(a * a)))
    total, total2 = csum[-1], csum2[-1]
    best_i, best_score = 0, -1.0
    min_seg = max(8, n // 20)  # ignore edge splits whose tiny segments
    for i in range(min_seg, n - min_seg):  # would inflate the statistic
        nl, nr = i, n - i
        left = csum[i] / nl
        right = (total - csum[i]) / nr
        var_l = max(csum2[i] / nl - left * left, 0.0)
        var_r = max((total2 - csum2[i]) / nr - right * right, 0.0)
        within = ((var_l * nl + var_r * nr) / n) ** 0.5 + 1e-12
        score = abs(left - right) / within
        if score > best_score:
            best_i, best_score = i, score
    return best_i, float(best_score)


def compress(series: np.ndarray, *, window: int = 16) -> CompressedState:
    """Compress a 1-D series into a deterministic ``CompressedState``."""
    a = np.asarray(series, dtype=np.float64).ravel()
    if a.size == 0:
        raise ValueError("cannot compress an empty series")
    err = _causal_prediction_error(a, window)
    idx, score = _best_split(a)
    # residual = what the two-segment model does NOT explain (discarded entropy)
    if 0 < idx < a.size:
        resid = np.concatenate(
            [a[:idx] - a[:idx].mean(), a[idx:] - a[idx:].mean()]
        )
    else:
        resid = a - a.mean()
    return CompressedState(
        n_in=int(a.size),
        mean=float(a.mean()),
        pe_energy=float(np.mean(err**2)),
        change_index=int(idx),
        change_score=float(score),
        residual_std=float(np.std(resid)),
    )


def compression_ratio(series: np.ndarray, state: CompressedState,
                      n_bins: int = 64) -> float:
    """bits_in / bits_out. > 1 means the state is smaller than the raw signal.

    bits_in is the Shannon content of the raw series; bits_out is the state
    stored as ``K_OUT`` float64 scalars.
    """
    bits_in = shannon_bits(series, n_bins)
    bits_out = float(state.k_out * 64)
    if bits_out <= 0:
        return 0.0
    return bits_in / bits_out


def discriminates(ruptured: np.ndarray, flat: np.ndarray, *,
                 window: int = 16) -> float:
    """Verification margin: change_score(ruptured) - change_score(flat).

    Positive means the compressed state retains the rupture while rejecting
    a rupture-free series — the core task-retention guarantee.
    """
    return (compress(ruptured, window=window).change_score
            - compress(flat, window=window).change_score)
