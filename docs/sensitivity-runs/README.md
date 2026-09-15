# Sensitivity analysis run outputs

Raw output of `scripts/sensitivity_analysis.py`, 10,000 draws, seed 20260914,
run 14 September 2026. Regenerate any of them with the flags in the first line
of each file. The write-up is `docs/SENSITIVITY_ANALYSIS.md`.

| File | Flags | What it isolates |
|---|---|---|
| fixed-scale.txt | (default) | primary: k = 4.47, each OR varies within its CI |
| floating-scale.txt | `--mode floating` | k recomputed from the drawn tobacco OR on every draw |
| fixed-scale-ci-width-only.txt | `--centre deployed` | diagnostic: keeps the deployed point estimates, applies only the published CI widths |
| fixed-scale-hpv-dsouza-oral.txt | `--hpv dsouza_oral` | HPV history scored at the D'Souza 2007 oral HPV-16 OR (14.6) |
| fixed-scale-no-betel.txt | `--restrict betel=never` | the profile space without betel, closer to a US user base |
| fixed-scale-alcohol-frequency-map.txt | `--alcohol-map frequency` | daily alcohol mapped to Bagnardi's moderate band instead of heavy |
