# Politica `rl_v1.0` (antes `carrera_v03`)

- Guardada: 2026-10-11 14:25 desde `runs/carrera_v03/checkpoints/model_5000000_steps.zip`.
- Entorno: `NaoRace-v0`; experimento `carrera_v03`; semilla 3.
- Commit del codigo al entrenar: `d9733e5-modificado`; comando: `C:\Users\camil\Documents\GitHub\NAO\src\train.py --config configs/carrera_v03.yaml --continuar policies/carrera_v02 --run-name carrera_v03`.
- Continua de: `policies/carrera_v02/model.zip`.
- Nota: Checkpoint de 5M de carrera_v03 (continúa de carrera_v02 15M; entrenada con salidas torcidas hasta ±15 cm / ±25° y el rumbo objetivo del paso 58c). Batería grande (vx 0.40, perturbaciones): con visión 100/100 en 12.8 s, desvío 7.4 cm; sin visión 82/100 sin caídas. Salidas malas: 70/70 sin perturbaciones; 135/140 con perturbaciones (5 caídas, todas en -25°, mu 0.4, semilla 1001). Usar vx_cmd 0.40.

Evaluar: `uv run python -m src.evaluate --model policies/rl_v1.0/model.zip --episodes 20`
Seguir entrenando: `uv run python -m src.train --config <config> --continuar policies/rl_v1.0`

Usar con el rumbo objetivo de la IMU alineado al carril (paso 58c; es el default de `NaoRace-v0`). Evaluar con `uv run python scripts/eval_carrera.py --modelo policies/rl_v1.0/model.zip --vx 0.40` y `uv run python scripts/eval_salida_mala.py --modelo policies/rl_v1.0/model.zip`.
