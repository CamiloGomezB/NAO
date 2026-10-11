# Evaluacion de carrera: `runs/carrera_v01/checkpoints/model_15000000_steps.zip`

`scripts/eval_carrera.py`, 2026-10-11 01:59, commit ea5e992. vx_cmd = 0.5 m/s, perturbaciones si. Colocacion y meta como `demo/caminatas/benchmark.py`.

| Vision | mu | Metas | Caidas | Salidas | Tiempo a meta [s] | Vel. media [m/s] | Desvio max [cm] | Rumbo max [deg] | Esfuerzo |
|---|---|---|---|---|---|---|---|---|---|
| si | 0.4 | 4/4 | 0 | 0 | 11.2 ± 0.6 | 0.447 | 9.4 | 5.5 | 65 |
| si | 0.6 | 4/4 | 0 | 0 | 11.2 ± 0.6 | 0.447 | 8.2 | 5.5 | 65 |
| si | 0.8 | 4/4 | 0 | 0 | 11.1 ± 0.5 | 0.449 | 8.0 | 5.0 | 64 |
| si | 1.0 | 4/4 | 0 | 0 | 11.1 ± 0.5 | 0.449 | 7.9 | 4.5 | 64 |
| si | 1.2 | 4/4 | 0 | 0 | 11.2 ± 0.6 | 0.448 | 7.9 | 5.3 | 63 |

**Total:** 20/20 metas, 0 caidas, 0 salidas.
Tiempo a meta medio 11.15 s (mejor 10.68 s).
