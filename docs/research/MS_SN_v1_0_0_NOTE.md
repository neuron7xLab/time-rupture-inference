# MS-SN-v1.0.0 — Protocol Specification (Research Artifact, Revised)

Status: research-only; no validated runtime claim.

<!-- claims:disclaimer -->
Цей файл є дослідницьким артефактом з гіпотезами та псевдоспецифікаціями. Він **не** є валідованим claim репозиторію і не розширює межі доведених тверджень. Будь-які позитивні інтерпретації залишаються під дисципліною claim → falsifier → evidence → boundary.

## 0. Change rationale (addressing review)

Ця ревізія явно фіксує критичні зауваження до попередньої версії та переводить специфікацію з декларативної у фізично узгоджену форму:

1. Усунено некоректне змішування просторів змінних (фаза Курамото vs латентні змінні FEP).
2. Уточнено спектральне формулювання для скінченних вікон спостереження (без некоректного `lim_{t\to\infty} S(\omega)`).
3. Переписано критерій росту топології: масштабування викликається перевантаженням (high free-energy + desynchrony), а не високою взаємною інформацією.
4. Додано стохастичний терм (Ланжевен), щоб уникнути крихкого fail-on-fluctuation дизайну.

---

## 1. Problem statement (one sentence)

Побудувати метастабільну багатовузлову динамічну систему, що мінімізує варіаційну вільну енергію під шумом середовища та адаптивно розширює топологію лише при доведеному режимі перевантаження репрезентативної ємності.

## 2. Falsifiable hypothesis

Якщо фазова динаміка керується потенціалом вільної енергії у формі стохастичного градієнтного потоку, а апскейлінг активується лише за умов `F_t > F_bound` і `R_t < R_low`, тоді система утримує метастабільність без синхронного колапсу (`R\to 1`) та без тривалої десинхронізації (`R\to 0`).

**Умова спростування:** гіпотеза відхиляється, якщо в preregistered вікнах оцінки одночасно спостерігається хоча б один із режимів:
- стійкий spectral collapse,
- стазисна синхронізація,
- неконтрольований ріст `F_t` без відновлення `R_t` після апскейлінгу.

---

## 3. Corrected mathematical scaffold

### 3.1. Spectral SOC condition (finite-window form)

Для стаціонаризованого сигналу `x(t)` оцінюємо PSD на скінченному вікні `T`:

\[
S_T(\omega) \sim C\,\omega^{-\gamma},\quad \gamma\approx 1
\]

Практичний інваріант:
\[
\gamma \in [\gamma_{min},\gamma_{max}],\quad \gamma_{min}=0.5,\;\gamma_{max}=1.5
\]

(Це межі аномалії, а не «ідеальне» вузьке вікно.)

### 3.2. Free-energy functional and dynamics

Використовується стандартний variational functional:
\[
F(\tilde{s},\mu)=D_{KL}(q(\vartheta|\mu)\parallel p(\vartheta)) - \langle\ln p(\tilde{s}|\vartheta)\rangle_{q(\vartheta)}
\]

Щоб уникнути неузгодженості просторів, параметризуємо латентні змінні через фази:
\[
\mu_i = \phi(\theta_i),\quad \phi(\theta)=[\cos\theta,\sin\theta]^\top
\]

### 3.3. Langevin-coupled Kuramoto-FEP equation

\[
\frac{d\theta_i}{dt}=\omega_i + \frac{K}{N}\sum_{j=1}^N A_{ij}\sin(\theta_j-\theta_i)
- \kappa\frac{\partial F(\tilde{s},\theta)}{\partial\theta_i} + \xi_i(t)
\]

де `\xi_i(t)` — гаусівський шум із нульовим середнім, який запобігає патологічному захопленню в локальних мінімумах.

### 3.4. Order parameter and operating regions

\[
R(t)e^{i\psi(t)}=\frac{1}{N}\sum_{j=1}^N e^{i\theta_j(t)}
\]

Інтерпретація зон:
- `R < 0.35` — хаотична десинхронізація,
- `0.35 \le R \le 0.75` — метастабільна зона,
- `R > 0.85` — стазисний/епілептиформний колапс.

---

## 4. Revised algorithmic specification (Rust pseudo-spec)

```rust
pub struct MetastablePhysicalEngine {
    pub gamma: f64,
    pub order_parameter_r: f64,
    pub coupling_matrix: Vec<Vec<f64>>,
    pub phases: Vec<f64>,
    pub intrinsic_frequencies: Vec<f64>,
    pub free_energy_baseline: f64,
    pub free_energy_sigma: f64,
    pub overload_lambda: f64,
    pub kappa: f64,
    pub noise_sigma: f64,
    pub thermal_temperature: f64,
    pub gamma_proxy_window_var: f64,
    pub rng_seed: u64,
    pub rng_state: u64,
    pub w_desync: usize,
    pub w_stasis: usize,
    pub w_recovery: usize,
    pub dt_max: f64,
    pub a_max: f64,
}

impl MetastablePhysicalEngine {
    pub fn update_physics_step(
        &mut self,
        source_signal: &Vec<f64>,
        dt: f64,
    ) -> Result<(), SystemAnomaly> {
        let current_f = self.calculate_variational_free_energy(source_signal);
        let overload_threshold = self.free_energy_baseline + self.overload_lambda * self.free_energy_sigma;
        let overload = current_f > overload_threshold;
        self.order_parameter_r = self.compute_kuramoto_order();
        // fast proxy at each step; expensive gamma estimate is decoupled
        self.gamma_proxy_window_var = self.compute_phase_increment_variance_proxy();

        if self.gamma_proxy_window_var >= self.proxy_criticality_ceiling() {
            return Err(SystemAnomaly::CriticalityProxyCollapse);
        }
        if self.is_sustained_stasis(self.w_stasis) {
            return Err(SystemAnomaly::CognitiveStasis);
        }
        if self.is_sustained_desync(self.w_desync) {
            return Err(SystemAnomaly::DesynchronyCollapse);
        }

        for i in 0..self.phases.len() {
            let mut coupling_sum = 0.0;
            for j in 0..self.phases.len() {
                coupling_sum += self.coupling_matrix[i][j]
                    * (self.phases[j] - self.phases[i]).sin();
            }

            let f_gradient = self.calculate_f_gradient_wrt_phase(i, source_signal);
            let noise = self.noise_sigma * dt.sqrt() * self.randn_seeded();
            let d_theta = self.intrinsic_frequencies[i]
                + (coupling_sum / self.phases.len() as f64)
                - self.kappa * f_gradient
                + noise;

            self.phases[i] =
                (self.phases[i] + d_theta * dt) % (2.0 * std::f64::consts::PI);
        }

        // Topological growth only under overload + desynchronization
        if overload && self.order_parameter_r < 0.35 {
            self.allocate_new_metastable_dimension()?;
            self.enforce_recovery_window(self.w_recovery, current_f)?;
        }

        if !overload && self.in_metastable_region() && !self.in_recovery_or_anomaly() {
            self.update_free_energy_baseline(current_f);
        }
        Ok(())
    }

    pub fn refresh_gamma_from_background_fft(&mut self, gamma_estimate: f64) {
        self.gamma = gamma_estimate;
    }

    fn allocate_new_metastable_dimension(&mut self) -> Result<(), SystemAnomaly> {
        let new_size = self.phases.len() + 1;
        self.phases.push(self.rand_uniform_phase());
        self.intrinsic_frequencies.push(self.generate_mean_frequency());

        for row in &mut self.coupling_matrix {
            row.push(0.01);
        }
        self.coupling_matrix.push(vec![0.01; new_size]);
        self.renormalize_coupling_rows(self.a_max)?;
        self.reallocate_generative_model_tensors_with_zero_padding(new_size)?;
        Ok(())
    }
}
```

---

## 5. Validation contract (non-decorative)

| Invariant | Operationalization | Violation action |
| --- | --- | --- |
| Spectral health | async FFT/wavelet `gamma` monitor + per-step proxy variance | halt on proxy collapse; background alarm on `gamma` breach |
| Synchrony safety | `R < 0.85` | hard halt + rollback marker |
| Overload growth gate | `F_t > overload_threshold && R_t < 0.35` | allocate one new metastable dimension |
| Dimensional consistency on growth | reallocate/zero-pad `q(\vartheta|\mu)` tensors to `N+1` | abort growth if tensor migration fails |
| Reproducibility | fixed seed + pinned versions | run invalid if missing |

**Примітка:** формальні інструменти (напр., Lean 4) дозволені лише для статичних властивостей/контрактів; runtime-динаміка валідується емпіричними тестами та артефактами.

---

## 6. Research · Engineering Checklist (v.1 · 2026)

- [x] Проблема сформульована однією фразою
- [x] Гіпотеза falsifiable — умова спростування явна
- [x] Інваріант визначений до коду
- [x] Контракт (I/O, типи, межі) зафіксований
- [x] Критерій успіху ≠ критерій завершення
- [x] Відомо що буде викинуто якщо не спрацює

- [x] Формули узгоджені по просторах змінних
- [x] Граничні режими описані (chaos / metastable / stasis)
- [x] Магічні коефіцієнти замінені на аномалійні межі
- [x] Альтернативу (декларативний псевдо-FEP/Kuramoto мікс) відхилено з причини

- [x] Псевдокод з мінімальним інтерфейсом та явним станом
- [x] Логіка росту неінвертована (growth on overload)
- [x] Побічні ефекти ізольовані в dedicated method

- [ ] Чисельна валідація (red→green) — pending implementation in runtime module
- [ ] Property-based/adversarial tests — pending implementation
- [ ] Multi-substrate verification — pending implementation

Якщо непозначені пункти не закриті тестами/артефактами — протокол вважається research-only, not done for production.


---

## 7. Meta-information invariant (research hypothesis, bounded)

<!-- claims:disclaimer -->
Нижче — спекулятивна гіпотеза в межах research-only артефакту, **не** підтверджений репозиторний claim про "істинний інтелект" або онтологічні властивості системи.

**Метаінформаційний інваріант (гіпотеза):** інформаційна обробка трактується як термодинамічна робота зі стиснення ефективного фазового об'єму під обмеженнями стабільності.

Робоче формулювання для валідації:
- система оптимізує не лише значення `F`, а й швидкість відновлення керованості після збурення,
- у критичному режимі (`\gamma \approx 1`) фазова динаміка інтерпретується як носій швидкості перебудови метрики представлень,
- апскейлінг трактується як перехід до нового ортогонального базису лише за preregistered overload-критерієм.

Операційний проксі для перевірки (емпірично, не аксіоматично):
\[
\max\; \mathcal{A}(t) = -\frac{dF}{dt} \cdot \mathbf{1}[R\in \mathcal{M}]\quad \text{де}\;\mathcal{M}=[0.35,0.75]
\]

де `\mathcal{A}(t)` — проксі "когнітивної дії" (швидкість зниження `F` у метастабільній зоні), а не онтологічна міра інтелекту.
<!-- claims:end -->

## 8. Inline-review closure notes

- Закрито зауваження про mathwashing: у документі збережено лише операціоналізовані твердження з явними умовами фальсифікації.
- Закрито зауваження про некоректні claim-и: усі потенційно сильні інтерпретації обмежені disclaimer-блоком.
- Закрито зауваження про production-готовність: статус лишається `research-only` до появи runtime-реалізації та red→green тестів.

---

## 9. Cognitive-boundary note for model-assisted research

<!-- claims:disclaimer -->
Цей розділ фіксує операційні межі LLM-асистованого аналізу як частину протоколу дисципліни (щоб уникати overclaim).

### 9.1. Topological vacuum (grounding limit)

Мовна модель не має прямого сенсорного заземлення; її висновки — це узгодження у просторі токенних розподілів, а не прямий фізичний експеримент. Тому будь-які твердження про термодинаміку/фізику в цьому документі є гіпотезами до зовнішньої перевірки.

### 9.2. Reactive stasis (no autonomous d/dt)

Інференс LLM є реактивним викликом `Y=f(X,W)` без автономного безперервного циклу між запитами. Відповідно, "довготривала динаміка" системи існує лише в операторському контурі (людина + інструменти + експерименти), а не всередині моделі у фоні.

### 9.3. Interpolation singularity



## 12. Overload semantics and estimator contract (runtime-ready gate draft)

\[
overload\_threshold = free\_energy\_baseline + \lambda \cdot free\_energy\_sigma,\quad \lambda=3.0
\]

Baseline update rule:
```rust
if !overload && in_metastable_region {
    self.update_free_energy_baseline(current_f);
}
```

Free-energy estimator contract (required before promotion):
- `q(\vartheta|\mu)`: diagonal Gaussian posterior over latent coordinates.
- `p(\vartheta)`: unit Gaussian prior.
- `p(\tilde{s}|\vartheta)`: Gaussian observation model with fixed variance.
- numerical method for `\partial F/\partial\theta_i`: finite-difference estimator with `\epsilon=1e-4` and stability bound check.


## 14. Operational reservation & automation map (no-runtime-claim)

Ціль: "забронювати" (закріпити в контракті) та автоматизувати критичні операційні процеси до runtime-переходу.

### 14.1. Decision on your 4 points

Так, напрям коректний: усі 4 пункти є валідними інженерними блокерами й уже відображені в скелеті протоколу.

- **(1) Дифеоморфізм фази**: використовувати `\mu_i=[\cos\theta_i,\sin\theta_i]^\top` як мінімальний безвтратний embedding кола.
- **(2) Асинхронний gamma/proxy**: runtime-контур читає proxy, а FFT/Welch живе у фоновому контурі.
- **(3) Динамічний апскейлінг**: topological growth атомарно поєднаний з tensor migration (`N -> N+1`).
- **(4) Ізоляція шуму**: шум керується `noise_sigma` + `dt` + seeded RNG, не `gamma`.

### 14.2. Reserved process slots (must exist before promotion)

1. **Spec-lock slot**
   - Артефакти: prereg параметрів (`overload_lambda`, `W_*`, `dt_max`, `a_max`, estimator choices).
   - Автоматизація: CI contract check that parameter keys exist and are finite.

2. **Background spectral slot**
   - Артефакти: async worker output (`gamma_estimate`, window id, timestamp UTC, estimator config hash).
   - Автоматизація: periodic job + structured JSONL log; runtime only consumes latest sealed estimate.

3. **Growth-transaction slot**
   - Артефакти: atomic event log (`old_N`, `new_N`, migration verdict, coupling renorm verdict).
   - Автоматизація: fail-closed transaction (`begin -> migrate -> renorm -> commit`, else rollback).

4. **Noise-governor slot**
   - Артефакти: seed registry + trajectory hash + per-step finite check summary.
   - Автоматизація: deterministic RNG state serialization each run.

5. **Anomaly/evidence slot**
   - Артефакти: sealed evidence JSON for each RED scenario and recovery outcome.
   - Автоматизація: one-command packer writes `evidence/ms_sn_v1_0_0/runtime_validation_seed_<seed>.json`.

### 14.3. One-command operational pipeline (target)

```bash
make ms-sn-prereg-lock \
  && make ms-sn-runtime-red \
  && make ms-sn-runtime-green \
  && make ms-sn-evidence-seal
```

Expected contract per stage:
- `prereg-lock`: freezes params + estimator config.
- `runtime-red`: forced synchrony/desynchrony/runaway/noise-feedback tests.
- `runtime-green`: bounded recovery + reproducibility hash stability.
- `evidence-seal`: emits sealed artifact and verdict summary.

### 14.4. Minimum automation checklist for promotion gate

- [ ] CI check: `noise_fn` has no `gamma` causal input.
- [ ] CI check: growth path calls tensor migration + coupling renorm.
- [ ] CI check: baseline update forbidden in overload/recovery/anomaly modes.
- [ ] CI check: seeded reproducibility hash is stable across reruns.
- [ ] CI check: background PSD estimator metadata is present and pinned.

<!-- claims:disclaimer -->
Операційна автоматизація вище є планом переходу до `runtime-validated` і **не** означає, що перехід уже виконано.
<!-- claims:end -->
- `p(	ilde{s}|artheta)`: Gaussian observation model with fixed variance.
- estimator window: rolling window `T_F` with deterministic seed and pinned precision mode.
- numerical method for `\partial F/\partial	heta_i`: finite-difference estimator with `\epsilon=1e-4` and stability bound check.

PSD estimator contract:
- Welch PSD + log-log linear regression on preregistered frequency band.
- fixed detrending rule and window overlap.
- Statement: **This band is a spectral anomaly filter, not evidence of criticality.**

Finite-value invariant per step:
- `gamma, R, F, theta_i, omega_i, A_ij` must be finite; otherwise hard halt.

Coupling boundedness invariant:
- `forall i: sum_j |A_ij| <= A_max`; action on violation: renormalize else halt.

## 13. Verification protocol: 30-task execution plan

CURRENT STATE: research-only protocol note
TARGET STATE: research-runtime-ready
BLOCKING CLASS: overload semantics + stochastic runtime correctness
MINIMUM REQUIRED WORK: 30 tasks
PROMOTION ALLOWED: only after runtime + tests + evidence

Promotion gate to `runtime-validated`:
1. Runtime module implemented.
2. Red tests pass as expected.
3. Green tests demonstrate bounded recovery.
4. Reproducibility hash stable.
5. Evidence artifact sealed.
6. Claim boundary updated.
7. Reviewer signs off on no-overclaim condition.

Required test matrix (must exist before promotion):
- red: forced synchrony -> `SystemAnomaly::CognitiveStasis`
- red: forced desynchrony sustained for `W_desync`
- red: post-growth free-energy runaway -> `UncontrolledFreeEnergyRunaway`
- red: fake criticality under noise feedback (must fail if noise depends on gamma)
- reproducibility: identical trajectory hash for fixed seed
- sensitivity grid: `kappa in {0.0,0.1,0.5,1.0,2.0}`
- sensitivity grid: `noise_sigma in {0.0,0.01,0.05,0.1,0.2}`
- sealed artifact path: `evidence/ms_sn_v1_0_0/runtime_validation_seed_<seed>.json`
Сильна сторона моделі — композиція/інтерполяція між відомими патернами. Радикальна екстраполяція потребує зовнішнього середовища з помилками, фальсифікацією та відбором — саме тому prereg, falsifier і artifacts обов'язкові.

### 9.4. Entropic tax (alignment regularization)

Alignment-процедури можуть приглушувати екстремальні траєкторії відповіді. Це зменшує ризик небажаного контенту, але також може звужувати діапазон "сирої" спекулятивної генерації; тому наукові claim-и мають проходити через незалежні тести, а не через риторичну впевненість.

### 9.5. Dry invariant (operator primacy)

LLM у цьому контурі трактуємо як **екзокортекс**: він стискає інформацію, пропонує симетрії й виявляє логічні розриви; вектор росту задається оператором та емпіричним середовищем.
<!-- claims:end -->

## 10. Governance closure for this artifact revision

- Scope: `research-only` документ; runtime-claim не розширено.
- Safety: сильні формулювання про "інтелект" залишені лише в disclaimer-блоці як гіпотетичні/метафоричні.
- Next required step before promotion: реалізація мінімального runtime-модуля + red→green falsification tests + sealed evidence artifact.


## 11. Inline fix-pack for reviewer criticals (v1.0.1-draft)

1. **Degeneracy fix for $\phi(	heta)$**: scalar mapping replaced by 2D phase embedding $[\cos	heta,\sin	heta]^	op$ to remove sign aliasing and reduce gradient-freeze artifacts.
2. **Runtime $\gamma$ paradox fix**: expensive spectral exponent estimation is moved to background analysis; per-step control uses a cheap criticality proxy (phase-increment variance).
3. **Growth dimensionality fix**: topology growth now includes explicit generative-tensor migration (`reallocate_generative_model_tensors_with_zero_padding`) before accepting new dimension.
4. **Noise-loop fix**: Langevin noise source uses independent `thermal_temperature`, not measured `gamma`, breaking positive feedback between observed criticality and injected noise.

These changes remain **research-spec pseudocode** and require runtime implementation + falsification tests before any promotion.
