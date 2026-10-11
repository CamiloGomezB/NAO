# Politica `carrera_v01`

- Guardada: 2026-10-11 02:07 desde `runs/carrera_v01/checkpoints/model_15000000_steps.zip`.
- Entorno: `NaoRace-v0`; experimento `carrera_v01`; semilla 0.
- Commit del codigo al entrenar: `ea5e992-modificado`; comando: `C:\Users\camil\Documents\GitHub\NAO\src\train.py --config configs/carrera_v01.yaml --run-name carrera_v01`.
- Continua de: `None`.
- Nota: Checkpoint de 15M (paso 59; el entrenamiento se detuvo en 15.3M para seguir con carrera_v02). Con visión, vx_cmd 0.5: 10/10 metas en 10.5-10.6 s con desvío máximo de 3.4-5.6 cm; con perturbaciones 20/20 en 11.15 s. A vx_cmd 0.40, 20/20 en 13.6 s. Sin visión se cae o se sale (E45).

Evaluar: `uv run python -m src.evaluate --model policies/carrera_v01/model.zip --episodes 20`
Seguir entrenando: `uv run python -m src.train --config <config> --continuar policies/carrera_v01`

Evaluar con `uv run python scripts/eval_carrera.py --modelo policies/carrera_v01/model.zip` (no con `src.evaluate`, que es de `NaoWalk-v0`).
