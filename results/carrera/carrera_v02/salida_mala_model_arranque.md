# Salidas malas: `policies/carrera_v02/model.zip`

`scripts/eval_salida_mala.py`. Rumbo objetivo de la IMU: **arranque**. vx_cmd 0.4, mu [0.8], 2 semillas por celda, perturbaciones no. Cada celda: metas / corridas y tiempo medio. y + = robot a la izquierda; rumbo + = girado a la izquierda.

## Con vision — 16/70 metas, 0 caidas, 54 salidas

| y0 \ rumbo0 | +0° | +8° | -8° | +15° | -15° | +25° | -25° |
|---|---|---|---|---|---|---|---|
| +0 cm | 2/2 12.7 s | 2/2 13.0 s | 0/2 | 0/2 | 0/2 | 0/2 | 0/2 |
| +10 cm | 2/2 12.7 s | 0/2 | 0/2 | 0/2 | 0/2 | 0/2 | 0/2 |
| -10 cm | 2/2 12.7 s | 2/2 13.0 s | 0/2 | 0/2 | 0/2 | 0/2 | 0/2 |
| +15 cm | 2/2 12.7 s | 0/2 | 0/2 | 0/2 | 0/2 | 0/2 | 0/2 |
| -15 cm | 2/2 13.0 s | 2/2 13.0 s | 0/2 | 0/2 | 0/2 | 0/2 | 0/2 |

## Sin vision — 10/70 metas, 0 caidas, 60 salidas

| y0 \ rumbo0 | +0° | +8° | -8° | +15° | -15° | +25° | -25° |
|---|---|---|---|---|---|---|---|
| +0 cm | 2/2 13.7 s | 0/2 | 0/2 | 0/2 | 0/2 | 0/2 | 0/2 |
| +10 cm | 2/2 13.7 s | 0/2 | 0/2 | 0/2 | 0/2 | 0/2 | 0/2 |
| -10 cm | 2/2 13.7 s | 0/2 | 0/2 | 0/2 | 0/2 | 0/2 | 0/2 |
| +15 cm | 2/2 13.7 s | 0/2 | 0/2 | 0/2 | 0/2 | 0/2 | 0/2 |
| -15 cm | 2/2 13.7 s | 0/2 | 0/2 | 0/2 | 0/2 | 0/2 | 0/2 |
