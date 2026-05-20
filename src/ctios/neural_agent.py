# SPDX-License-Identifier: MIT
"""Small white-box neural temporal adapter (causal, deterministic, obs-only)."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class NeuralStep:
    prediction: float
    error: float
    uncertainty: float


class NeuralTemporalAdapter:
    def __init__(
        self,
        d_model: int = 16,
        lr: float = 1e-2,
        seed: int = 0,
        use_prev_error: bool = True,
        max_history: int = 256,
    ) -> None:
        r = np.random.default_rng(seed)
        self._d_model = int(d_model)
        self._lr = float(lr)
        self._use_prev_error = bool(use_prev_error)
        self._max_history = int(max_history)
        if self._d_model < 1:
            raise ValueError("d_model must be >= 1")
        if not np.isfinite(self._lr) or self._lr <= 0.0:
            raise ValueError("lr must be finite and > 0")
        if self._max_history < 1:
            raise ValueError("max_history must be >= 1")

        self._in_dim = 2 if self._use_prev_error else 1
        self.W_in = r.normal(0.0, 0.1, (self._in_dim, self._d_model)).astype(np.float64)
        self.W_q = r.normal(0.0, 0.1, (self._d_model, self._d_model)).astype(np.float64)
        self.W_k = r.normal(0.0, 0.1, (self._d_model, self._d_model)).astype(np.float64)
        self.W_v = r.normal(0.0, 0.1, (self._d_model, self._d_model)).astype(np.float64)
        self.W_out = r.normal(0.0, 0.1, (self._d_model, 1)).astype(np.float64)
        self.reset()

    def reset(self) -> None:
        self._hist = np.zeros((self._max_history, self._in_dim), dtype=np.float64)
        self._hist_len = 0
        self._last_error = 0.0

    @staticmethod
    def _softmax(z: np.ndarray) -> np.ndarray:
        zmax = np.max(z, axis=-1, keepdims=True)
        stable = z - zmax
        ex = np.exp(stable)
        return np.asarray(ex / (np.sum(ex, axis=-1, keepdims=True) + 1e-12), dtype=np.float64)

    @staticmethod
    def _causal_mask(t: int) -> np.ndarray:
        mask = np.zeros((t, t), dtype=bool)
        mask[np.triu_indices(t, k=1)] = True
        return mask

    def _history_view(self) -> np.ndarray:
        return self._hist[: self._hist_len]

    def _append_feature(self, feat: np.ndarray) -> None:
        if self._hist_len < self._max_history:
            self._hist[self._hist_len] = feat
            self._hist_len += 1
            return
        self._hist[:-1] = self._hist[1:]
        self._hist[-1] = feat

    def _forward_from_history(self) -> tuple[float, np.ndarray, np.ndarray]:
        x = self._history_view()
        h = x @ self.W_in
        q = h @ self.W_q
        k = h @ self.W_k
        v = h @ self.W_v
        scores = (q @ k.T) / np.sqrt(float(self._d_model))
        scores = np.clip(scores, -40.0, 40.0)
        masked_scores = np.where(self._causal_mask(scores.shape[0]), -np.inf, scores)
        weights = self._softmax(masked_scores)
        out = weights @ v
        out_last = np.asarray(out[-1], dtype=np.float64)
        pred = float((out_last @ self.W_out).squeeze())
        return pred, weights, out_last

    def predict(self) -> float:
        if self._hist_len == 0:
            return 0.0
        pred, _, _ = self._forward_from_history()
        return pred

    def step(self, observed_interval: float) -> NeuralStep:
        x_now = float(observed_interval)
        if not np.isfinite(x_now):
            raise ValueError("observed_interval must be finite")

        pred_before = self.predict()
        err = x_now - pred_before
        feat = np.asarray([x_now] + ([self._last_error] if self._use_prev_error else []), dtype=np.float64)
        self._append_feature(feat)

        pred_after, _, out_last = self._forward_from_history()
        err_after = pred_after - x_now

        grad_w_out = np.clip(err_after * out_last[:, None], -1e2, 1e2)
        self.W_out -= self._lr * grad_w_out

        back = (self.W_out[:, 0] * err_after) @ self.W_v.T
        grad_w_in = np.clip(np.outer(feat, back), -1e2, 1e2)
        self.W_in -= self._lr * grad_w_in

        self._last_error = err
        return NeuralStep(prediction=pred_before, error=err, uncertainty=float(abs(err)))
