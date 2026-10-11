# Benchmark de caminatas en el carril de 5 m

Generado por `demo/caminatas/benchmark.py` el 2026-10-11 00:48 (commit ea5e992, PCGB, MuJoCo 3.14.0).

- **RL**: politica del equipo (`checkpoints/best_model.zip`), entrenada con friccion **mu = 1.0 sin aleatorizar**.
- **naoqi_like**: pasos planeados + control preview del ZMP (esquema de ALMotion), 0.12 m/s pedidos.
- **bhuman_like**: esquema Walk2014 (pasos de 250 ms, FSR + giroscopio), 0.30 m/s pedidos.
- **Vision**: simulada con el error medido (sigma_d 1.6 cm, sigma_psi 1.2 deg, 10 Hz).
- Salida con error de colocacion aleatorio (sigma 2 cm y 2 deg), el mismo para las 3 caminatas.

| Caminata | Vision | mu | Metas | Caidas | Salidas | Tiempo a meta [s] | Vel. media [m/s] | Desvio max [cm] | Rumbo max [deg] | Esfuerzo [N²m²s/m] |
|---|---|---|---|---|---|---|---|---|---|---|
| bhuman | no | 0.4 | 5/5 | 0 | 0 | 18.3 ± 0.0 | 0.272 | 6.5 | 5.7 | 44 |
| bhuman | no | 0.6 | 0/5 | 0 | 5 | — | 0.277 | 25.5 | 13.6 | 47 |
| bhuman | no | 0.8 | 2/5 | 0 | 3 | 16.4 ± 0.0 | 0.303 | 22.1 | 11.2 | 45 |
| bhuman | no | 1.0 | 4/5 | 0 | 1 | 16.2 ± 0.0 | 0.305 | 18.1 | 9.5 | 46 |
| bhuman | no | 1.2 | 3/5 | 0 | 2 | 16.4 ± 0.0 | 0.301 | 20.9 | 8.9 | 46 |
| bhuman | si | 0.4 | 5/5 | 0 | 0 | 18.3 ± 0.1 | 0.273 | 2.7 | 5.7 | 44 |
| bhuman | si | 0.6 | 5/5 | 0 | 0 | 16.8 ± 0.0 | 0.296 | 4.0 | 8.0 | 45 |
| bhuman | si | 0.8 | 5/5 | 0 | 0 | 16.4 ± 0.0 | 0.304 | 2.8 | 5.6 | 44 |
| bhuman | si | 1.0 | 5/5 | 0 | 0 | 16.2 ± 0.0 | 0.307 | 2.8 | 5.8 | 45 |
| bhuman | si | 1.2 | 5/5 | 0 | 0 | 16.4 ± 0.0 | 0.304 | 2.8 | 6.3 | 46 |
| naoqi | no | 0.4 | 5/5 | 0 | 0 | 45.4 ± 0.0 | 0.110 | 7.2 | 4.6 | 99 |
| naoqi | no | 0.6 | 5/5 | 0 | 0 | 47.8 ± 0.0 | 0.104 | 7.0 | 5.6 | 116 |
| naoqi | no | 0.8 | 0/5 | 0 | 5 | — | 0.101 | 25.7 | 8.6 | 116 |
| naoqi | no | 1.0 | 2/5 | 0 | 3 | 49.8 ± 0.0 | 0.100 | 24.3 | 6.0 | 121 |
| naoqi | no | 1.2 | 2/5 | 0 | 3 | 49.9 ± 0.0 | 0.099 | 19.3 | 6.1 | 123 |
| naoqi | si | 0.4 | 5/5 | 0 | 0 | 45.3 ± 0.0 | 0.110 | 2.5 | 5.3 | 99 |
| naoqi | si | 0.6 | 5/5 | 0 | 0 | 47.8 ± 0.0 | 0.104 | 2.5 | 6.8 | 116 |
| naoqi | si | 0.8 | 5/5 | 0 | 0 | 48.8 ± 0.0 | 0.102 | 2.4 | 6.6 | 116 |
| naoqi | si | 1.0 | 5/5 | 0 | 0 | 49.8 ± 0.0 | 0.100 | 2.4 | 5.8 | 120 |
| naoqi | si | 1.2 | 5/5 | 0 | 0 | 49.9 ± 0.0 | 0.100 | 2.3 | 5.0 | 122 |
| rl | no | 0.4 | 0/5 | 0 | 5 | — | 0.198 | 26.6 | 12.9 | 117 |
| rl | no | 0.6 | 4/5 | 0 | 1 | 24.8 ± 0.0 | 0.202 | 18.2 | 6.7 | 115 |
| rl | no | 0.8 | 2/5 | 0 | 3 | 24.8 ± 0.0 | 0.201 | 24.7 | 3.0 | 112 |
| rl | no | 1.0 | 4/5 | 0 | 1 | 24.8 ± 0.0 | 0.201 | 19.4 | 4.7 | 110 |
| rl | no | 1.2 | 5/5 | 0 | 0 | 24.8 ± 0.0 | 0.202 | 15.3 | 9.3 | 109 |
| rl | si | 0.4 | 5/5 | 0 | 0 | 24.2 ± 0.0 | 0.205 | 6.5 | 7.4 | 115 |
| rl | si | 0.6 | 5/5 | 0 | 0 | 24.2 ± 0.0 | 0.206 | 7.0 | 7.9 | 115 |
| rl | si | 0.8 | 5/5 | 0 | 0 | 24.3 ± 0.1 | 0.205 | 7.1 | 8.4 | 114 |
| rl | si | 1.0 | 5/5 | 0 | 0 | 24.3 ± 0.1 | 0.205 | 7.5 | 8.1 | 114 |
| rl | si | 1.2 | 5/5 | 0 | 0 | 24.3 ± 0.1 | 0.205 | 7.3 | 8.5 | 115 |
