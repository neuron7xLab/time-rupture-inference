# CTI-OS Proof-of-Life — Release Gate

**Verdict: RED / FAIL**

- prereg_hash: `55f90a8e376598a7c795be13eaf6307933567aa3f60757f332924bf1787fea30`
- git_commit: `3c23f59385fc4002c033c4231f6c63aaf5147257`
- config_source_hash: `e8c4bf7d78afa3442aec2b6294d6a98de83e541989ba29193c5018e34416bffa`
- win-rate learned>injected: 1.00
- win-rate learned>best-naive: 0.00

## Checks
- [x] learned_beats_injected_post_mae
- [ ] learned_beats_best_naive_post_mae
- [x] learned_beats_injected_aue
- [x] adaptation_under_threshold
- [ ] detection_delay_bounded
- [x] false_alarm_bounded
- [x] win_rate_vs_injected
- [ ] win_rate_vs_baseline
- [ ] ablation_shows_necessity
- [x] no_hidden_variable_leakage
- [x] deterministic_replay
- [x] prereg_committed_before_run

## Failure reasons
- FAILED: learned_beats_best_naive_post_mae
- FAILED: detection_delay_bounded
- FAILED: win_rate_vs_baseline
- FAILED: ablation_shows_necessity

## Aggregate metrics
```
{"exp_smoothing_a0.1":{"adaptation_time":29.9375,"area_under_post_shift_error":249.76558782038387,"detection_delay":Infinity,"false_alarm_rate":0.0,"post_shift_mae":0.9990623512815355,"pre_shift_mae":0.8422696272707626,"recovery_slope":0.19147247047972044,"stability_pre_shift":0.6037580853697331},"injected":{"adaptation_time":Infinity,"area_under_post_shift_error":1750.4883817583263,"detection_delay":Infinity,"false_alarm_rate":0.0,"post_shift_mae":7.001953527033306,"pre_shift_mae":0.7885717399549347,"recovery_slope":0.0,"stability_pre_shift":0.35580886147002594},"last_interval":{"adaptation_time":9.4375,"area_under_post_shift_error":285.9899684742514,"detection_delay":Infinity,"false_alarm_rate":0.0,"post_shift_mae":1.1439598738970056,"pre_shift_mae":1.142331788726347,"recovery_slope":0.586963519244208,"stability_pre_shift":0.9071384162944347},"learned_frozen_post_shift":{"adaptation_time":Infinity,"area_under_post_shift_error":1796.539741934108,"detection_delay":Infinity,"false_alarm_rate":0.0,"post_shift_mae":7.186158967736432,"pre_shift_mae":1.1716467373455517,"recovery_slope":0.0,"stability_pre_shift":1.9566630864706882},"learned_full":{"adaptation_time":34.25,"area_under_post_shift_error":280.0127998648479,"detection_delay":Infinity,"false_alarm_rate":0.0,"post_shift_mae":1.1200511994593918,"pre_shift_mae":1.1619600522688471,"recovery_slope":0.15491258374804334,"stability_pre_shift":1.9577658532114377},"learned_no_drift":{"adaptation_time":34.25,"area_under_post_shift_error":280.0127998648479,"detection_delay":Infinity,"false_alarm_rate":0.0,"post_shift_mae":1.1200511994593918,"pre_shift_mae":1.1619600522688471,"recovery_slope":0.15491258374804334,"stability_pre_shift":1.9577658532114377},"learned_no_memory":{"adaptation_time":9.4375,"area_under_post_shift_error":285.9899684742514,"detection_delay":Infinity,"false_alarm_rate":0.0,"post_shift_mae":1.1439598738970056,"pre_shift_mae":1.142331788726347,"recovery_slope":0.586963519244208,"stability_pre_shift":0.9071384162944347},"learned_no_update":{"adaptation_time":Infinity,"area_under_post_shift_error":4000.488381758326,"detection_delay":Infinity,"false_alarm_rate":0.0,"post_shift_mae":16.001953527033308,"pre_shift_mae":8.989065045646198,"recovery_slope":0.0,"stability_pre_shift":0.9729989605523894},"moving_average_w20":{"adaptation_time":30.25,"area_under_post_shift_error":259.2285510513139,"detection_delay":Infinity,"false_alarm_rate":0.0,"post_shift_mae":1.0369142042052557,"pre_shift_mae":0.8386101041625965,"recovery_slope":0.18983641808284396,"stability_pre_shift":0.6049554593718448},"oracle":{"adaptation_time":0.125,"area_under_post_shift_error":197.8784057485503,"detection_delay":Infinity,"false_alarm_rate":0.0,"post_shift_mae":0.7915136229942012,"pre_shift_mae":0.7885717399549347,"recovery_slope":0.030233690170560712,"stability_pre_shift":0.35580886147002594},"random":{"adaptation_time":0.0625,"area_under_post_shift_error":1321.5512293852653,"detection_delay":Infinity,"false_alarm_rate":0.0,"post_shift_mae":5.2862049175410615,"pre_shift_mae":6.6182839652798755,"recovery_slope":0.0902953723548538,"stability_pre_shift":21.393125038421303}}
```