# Análisis del barrido `ronda2`

Generado por `scripts/analizar_barrido.py` con 20 agentes evaluados.

## 1. Resumen

- **Pasan el filtro duro** (0 caídas, 0 salidas en la batería corta): **17/20**.
- Descartados: 3.
- Puntaje (tiempo medio + 1σ) de los que pasan: mejor 11.38 s, mediana 11.92 s, peor 13.40 s.
- **Base `carrera_v03`** con la misma batería: puntaje 12.54 s. **16** agentes la superan.

## 2. Parámetros: pasan contra descartados, y correlación con el puntaje

Spearman entre los que pasan: negativo = el parámetro más alto da **mejor** puntaje (menos tiempo).

| Parámetro | Media, pasan (17) | Media, descartados (3) | Media, 5 mejores | Spearman con el puntaje |
|---|---|---|---|---|
| peso:seguimiento_vx | 1.36 | 1.42 | 1.84 | -0.64 |
| peso:meta | 22 | 30.5 | 23.6 | -0.08 |
| peso:rumbo | 0.565 | 0.668 | 0.525 | +0.12 |
| peso:centrado | -3.2 | -2.09 | -3.03 | -0.16 |
| peso:barrera_margen | -9.68 | -12.1 | -7.64 | -0.57 |
| peso:vel_lateral | -11.2 | -6.78 | -10.6 | -0.15 |
| peso:vel_giro | -1.02 | -1.12 | -0.864 | -0.10 |
| peso:salida_carril | -354 | -367 | -331 | -0.53 |
| peso:caida | -184 | -231 | -140 | -0.38 |
| peso:patron_marcha | 0.631 | 0.653 | 0.594 | +0.32 |
| peso:inclinacion | -2.51 | -2.2 | -2.36 | -0.20 |
| peso:choque_piernas | -2.75 | -2.28 | -3.36 | +0.33 |
| peso:cambio_accion | -0.0599 | -0.0368 | -0.0797 | +0.54 |
| friccion_min | 0.397 | 0.395 | 0.408 | -0.19 |
| friccion_max | 1.14 | 1.15 | 1.16 | -0.04 |
| vx_max | 0.538 | 0.515 | 0.561 | -0.21 |
| sigma_d_max_cm | 4.06 | 4.84 | 3.91 | +0.05 |
| sigma_psi_max_grados | 4.1 | 4.02 | 4.25 | -0.06 |

## 3. Por qué se descartan

| Prueba | Falta | Corridas |
|---|---|---|
| salida_mala | CAIDA | 7 |
| normal | CAIDA | 1 |

## 4. Los 5 mejores (pasan a la siguiente ronda)

| # | Agente | Puntaje [s] | t medio [s] | Desvío máx. [cm] | vx_max | Fricción | salida | caída | centrado | barrera | rumbo | seguim. vx | vel_giro | cambio_acc |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | agente_071 | 11.38 | 11.26 | 25.2 | 0.564 | [0.362, 1.064] | -303 | -177 | -0.89 | -5.6 | 0.37 | 1.62 | -1.40 | -0.076 |
| 2 | agente_026 | 11.51 | 11.26 | 21.0 | 0.583 | [0.439, 1.19] | -310 | -73 | -2.76 | -2.9 | 0.81 | 1.97 | -0.13 | -0.071 |
| 3 | agente_062 | 11.58 | 11.31 | 13.2 | 0.496 | [0.439, 1.093] | -394 | -108 | -4.19 | -17.1 | 0.53 | 1.94 | -1.48 | -0.066 |
| 4 | agente_081 | 11.64 | 11.40 | 14.2 | 0.59 | [0.413, 1.295] | -331 | -243 | -4.33 | -7.2 | 0.39 | 1.83 | -0.63 | -0.088 |
| 5 | agente_004 | 11.72 | 11.47 | 26.3 | 0.574 | [0.388, 1.135] | -317 | -100 | -2.99 | -5.3 | 0.53 | 1.82 | -0.69 | -0.099 |
