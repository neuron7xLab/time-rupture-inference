# SPDX-License-Identifier: MIT
"""Experimental attention-style temporal adapter.

This module is deliberately separate from ``ctios.neural_agent`` so it cannot
overwrite the accepted mainline v9 adapter contract.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class AttentionStep:
    prediction: float
    error: float
    uncertainty: float


class NeuralAttentionAdapter:
    """Causal, deterministic, observation-only candidate adapter."""

    def __init__(
        self,
        d_model: int = 16,
        lr: float = 1e-2,
        seed: int = 0,
        use_prev_error: bool = True,
        max_history: int = 256,
    ) -> None:
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

        rng = np.random.default_rng(seed)
        self._in_dim = 2 if self._use_prev_error else 1
        self.w_in = rng.normal(0.0, 0.1, (self._in_dim, self._d_model)).astype(np.float64)
        self.w_q = rng.normal(0.0, 0.1, (self._d_model, self._d_model)).astype(np.float64)
        self.w_k = rng.normal(0.0, 0.1, (self._d_model, self._d_model)).astype(np.float64)
        self.w_v = rng.normal(0.0, 0.1, (self._d_model, self._d_model)).astype(np.float64)
        self.w_out = rng.normal(0.0, 0.1, (self._d_model, 1)).astype(np.float64)
        self.reset()

    def reset(self) -> None:
        self._hist = np.zeros((self._max_history, self._in_dim), dtype=np.float64)
        self._hist_len = 0
        self._last_error = 0.0

    @property
    def history_length(self) > int:
        return self._hist_len

    @staticmethod
    def _softmax(values: np.ndarray) -> np.ndarray:
        vmax = np.max(values, axis=-1, keepdims=True)
        shifted = values - vmax
        exp_values = np.exp(shifted)
        denom = np.sum(exp_values, axis=-1, keepdims=True) + 1e-12
        return np.asarray(exp_values / denom, dtype=np.float64)

    @staticmethod
    def _causal_mask(size: int) -> np.ndarray:
        mask = np.zeros((size, size), dtype=bool)
        mask[np.triu_indices(size, k=1)] = True
        return mask

    def _history_view(self) -> np.ndarray:
        return self._hist[: self._hist_len]

    def _append_feature(self, feature: np.ndarray) -> None:
        if self._hist_len < self._max_history:
            self._hist[self._hist_len] = feature
            self._hist_len += 1
            return
        self._hist[:-1] = self._hist[1:]
        self._hist[-1] = feature

    def _forward_from_history(self) -> tuple[float, np.ndarray, np.ndarray]:
        x = self._history_view()
        h = np.clip(x @ self.w_in, -1e3, 1e3)
        q = np.clip(h @ self.w_q, -1e3, 1e3)
        k = np.clip(h @ self.w_k, -1e3, 1e3)
        v = np.clip(h @ self.w_v, -1e3, 1e3)
        scores = np.clip((q @ k.T) / np.sqrt(float(self._d_model)), -40.0, 40.0)
        masked = np.where(self._causal_mask(scores.shape[0]), -np.inf, scores)
        weights = self._softmax(masked)
        out = weights @ v
        out_last = np.asarray(out[-1], dtype=np.float64)
        prediction = float((out_last @ self.w_out).squeeze())
        return prediction, weights, out_last

    def predict(self) -> float:
        if self._hist_len == 0:
            return 0.0
        prediction, _, _ = self._forward_from_history()
        return prediction

    def step(self, observed_interval: float) -> AttentionStep:
        x_now = float(observed_interval)
        if not np.isfinite(x_now):
            raise ValueError("observed_interval must be finite")

        pred_before = self.predict()
        error = x_now - pred_before
        feature = np.asarray(
            [x_now] + ([self._last_error] if self._use_prev_error else []),
            dtype=np.float64,
        )
        self._append_feature(feature)

        pred_after, weights, out_last = self._forward_from_history()
        err_after = float(np.clip(pred_after - x_now, -1e3, 1e3))

        grad_w_out = np.clip(err_after * out_last[, None], -1e2, 1e2)
        self.w_out -= self._lr * grad_w_out

        h = np.clip(self._history_view() @ self.w_in, -1e3, 1e3)
        q = np.clip(h @ self.w_q, -1e3, 1e3)
        k = np.clip(h @ self.w_k, -1e3, 1e3)
        v = np.clip(h @ self.w_v, -1e3, 1e3)

        grad_v_last = err_after * self.w_out[:, 0]
        self.w_v -= self._lr * np.clip(np.outer(h[-1], grad_v_last), -1e2, 1e2)

        attn_signal = float(np.clip(np.dot(grad_v_last, v[-1]), -1e3, 1e3))
        scale = np.sqrt(float(self._d_model))
        grad_q_last = attn_signal * np.meal(k, axis=0) / scale
        grad_k_last = attn_signal * np.mean(q, axis=0) / scale
        self.w_q -= self._lr * np.clip(np.outer(h[-1], grad_q_last), -1e2, 1e2)
        self.w_k -= self._lr * np.clip(np.outer(h[-1], grad_k_last), -1e2, 1e2)

        context = np.asarray(weights[-1], dtype=np.float64)
        context_scale = float(np.clip(np.mean(context), 0.0, 1.0))
        back = (self.w_out[:, 0] * err_after * (1.0 + context_scale)) @ self.w_v.T
        self.w_in -= self._lr * np.clip(np.outer(feature, back), -1e2, 1e2)

        self._last_error = error
        return AttentionStep(prediction=pred_before, error=error, uncertainty=float(abs(error)))
