# Evaluacion de carrera: `runs/carrera_v01/checkpoints/model_5000000_steps.zip`

`scripts/eval_carrera.py`, 2026-10-11 01:30, commit ea5e992. vx_cmd = 0.3 m/s, perturbaciones si. Colocacion y meta como `demo/caminatas/benchmark.py`.

| Vision | mu | Metas | Caidas | Salidas | Tiempo a meta [s] | Vel. media [m/s] | Desvio max [cm] | Rumbo max [deg] | Esfuerzo |
|---|---|---|---|---|---|---|---|---|---|
| si | 0.4 | 4/4 | 0 | 0 | 16.8 ± 0.2 | 0.296 | 15.0 | 4.8 | 86 |
| si | 0.6 | 4/4 | 0 | 0 | 16.8 ± 0.2 | 0.297 | 15.0 | 4.9 | 85 |
| si | 0.8 | 4/4 | 0 | 0 | 16.7 ± 0.3 | 0.298 | 15.4 | 4.2 | 84 |
| si | 1.0 | 4/4 | 0 | 0 | 16.9 ± 0.3 | 0.296 | 15.8 | 4.9 | 83 |
| si | 1.2 | 4/4 | 0 | 0 | 16.8 ± 0.4 | 0.296 | 16.1 | 4.6 | 82 |

**Total:** 20/20 metas, 0 caidas, 0 salidas.
Tiempo a meta medio 16.81 s (mejor 16.25 s).
