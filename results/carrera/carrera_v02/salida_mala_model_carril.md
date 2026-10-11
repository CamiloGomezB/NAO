# Salidas malas: `policies/carrera_v02/model.zip`

`scripts/eval_salida_mala.py`. Rumbo objetivo de la IMU: **carril**. vx_cmd 0.4, mu [0.8], 2 semillas por celda, perturbaciones no. Cada celda: metas / corridas y tiempo medio. y + = robot a la izquierda; rumbo + = girado a la izquierda.

## Con vision — 69/70 metas, 1 caidas, 0 salidas

| y0 \ rumbo0 | +0° | +8° | -8° | +15° | -15° | +25° | -25° |
|---|---|---|---|---|---|---|---|
| +0 cm | 2/2 12.7 s | 2/2 12.7 s | 2/2 12.7 s | 2/2 12.7 s | 2/2 12.7 s | 2/2 12.8 s | 2/2 13.0 s |
| +10 cm | 2/2 12.7 s | 2/2 12.7 s | 2/2 12.7 s | 2/2 13.0 s | 2/2 12.7 s | 2/2 13.0 s | 2/2 13.0 s |
| -10 cm | 2/2 12.9 s | 2/2 12.7 s | 2/2 12.8 s | 2/2 12.7 s | 2/2 12.8 s | 2/2 12.8 s | 2/2 13.1 s |
| +15 cm | 2/2 12.7 s | 2/2 12.7 s | 2/2 12.8 s | 2/2 13.4 s | 2/2 12.8 s | 2/2 12.9 s | 2/2 13.0 s |
| -15 cm | 2/2 13.0 s | 2/2 12.9 s | 2/2 13.1 s | 2/2 13.0 s | 2/2 13.0 s | 2/2 12.9 s | 1/2 13.5 s |

## Sin vision — 10/70 metas, 0 caidas, 60 salidas

| y0 \ rumbo0 | +0° | +8° | -8° | +15° | -15° | +25° | -25° |
|---|---|---|---|---|---|---|---|
| +0 cm | 2/2 13.7 s | 0/2 | 0/2 | 0/2 | 0/2 | 0/2 | 0/2 |
| +10 cm | 2/2 13.7 s | 0/2 | 0/2 | 0/2 | 0/2 | 0/2 | 0/2 |
| -10 cm | 2/2 13.7 s | 0/2 | 0/2 | 0/2 | 0/2 | 0/2 | 0/2 |
| +15 cm | 2/2 13.7 s | 0/2 | 0/2 | 0/2 | 0/2 | 0/2 | 0/2 |
| -15 cm | 2/2 13.7 s | 0/2 | 0/2 | 0/2 | 0/2 | 0/2 | 0/2 |
