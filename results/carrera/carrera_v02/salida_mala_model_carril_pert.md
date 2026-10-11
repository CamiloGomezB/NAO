# Salidas malas: `policies/carrera_v02/model.zip`

`scripts/eval_salida_mala.py`. Rumbo objetivo de la IMU: **carril**. vx_cmd 0.4, mu [0.4, 1.2], 2 semillas por celda, perturbaciones si. Cada celda: metas / corridas y tiempo medio. y + = robot a la izquierda; rumbo + = girado a la izquierda.

## Con vision — 128/140 metas, 12 caidas, 0 salidas

| y0 \ rumbo0 | +0° | +8° | -8° | +15° | -15° | +25° | -25° |
|---|---|---|---|---|---|---|---|
| +0 cm | 4/4 12.9 s | 4/4 12.8 s | 4/4 12.9 s | 3/4 12.7 s | 4/4 13.0 s | 1/4 13.0 s | 4/4 13.1 s |
| +10 cm | 4/4 13.0 s | 4/4 12.9 s | 4/4 13.0 s | 3/4 12.8 s | 4/4 13.0 s | 2/4 13.2 s | 4/4 13.2 s |
| -10 cm | 4/4 12.9 s | 4/4 12.9 s | 4/4 13.0 s | 4/4 13.0 s | 4/4 13.0 s | 3/4 13.1 s | 4/4 13.3 s |
| +15 cm | 4/4 13.0 s | 4/4 13.0 s | 4/4 13.0 s | 3/4 12.9 s | 4/4 13.0 s | 1/4 13.3 s | 4/4 13.3 s |
| -15 cm | 4/4 12.9 s | 4/4 13.0 s | 4/4 13.0 s | 4/4 13.2 s | 4/4 13.2 s | 4/4 13.0 s | 4/4 13.3 s |

## Sin vision — 19/140 metas, 0 caidas, 121 salidas

| y0 \ rumbo0 | +0° | +8° | -8° | +15° | -15° | +25° | -25° |
|---|---|---|---|---|---|---|---|
| +0 cm | 4/4 13.7 s | 0/4 | 0/4 | 0/4 | 0/4 | 0/4 | 0/4 |
| +10 cm | 4/4 13.7 s | 0/4 | 0/4 | 0/4 | 0/4 | 0/4 | 0/4 |
| -10 cm | 4/4 13.7 s | 0/4 | 0/4 | 0/4 | 0/4 | 0/4 | 0/4 |
| +15 cm | 3/4 13.6 s | 0/4 | 0/4 | 0/4 | 0/4 | 0/4 | 0/4 |
| -15 cm | 4/4 13.7 s | 0/4 | 0/4 | 0/4 | 0/4 | 0/4 | 0/4 |
