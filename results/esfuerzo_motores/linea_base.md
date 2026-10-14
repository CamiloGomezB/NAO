# Línea base del esfuerzo de los motores (paso 62b, fase M2)

Par RMS de cada articulación ÷ par continuo de su motor real, en %. **Límite: 80 %.** Par continuo en la articulación (motor × reductora, sin eficiencia del engranaje): tipo 5 (HipPitch, KneePitch, AnklePitch) 2.33 N·m; tipo 1 (HipYawPitch, HipRoll, AnkleRoll) 2.47 N·m (`src/race/valores_v6.py`). Los hombros no tienen dato del motor y quedan fuera.

Fuentes: `results/riesgo_motores/riesgo.json` (μ 0.8, sin perturbaciones, 3 semillas; media), `results/barridos/esfuerzo_prueba/base_rl_v1.1.json` (batería completa de 44 corridas con perturbaciones, `vx_cmd` 0.45; peor corrida) y el robot quieto 1 s en la pose de partida (`NaoRaceEnv`, μ 0.8).

| Articulación | Quieto | B-Human (0.30) | NAOqi (0.12) | rl_v1.0 (0.45) | rl_v1.1 (0.45) | rl_v1.1, batería, peor |
|---|---|---|---|---|---|---|
| LHipYawPitch | 1 | 37 | 34 | 19 | 18 | 20 |
| LHipRoll | 0 | 30 | 56 | 46 | 37 | 43 |
| LHipPitch | 3 | 53 | 35 | 71 | 66 | 63 |
| LKneePitch | 34 | 70 | 60 | **102** | **101** | **102** |
| LAnklePitch | 5 | 44 | 39 | **105** | **100** | **104** |
| LAnkleRoll | 1 | 41 | 24 | 37 | 24 | 32 |
| RHipRoll | 0 | 31 | 56 | 47 | 39 | 43 |
| RHipPitch | 1 | 55 | 35 | 70 | 63 | 65 |
| RKneePitch | 34 | 67 | 61 | **96** | **97** | **102** |
| RAnklePitch | 4 | 40 | 38 | **107** | **105** | **109** |
| RAnkleRoll | 0 | 40 | 24 | 26 | 27 | 36 |

**Pasa el límite del 80 % (todas las articulaciones):** rl_v1.0 (vx 0.40): no, rl_v1.0 (vx 0.45): no, rl_v1.1 (vx 0.45): no, rl_v1.1 (vx 0.50): no, B-Human (0.30): sí, NAOqi (0.12): sí. `rl_v1.1` en la batería completa: 44/44 corridas sobre el 80 %.

**Lectura:** quieto, la rodilla ya usa ~34 % (la postura agachada de la pose home); el resto lo pone la marcha. Las que pasan el límite son rodillas y tobillos (pitch); caderas y roll quedan bajo 70 %.
