# Politica `rl_v1.1`

- Guardada: 2026-10-13 08:09 desde `runs/barrido_ronda2_071/checkpoints/model_3000000_steps.zip`.
- Entorno: `NaoRace-v0`; experimento `barrido_ronda2`; semilla 1287219631.
- Commit del codigo al entrenar: `5a5c01d-modificado`; comando: `C:\Users\camil\Documents\GitHub\NAO\src\train.py --config C:\Users\camil\Documents\GitHub\NAO\results\barridos\ronda2\agente_071\config.yaml --run-name barrido_ronda2_071 --continuar C:\Users\camil\Documents\GitHub\NAO\runs\barrido_ronda1_071\final_model.zip`.
- Continua de: `runs/barrido_ronda1_071/final_model.zip`.
- Nota: Versión 1.1 de la política de carrera = agente_071 de la ronda 2 (paso 62), checkpoint de 3M (sobre su modelo de la ronda 1, que partió de rl_v1.0 = carrera_v03). Batería completa de 44 corridas: pasa sin faltas, puntaje 11.38 s (rl_v1.0: 12.54 s). Batería del benchmark (vx_cmd 0.45): 25/25 en 10.68-10.78 s (rl_v1.0: 11.2 s; B-Human 16.2-18.3 s). Con perturbaciones y salidas torcidas llegó a 25 cm del centro. Usar vx_cmd 0.45.

Evaluar: `uv run python -m src.evaluate --model policies/rl_v1.1/model.zip --episodes 20`
Seguir entrenando: `uv run python -m src.train --config <config> --continuar policies/rl_v1.1`
