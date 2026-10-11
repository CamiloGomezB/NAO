# Salidas malas: `runs/carrera_v03/checkpoints/model_15000000_steps.zip`

`scripts/eval_salida_mala.py`. Rumbo objetivo de la IMU: **carril**. vx_cmd 0.4, mu [0.4, 1.2], 2 semillas por celda, perturbaciones si. Cada celda: metas / corridas y tiempo medio. y + = robot a la izquierda; rumbo + = girado a la izquierda.

## Con vision — 122/140 metas, 0 caidas, 18 salidas

| y0 \ rumbo0 | +0° | +8° | -8° | +15° | -15° | +25° | -25° |
|---|---|---|---|---|---|---|---|
| +0 cm | 4/4 12.7 s | 4/4 12.7 s | 4/4 12.7 s | 4/4 12.7 s | 4/4 12.7 s | 4/4 12.7 s | 4/4 12.8 s |
| +10 cm | 3/4 12.7 s | 3/4 12.7 s | 3/4 12.8 s | 3/4 12.7 s | 3/4 12.7 s | 2/4 12.7 s | 3/4 12.9 s |
| -10 cm | 4/4 12.7 s | 4/4 12.6 s | 4/4 12.7 s | 4/4 12.7 s | 4/4 12.7 s | 4/4 12.7 s | 4/4 12.8 s |
| +15 cm | 3/4 12.8 s | 2/4 12.8 s | 3/4 12.9 s | 2/4 12.7 s | 3/4 12.9 s | 2/4 12.8 s | 3/4 12.9 s |
| -15 cm | 4/4 12.7 s | 4/4 12.6 s | 4/4 12.6 s | 4/4 12.6 s | 4/4 12.7 s | 4/4 12.6 s | 4/4 12.8 s |

## Sin vision — 15/140 metas, 0 caidas, 125 salidas

| y0 \ rumbo0 | +0° | +8° | -8° | +15° | -15° | +25° | -25° |
|---|---|---|---|---|---|---|---|
| +0 cm | 3/4 13.7 s | 0/4 | 0/4 | 0/4 | 0/4 | 0/4 | 0/4 |
| +10 cm | 3/4 13.7 s | 0/4 | 0/4 | 0/4 | 0/4 | 0/4 | 0/4 |
| -10 cm | 3/4 14.0 s | 0/4 | 0/4 | 0/4 | 0/4 | 0/4 | 0/4 |
| +15 cm | 3/4 13.7 s | 0/4 | 0/4 | 0/4 | 0/4 | 0/4 | 0/4 |
| -15 cm | 3/4 14.0 s | 0/4 | 0/4 | 0/4 | 0/4 | 0/4 | 0/4 |
