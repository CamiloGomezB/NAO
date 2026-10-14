# Diagnóstico de rectitud de `rl_v1.2` (2026-10-14, E59)

Cómo se midió: corridas con la cámara simulada (`eval_carrera.correr`), con la cámara renderizada (el corredor de
`demo/caminatas/carrera_vivo.py`) y la sensibilidad de la política, sumando 5 cm o 5° a una entrada de la
observación y midiendo cuánto cambia la acción. Datos crudos en `diagnostico_rectitud.json`.

| Prueba (cámara simulada, `vx_cmd` 0.45, μ 0.4/0.8/1.2 × 3 semillas, sin perturbaciones) | `rl_v1.1` | `rl_v1.2` |
|---|---|---|
| Desvío máximo medio, con visión | 3.5 cm | **17.6 cm** |
| Desvío final medio, con visión | +1.1 cm | **−17.5 cm** (a la derecha) |
| Desvío máximo medio, sin visión | 14.7 cm (2 salidas) | 17.2 cm (2 salidas) |
| Cambio de la acción si la cámara dice d + 5 cm | 0.087 | 0.067 |
| Cambio de la acción si la cámara dice psi + 5° | 0.177 | 0.163 |
| Cambio de la acción si el rumbo de la IMU dice + 5° | 0.459 | 0.441 |

**Cámara renderizada** (como el visor, semilla 1000, `vx_cmd` 0.45): `rl_v1.1` μ 1.0: final +1.1 cm; μ 0.6: −13.4 cm.
`rl_v1.2` μ 1.0: −3.8 cm; μ 0.6: −6.4 cm. Con la cámara renderizada la deriva fue menor que con la simulada en esas
dos corridas, pero en el visor Camilo la vio llegar cerca de la línea derecha.

**Otros checkpoints del mismo entrenamiento:**

| Checkpoint (benchmark parcial: μ 0.4–1.2 × 3 semillas) | Desvío máx. medio | Final medio | Peor esfuerzo | Tiempo |
|---|---|---|---|---|
| Barrido 62g, `agente_000` 2M | 4.2 cm | +2.4 cm | 95 % | 11.24 s |
| Barrido 62g, `agente_000` 4M (base del 62g2) | **2.7 cm** | −0.5 cm | 80 % | 10.94 s |
| 62g2, 1M | **2.6 cm** | −1.4 cm | 75 % | 11.19 s |
| 62g2, 2M | 17.2 cm | −17.2 cm | 78 % | 11.42 s |
| 62g2, 3M = `rl_v1.2` | 18.0 cm | −17.9 cm | 76 % | 10.95 s |
