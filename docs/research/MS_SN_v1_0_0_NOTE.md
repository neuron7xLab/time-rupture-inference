# MS-SN-v1.0.0 — Protocol Specification (Research Artifact, Revised)

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
\mu_i = \phi(\theta_i),\quad \phi(\theta)=\cos\theta
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
    pub free_energy_bound: f64,
}

impl MetastablePhysicalEngine {
    pub fn update_physics_step(
        &mut self,
        source_signal: &Vec<f64>,
        dt: f64,
    ) -> Result<(), SystemAnomaly> {
        let current_f = self.calculate_variational_free_energy(source_signal);
        self.order_parameter_r = self.compute_kuramoto_order();
        self.gamma = self.compute_spectral_density_exponent();

        // FAIL-CLOSED only on true anomalies, not micro-fluctuations
        if self.gamma <= 0.5 || self.gamma >= 1.5 {
            return Err(SystemAnomaly::SpectralCollapse);
        }
        if self.order_parameter_r >= 0.85 {
            return Err(SystemAnomaly::CognitiveStasis);
        }

        for i in 0..self.phases.len() {
            let mut coupling_sum = 0.0;
            for j in 0..self.phases.len() {
                coupling_sum += self.coupling_matrix[i][j]
                    * (self.phases[j] - self.phases[i]).sin();
            }

            let f_gradient = self.calculate_f_gradient_wrt_phase(i, source_signal);
            let noise = self.generate_thermal_noise(self.gamma);
            let d_theta = self.intrinsic_frequencies[i]
                + (coupling_sum / self.phases.len() as f64)
                - f_gradient
                + noise;

            self.phases[i] =
                (self.phases[i] + d_theta * dt) % (2.0 * std::f64::consts::PI);
        }

        // Topological growth only under overload + desynchronization
        if current_f > self.free_energy_bound && self.order_parameter_r < 0.35 {
            self.allocate_new_metastable_dimension();
        }

        self.free_energy_bound = current_f;
        Ok(())
    }

    fn allocate_new_metastable_dimension(&mut self) {
        let new_size = self.phases.len() + 1;
        self.phases.push(0.0);
        self.intrinsic_frequencies.push(self.generate_mean_frequency());

        for row in &mut self.coupling_matrix {
            row.push(0.01);
        }
        self.coupling_matrix.push(vec![0.01; new_size]);
    }
}
```

---

## 5. Validation contract (non-decorative)

| Invariant | Operationalization | Violation action |
| --- | --- | --- |
| Spectral health | `0.5 < gamma < 1.5` | hard halt + anomaly artifact |
| Synchrony safety | `R < 0.85` | hard halt + rollback marker |
| Overload growth gate | `F_t > F_bound && R_t < 0.35` | allocate one new metastable dimension |
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
