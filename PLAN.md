# Plan de trabajo — Caminata RL para NAO V6

Stack: **MuJoCo + Stable-Baselines3 (PPO)**, Windows nativo, entrenamiento en CPU.
Regla: cada paso termina con una **confirmación**, una **entrada en la bitácora** ([`docs/bitacora.md`](docs/bitacora.md)) y un **commit**.

> **Paso actual: 46** (ruta crítica; 42–45 se intercalan) · Objetivo vigente: **caminata por RL para la Carrera Individual de la Copa NAO CCM MX 2026 (3 de noviembre de 2026)**,
> más rápida que las caminatas de **B-Human** y **NAOqi** (tres carriles de comparación), con visión de carril y portable al repo final **PenaltyStack**.
> Diseño: [`docs/plan_rl_carrera.md`](docs/plan_rl_carrera.md) · Repo final: [`docs/integracion_penaltystack.md`](docs/integracion_penaltystack.md) · Historial, errores y soluciones: [`docs/bitacora.md`](docs/bitacora.md).

**Cómo se usa este plan**

- `[x]` hecho y verificado · `[~]` en curso · `[ ]` pendiente · `[!]` bloqueado o fallido (el motivo va en la bitácora).
- Después del ✅ va el **criterio de aceptación**: el paso solo se marca hecho cuando se cumple.
- Si un paso falla, **no se borra**: se marca `[!]`, se documenta en la bitácora y, si hace falta, se agrega un paso nuevo con la corrección (p. ej. `56b`).
- Todo se trabaja en la rama **`main`**, con un commit por paso. Los entrenamientos corren en **un solo PC**:
  la laptop Ryzen 7 5800H.
- La primera sesión con el robot (paso 69) y la precisión de la cámara en pista (paso 70) conviene hacerlas pronto.
- **Todo entrenamiento de RL usa fricción aleatoria**: no se sabe qué piso habrá en la competencia (paso 47).
- El paso 75 (colores definitivos) se ejecuta cuando la organización avise, pero el procedimiento se ensaya antes.

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
- [ ] ~~36. Revalidar el modelo~~ → pasa a los pasos **44–49**
- [ ] ~~37. Reentrenar V2 brazos en el V6~~ → reemplazado por el entrenamiento por población (**Fase M**)
- [ ] ~~38. Actualizar README, SOURCE.md, resultados y GIF~~ → pasa a los pasos **44** y **80**

---

## Proyecto actual: Carrera Individual — Copa NAO CCM MX 2026 (pasos 39–80)

**Meta:** una política de RL que haga caminar al NAO V6 real por el carril de **5 m × 70 cm** más rápido que
los dos baselines, sin salirse del carril y sin caer. Debe ser **portable a PenaltyStack**, el repo final
del equipo.

**Piezas:**
- **RL de la caminata:** este repo.
- **Visión de carril (cámara) y simulador de la pista:** vienen de
  [danielpaya/nao_linea](https://github.com/danielpaya/nao_linea) y se integran en `main` en el paso 40. Desde
  ahí, el MuJoCo de la pista es el que se usa en este repo.
- **Tres carriles de comparación:**
  - **baseline 1:** caminata de **NAOqi**;
  - **baseline 2:** caminata de **B-Human**, la de PenaltyStack;
  - **RL** del equipo.

**Documentos:**
- Diseño: [`docs/plan_rl_carrera.md`](docs/plan_rl_carrera.md).
- Condiciones del repo final: [`docs/integracion_penaltystack.md`](docs/integracion_penaltystack.md).

> **Numeración renovada el 2026-10-10.** Los pasos 40–76 anteriores se reorganizaron como 40–80 al sumar
> la cámara, los 3 carriles, la fricción y los 100 agentes. Equivalencias para leer documentos
> anteriores, como los de nao_linea:
>
> | Antes | Ahora | | Antes | Ahora |
> |---|---|---|---|---|
> | 40 contrato | 41 | | 61 GPU | 65 |
> | 41 políticas | 42 | | 62–64 portabilidad | 66–68 |
> | 42 segundo equipo | 43 | | 65 sesión real #1 | 69 |
> | 43 validar física | 44 | | 66 identificación | 71 |
> | 44 diagnóstico | 45 | | 67 baseline real | 73 |
> | 45 valores aproximados | 46 | | 68 pruebas escalonadas | 72 |
> | 46 revalidar | 49 | | 69 ciclo sim-to-real | 74 |
> | 47 baseline B-Human en sim | 50 | | 70 método de cámara | 40 (integrar) y 70 (precisión en pista) |
> | 48–52 entorno de carrera | 53–56 y 52 | | 71 cámara simulada | 57 |
> | 53–56 rectitud | 58 | | 72 cámara en el robot | 68 y 72 |
> | 57–60 generaciones | 59–64 | | 73–76 cierre | 77–80 |

**Ruta crítica del RL** (lo que hay que hacer en orden para tener la política de carrera):

> 41 contrato → 46 valores del V6 → 53–58 entorno de carrera con cámara y faltas → 58b la política en los 3 carriles → 59 base → 60–63 los 100 agentes → 77–78 selección
>
> Los demás pasos (42, 43, 44, 45, 48b, 49, 50–52) se intercalan cuando haya un entrenamiento corriendo.

## Fase I — Organización e integración
- [x] **39. Documentación y replanificación** (`CLAUDE.md`, bitácora, `docs/plan_rl_carrera.md`, `docs/integracion_penaltystack.md`, contrato de articulaciones en `third_party/penaltystack/`, README, este plan) — ✅ El compañero entiende el plan, el paso actual, el baseline y las condiciones de PenaltyStack sin preguntar
- [x] **40. Integrar nao_linea en `main`**: visión de carril (`carril/`), escena MuJoCo de la pista con la cámara del NAO (`demo/build_scene.py`), demo con el RL actual (`demo/run_demo.py`), caminatas de los baselines y benchmark de 3 carriles (`demo/caminatas/`), kit del robot (`robot/`) y resultados. Sin `__pycache__`, `MUJOCO_LOG.TXT`, `.bundle` ni `.zip` — ✅ La demo con cámara y la carrera de 3 carriles corren en este PC con el RL actual; el usuario ve la cámara funcionando
  - Hecho (2026-10-10): código integrado; pista, cámara y visión verificadas (`scripts/check_vision.py`: 100 % válidas, error medio 1.27 cm y 0.86°); caminatas de los baselines llegan a la meta.
  - ~~Bloqueado por Smart App Control~~ → resuelto el 2026-10-10: el usuario lo desactivó. Demo RL + cámara sin ventanas: solo RL se sale a 0.54 m; RL + visión llega en 24.2 s. Benchmark corto idéntico al de nao_linea.
  - 2026-10-10: el usuario vio que el visor no mostraba bien los 3 carriles. Se corrigió:
    - `run_demo.py --live` abre los 3 carriles con sus 3 robots, cada uno con su color y con su cámara real;
    - la meta está en los 3 carriles y hay una ventana con las 3 cámaras.
  - 2026-10-10: el visor se veía roto por la GPU integrada AMD → los scripts piden la NVIDIA. **Aprobado por el usuario** el 2026-10-10: los 3 carriles, la cámara, `d`/`psi` y la fricción (μ = 1.0 en la demo) funcionan bien.
- [x] **41. Contrato v1 en código** (`src/race/contract.py`): orden de articulaciones de B-Human, ciclo de 24 ms, observación de 54 valores (incluye `d`, `psi` y válido de la cámara) armada desde un `frame` con el formato de PenaltyStack, y acción de 13 ángulos — ✅ Prueba automática: un `frame` de ejemplo produce la observación esperada y la acción vuelve con los nombres correctos
  - Hecho (2026-10-10): `src/race/contract.py` (Python 2.7/3, sin numpy) + `scripts/check_contract.py` en OK (8 grupos de pruebas). Pendiente para el paso 69: correrlo en el Python 2.7 real del NAO (en el PC no hay 2.7).
- [ ] **42. Políticas compartidas en el repo** (`policies/carrera_vNN/`: modelo, normalización, config, métricas y README de la generación) — ✅ Desde un clon limpio se evalúa la misma política sin entrenar y se puede continuar desde ella
- [ ] **43. Rendimiento de entrenamiento en este PC** (laptop Ryzen 7 5800H, el único equipo de entrenamiento): pasos/s con el modelo V6 y la fricción aleatoria — ✅ Pasos/s medidos y costo real del barrido de 100 agentes recalculado (sección 11.3 del diseño)

## Fase J — Modelo V6, fricción y pista
- [ ] **44. Validar la física V6 contra el RSI3** (masa, masa e inercia por cuerpo, ejes y rangos) + actualizar `SOURCE.md` y la sección 10 del README — ✅ Verificación automática en OK; la documentación ya no habla del V5
- [ ] **45. Diagnóstico de caídas y choque entre piernas**: (a) caídas de la demo interactiva al pausar y reanudar, reproducidas sin visor; (b) distancia mínima entre piernas y choques, con acciones aleatorias y en un entrenamiento corto desde cero — ✅ Informe en `results/` con % de caídas al reanudar, motivo y articulación
- [ ] **46. Quitar los valores del modelo aproximado**: pose de pie, escalas de acción (HipRoll asimétrico, HipYawPitch), altura objetivo y de caída, período de marcha y ciclo de 24 ms — ✅ `inspect_actions` muestra que ninguna acción extrema cruza las piernas; `check_standing` en OK
- [x] **47. Fricción explícita y configurable** en el piso y en los pies (MuJoCo usa el mayor), aleatoria por episodio en [0.4, 1.2] con asimetría entre pies; probar `condim` 3 contra 4 — ✅ Prueba automática de que el μ pedido es el μ efectivo; decisión de `condim` documentada
  - Hecho (2026-10-10): `NaoWalkEnv` sortea μ en [0.4, 1.2] con asimetría ≤ 0.1 por defecto (`friction` fijo solo para evaluar); `src.train` rechaza fricción fija salvo `--friccion-fija`; `src.evaluate --mu`; `configs/ppo_brazos_friccion.yaml`; `scripts/check_friction.py` en OK. `condim` se mantiene en 3 (comparación con 4 no concluyente; se repite en el paso 51).
- [x] **48. Colores de la pista en un solo archivo** (`config/pista.yaml`: piso, veta, línea, salida y meta), usado por la escena, la demo, el benchmark, la verificación de la visión y el robot (`config/pista_robot.json`); `scripts/cambiar_colores.py` cambia, regenera y verifica — ✅ Cambiar colores = un comando con verificación automática
  - Hecho (2026-10-10): visión con modo **brillo** o **color** según los colores; matriz de 63 combinaciones con 57 OK (`results/camara/matriz_colores.md`); el robot toma la polaridad y el modo de `pista_robot.json`.
- [ ] **48b. Escena de 3 carriles con física compartida** para medir choques entre robots (hoy cada robot de `carrera_vivo` va en su propia física) — ✅ La escena detecta contactos entre robots de carriles vecinos
- [ ] **49. Revalidar contactos, de pie y barrido articular con el V6** — ✅ `check_contacts`, `check_standing` y `joint_sweep` en OK + revisión visual del usuario

## Fase K — Benchmark de los tres carriles (RL, B-Human, NAOqi)
- [ ] **50. WalkingEngine original de B-Human en el simulador de PenaltyStack** a 0.15, 0.25 y 0.30 m/s, para validar la réplica tipo B-Human. Requiere compilar su runtime con VS 2022 Build Tools — ✅ `results/baseline_penaltystack.md`; diferencia con la réplica documentada
- [ ] **51. Benchmark de 3 carriles completo y regenerado** con la batería común: 5 fricciones × colocaciones fijas por semilla × con y sin visión. Incluye la escena compartida para choques — ✅ `results/benchmark/` con la tabla completa (150+ corridas) y fila de cada caminata en la tabla del README
- [ ] **52. Métricas de carrera unificadas** en `evaluate.py` y el benchmark (tiempo en 5 m, velocidad, desvío y rumbo máximos, salidas, caídas, choques, consistencia; mismo JSON) — ✅ Las dos herramientas dan los mismos números para la misma corrida

## Fase L — Entorno de carrera `NaoRace` con cámara (contrato v1)
- [ ] **53. Observación de 54 valores** (IMU, rumbo, `d`, `psi`, válido, articulaciones, acción anterior, carga de los pies, reloj, `vx_cmd`) — ✅ `inspect_obs` en OK y coincide con el contrato del paso 41
- [ ] **54. Acción de 13 ángulos cada 24 ms** + comando `vx_cmd` — ✅ `inspect_actions` en OK
- [ ] **55. Recompensa con las faltas del reglamento** (sección 6.4 del diseño): salida de carril (−200), choque con otro robot (−400) y caída (−100) como terminales, barrera de margen a menos de 10 cm de la línea, centrado (`d`²) y rumbo (`psi`) del carril, bono de meta. **Pesos iniciales y rangos del barrido en un solo archivo** (`configs/carrera/pesos.yaml`), del que leen el entorno y el lanzador de los 100 agentes — ✅ `inspect_reward` ordena bien los comportamientos: salirse del carril siempre es peor que ir lento, y el YAML coincide con la tabla del diseño
- [ ] **56. Episodio de carrera** (desde quieto, error de colocación, 0.5 s de medición de la visión, carril, meta, 30 s, fricción sorteada) — ✅ `check_env` en OK + video revisado por el usuario
- [ ] **57. Cámara simulada**: `d` y `psi` reales + ruido gaussiano, retardo, pérdidas y mediciones malas a 10 Hz, con los σ de nao_linea y su rango hasta 3×, **con las mismas convenciones que la visión real** (sección 6.7 del diseño) — ✅ Prueba automática de la estadística del ruido, reproducible con semilla; en las mismas trayectorias, la señal simulada y la de `VisionCamara` (cámara renderizada) tienen el mismo signo, frecuencia y error dentro del rango
- [ ] **58. Pérdida de rectitud simulada** (asimetrías, perturbaciones, deriva de la IMU, tramos sin visión) + prueba de rectitud de 100 episodios — ✅ Deriva sin visión y desvío con visión registrados
- [ ] **58b. La política nueva en los 3 carriles**: en `carrera_vivo` y el benchmark, el RL recibe `d`, `psi` y válido **de su propia cámara** (`VisionCamara`), sin el truco del giroscopio; los baselines siguen igual — ✅ `run_demo.py --live` muestra el RL nuevo corriendo con su cámara junto a B-Human y NAOqi; la batería de selección (pasos 61–63) usa este mismo camino

## Fase M — Entrenamiento por población: 100 agentes
- [ ] **59. Base común `carrera_v01`** con los pesos iniciales y fricción aleatoria — ✅ Cruza los 5 m sin caer ni salirse en la batería; fila en la tabla de generaciones
- [ ] **60. Lanzador de barridos**: sortea pesos, rango de fricción, velocidad máxima, ruido de cámara y semilla por agente; los corre en cola en este PC (reanudable si se interrumpe), evalúa con la batería y guarda todo en `results/barridos/` — ✅ Prueba completa con 4 agentes
- [ ] **61. Ronda 1: 100 agentes** desde la base (~1M pasos c/u) → batería corta → 20 mejores — ✅ Tabla de los 100 con configuración y puntaje
- [ ] **62. Ronda 2: 20 agentes** (~5M pasos) → batería completa → 5 mejores — ✅ Tabla y análisis de qué pesos y rangos ganan
- [ ] **63. Ronda 3: 5 agentes** (~20M pasos) con domain randomization completa, cámara renderizada y escena de 3 carriles con vecinos → campeón — ✅ Campeón con 0 faltas en la batería y tiempo comparado con B-Human y NAOqi
- [ ] **64. Ciclo de generaciones**: lo aprendido define nuevos rangos y una nueva base — ✅ Cada generación documentada en la bitácora y en la tabla del README
- [ ] **65. (Opcional) Reducir el costo del barrido** si no alcanza el tiempo en un solo PC: menos pasos por ronda, menos agentes o GPU (la torre con RTX 5060 no está disponible por ahora) — ✅ Decisión documentada con mediciones

## Fase N — Portabilidad a PenaltyStack
- [ ] **66. Exportar la política** (pesos y normalización en JSON o `.npz` + versión del contrato) y módulo de inferencia compatible con Python 2.7 y 3 — ✅ Diferencia con SB3 < 1e-5; tiempo de inferencia medido en PC
- [ ] **67. Correr la política dentro del simulador de PenaltyStack**, junto a la caminata original de B-Human — ✅ Camina 5 m; comparación directa en el mismo simulador
- [ ] **68. Ejecutor a bordo**: visión en Python puro + política exportada, START (táctil frontal 0.25 s), ABORT (pecho 0.3 s), ciclo de 24 ms y paro por inclinación, desplegado con el mecanismo de PenaltyStack — ✅ Probado en seco y revisado por el autor de PenaltyStack

## Fase O — Robot real
- [ ] **69. Sesión real #1** (robot suspendido): Python y numpy a bordo; tiempo de inferencia + visión; respuesta de los servos; ruido de IMU y FSR; deriva de `AngleZ`; **μ de la duela** (plano inclinado); ALMotion vs LoLA — ✅ Datos en `data/real/sesion_01/` y decisiones documentadas
- [ ] **70. Precisión de la cámara en pista réplica** (`race_nao.py --dry-run` y `--medir`, 30 posiciones con cinta métrica) — ✅ σ real de `d` y `psi` comparado con el simulado; rango de ruido del paso 57 ajustado
- [ ] **71. Identificación de servos y ruidos** → valores en el simulador — ✅ Gráfica simulación vs real por articulación
- [ ] **72. Pruebas escalonadas de la política con visión** (suspendido → arnés → 1 m → 5 m, `vx_cmd` creciente) — ✅ Cada prueba registrada con video, log y resultado
- [ ] **73. Comparación real de los 3 carriles**: NAOqi (`moveToward` + visión), B-Human (framework en el NAO) y RL, en la misma pista réplica, 5 corridas c/u — ✅ Tabla de tiempo, salidas y caídas de las tres
- [ ] **74. Ciclo sim-to-real** (diferencia observada → ajuste → nueva generación) — ✅ Cada iteración documentada

## Fase P — Competencia y cierre
- [ ] **75. Colores definitivos de la pista** (cuando los avisen): `uv run python scripts/cambiar_colores.py --piso <color> --linea <color>` (guarda, regenera y verifica la visión), copiar `config/pista_robot.json` al robot, batería de la política final y, en el evento, calibración en la zona de calibraciones — ✅ Procedimiento ensayado de antemano en menos de 1 hora con un juego de colores distinto
- [ ] **76. Lista de chequeo del reglamento**: sin Wi-Fi ni comunicación externa, todo a bordo, activación por sensor en < 10 s, paro por el pecho, carga por Ethernet — ✅ Lista firmada por el equipo en el simulacro
- [ ] **77. Benchmark final de los 3 carriles** (simulación y robot real, mismo protocolo, 10 corridas) — ✅ Tabla final: el RL contra B-Human y NAOqi
- [ ] **78. Selección, congelamiento e integración en PenaltyStack** (la más rápida con 0 faltas; si el RL no supera a B-Human de forma confiable, se compite con B-Human + visión) — ✅ Política `carrera_final`, tag de Git y PR al repo final
- [ ] **79. Simulacro completo de competencia** — ✅ Corrida completa sin cambios de último minuto
- [ ] **80. Documentación final para el paper** — ✅ Una persona externa entiende el proceso completo leyendo el repo
