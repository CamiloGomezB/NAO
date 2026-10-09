# Plan de trabajo — Caminata RL para NAO V6

Stack: **MuJoCo + Stable-Baselines3 (PPO)**, Windows nativo, entrenamiento en CPU.
Regla: cada paso termina con una **confirmación**, una **entrada en la bitácora** ([`docs/bitacora.md`](docs/bitacora.md)) y un **commit**.

> **Paso actual: 40** · Objetivo vigente: **caminata por RL para la Carrera Individual de la Copa NAO CCM MX 2026 (3 de noviembre de 2026)**,
> portable al repo final **PenaltyStack**. Baseline: la caminata de PenaltyStack (WalkingEngine de B-Human).
> Diseño: [`docs/plan_rl_carrera.md`](docs/plan_rl_carrera.md) · Repo final: [`docs/integracion_penaltystack.md`](docs/integracion_penaltystack.md) · Historial, errores y soluciones: [`docs/bitacora.md`](docs/bitacora.md).

**Cómo se usa este plan**

- `[x]` hecho y verificado · `[~]` en curso · `[ ]` pendiente · `[!]` bloqueado o fallido (el motivo va en la bitácora).
- Después del ✅ va el **criterio de aceptación**: el paso solo se marca hecho cuando se cumple.
- Si un paso falla, **no se borra**: se marca `[!]`, se documenta en la bitácora y, si hace falta, se agrega un paso nuevo con la corrección (p. ej. `56b`).
- Dos frentes pueden avanzar en paralelo, uno por persona del equipo:
  - **Simulación/RL:** fases J, K, L y M.
  - **Portabilidad y robot real:** fases N y O. El paso 47 (baseline) y el 65 (primera sesión con el robot) conviene hacerlos pronto.
- La **Fase P (cámara)** espera a que el equipo defina el método y no bloquea a las demás.

---

## Historial: sprint inicial de caminata en simulación (pasos 1–38)

## Fase A — Preparación
- [x] **1. Estructura del repo y `.gitignore`** — ✅ Carpetas visibles en VSCode
- [x] **2. Entorno virtual con `uv` + `pyproject.toml` con versiones fijadas** — ✅ `uv sync` sin errores
- [x] **3. Instalar MuJoCo y abrir el visor con un modelo de prueba** — ✅ Se abre la ventana 3D
- [x] **4. Push a GitHub** — ✅ Visible en github.com/CamiloGomezB/NAO

## Fase B — Modelo del NAO
- [x] **5. Buscar el modelo NAO V6 y revisar licencia** — ✅ Fuente y licencia acordadas
- [x] **6. Convertir a MJCF y cargar** — ✅ Lista de articulaciones y masa total ≈ 5.3 kg
- [x] **7. Verlo en el visor, suspendido** — ✅ Parece un NAO (partes bien ubicadas)
- [x] **8. Colisiones de pies con el suelo** — ✅ Se apoya sin hundirse ni rebotar
- [x] **9. Pose de pie con controlador PD** — ✅ Se mantiene de pie ~10 s
- [x] **10. Mover cada articulación por separado** — ✅ Direcciones y rangos correctos

## Fase C — Entorno RL
- [x] **11. Esqueleto `NaoWalkEnv` (Gymnasium)** — ✅ `check_env()` pasa
- [x] **12. Observaciones** — ✅ Valores con sentido, sin NaN
- [x] **13. Acciones (posiciones objetivo sobre pose nominal)** — ✅ Acción 0 = de pie; aleatorias no explotan
- [x] **14. Detección de caída / terminación** — ✅ El episodio termina al caer
- [x] **15. Recompensa inicial desglosada por términos** — ✅ Tabla de términos coherente
- [x] **16. Render de video offscreen** — ✅ `.mp4` visto por el usuario
- [x] **17. Benchmark de entornos en paralelo** — ✅ Pasos/s con 1, 8, 12 entornos

## Fase D — Primer entrenamiento
- [x] **18. `train.py` + `configs/ppo.yaml`** — ✅ Entrenamiento de 1 min guarda checkpoint
- [x] **19. `evaluate.py` separado** — ✅ Carga checkpoint e imprime métricas
- [x] **20. TensorBoard** — ✅ Curvas visibles en el navegador
- [x] **21. Entrenamiento corto (~20–30 min)** — ✅ La recompensa sube; aguanta más de pie

## Fase E — Caminata

- [x] **22. Variantes de recompensa/acciones** — V1 `ppo_natural.yaml` (doble apoyo, 0.2 m/s), V2 `ppo_brazos.yaml` (+ hombros)
- [x] **23. Entrenar V1 y V2 (5M pasos c/u)** — ✅ Curvas subiendo, checkpoints guardados
- [x] **24. Revisar video de las variantes** — ✅ Juicio del usuario: ¿mejora la marcha?
- [x] **25. Comparar base vs V1 vs V2** — ✅ Tabla comparativa con las mismas métricas
- [x] **26. Seleccionar `checkpoints/best_model.zip`** — ✅ Justificado con métricas

## Fase F — Evaluación y evidencia
- [x] **27. Evaluación en 20+ episodios con seeds fijas** — ✅ `results/metrics.json`
- [x] **28. Gráficas de entrenamiento** — ✅ `results/training_curves.png`
- [x] **29. GIF/video de la demo** — ✅ `media/demo.gif` aprobado

## Fase G — Reproducibilidad y entrega
- [x] **30. README completo** — ✅ Se entiende al leerlo
- [x] **31. Prueba de instalación limpia** — ✅ Demo corre siguiendo el README al pie de la letra
- [x] **32. Push final y revisión en GitHub** — ✅ Repo completo visible

## Fase H — Correcciones tras la entrega (reestructurada)
Retroalimentación: (1) el modelo debe ser específicamente el **NAO V6 completo**, no una aproximación del V5;
(2) explicar **qué variables usa el RL**, cuáles no y por qué (sin código ni matemáticas).

- [x] **33. Documento de variables del RL** (`docs/variables_rl.md`) — ✅ Se entiende sin leer código
- [x] **34–35. Modelo V6 desde la descripción oficial de B-Human** (`scripts/build_nao_v6.py` genera `nao.xml` y las mallas desde `NaoV6H25.rsi3`) — hecho en el commit `d9207ec`, **sin validar**
- [ ] ~~36. Revalidar el modelo~~ → pasa a los pasos **43–46**
- [ ] ~~37. Reentrenar V2 brazos en el V6~~ → reemplazado por las generaciones de carrera (**Fase M**)
- [ ] ~~38. Actualizar README, SOURCE.md, resultados y GIF~~ → pasa a los pasos **43** y **76**

---

## Proyecto actual: Carrera Individual — Copa NAO CCM MX 2026 (pasos 39–76)

**Meta:** una política de RL que haga caminar al NAO V6 real por el carril de **5 m × 70 cm** lo más
**rápido** y lo más **recto** posible, **sin caer**. Debe ser **portable a PenaltyStack**, el repo final del equipo.

**Alcance de este repo:** solo el RL de la caminata. La cámara está pendiente de definir: sus pasos (Fase P)
quedan reservados y no bloquean el resto.

**Baseline:** la caminata de PenaltyStack, el WalkingEngine de B-Human.

**Documentos:**
- Diseño: [`docs/plan_rl_carrera.md`](docs/plan_rl_carrera.md).
- Condiciones del repo final: [`docs/integracion_penaltystack.md`](docs/integracion_penaltystack.md).

## Fase I — Organización e integración con PenaltyStack
- [x] **39. Documentación y replanificación** (`CLAUDE.md`, bitácora, `docs/plan_rl_carrera.md`, `docs/integracion_penaltystack.md`, contrato de articulaciones en `third_party/penaltystack/`, README, este plan) — ✅ El compañero entiende el plan, el paso actual, el baseline y las condiciones de PenaltyStack sin preguntar
- [ ] **40. Contrato v1 en código** (`src/race/contract.py`): orden de articulaciones de B-Human, ciclo de 24 ms, observación de 51 valores armada desde un `frame` con el formato de `SensorAdapter` de PenaltyStack y la acción de 13 ángulos devuelta en ese orden — ✅ Prueba automática: un `frame` de ejemplo produce la observación esperada y la acción vuelve con los nombres correctos
- [ ] **41. Políticas compartidas en el repo** (`policies/carrera_vNN/`: modelo, normalización, config, metadatos, métricas y README de la generación; `.gitignore` y `scripts/export_model.py` adaptados) — ✅ El compañero clona, evalúa la misma política sin entrenar y puede continuar desde ella
- [ ] **42. Segundo equipo de entrenamiento** (torre Ryzen + RTX 5060): instalación limpia, benchmark de entornos en paralelo, nombre del equipo en los metadatos — ✅ Pasos/s medidos en ambos equipos y métricas comparables con la misma config

## Fase J — Modelo V6 al día y baseline
- [ ] **43. Validar la física V6 contra el RSI3** (masa, masa e inercia por cuerpo, ejes y rangos) + actualizar `SOURCE.md` y la sección 10 del README — ✅ Verificación automática en OK; la documentación ya no habla del V5
- [ ] **44. Diagnóstico de caídas y choque entre piernas en el V6**: (a) reproducir sin visor las caídas de la demo interactiva al **pausar y reanudar** (`scripts/demo_interactive.py`, muchas pausas automáticas) y compararlas con las 399/400 paradas del modelo aproximado; (b) distancia mínima entre piernas y choques con la política actual, con acciones aleatorias y en un entrenamiento corto desde cero — ✅ Informe en `results/` con números: % de caídas al reanudar, motivo (choque entre piernas o equilibrio), cuándo chocan y con qué articulación
- [ ] **45. Quitar los valores del modelo aproximado**: pose de pie, escalas de acción (HipRoll asimétrico, HipYawPitch), altura objetivo, altura de caída, período de marcha y ciclo de 24 ms, con los valores del V6 y de B-Human como referencia — ✅ `inspect_actions` muestra que ninguna acción extrema cruza las piernas; `check_standing` en OK
- [ ] **46. Revalidar contactos, de pie y barrido articular con el V6** — ✅ `check_contacts`, `check_standing` y `joint_sweep` en OK + revisión visual del usuario
- [ ] **47. Medir el baseline de PenaltyStack en simulación** (WalkingEngine de B-Human en su simulador, en línea recta a 0.15, 0.25 y 0.30 m/s, 5 corridas cada una; requiere compilar su runtime con VS 2022 Build Tools) — ✅ `results/baseline_penaltystack.md` con tiempo en 5 m, deriva lateral, rumbo máximo y caídas; fila en la tabla del README

## Fase K — Entorno de carrera `NaoRace` (contrato v1, sin cámara)
- [ ] **48. Observación v1** (51 valores, solo sensores reales: IMU, error de rumbo, ángulos, velocidades, acción anterior, carga de los pies desde los FSR, reloj, `vx_cmd`; sin velocidad lineal) — ✅ `inspect_obs` en OK y la misma observación sale del contrato del paso 40
- [ ] **49. Acción v1** (13 ángulos: piernas, HipYawPitch limitado, HipRoll asimétrico y hombros, cada 24 ms) + comando `vx_cmd` — ✅ `inspect_actions` en OK
- [ ] **50. Recompensa v1** con los pesos iniciales de `docs/plan_rl_carrera.md` (sección 5.4), incluidos rumbo, deriva lateral, choque entre piernas y salida de carril — ✅ `inspect_reward` ordena bien los comportamientos
- [ ] **51. Episodio de carrera** (arranque desde quieto, rumbo y posición inicial desviados, carril de 70 cm como terminación, 30 s) — ✅ `check_env` en OK + video revisado por el usuario
- [ ] **52. Métricas de carrera en `evaluate.py`** (tiempo en 5 m, deriva lateral final, rumbo máximo, choques entre piernas, salidas de carril, caídas, consistencia) — ✅ JSON con métricas de carrera

## Fase L — Caminar recto sin cámara (pérdida de rectitud simulada)
- [ ] **53. Perturbaciones de rumbo**: empujones de giro y laterales, inclinación del suelo y cambios del rumbo objetivo — ✅ Se activan por config y se ven en el video
- [ ] **54. Asimetrías aleatorias entre lados**: fricción por pie, ganancia de servos por pierna, errores de calibración, centro de masa y holgura — ✅ Deriva medida sin y con asimetrías, con la misma política
- [ ] **55. Estimación de rumbo imperfecta**: ruido gaussiano, sesgo que deriva, retardo y pérdidas, con wrappers propios de Gymnasium — ✅ Prueba automática de la estadística del ruido, reproducible con semilla
- [ ] **56. Prueba de rectitud** (100 episodios con todo lo anterior, 5 m) — ✅ Deriva lateral final, rumbo máximo y % dentro del carril registrados; meta inicial ≥ 95 % dentro del carril

## Fase M — Generaciones de RL ("muchos RL, cada vez mejores")
- [ ] **57. Generación `carrera_v01`** — ✅ Cruza los 5 m recto y sin caer en simulación; fila en la tabla de generaciones
- [ ] **58. Currículo de velocidad** (ampliar el rango de `vx_cmd` mientras la marcha siga estable y recta) — ✅ Curva de velocidad máxima estable vs pasos de entrenamiento
- [ ] **59. Domain randomization general** (fricción de duela, masas, rigidez de servos, retardo, ruido de IMU y FSR) — ✅ 0 caídas en 100 episodios aleatorizados a la velocidad elegida
- [ ] **60. Ciclo de generaciones** (`v02`, `v03`, …): una hipótesis → un cambio → comparación con el baseline de PenaltyStack — ✅ Cada generación con config, métricas y conclusión en la bitácora
- [ ] **61. (Opcional) Entrenamiento en GPU** (MJX / MuJoCo Playground en WSL2 con la RTX 5060), solo si el tiempo de entrenamiento limita — ✅ Decisión documentada con mediciones

## Fase N — Portabilidad a PenaltyStack
- [ ] **62. Exportar la política** (pesos y normalización en JSON o `.npz` + versión del contrato) y **módulo de inferencia** compatible con Python 2.7 y 3, sin dependencias y con numpy opcional — ✅ Diferencia con SB3 < 1e-5 en 1000 observaciones; tiempo de inferencia medido en PC
- [ ] **63. Correr la política dentro del simulador de PenaltyStack** en lugar del motor de B-Human (rama de prueba en PenaltyStack, coordinada con su autor) — ✅ Camina 5 m; comparación directa con el baseline en el mismo simulador
- [ ] **64. Ejecutor a bordo** integrado a PenaltyStack (START: táctil frontal 0.25 s tras el silbato; ABORT: pecho 0.3 s; ciclo de 24 ms; paro por inclinación), desplegado con su mecanismo de Ethernet — ✅ Paquete generado y probado en seco; revisado por el autor de PenaltyStack

## Fase O — Robot real
- [ ] **65. Sesión real #1** (robot suspendido): Python y numpy a bordo, tiempo de inferencia, respuesta de los servos, ruido de IMU y FSR, **deriva de `AngleZ`**, ALMotion vs LoLA — ✅ Datos en `data/real/sesion_01/` y decisión de interfaz documentada
- [ ] **66. Identificación de servos y del ruido de rumbo** → valores en el simulador (pasos 55 y 59) — ✅ Gráfica simulación vs real por articulación
- [ ] **67. Baseline en el robot real**: la caminata de B-Human con el framework de B-Human en el NAO (pista de 5 m marcada con cinta, 5 corridas) — ✅ Tabla de tiempo, caídas y deriva
- [ ] **68. Pruebas escalonadas de la política** (suspendido → arnés → 1 m → 5 m, con `vx_cmd` creciente) — ✅ Cada prueba registrada con video, log y resultado
- [ ] **69. Ciclo sim-to-real** (diferencia observada → ajuste → nueva generación) — ✅ Cada iteración documentada

## Fase P — Cámara (pendiente de definición del equipo; no bloquea lo anterior)
- [ ] **70. Definir el método de cámara** (lo trae el equipo): qué mide, a qué frecuencia y con qué error — ✅ Documento con entradas, salidas y precisión medida en la pista
- [ ] **71. Simular la salida de la cámara con ruido gaussiano** (valor real + ruido + retardo + pérdidas a 10 Hz) y agregarla como contrato v2 de la política — ✅ Política v2 entrenada; mejora de la deriva lateral medida
- [ ] **72. Integración en el robot real** — ✅ 5 corridas seguidas sin pisar las líneas

## Fase Q — Benchmark, integración final y cierre
- [ ] **73. Benchmark final RL vs baseline de PenaltyStack** (simulación y robot real, mismo protocolo, 10 corridas) — ✅ Tabla final
- [ ] **74. Selección, congelamiento e integración en PenaltyStack** (la más rápida con 0 caídas y 0 salidas; si ninguna cumple, baseline) — ✅ Política `carrera_final`, tag de Git y PR al repo final
- [ ] **75. Simulacro completo de competencia** — ✅ Corrida completa sin cambios de último minuto
- [ ] **76. Documentación final para el paper** — ✅ Una persona externa entiende el proceso completo leyendo el repo
