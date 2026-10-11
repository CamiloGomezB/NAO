# Salidas malas: `runs/carrera_v03/checkpoints/model_5000000_steps.zip`

`scripts/eval_salida_mala.py`. Rumbo objetivo de la IMU: **carril**. vx_cmd 0.4, mu [0.8], 2 semillas por celda, perturbaciones no. Cada celda: metas / corridas y tiempo medio. y + = robot a la izquierda; rumbo + = girado a la izquierda.

## Con vision — 70/70 metas, 0 caidas, 0 salidas

| y0 \ rumbo0 | +0° | +8° | -8° | +15° | -15° | +25° | -25° |
|---|---|---|---|---|---|---|---|
| +0 cm | 2/2 12.4 s | 2/2 12.4 s | 2/2 12.3 s | 2/2 12.4 s | 2/2 12.3 s | 2/2 12.5 s | 2/2 12.5 s |
| +10 cm | 2/2 12.6 s | 2/2 12.5 s | 2/2 12.4 s | 2/2 12.4 s | 2/2 12.3 s | 2/2 12.6 s | 2/2 12.7 s |
| -10 cm | 2/2 12.4 s | 2/2 12.4 s | 2/2 12.4 s | 2/2 12.4 s | 2/2 12.4 s | 2/2 12.5 s | 2/2 12.7 s |
| +15 cm | 2/2 12.6 s | 2/2 12.6 s | 2/2 12.6 s | 2/2 12.5 s | 2/2 12.4 s | 2/2 12.6 s | 2/2 12.6 s |
| -15 cm | 2/2 12.5 s | 2/2 12.4 s | 2/2 12.5 s | 2/2 12.4 s | 2/2 12.4 s | 2/2 12.5 s | 2/2 12.6 s |

## Sin vision — 10/70 metas, 0 caidas, 60 salidas

| y0 \ rumbo0 | +0° | +8° | -8° | +15° | -15° | +25° | -25° |
|---|---|---|---|---|---|---|---|
| +0 cm | 2/2 12.6 s | 0/2 | 0/2 | 0/2 | 0/2 | 0/2 | 0/2 |
| +10 cm | 2/2 12.6 s | 0/2 | 0/2 | 0/2 | 0/2 | 0/2 | 0/2 |
| -10 cm | 2/2 12.6 s | 0/2 | 0/2 | 0/2 | 0/2 | 0/2 | 0/2 |
| +15 cm | 2/2 12.6 s | 0/2 | 0/2 | 0/2 | 0/2 | 0/2 | 0/2 |
| -15 cm | 2/2 12.6 s | 0/2 | 0/2 | 0/2 | 0/2 | 0/2 | 0/2 |
