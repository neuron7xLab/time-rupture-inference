<!-- claims:disclaimer -->
# NCTP-1 / NeuroChrono Temporal Protocol

## 7 задач на інференс та екстраполяцію (пріоритетне виконання)

---

## Операційна рамка


## Runtime boundary

Current executable runtime is a deterministic baseline scaffold.
TASK-01..04 have prototype implementations.
TASK-05..07 are packet-compatible placeholders only.
No causal, memory-retrieval, or regime-extrapolation validity claim is made.


Цей артефакт фіксує **7 першочергових задач** для обчислень у NCTP-1 та задає
єдиний інференсний пакет, контракти входів/виходів, формули, метрики, acceptance логіку
і мінімальний порядок виконання.

> Формулювання тут є engineering protocol (brain-inspired), а не claims про brain simulation,
> biological neuroplasticity, consciousness або AGI.

---

# TASK-01 — Multi-Horizon Temporal Inference

## Мета
Обчислити прогноз майбутніх станів/значень на горизонтах `H=[1,4,8,16,32,64]`.

## Вхід
```python
X        # FloatTensor[B, T, C]
t        # FloatTensor[B, T]
dt       # FloatTensor[B, T]
mask     # BoolTensor[B, T, C]
context  # Optional[FloatTensor[B, T, K]]
H        # List[int]
```

## Вихід
```python
Y_hat = {
    "h1":  Tensor[B, Y],
    "h4":  Tensor[B, Y],
    "h8":  Tensor[B, Y],
    "h16": Tensor[B, Y],
    "h32": Tensor[B, Y],
    "h64": Tensor[B, Y],
}
```

## Формалізація
```text
ŷ_{T+h} = f(X₁:T, t₁:T, dt₁:T, mask₁:T, context₁:T), h ∈ H
```

## Обчислення
```text
h_t = ChronoEncoder(x_t, t_t, dt_t, mask_t, context_t)
r_t = LocalRhythmBank(h_t)
s_t = MultiScaleTemporalCore(r_t, dt_t)
ŷ_{T+h} = MultiHorizonReadout(s_T, h)
```

## Loss / Metrics
```text
L_forecast = Σ_h w_h · Loss(y_{T+h}, ŷ_{T+h})
Loss ∈ {MAE, Huber, NLL}
Metrics: MAE_h, RMSE_h, sMAPE_h, NLL_h, worst_horizon_error, mean_horizon_error
```

---

# TASK-02 — Precision-Weighted Error Inference

## Мета
Обчислити зважену помилку з урахуванням невизначеності/precision.

## Вхід/Вихід
```python
Y_hat, Y_true, sigma, epsilon=1e-6
error, precision, weighted_error, confidence
```

## Формули
```text
error = Y_true - Y_hat
precision = 1 / (sigma² + epsilon)
weighted_error = precision · error
confidence = sigmoid(-sigma)
```

## Loss / Metrics
```text
L_precision = |empirical_error - predicted_uncertainty|
L_nll = 0.5·log(σ²) + 0.5·((y-μ)²/σ²)
Metrics: ECE, NLL, uncertainty_error_correlation, coverage_probability, sharpness
```

---

# TASK-03 — Drift / Rupture Inference

## Мета
Визначити прихований regime shift (level/variance/rhythm/context/delay).

## Вхід
```python
weighted_error, state_t, state_prev, sigma, dt, memory_conflict
```

## Вихід
```python
drift_score, rupture_label_hat, update_gain, reset_probability, memory_priority
```

## Формалізація
```text
P(rupture_t=1 | error_t, precision_t, Δstate_t, uncertainty_t, dt_t)
Δstate_t = state_t - state_{t-1}
```

## Обчислення
```text
z_t=[weighted_error_t, EMA(error²), Δstate_t, uncertainty_t, dt_t, memory_conflict_t]
drift_score_t = sigmoid(MLP_drift(z_t))
update_gain_t = sigmoid(MLP_gain(z_t))
reset_probability_t = sigmoid(MLP_reset(z_t))
memory_priority_t = sigmoid(MLP_memory(z_t))
```

## Adaptive state update
```text
s_t_adapted = (1-reset_probability_t)·s_t + reset_probability_t·ResetState(s_t)
```

## Metrics
```text
detection_delay, false_alarm_rate, missed_shift_rate, recovery_time,
overshoot, settling_time, post_shift_MAE
```

---

# TASK-04 — Causal-Delay Inference

## Мета
Оцінити через який лаг дія `A_t` впливає на `Y_{t+h}`.

## Вхід/Вихід
```python
state_t, action_t, context_t, H
-> delay_distribution, causal_credit, effect_prediction, causal_effect
```

## Формули
```text
P(delay=h | state_t, action_t, context_t)
ŷ_{t+h} = f(state_t, action_t, h)
Δ_cf_h = ŷ_A - ŷ_A'
```

## Metrics
```text
delay_attribution_accuracy, lag_recovery_error, counterfactual_sensitivity,
action_masking_degradation, intervention_consistency
```

---

# TASK-05 — Episodic Memory Retrieval Inference

## Мета
Знаходити релевантні минулі стани/режими/події для поточного контексту.

## Вхід/Вихід
```python
query_state, memory_keys, memory_values, memory_times, current_time, memory_meta
-> retrieved_state, retrieval_weights, memory_conflict, memory_relevance, write_priority
```

## Формули
```text
score_i = cosine(query,key_i) - λ·|t_now - t_i| + α·priority_i - stale_penalty_i
retrieval_weights = softmax(score)
retrieved_state = Σ_i retrieval_weights_i·memory_value_i
memory_conflict = entropy(retrieval_weights)  або 1-max(retrieval_weights)
```

## Metrics
```text
rare_event_recall, retrieval_precision, old_regime_return_accuracy,
memory_interference_rate, stale_memory_usage
```

---

# TASK-06 — Regime Extrapolation

## Мета
Екстраполювати майбутню траєкторію режиму і latent state.

## Вхід/Вихід
```python
state_t, drift_score_t, memory_state, uncertainty_t, context_t, future_horizons
-> regime_probs, future_regime_path, regime_change_time, extrapolated_state
```

## Режими
```text
{stable, gradual_drift, abrupt_shift, old_regime_return, high_uncertainty, unknown}
```

## Формули
```text
P(regime_{t+h} | state_t, drift_score_t, memory_t, uncertainty_t)
s_{t+h} = ExtrapolateState(s_t, regime_{t+h})
```

## Metrics
```text
regime_classification_accuracy, future_regime_path_accuracy,
change_time_error, post_regime_forecast_MAE, uncertainty_under_shift
```

---

# TASK-07 — Counterfactual Temporal Extrapolation

## Мета
Порахувати майбутню траєкторію під альтернативною дією/подією/режимом.

## Вхід/Вихід
```python
state_t, action_real, action_counterfact, context_t, memory_state, H
-> Y_real_hat, Y_counterfact_hat, counterfactual_delta, causal_effect_score
```

## Формули
```text
ŷ_real_{t+h} = f(s_t, A_real, context_t, h)
ŷ_cf_{t+h}   = f(s_t, A_cf,   context_t, h)
Δ_cf_h       = ŷ_cf_{t+h} - ŷ_real_{t+h}
```

## Metrics
```text
counterfactual_accuracy, intervention_consistency, action_effect_sensitivity,
delayed_effect_score, causal_delta_stability
```

---

# Уніфікований обчислювальний граф (7 задач)

```text
Input Temporal Stream
  -> ChronoEncoder
  -> LocalRhythmBank
  -> MultiScaleTemporalCore
  -> State s_t
  -> [TASK-01..TASK-07]
  -> Forecasts, Uncertainty, Drift, Memory retrieval,
     Delay distribution, Regime path, Counterfactual trajectories
```

---

# Єдиний вихідний об’єкт (inference packet)

```python
inference_packet = {
    "state": s_t,
    "forecast": {"Y_hat": Y_hat, "horizons": H},
    "precision_error": {"error": error, "precision": precision, "weighted_error": weighted_error},
    "drift": {"drift_score": drift_score, "rupture_label_hat": rupture_label_hat, "update_gain": update_gain, "reset_probability": reset_probability},
    "memory": {"retrieved_state": retrieved_state, "retrieval_weights": retrieval_weights, "memory_conflict": memory_conflict, "write_priority": write_priority},
    "causal_delay": {"delay_distribution": delay_distribution, "causal_credit": causal_credit, "effect_prediction": effect_prediction},
    "regime_extrapolation": {"regime_probs": regime_probs, "future_regime_path": future_regime_path, "regime_change_time": regime_change_time, "extrapolated_state": extrapolated_state},
    "counterfactual": {"Y_real_hat": Y_real_hat, "Y_counterfact_hat": Y_counterfact_hat, "counterfactual_delta": counterfactual_delta, "causal_effect_score": causal_effect_score},
}
```

---

## Мінімальний обчислювальний порядок

```text
1) Обчислити s_t (ChronoEncoder + RhythmBank + TemporalCore)
2) TASK-01 -> Y_hat
3) TASK-02 -> error/precision/weighted_error
4) TASK-03 -> drift/update_gain/reset_probability
5) TASK-05 -> retrieved_state/memory_conflict
6) TASK-04 -> delay_distribution/causal_credit
7) TASK-06 -> regime_path
8) TASK-07 -> counterfactual trajectories
9) Зібрати inference_packet
```

---

## Checklist alignment (RESEARCH · ENGINEERING v1)

- PRE-WORK: one-line problem + falsifiable objective + contract fixed.
- MATH: формули по 7 задачах задані явно.
- IMPLEMENTATION: модулі та I/O розділені по відповідальностях.
- VALIDATION: метрики/acceptance задані для кожної задачі.
- FALSIFICATION: drift/counterfactual/regime tasks містять failure-sensitive метрики.
- ARTIFACT/GOVERNANCE: пакет і протокол стандартизовано для CI/reporting.

<!-- claims:end -->


<!-- claims:disclaimer -->
## Runtime implementation boundary

Current executable runtime is a deterministic baseline scaffold.

Implemented as executable prototypes:
- TASK-01 — multi-horizon linear extrapolation baseline.
- TASK-02 — precision-weighted error baseline.
- TASK-03 — drift/rupture score baseline.
- TASK-04 — inverse-horizon causal-delay prior baseline.

Packet-compatible placeholders only:
- TASK-05 — episodic memory retrieval.
- TASK-06 — regime extrapolation.
- TASK-07 — counterfactual temporal extrapolation.

No causal validity, biological memory, regime-discovery, consciousness, AGI, or brain-simulation claim is made from placeholder outputs.

Zero counterfactual delta means "not implemented / no intervention model", not "no causal effect".
<!-- claims:end -->
