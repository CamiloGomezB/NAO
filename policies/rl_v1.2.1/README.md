# Politica `rl_v1.2.1`

- Guardada: 2026-10-14 11:00 desde `runs/esfuerzo_recto_v13_000/checkpoints/model_2000000_steps.zip`.
- Entorno: `NaoRace-v0`; experimento `esfuerzo_recto_v13`; semilla 1287221631.
- Commit del codigo al entrenar: `a1f6170-modificado`; comando: `C:\Users\camil\Documents\GitHub\NAO\src\train.py --config C:\Users\camil\Documents\GitHub\NAO\results\barridos\recto_v13\agente_000\config.yaml --run-name esfuerzo_recto_v13_000 --continuar C:\Users\camil\Documents\GitHub\NAO\runs\esfuerzo_esfuerzo_v12_cont_000\checkpoints\model_1000000_steps.zip`.
- Continua de: `runs/esfuerzo_esfuerzo_v12_cont_000/checkpoints/model_1000000_steps.zip`.
- Nota: Versión 1.2.1 (fase M3, arreglo de la 1.2): mismos límites de motores (esfuerzo_motor -0.5, modo instante, umbral 75 %) + centrado -5 (antes -0.89), 2M pasos desde el checkpoint de 1M del 62g2 (que iba recto). Batería completa de 44 corridas: 0 faltas, todas las articulaciones <= 80 % (peor 77 %), desvío medio de las salidas normales 5.6 cm (rl_v1.2: 17.7). Benchmark: 25/25, desvío máximo 6.5 cm, peor 79 %, 11.74 s. Usar vx_cmd 0.45.

Evaluar: `uv run python -m src.evaluate --model policies/rl_v1.2.1/model.zip --episodes 20`
Seguir entrenando: `uv run python -m src.train --config <config> --continuar policies/rl_v1.2.1`

## Resultados (2026-10-14)

- **Batería del benchmark** (con visión, μ 0.4–1.2 × 5 semillas, `vx_cmd` 0.45; `results/carrera/rl_v1.2.1/benchmark_vx0.45/`):
  25/25 metas, 0 faltas, **0/25 corridas sobre el 80 %** (peor 79 %), **desvío máximo de 6.5 cm**, 11.74 s de media.
- **Batería completa** (44 corridas, perturbaciones y salidas torcidas): 0 faltas, peor 77 %, desvío medio de las
  salidas normales de 5.6 cm.
- **Motores** (`results/riesgo_motores/riesgo.json`): rodillas 64–70 %, tobillos 56–60 %, rodillas dentro de la
  velocidad del motor. Picos de impacto del pie de ~3 × peso.
- Es un arreglo de `rl_v1.2`, que cumplía el 80 % pero llegaba torcida (E59). Cómo se entrenó:
  `docs/paper/entrenamiento_rl.md`, sección 12h.

Verla en el visor de 3 carriles (la usa por defecto): `uv run python demo/caminatas/carrera_vivo.py --rl-vx 0.45`.
