# CTI-OS Proof-of-Life v3 — Release Gate

**Verdict: GREEN / PASS**

- prereg_hash: `d284c5ea9366c674a0785a7c81a005b48892f2c8e5616cec0fcc025d876178cb`
- git_commit: `63fe21aefe6d9afc2809068fe48ebe7e8d5531c2`
- grid win-rate learned>injected: 1.000
- grid win-rate learned>best-naive: 1.000
- operational adaptation markers (neuroplastic-like label only, NOT biological): `{'synaptic': np.True_, 'homeostatic': True, 'neuromodulation': True, 'extinction': True}`

## Allowed claim (verbatim, critique §3)
> The learned agent adapts to hidden temporal regime shifts better than fixed and naive baselines under preregistered metrics, deterministic replay, no-leakage constraints, and ablation controls.

## Forbidden claim
> NOT claimed: CTI-OS understands time / has cognition; NOT neuroplastic; NOT simulating causality or world understanding.

## Checks
- [x] learned_beats_injected_post_mae
- [x] learned_beats_best_naive_post_mae
- [x] learned_beats_injected_aue
- [x] adaptation_under_threshold
- [x] detection_delay_bounded
- [x] false_alarm_bounded
- [x] win_rate_vs_injected
- [x] win_rate_vs_baseline
- [x] ablation_shows_necessity
- [x] no_hidden_variable_leakage
- [x] deterministic_replay
- [x] prereg_committed_before_run
- [x] statistical_power_grid
- [x] pass_holds_on_every_shift
- [x] shuffled_order_no_gain
- [x] np_marker_synaptic
- [x] np_marker_homeostatic
- [x] np_marker_neuromodulation
- [x] np_marker_extinction

## Per-shift post_shift_mae (learned / injected / best-naive)
- delta=7.0: learned=0.882 injected=7.008 best_naive=1.006
- delta=12.0: learned=0.892 injected=12.008 best_naive=1.167
- delta=-5.0: learned=0.874 injected=4.992 best_naive=0.936

## Grid-mean metrics
```
{"exp_smoothing_a0.1":{"adaptation_time":30.96666666666667,"area_under_post_shift_error":260.88024176790657,"detection_delay":Infinity,"false_alarm_rate":0.0,"post_shift_mae":1.0435209670716266,"pre_shift_mae":0.8453866586950881,"recovery_slope":0.21334563912117763,"stability_pre_shift":0.6135524754518201},"injected":{"adaptation_time":Infinity,"area_under_post_shift_error":2000.6915573908516,"detection_delay":Infinity,"false_alarm_rate":0.0,"post_shift_mae":8.002766229563406,"pre_shift_mae":0.7932068327166086,"recovery_slope":0.0,"stability_pre_shift":0.3641835173529964},"last_interval":{"adaptation_time":10.722222222222223,"area_under_post_shift_error":287.66732238749233,"detection_delay":Infinity,"false_alarm_rate":0.0,"post_shift_mae":1.1506692895499695,"pre_shift_mae":1.1454769344685052,"recovery_slope":0.6937850539389774,"stability_pre_shift":0.9242576062124787},"learned_frozen_post_shift":{"adaptation_time":Infinity,"area_under_post_shift_error":2017.292075158715,"detection_delay":Infinity,"false_alarm_rate":0.0,"post_shift_mae":8.069168300634859,"pre_shift_mae":1.1756035891065688,"recovery_slope":0.0,"stability_pre_shift":1.9707145157262278},"learned_full":{"adaptation_time":16.755555555555556,"area_under_post_shift_error":220.75193557599724,"detection_delay":1.0999999999999999,"false_alarm_rate":0.0030000000000000005,"post_shift_mae":0.883007742303989,"pre_shift_mae":1.1725457930317167,"recovery_slope":0.3739644109033174,"stability_pre_shift":1.978889197921755},"learned_no_drift":{"adaptation_time":35.52222222222222,"area_under_post_shift_error":296.80594841645075,"detection_delay":Infinity,"false_alarm_rate":0.0,"post_shift_mae":1.1872237936658028,"pre_shift_mae":1.1639975711277433,"recovery_slope":0.1698968946421795,"stability_pre_shift":1.9743891000170717},"learned_no_memory":{"adaptation_time":10.722222222222223,"area_under_post_shift_error":287.66732238749233,"detection_delay":Infinity,"false_alarm_rate":0.005,"post_shift_mae":1.1506692895499695,"pre_shift_mae":1.1454769344685052,"recovery_slope":0.6937850539389774,"stability_pre_shift":0.9242576062124787},"learned_no_update":{"adaptation_time":Infinity,"area_under_post_shift_error":3418.741338839221,"detection_delay":Infinity,"false_alarm_rate":0.0,"post_shift_mae":13.674965355356884,"pre_shift_mae":8.97799148875914,"recovery_slope":0.0,"stability_pre_shift":0.9886232834558232},"moving_average_w20":{"adaptation_time":31.022222222222222,"area_under_post_shift_error":272.5805017713758,"detection_delay":Infinity,"false_alarm_rate":0.0,"post_shift_mae":1.090322007085503,"pre_shift_mae":0.8422102510957629,"recovery_slope":0.21568681923285848,"stability_pre_shift":0.6107983146912946},"oracle":{"adaptation_time":0.26666666666666666,"area_under_post_shift_error":198.3309294868285,"detection_delay":Infinity,"false_alarm_rate":0.0,"post_shift_mae":0.7933237179473137,"pre_shift_mae":0.7932068327166086,"recovery_slope":0.09280507957649553,"stability_pre_shift":0.3641835173529964},"random":{"adaptation_time":4.933333333333333,"area_under_post_shift_error":1892.2204799406034,"detection_delay":Infinity,"false_alarm_rate":0.0,"post_shift_mae":7.568881919762411,"pre_shift_mae":6.378320937406298,"recovery_slope":0.7910355756563888,"stability_pre_shift":19.773339472406697}}
```