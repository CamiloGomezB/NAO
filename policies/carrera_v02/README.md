# Politica `carrera_v02`

- Guardada: 2026-10-11 03:37 desde `runs/carrera_v02/checkpoints/model_15000000_steps.zip`.
- Entorno: `NaoRace-v0`; experimento `carrera_v02`; semilla 2.
- Commit del codigo al entrenar: `ea5e992-modificado`; comando: `C:\Users\camil\Documents\GitHub\NAO\src\train.py --config configs/carrera_v02.yaml --continuar runs/carrera_v01/checkpoints/model_15000000_steps.zip --run-name carrera_v02`.
- Continua de: `runs/carrera_v01/checkpoints/model_15000000_steps.zip`.
- Nota: Elegida (05:55) tras evaluar 5–40M: checkpoint de 15M de carrera_v02 (continúa de carrera_v01 a 15M). Con visión: 10/10 en 10.6 s; con perturbaciones 20/20 en 10.85 s (vx 0.5) y 13.1 s (vx 0.40). Sin visión: 10/10 sin faltas (nominal); con perturbaciones 10-14/20, 0 caídas.

Evaluar: `uv run python -m src.evaluate --model policies/carrera_v02/model.zip --episodes 20`
Seguir entrenando: `uv run python -m src.train --config <config> --continuar policies/carrera_v02`

Selección: `results/carrera/carrera_v02/seleccion_100/` (100 episodios por condición, `vx_cmd` 0.40, perturbaciones): con visión 100/100 en 13.0 ± 0.5 s; sin visión 89/100 y 0 caídas. Usar `vx_cmd` 0.40. Evaluar con `uv run python scripts/eval_carrera.py --modelo policies/carrera_v02/model.zip`.
