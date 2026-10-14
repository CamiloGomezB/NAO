# Politica `rl_v1.2`

- Guardada: 2026-10-14 04:44 desde `runs/esfuerzo_esfuerzo_v12_cont_000/checkpoints/model_3000000_steps.zip`.
- Entorno: `NaoRace-v0`; experimento `esfuerzo_esfuerzo_v12_cont`; semilla 1287220631.
- Commit del codigo al entrenar: `cee48ff-modificado`; comando: `C:\Users\camil\Documents\GitHub\NAO\src\train.py --config C:\Users\camil\Documents\GitHub\NAO\results\barridos\esfuerzo_v12_cont\agente_000\config.yaml --run-name esfuerzo_esfuerzo_v12_cont_000 --continuar C:\Users\camil\Documents\GitHub\NAO\runs\esfuerzo_esfuerzo_v12_000\checkpoints\model_4000000_steps.zip`.
- Continua de: `runs/esfuerzo_esfuerzo_v12_000/checkpoints/model_4000000_steps.zip`.
- Nota: Versión 1.2 (fase M2): rl_v1.1 + castigo al esfuerzo de los motores (esfuerzo_motor -0.5, modo instante, umbral 75 %), 4M pasos (barrido esfuerzo_v12, agente_000) + 3M (esfuerzo_v12_cont), checkpoint de 3M. Batería completa de 44 corridas: 0 faltas, TODAS las articulaciones <= 80 % del par continuo del motor real (peor 78.8 %, RKneePitch), puntaje 11.78 s (rl_v1.1: 11.26 s de media pero 44/44 corridas sobre el 80 %). Usar vx_cmd 0.45.

Evaluar: `uv run python -m src.evaluate --model policies/rl_v1.2/model.zip --episodes 20`
Seguir entrenando: `uv run python -m src.train --config <config> --continuar policies/rl_v1.2`

## Resultados (2026-10-14)

- **Batería del benchmark** (con visión, μ 0.4–1.2 × 5 semillas, `vx_cmd` 0.45; `results/carrera/rl_v1.2/benchmark_vx0.45/`):
  25/25 metas, 0 caídas, 0 salidas, **0/25 corridas sobre el 80 %** (peor 77 %, RHipPitch), 10.91 s de media
  (10.71–11.0 s). Desvío máximo 11–18 cm.
- **Motores** (`results/riesgo_motores/riesgo.json`): rodillas 70–72 % y tobillos 60–65 % del par continuo
  (`rl_v1.1`: 97–105 %).
- Cómo se entrenó: `docs/paper/entrenamiento_rl.md`, sección 12g.

Verla en el visor de 3 carriles: `uv run python demo/caminatas/carrera_vivo.py --rl-vx 0.45`.
