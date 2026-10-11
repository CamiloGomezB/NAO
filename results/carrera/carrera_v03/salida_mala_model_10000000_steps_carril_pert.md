# Salidas malas: `runs/carrera_v03/checkpoints/model_10000000_steps.zip`

`scripts/eval_salida_mala.py`. Rumbo objetivo de la IMU: **carril**. vx_cmd 0.4, mu [0.4, 1.2], 2 semillas por celda, perturbaciones si. Cada celda: metas / corridas y tiempo medio. y + = robot a la izquierda; rumbo + = girado a la izquierda.

## Con vision — 137/140 metas, 3 caidas, 0 salidas

| y0 \ rumbo0 | +0° | +8° | -8° | +15° | -15° | +25° | -25° |
|---|---|---|---|---|---|---|---|
| +0 cm | 4/4 12.8 s | 4/4 12.8 s | 4/4 12.8 s | 4/4 12.9 s | 4/4 12.8 s | 3/4 13.0 s | 4/4 12.9 s |
| +10 cm | 4/4 12.8 s | 4/4 12.9 s | 4/4 12.9 s | 4/4 13.0 s | 4/4 12.9 s | 4/4 13.2 s | 4/4 13.0 s |
| -10 cm | 4/4 12.7 s | 4/4 12.7 s | 4/4 12.7 s | 4/4 12.8 s | 4/4 12.7 s | 3/4 13.0 s | 4/4 12.8 s |
| +15 cm | 4/4 13.0 s | 4/4 13.0 s | 4/4 13.0 s | 4/4 13.2 s | 4/4 13.0 s | 4/4 13.3 s | 4/4 13.0 s |
| -15 cm | 4/4 12.7 s | 4/4 12.7 s | 4/4 12.7 s | 4/4 12.8 s | 4/4 12.7 s | 3/4 13.0 s | 4/4 12.8 s |

## Sin vision — 20/140 metas, 0 caidas, 120 salidas

| y0 \ rumbo0 | +0° | +8° | -8° | +15° | -15° | +25° | -25° |
|---|---|---|---|---|---|---|---|
| +0 cm | 4/4 12.9 s | 0/4 | 0/4 | 0/4 | 0/4 | 0/4 | 0/4 |
| +10 cm | 4/4 12.9 s | 0/4 | 0/4 | 0/4 | 0/4 | 0/4 | 0/4 |
| -10 cm | 4/4 12.9 s | 0/4 | 0/4 | 0/4 | 0/4 | 0/4 | 0/4 |
| +15 cm | 4/4 12.9 s | 0/4 | 0/4 | 0/4 | 0/4 | 0/4 | 0/4 |
| -15 cm | 4/4 12.9 s | 0/4 | 0/4 | 0/4 | 0/4 | 0/4 | 0/4 |
