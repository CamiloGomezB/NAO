# Plan de trabajo — Caminata RL para NAO V6

Stack: **MuJoCo + Stable-Baselines3 (PPO)**, Windows nativo, entrenamiento en CPU.
Regla: cada paso termina con una **confirmación**, una **entrada en la bitácora** ([`docs/bitacora.md`](docs/bitacora.md)) y un **commit**.

> **Paso actual: 62** (ronda 2: los 20 mejores con 5M pasos, corriendo desde el 2026-10-11 23:41, fin ~10:00; pendientes de revisión del usuario: 49, 56, 58 y 58b; silbato pospuesto en 68b) · Objetivo vigente: **caminata por RL para la Carrera Individual de la Copa NAO CCM MX 2026 (3 de noviembre de 2026)**,
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

**Orden de trabajo:** los pasos se hacen **en orden numérico**.
- Si un paso no se puede hacer en su turno (por ejemplo, porque falta una herramienta), se marca `[!]` con el motivo y
  se avisa al usuario. No se salta en silencio.
- Hasta el 2026-10-10 hubo una "ruta crítica" que permitía saltar pasos: se eliminó por E41.
- **Noche del 2026-10-11:** el usuario autorizó trabajar solo toda la noche para dejar entrenando el RL. Orden de esa
  noche:
  1. 42, 43, 44, 45 y 49;
  2. el entorno de carrera, pasos 53–58;
  3. el entrenamiento base, paso 59;
  4. mientras entrena, 48b, 51 y 52;
  5. el 50 necesita Visual Studio 2022 Build Tools, que no están instalados.

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
- [x] **42. Políticas compartidas en el repo** (`policies/carrera_vNN/`: modelo, normalización, config, métricas y README de la generación) — ✅ Desde un clon limpio se evalúa la misma política sin entrenar y se puede continuar desde ella
  - Hecho (2026-10-11): `scripts/guardar_politica.py` copia el modelo, la normalización, la config, los metadatos y un README a `policies/<nombre>/`; `src.train --continuar <carpeta o .zip>` (registra `continua_de` en los metadatos); `env_id` configurable en `src.train` y `env_factory`. Probado el ciclo completo: guardar → evaluar → continuar.
- [x] **43. Rendimiento de entrenamiento en este PC** (laptop Ryzen 7 5800H, el único equipo de entrenamiento): pasos/s con el modelo V6 y la fricción aleatoria — ✅ Pasos/s medidos y costo real del barrido de 100 agentes recalculado (sección 11.3 del diseño)
  - Hecho (2026-10-11): 16 entornos con el V6 y fricción aleatoria → **3,725 pasos/s** de entrenamiento (45 min cada 10M pasos). La simulación pura da 7,465 pasos/s y usa 5.0 GB de RAM. Con el ciclo de 24 ms del entorno de carrera se estiman ~3,100–3,300 pasos/s, es decir ~65–70M pasos en 6 h. Barrido de 100 agentes (100×1M + 20×5M + 5×20M = 300M pasos): ~22–27 h en este PC.

## Fase J — Modelo V6, fricción y pista
- [x] **44. Validar la física V6 contra el RSI3** (masa, masa e inercia por cuerpo, ejes y rangos) + actualizar `SOURCE.md` y la sección 10 del README — ✅ Verificación automática en OK; la documentación ya no habla del V5
  - Hecho (2026-10-11): `scripts/check_modelo_v6.py` lee el RSI3 por separado y lo compara con el modelo compilado. 25 cuerpos, 24 articulaciones y 23 servos **idénticos** (diferencias de 1e-15); masa de **5.35975 kg**, la misma del URDF oficial de Aldebaran. `assets/nao/SOURCE.md` reescrito para el V6 (el V5 queda como histórico), sección 10 del README y tabla de scripts actualizadas. Las mediciones del paso 46 quedan validadas.
- [x] **45. Diagnóstico de caídas y choque entre piernas**: (a) caídas de la demo interactiva al pausar y reanudar, reproducidas sin visor; (b) distancia mínima entre piernas y choques, con acciones aleatorias y en un entrenamiento corto desde cero — ✅ Informe en `results/` con % de caídas al reanudar, motivo y articulación
  - Hecho (2026-10-11): `scripts/diag_caidas.py` → `results/diagnostico_45.md`. En el V6, la pausa de la demo (congelar la última acción en doble apoyo) tumba al robot en **45 % de las pausas** (28/62); la mayoría **durante la pausa** (19) y no al reanudar (9); motivo: inclinación; articulación con mayor error: **RAnklePitch** (20/28). Detener el reloj de marcha no ayuda (29/60). Pausar en la pose de pie (acción 0) baja a 5.6 % (8/142). Piernas: la política del sprint no las choca; una desde cero en el V6 las toca en 0.16 % de los pasos (1.2 mm); al azar 7.7 % (escalas del sprint) y 1.06 % (contrato v1, solo al caer). Registro E42.
- [x] **46. Quitar los valores del modelo aproximado**: pose de pie, escalas de acción (HipRoll asimétrico, HipYawPitch), altura objetivo y de caída, período de marcha y ciclo de 24 ms — ✅ `inspect_actions` muestra que ninguna acción extrema cruza las piernas; `check_standing` en OK
  - Hecho (2026-10-10), sin tocar `src/envs/nao_walk_env.py` (lo usa la política del sprint en la demo): valores del V6 en `src/race/contract.py` y `src/race/valores_v6.py`.
    - pose `home` = altura de cadera de B-Human (232 vs 230 mm);
    - **presupuesto lateral combinado** (0.09 rad): las dos piernas hacia adentro a la vez se escalan, con 0 cruces en 20,000 acciones (antes 23.9 %);
    - altura objetivo 0.316 m, altura de caída 0.24 m, marcha de 0.5 s y ciclo de 24 ms.
  - El criterio "`inspect_actions`" se cumple con `scripts/check_valores_v6.py`, porque `inspect_actions` prueba el entorno del sprint. `check_valores_v6`, `check_contract` y `check_standing` dan OK.
- [x] **47. Fricción explícita y configurable** en el piso y en los pies (MuJoCo usa el mayor), aleatoria por episodio en [0.4, 1.2] con asimetría entre pies; probar `condim` 3 contra 4 — ✅ Prueba automática de que el μ pedido es el μ efectivo; decisión de `condim` documentada
  - Hecho (2026-10-10): `NaoWalkEnv` sortea μ en [0.4, 1.2] con asimetría ≤ 0.1 por defecto (`friction` fijo solo para evaluar); `src.train` rechaza fricción fija salvo `--friccion-fija`; `src.evaluate --mu`; `configs/ppo_brazos_friccion.yaml`; `scripts/check_friction.py` en OK. `condim` se mantiene en 3 (comparación con 4 no concluyente; se repite en el paso 51).
- [x] **48. Colores de la pista en un solo archivo** (`config/pista.yaml`: piso, veta, línea, salida y meta), usado por la escena, la demo, el benchmark, la verificación de la visión y el robot (`config/pista_robot.json`); `scripts/cambiar_colores.py` cambia, regenera y verifica — ✅ Cambiar colores = un comando con verificación automática
  - Hecho (2026-10-10): visión con modo **brillo** o **color** según los colores; matriz de 63 combinaciones con 57 OK (`results/camara/matriz_colores.md`); el robot toma la polaridad y el modo de `pista_robot.json`.
- [x] **48b. Escena de 3 carriles con física compartida** para medir choques entre robots (hoy cada robot de `carrera_vivo` va en su propia física) — ✅ La escena detecta contactos entre robots de carriles vecinos
  - Hecho (2026-10-11), con una simplificación: cada robot sigue en su propia física, pero sus poses se copian a la escena de 3 carriles (`escena_tres`) y MuJoCo detecta ahí los contactos entre robots (`demo/caminatas/choques.py`). La detección es exacta, aunque tras el choque los robots no se empujan; para la selección basta, porque un contacto descarta al agente. `scripts/check_choques_robots.py`: OK (34.8 cm entre robots de pie; el choque aparece al correr el RL 35 cm, después de salirse del carril a 25.9 cm). `carrera_vivo` marca "CHOQUE CON OTRO ROBOT".
- [~] **49. Revalidar contactos, de pie y barrido articular con el V6** — ✅ `check_contacts`, `check_standing` y `joint_sweep` en OK + revisión visual del usuario
  - Parte automática hecha (2026-10-11), **falta la revisión visual del usuario**. `check_contacts`: OK (penetración en reposo 0.39 mm, máxima 4.79 mm al soltarlo desde 3 cm, 4 contactos por pie). `check_standing`: OK (10 s de pie, 20/20 con ruido, resiste empujones de 15–20 N × 0.1 s). `joint_sweep`: OK, las 23 articulaciones recorren su rango y los topes son choques reales (hombro contra cadera, rodilla contra cadera, pies entre sí). Video: `videos/joint_sweep.mp4`.

## Fase K — Benchmark de los tres carriles (RL, B-Human, NAOqi)
- [!] **50. WalkingEngine original de B-Human en el simulador de PenaltyStack** a 0.15, 0.25 y 0.30 m/s, para validar la réplica tipo B-Human. Requiere compilar su runtime con VS 2022 Build Tools — ✅ `results/baseline_penaltystack.md`; diferencia con la réplica documentada
  - Bloqueado (2026-10-11): este PC no tiene CMake ni Visual Studio 2022 Build Tools (`which cmake cl` → no encontrados; no existe `Program Files*/Microsoft Visual Studio`). Instalarlos es un cambio en el sistema que tiene que hacer o autorizar el usuario. Mientras tanto, la referencia de B-Human es la réplica tipo B-Human del benchmark (16.2–16.9 s con visión).
- [x] **51. Benchmark de 3 carriles completo y regenerado** con la batería común: 5 fricciones × colocaciones fijas por semilla × con y sin visión. Incluye la escena compartida para choques — ✅ `results/benchmark/` con la tabla completa (150+ corridas) y fila de cada caminata en la tabla del README
  - Hecho (2026-10-11): `demo/caminatas/benchmark.py --procesos 2` → `results/benchmark/` con **150 corridas** (3 caminatas × con/sin visión × μ 0.4–1.2 × 5 semillas). Con visión, todas llegan sin faltas: B-Human 16.2–18.3 s, NAOqi 45.3–49.9 s y RL del sprint 24.2–24.3 s. Sin visión: B-Human 14/25, NAOqi 14/25 y RL 15/25 metas, con el resto salidas de carril. Choques entre robots: solo pueden pasar después de salirse del carril (paso 48b), así que no se cuentan aparte. Filas actualizadas en el README.
- [x] **52. Métricas de carrera unificadas** en `evaluate.py` y el benchmark (tiempo en 5 m, velocidad, desvío y rumbo máximos, salidas, caídas, choques, consistencia; mismo JSON) — ✅ Las dos herramientas dan los mismos números para la misma corrida
  - Hecho (2026-10-11) para la política de carrera: `scripts/eval_carrera.py` y `demo/caminatas/benchmark.py --rl-carrera` usan la misma función (`eval_carrera.correr`), con los mismos campos y el mismo `resumen`. Comprobado con el checkpoint de 5M de `carrera_v01` (μ 1.0 y 0.4, semilla 1000): las 9 métricas de cada corrida son **idénticas**. `src/evaluate.py` sigue siendo el evaluador de `NaoWalk-v0` (política del sprint), que el benchmark mide con su propio código desde el paso 40.

## Fase L — Entorno de carrera `NaoRace` con cámara (contrato v1)
- [x] **53. Observación de 54 valores** (IMU, rumbo, `d`, `psi`, válido, articulaciones, acción anterior, carga de los pies, reloj, `vx_cmd`) — ✅ `inspect_obs` en OK y coincide con el contrato del paso 41
  - Hecho (2026-10-11): `src/envs/nao_race_env.py` (`NaoRace-v0`). `scripts/check_race_env.py` (reemplaza a `inspect_obs` para este entorno) arma la observación con `contract.armar_observacion` a partir de un frame con formato PenaltyStack sacado de la simulación: **diferencia 0.0** en 200 pasos; `d`, `psi` y válido en los índices 7–9.
- [x] **54. Acción de 13 ángulos cada 24 ms** + comando `vx_cmd` — ✅ `inspect_actions` en OK
  - Hecho (2026-10-11): los 13 servos reciben exactamente `contract.accion_a_objetivos` (con el presupuesto lateral del paso 46), una acción cada 24 ms (12 × 2 ms); lo demás queda en home; RHipYawPitch sigue a la izquierda (restricción blanda, 2e-3 rad). `vx_cmd` sorteado en [0.15, 0.5] m/s por episodio, con un cambio a mitad del episodio en el 30 %. Prueba: `check_race_env.py`, sección 3.
- [!] **55. Recompensa con las faltas del reglamento** (sección 6.4 del diseño): salida de carril (−200), choque con otro robot (−400) y caída (−100) como terminales, barrera de margen a menos de 10 cm de la línea, centrado (`d`²) y rumbo (`psi`) del carril, bono de meta. **Pesos iniciales y rangos del barrido en un solo archivo** (`configs/carrera/pesos.yaml`), del que leen el entorno y el lanzador de los 100 agentes — ✅ `inspect_reward` ordena bien los comportamientos: salirse del carril siempre es peor que ir lento, y el YAML coincide con la tabla del diseño
  - Implementado (2026-10-11): términos y faltas probados en `check_race_env.py`, sección 4; `configs/carrera/pesos.yaml` con `pesos` (= tabla 6.4) y `rangos`, leído por el entorno. **El orden de comportamientos NO se cumple del todo** (`scripts/check_recompensa_carrera.py`, E47): salirse a 4.8–4.9 m, justo antes de la meta, da más retorno (579–597) que caminar lento 30 s (547). Hace falta `salida_carril` < −271. Con descuento 0.99, salirse después de 4 s ya vale más que ir lento. Las políticas de la noche no se salen gracias al filtro duro de la selección, pero la recompensa sola no lo garantiza.
- [x] **55b. Castigo de salida de carril suficiente**: `salida_carril` ≤ −300 en los pesos iniciales y el rango del barrido en [−400, −300] (o terminar el episodio poco después de la meta), en una generación propia — ✅ `check_recompensa_carrera.py` en OK
  - Hecho (2026-10-11, 14:35): `salida_carril` −200 → **−300** y rango del barrido [−400, −300]; `choque_robot` −600 (2 × salida). `scripts/check_recompensa_carrera.py` (ahora con `--modelo`) da **OK con `policies/carrera_v03`**: lento 1264 < cualquier salida antes de la meta. **Con `carrera_v01` sigue en FALLA** (haría falta < −452), porque el umbral depende de cuánto acumula cada política yendo lenta (368 en v01 y 1264 en v03). Ningún peso fijo lo garantiza para toda política: la garantía es el filtro duro de la selección (E53). El entrenamiento con el peso nuevo ocurre en la ronda 1 (paso 61).
- [~] **56. Episodio de carrera** (desde quieto, error de colocación, 0.5 s de medición de la visión, carril, meta, 30 s, fricción sorteada) — ✅ `check_env` en OK + video revisado por el usuario
  - En curso (2026-10-11): desde quieto con colocación normal σ 2 cm / 2° recortada a ±10 cm / ±8°, 0.5 s de pie dentro de `reset` con la cámara midiendo (198/200 episodios con medición al arrancar), carril de 70 cm, meta en 5 m, 30 s (1250 pasos), fricción por pie en [0.35, 1.25]. `check_env` en OK. **Falta el video revisado por el usuario.**
- [x] **57. Cámara simulada**: `d` y `psi` reales + ruido gaussiano, retardo, pérdidas y mediciones malas a 10 Hz, con los σ de nao_linea y su rango hasta 3×, **con las mismas convenciones que la visión real** (sección 6.7 del diseño) — ✅ Prueba automática de la estadística del ruido, reproducible con semilla; en las mismas trayectorias, la señal simulada y la de `VisionCamara` (cámara renderizada) tienen el mismo signo, frecuencia y error dentro del rango
  - Hecho (2026-10-11): cámara simulada a 10 Hz con σ_d 1–5 cm, σ_psi 1–4°, retardo 50–250 ms, pérdidas 0–30 %, mediciones malas 0–8 % (±15 cm) y apagones de 0.5–2 s; reproducible con semilla. `check_race_env.py` mide la estadística (σ medida 3.00 cm frente a 3.00 sorteada; 2.64° frente a 2.50°). `scripts/check_camara_sim.py` compara con la cámara renderizada en 25 poses de la pista: mismo signo, error rms 1.05 cm / 0.72° (dentro del rango simulado), 10 Hz las dos.
- [~] **58. Pérdida de rectitud simulada** (asimetrías, perturbaciones, deriva de la IMU, tramos sin visión) + prueba de rectitud de 100 episodios — ✅ Deriva sin visión y desvío con visión registrados
  - En curso (2026-10-11): implementado en `NaoRace-v0` (ganancia de servos por pierna ±15 %, calibración ±1.5° por articulación, centro de masa ±1 cm, suelo ±1°, empujones de hasta 6 N y 0.4 N·m cada 2–6 s, deriva de la IMU, ruido de sensores, apagones de visión). La prueba de rectitud de 100 episodios (`scripts/eval_carrera.py --perturbaciones`) espera a tener una política que camine. **Primera corrida (02:10, `policies/carrera_v01`, `vx_cmd` 0.40, 100 episodios por condición, `results/carrera/carrera_v01/rectitud_58/`):** con visión, 100/100 metas sin faltas, 13.2 ± 0.7 s, desvío máximo medio de 7.8–8.6 cm. Sin visión, 0/100: casi no avanza (0.03–0.05 m/s), con 45 caídas y 47 salidas, así que todavía no hay deriva de marcha que medir (E45). Se repite con `carrera_v02`.
- [~] **58b. La política nueva en los 3 carriles**: en `carrera_vivo` y el benchmark, el RL recibe `d`, `psi` y válido **de su propia cámara** (`VisionCamara`), sin el truco del giroscopio; los baselines siguen igual — ✅ `run_demo.py --live` muestra el RL nuevo corriendo con su cámara junto a B-Human y NAOqi; la batería de selección (pasos 61–63) usa este mismo camino
  - En curso (2026-10-11): `CorredorRLCarrera` en `demo/caminatas/carrera_vivo.py` (y `--rl <modelo>`): la política de carrera recibe `d`, `psi` y válido CRUDOS de su propia `VisionCamara`, sin el truco del giroscopio. Probado con captura sin pantalla. `scripts/eval_carrera.py` usa la colocación, la meta y las métricas del benchmark. **Lazo cerrado con la cámara renderizada (02:15, `policies/carrera_v01`):** 18/18 metas sin faltas (μ 0.4/0.8/1.2 × 3 semillas × `vx_cmd` 0.40 y 0.5), en 12.7 s y 10.3–10.5 s, con desvío máximo de 1.4–8.8 cm (`results/carrera/carrera_v01/camara_renderizada_58b.json`). **Falta que el usuario lo vea** en `uv run python demo/run_demo.py --live`.

- [x] **58c. Rumbo objetivo de la IMU alineado al carril al arrancar** (E50): tras los 0.5 s de pie, rumbo objetivo = rumbo de la IMU − `psi` medio de la cámara (o el de la IMU si no hubo medición). Función en `src/race/contract.py`, usada igual en `NaoRace-v0`, la demo y el robot; generación nueva con colocación más amplia (p. ej. ±15 cm, ±25°) — ✅ La batería de salidas malas (`salida_mala.json`) llega en todas las celdas con visión
  - En curso (2026-10-11, 12:00–): `contract.rumbo_objetivo_inicial` (Python 2.7) y `NaoRace-v0(rumbo_objetivo="carril")`, nuevo default; v01 y v02 quedan fijos en `arranque` en sus configs. El corredor de la demo hace lo mismo con la cámara renderizada. Pruebas: `check_contract.py` y `check_race_env.py` (sección 7) en OK. Batería nueva `scripts/eval_salida_mala.py` (70 salidas: y 0/±10/±15 cm × rumbo 0/±8/±15/±25°). Con `v02` sin reentrenar: con visión pasa de 16/70 a **69/70** (1 caída en −15 cm / −25°). **Criterio cumplido con `carrera_v03` (5M):** 70/70 salidas malas con visión, y 30/30 con la cámara renderizada real (y 0/±15 cm × rumbo 0/±15/±25°, μ 0.4 y 1.2), en 12.3–12.9 s.

## Fase M — Entrenamiento por población: 100 agentes
- [x] **59. Base común `carrera_v01`** con los pesos iniciales y fricción aleatoria — ✅ Cruza los 5 m sin caer ni salirse en la batería; fila en la tabla de generaciones
  - En curso (2026-10-11): `configs/carrera_v01.yaml`, lanzado a las 00:26. **Se detuvo en 15.3M pasos (02:00)** para seguir con `carrera_v02`. **Con visión cumple:** el checkpoint de 15M llega 10/10 sin faltas en 10.5–10.6 s (B-Human: 16.2–18.3 s), con desvío máximo de 3.4–5.6 cm, y 20/20 con perturbaciones. **Sin visión no cumple:** se cae o se sale (E45). Guardado en `policies/carrera_v01/` (15M). Resultados en `results/carrera/carrera_v01/`. Se marca hecho con la batería con visión, que es la condición de carrera. Sin visión todas las caminatas se salen (B-Human 11/25), y la caída sin visión se resolvió en el 59b.
- [x] **59b. `carrera_v02`: más pérdida de visión** (15 % de episodios sin cámara; apagones en el 60 % de los episodios, de 1–8 s), continuando desde `carrera_v01` a 15M — ✅ Sin visión no se cae, y con visión sigue cumpliendo la batería de la 59
  - En curso (2026-10-11): `configs/carrera_v02.yaml`, 40M pasos lanzados a las 02:05. **Hipótesis confirmada:** el checkpoint de 15M (elegido, `policies/carrera_v02/`) llega sin visión en 89/100 con perturbaciones y **0 caídas** (`v01`: 0/100, 45 caídas); con visión sigue en 100/100 y 13.0 s. Con la cámara renderizada: 36/36 (con y sin cámara). Costo: desvío máximo de hasta ~18 cm con cámara (`v01`: ~9). Entrenamiento terminado (05:53, 40M). Los checkpoints de 25M, 30M, 35M y 40M **no** pasan la batería con visión y perturbaciones (E48), así que se queda el de 15M. Criterio cumplido con el de 15M.
- [!] **59c. `carrera_v03`: salidas mucho más torcidas en el entrenamiento** (colocación σ 6 cm / 10°, máx. ±15 cm / ±25°), continuando desde `carrera_v02` con el rumbo objetivo del 58c — ✅ Batería de salidas malas con visión en todas las celdas, también con perturbaciones, y sin perder la batería grande de la 59b (100/100 con visión)
  - Hecho en parte (2026-10-11, 12:40–14:18, 20M pasos): el elegido es el checkpoint de 5M (`policies/carrera_v03/`). Con visión: 70/70 salidas malas sin perturbaciones; **batería grande 100/100 en 12.8 s** (mejor que `v02`: 13.0 s), desvío de 7.4 cm. **Criterio no cumplido del todo:** con perturbaciones, 135/140 salidas malas; las 5 caídas son el mismo caso (−25°, μ 0.4, semilla 1001, a ~1.1 s) en las 5 posiciones laterales. `v02` + 58c tenía 12 caídas. E52.
- [x] **60. Lanzador de barridos**: sortea pesos, rango de fricción, velocidad máxima, ruido de cámara y semilla por agente; los corre en cola en este PC (reanudable si se interrumpe), evalúa con la batería y guarda todo en `results/barridos/` — ✅ Prueba completa con 4 agentes
  - Hecho (2026-10-11): `scripts/barrido.py`. Cada agente sortea pesos (dentro de `rangos` de `configs/carrera/pesos.yaml`, con choque_robot = 2 × salida), rango de fricción, `vx_max`, ruido máximo de la cámara y semilla. Entrena en cola con `src.train --continuar <base>` (por defecto `policies/carrera_v01`), evalúa con la batería de `eval_carrera` (visión + perturbaciones, 5 fricciones) y puntúa según la sección 11.4. Es reanudable. **Prueba con 4 agentes** (20k pasos, `results/barridos/prueba_paso60/`): 4/4 completos, ~50 s cada uno; la segunda corrida se los salta a los 4.
- [x] **61. Ronda 1: 100 agentes** desde la base (~1M pasos c/u) → batería corta → 20 mejores — ✅ Tabla de los 100 con configuración y puntaje
  - Hecho (2026-10-11, 14:36–23:40, 0 errores): `results/barridos/ronda1/tabla.md` (los 100 con configuración y puntaje) y `analisis.md`. **70/100 pasan**, **49 superan a la base** (12.41 s), el mejor 11.43 s (`agente_045`). Ningún peso domina (máx. \|ρ\| = 0.28, `vx_max`); los descartes son sobre todo caídas en las salidas torcidas. Los 20 mejores están en `mejores.json`.
  - En curso (lanzada el 2026-10-11 a las 14:36): `scripts/barrido.py --nombre ronda1 --agentes 100 --pasos 1000000 --eval-semillas 2`, base `policies/carrera_v03` con su config. ~6 min por agente (5.5 de entrenamiento a ~3,000 pasos/s): fin estimado hacia las 00:35. Batería corta: con visión y perturbaciones, `vx_cmd` 0.45, μ 0.4–1.2 × 2 semillas + 4 salidas torcidas (±10 cm / ±15°, 0 / ±25°, μ 0.6). Referencia: la base pasa con puntaje 12.41 s (`results/barridos/ronda1/base_carrera_v03.json`). Resultados en `results/barridos/ronda1/`.
- [~] **62. Ronda 2: 20 agentes** (~5M pasos) → batería completa → 5 mejores — ✅ Tabla y análisis de qué pesos y rangos ganan
  - Cambio el 2026-10-12 a las 00:10 (E54): se evalúa **cada checkpoint** (1M–5M) de cada agente y se elige el mejor, porque el modelo final del primero empeoró (6 caídas) y su checkpoint de 4M pasa sin faltas (12.35 s). Relanzada a las 00:12; fin estimado ~11:30 (~33 min por agente).
  - En curso (lanzada el 2026-10-11 a las 23:41, encadenada a la ronda 1): `scripts/ronda_siguiente.py --anterior ronda1 --nombre ronda2 --pasos 5000000`. Cada uno de los 20 sigue con su config desde su modelo; batería completa de 44 corridas (5 μ × 4 semillas + 12 salidas torcidas × μ 0.4/1.0, perturbaciones, `vx_cmd` 0.45). Referencia: la base con la misma batería pasa con **12.54 s** (`results/barridos/ronda2/base_carrera_v03.json`). ~30 min por agente: fin estimado ~10:00 del 2026-10-12.
- [ ] **63. Ronda 3: 5 agentes** (~20M pasos) con domain randomization completa, cámara renderizada y escena de 3 carriles con vecinos → campeón — ✅ Campeón con 0 faltas en la batería y tiempo comparado con B-Human y NAOqi
- [ ] **64. Ciclo de generaciones**: lo aprendido define nuevos rangos y una nueva base — ✅ Cada generación documentada en la bitácora y en la tabla del README
- [ ] **65. (Opcional) Reducir el costo del barrido** si no alcanza el tiempo en un solo PC: menos pasos por ronda, menos agentes o GPU (la torre con RTX 5060 no está disponible por ahora) — ✅ Decisión documentada con mediciones

## Fase N — Portabilidad a PenaltyStack
- [ ] **66. Exportar la política** (pesos y normalización en JSON o `.npz` + versión del contrato) y módulo de inferencia compatible con Python 2.7 y 3 — ✅ Diferencia con SB3 < 1e-5; tiempo de inferencia medido en PC
- [ ] **67. Correr la política dentro del simulador de PenaltyStack**, junto a la caminata original de B-Human — ✅ Camina 5 m; comparación directa en el mismo simulador
- [ ] **68. Ejecutor a bordo**: visión en Python puro + política exportada, START (táctil frontal 0.25 s), ABORT (pecho 0.3 s), ciclo de 24 ms y paro por inclinación, desplegado con el mecanismo de PenaltyStack — ✅ Probado en seco y revisado por el autor de PenaltyStack

- [ ] **68b. Silbato (pospuesto)**: decidir con Luis Mario si el NAO arranca solo al escuchar el silbato o se queda el arranque manual por el táctil de la cabeza (lo actual, reglamentario). PenaltyStack (`9c08a41`) solo trae la estructura de datos `Whistle` de B-Human, sin detector. Pospuesto el 2026-10-11 hasta hablar con él — ✅ Decisión documentada; si es automático, detector a bordo con táctil de respaldo y prueba con ruido de público

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
