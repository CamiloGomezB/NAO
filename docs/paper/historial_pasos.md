# Historial paso a paso del proyecto (pasos 1–40, más 47 y 48)

Reconstrucción de **qué se hizo en cada paso, cómo se verificó y qué falló**, para la sección de metodología
del paper.
- Los problemas se citan por su ID del [registro de errores](registro_errores.md), por ejemplo (E07).
- Los detalles de cada sesión de trabajo están en la [bitácora](../bitacora.md).
- El plan con los criterios de aceptación está en [`PLAN.md`](../../PLAN.md).

**Fuentes:**
- el historial de Git (commit y fecha en cada paso);
- `PLAN.md`;
- el README;
- `assets/nao/SOURCE.md`;
- `results/`;
- la bitácora;
- las notas de las sesiones del sprint inicial.

**Método de trabajo en todos los pasos:**
- un paso a la vez, con un **criterio de aceptación** escrito de antemano;
- verificación automática cuando se puede, con un script que termina en `RESULTADO: OK` o `FALLA`;
- revisión visual del usuario cuando hace falta ver algo (visor, video, marcha);
- **un commit por paso**.

---

## Estado de los pasos 1–40 (revisado el 2026-10-10)

| Pasos | Estado |
|---|---|
| 1–33 | ✅ Completos |
| 34–35 | ✅ Hechos (modelo V6 generado). Su **validación** se movió al paso 44 |
| 36, 37, 38 | Reubicados en la replanificación del 2026-10-10: 36 → 44–49; 37 → entrenamiento por población (Fase M); 38 → 44 y 80 |
| 39–40 | ✅ Completos |
| 47, 48 (adelantados) | ✅ Completos |

---

## Etapa 1 — Sprint inicial: caminata en simulación (29–30 de septiembre de 2026)

**Objetivo:** que un NAO aprenda **desde cero** a caminar en simulación, con aprendizaje por refuerzo, en un
sprint de 48 horas.

**Stack elegido:** MuJoCo 3.14 + Stable-Baselines3 2.9 (PPO), Python 3.12 con `uv`, Windows nativo, en CPU
(laptop Ryzen 7 5800H).

**Por qué este stack:**
- era el recomendado;
- se instala igual en cualquier PC;
- la alternativa en GPU (MJX/JAX) necesitaba WSL/Linux y complicaba la reproducibilidad.

### Fase A — Preparación (pasos 1–4)

| Paso | Qué se hizo | Verificación | Commit |
|---|---|---|---|
| 1 | Estructura de carpetas y `.gitignore` | Carpetas visibles en VSCode | `cd92f6d` |
| 2 | Entorno virtual con `uv` y versiones fijadas en `pyproject.toml` / `uv.lock` | `uv sync` sin errores | `7338885` |
| 3 | Instalación de MuJoCo y visor con un modelo de prueba | Se abre la ventana 3D | `007ba4e` |
| 4 | Repositorio en GitHub | Visible en github.com/CamiloGomezB/NAO | — |

### Fase B — Modelo del NAO (pasos 5–10)

| Paso | Qué se hizo | Verificación | Commit |
|---|---|---|---|
| 5 | Elección del modelo base: `nao_v5` de *one_policy_to_run_them_all* (MIT, CoRL 2024), con datos de `ros-naoqi/nao_robot` (BSD-3). Se revisaron las licencias (E02) | Fuente y licencia acordadas | `25c1220` |
| 6 | MJCF "limpio": primitivas en lugar de mallas (E02), sin dedos, HipYawPitch acoplado como en el robot real (un solo motor), **ejes corregidos a la convención NAOqi** (E01), servos de posición PD | Lista de articulaciones; masa 5.305 kg | `6f55cb9` |
| 7 | Visor con el robot suspendido | Parece un NAO, con las partes bien ubicadas | `6024924` |
| 8 | Contacto pie-suelo (`scripts/check_contacts.py`): penetración, rebote y deslizamiento | Se apoya sin hundirse ni rebotar | `3535ee5` |
| 9 | De pie con el controlador PD (`scripts/check_standing.py`); reinicio robusto del visor (E03) | Se mantiene de pie ~10 s | `5ad65cd` |
| 10 | Barrido de cada articulación con video (`scripts/joint_sweep.py`); **autocolisiones** (E04); prueba en el suelo de rangos seguros (E05) | Direcciones y rangos correctos | `6b0c7d9` |

### Fase C — Entorno de RL (pasos 11–17)

| Paso | Qué se hizo | Verificación | Commit |
|---|---|---|---|
| 11 | Esqueleto `NaoWalkEnv` (Gymnasium) | `check_env()` pasa | `af7494a` |
| 12 | Observación de 43 valores: gravedad proyectada, giroscopio, velocidad lineal del torso, ángulos y velocidades articulares, acción anterior, contacto de los pies y reloj de marcha | Valores con sentido, sin NaN (`inspect_obs.py`) | `0e2442b` |
| 13 | Acción: desviaciones alrededor de la pose de pie, con rangos limitados y HipYawPitch fija (E05) | Acción 0 = de pie; las aleatorias no explotan | `0e2442b` |
| 14 | Caída: torso < 0.22 m, inclinación > 40° o una parte que no sea un pie toca el suelo | El episodio termina al caer, sin falsos positivos | `fb7d69e` |
| 15 | Recompensa por términos (velocidad, patrón de marcha, vivo, inclinación, altura, velocidad lateral, giro, cambio de acción, torque, caída) | Tabla de términos coherente (`inspect_reward.py`) | `5572edb` |
| 16 | Render de video sin pantalla | `.mp4` revisado por el usuario | `65a2b08` |
| 17 | Fábrica de entornos paralelos y benchmark (`benchmark_envs.py`); hilos de PyTorch (E06) | Pasos/s con 1, 8 y 12 entornos | `fa5d27b` |

### Fase D — Primer entrenamiento (pasos 18–21)

| Paso | Qué se hizo | Verificación | Commit |
|---|---|---|---|
| 18 | `src/train.py` + `configs/ppo.yaml`: PPO con red de 256×256 (ELU), 16 entornos, `VecNormalize` y metadatos de cada run (commit, versiones, comando) | Un entrenamiento de 1 min guarda un checkpoint | `1ed51c3` |
| 19 | `src/evaluate.py`, separado del entrenamiento: semillas fijas y métricas | Carga el checkpoint e imprime métricas | `94fbeeb` |
| 20 | TensorBoard con cada término de la recompensa y el motivo de las caídas | Curvas visibles en el navegador | `1ed51c3` |
| 21 | Entrenamiento base `ppo_base_5M`: 5M pasos, **22 min**, ~3,800 pasos/s | Camina **0.151 m/s**, **0 % de caídas** en 20 episodios. Ver E07 y E09 | — |

### Fase E — Mejorar la marcha (pasos 22–26)

| Paso | Qué se hizo | Resultado | Commit |
|---|---|---|---|
| 22 | **V1 "natural"** (`ppo_natural.yaml`): 20 % de doble apoyo y 0.2 m/s, contra la "marcha de soldado" (E07). **V2 "brazos"** (`ppo_brazos.yaml`): V1 + hombros (E08) | — | `1bc49f6` |
| 23 | Entrenar V1 y V2, 5M pasos cada una | Curvas subiendo | `61b30e2` |
| 24 | El usuario revisa los videos | V1: "ya no son pasitos de soldado". V2: balancea los brazos | — |
| 25 | Comparación base vs V1 vs V2, 20 episodios con semillas 1000–1019 (`results/comparison.md`) | Ver la tabla de abajo | `61b30e2` |
| 26 | Elección de **V2 brazos** como política entregada (`checkpoints/best_model.zip`) | Justificada con métricas | `61b30e2` |

| Variante | Velocidad | Caídas | Doble apoyo | Altura de pie izq./der. | Deriva lateral |
|---|---|---|---|---|---|
| Base | 0.151 m/s | 0 % | 0.2 % | 4.1 / 2.5 cm | −13 cm |
| V1 natural | 0.199 m/s | 0 % | 20.1 % | 3.7 / 3.3 cm | −4 cm |
| **V2 brazos** | **0.200 m/s** | **0 %** | **20.0 %** | 3.7 / 4.1 cm | +5 cm |

**Hallazgo:** V2 aprendió sola a balancear los brazos en oposición a las piernas. La correlación entre el
hombro izquierdo y la cadera derecha es +0.85, sin ninguna recompensa que lo pida.

### Fase F — Evidencia (pasos 27–29)

| Paso | Qué se hizo | Commit |
|---|---|---|
| 27 | Evaluación de 20 episodios con semillas fijas → `results/metrics.json` (4.00 m en 20 s, 0 caídas) | `61b30e2` |
| 28 | Curvas de entrenamiento → `results/training_curves.png` | `61b30e2` |
| 29 | GIF y video de la demo → `media/demo.gif` (aprobado por el usuario) | `61b30e2` |

### Fase G — Reproducibilidad y entrega (pasos 30–32)

| Paso | Qué se hizo | Commit |
|---|---|---|
| 30 | README completo | `1ed1c15` |
| 31 | Prueba de instalación limpia siguiendo el README; problema con `pip` en Windows (E10) | `c388b50` |
| 32 | Push final y revisión en GitHub | `1209fdc` |
| — | **Demo interactiva**: parar y reanudar con la barra espaciadora (E11) | `468e562` |

**Reproducibilidad verificada:** dos entrenamientos con la misma config y semilla dieron curvas y políticas
idénticas, episodio por episodio.

---

## Etapa 2 — Correcciones tras la entrega (30 de septiembre – 7 de octubre)

**Retroalimentación recibida:**
1. el modelo debe ser el **NAO V6 completo**, no una aproximación del V5 (E12);
2. hay que explicar qué variables usa el RL, sin código ni matemáticas.

| Paso | Qué se hizo | Estado | Commit |
|---|---|---|---|
| 33 | `docs/variables_rl.md`: las variables del RL explicadas sin código | ✅ | `d9207ec` |
| 34–35 | `scripts/build_nao_v6.py`: genera `assets/nao/nao.xml` y las mallas `.obj` desde **`NaoV6H25.rsi3` de B-Human**, verificado por SHA-256. Conserva cuerpos, ejes, rangos, masas, inercias, colisiones, mallas y servos. Masa de 5.360 kg | ✅ Hecho; sin validar → paso 44 | `d9207ec` |
| 36–38 | Revalidar el modelo, reentrenar en el V6, actualizar documentos | Reubicados (ver arriba) | — |

---

## Etapa 3 — Carrera Individual, Copa NAO CCM MX 2026 (8 de octubre en adelante)

**Nuevo objetivo:** caminata por RL para la **Carrera Individual**: carril de 5 m × 70 cm sobre duela, 3 de
noviembre de 2026.
- Hay que ser lo más rápido y lo más recto posible, sin caer.
- **Salirse del carril anula la carrera, y chocar con otro robot descalifica.**

### Paso 39 — Replanificación (2026-10-08)
- **Insumos:**
  - el reglamento (sección 3.2);
  - el roadmap del director;
  - el análisis de **PenaltyStack**, el repo final del equipo (686 archivos, dos ramas).
- **Indicaciones del administrador:**
  - este repo hace solo el RL de la caminata;
  - la baseline es la caminata de B-Human de PenaltyStack;
  - de PenaltyStack se toma solo lo que sirve para caminar.
- **Qué se hizo:**
  - `PLAN.md` reestructurado;
  - `docs/plan_rl_carrera.md` (diseño del RL);
  - `docs/integracion_penaltystack.md` (condiciones del repo final: ciclo de 12 ms, sensores con 8 FSR en
    kg, Python 2.7 a bordo, arranque por la cabeza y paro por el pecho);
  - la bitácora;
  - `CLAUDE.md` (protocolo de documentación);
  - copia del contrato de articulaciones.
- **Mediciones:**
  - separación de las piernas en el V6 (E16);
  - la política de septiembre en el V6: 0 caídas en 3 episodios.
- **Problemas:** E13, E14, E15, E16, E17, E18.
- **Commit:** `4ca136d`.

### Replanificación con cámara y tres carriles (2026-10-10, commit `dd631e4`)
- **Nueva revisión:** [danielpaya/nao_linea](https://github.com/danielpaya/nao_linea), de Daniel, con la
  visión de carril.
- **Decisiones del equipo:**
  - **tres carriles de comparación:** baseline 1 NAOqi, baseline 2 B-Human, y el RL;
  - fricción variable;
  - pesos importantes para las faltas del reglamento;
  - colores de la pista fáciles de cambiar;
  - ~100 agentes de RL;
  - un solo PC;
  - todo en `main`.
- **Diseño resultante:**
  - contrato v1 con **54 observaciones**, que suma `d`, `psi` y válido de la cámara;
  - faltas en dos capas: recompensa terminal y filtro duro en la selección;
  - entrenamiento por población (100 → 20 → 5 → 1).
- Plan renumerado: pasos 40–80.

### Paso 40 — Integrar nao_linea: pista, cámara, visión y 3 carriles (2026-10-10)
1. **Integración** (`b9469ca`):
   - código: `carril/` (visión), `demo/` (pista, demo y caminatas tipo NAOqi y tipo B-Human), `robot/` (kit
     para el NAO real);
   - resultados;
   - sin los archivos indebidos (E20).
2. **Verificación sin PyTorch.** PyTorch estaba bloqueado (E21).
   - Nuevo `scripts/check_vision.py`: 50 posiciones conocidas y **100 % de mediciones válidas**. Error medio de
     **0.19 cm / 0.03°** sin error de pose, y de **1.27 cm / 0.86°** con 1.5° de error de pose.
   - Las caminatas de los baselines llegan a la meta.
3. **Con PyTorch** (`cf06d3e`):
   - la demo RL + cámara: solo RL se sale a los 0.54 m; RL + visión llega en 24.2 s;
   - el benchmark corto da **resultados idénticos a nao_linea**;
   - un entrenamiento de humo con fricción aleatoria.
4. **Visor corregido** (`1eba78d`, `6394628`):
   - los 3 carriles con sus robots de color y cada uno con su cámara;
   - meta en los 3 carriles (E30, E31);
   - el visor se veía roto por la GPU integrada AMD (E32).
5. **Aprobado por el usuario** (`94771b4`).

**Resultado de la carrera de 3 carriles** (colocados a +10 cm y −6°, μ = 1.0):

| Caminata | Con su cámara | Sin visión |
|---|---|---|
| RL (sprint inicial) | META en 24.6 s | META en 24.8 s |
| Baseline 2: tipo B-Human | META en 16.2 s | Se sale del carril a los 9.0 s |
| Baseline 1: tipo NAOqi | META en 49.8 s | META en 49.9 s |

### Paso 47 (adelantado) — Fricción explícita y aleatoria (2026-10-10, `9cb9ca1`)
- **Qué se hizo:**
  - `NaoWalkEnv` sortea μ en [0.4, 1.2] por episodio, con hasta 0.1 de diferencia entre pies;
  - `set_friction` resuelve la regla del máximo de MuJoCo;
  - `src.train` rechaza la fricción fija;
  - `src.evaluate --mu`.
- **Prueba:** `scripts/check_friction.py`, en OK. Problemas: E18, E22, E23.

### Paso 48 (adelantado) — Colores de la pista en un solo archivo (2026-10-10, `9d8a4a2`)
- **Qué se hizo:**
  - `config/pista.yaml` y `config/pista_robot.json` (para el NAO);
  - `scripts/cambiar_colores.py`: cambia, regenera y verifica;
  - **modo de visión por color** (E24, E25).
- **Matriz de 63 combinaciones:** de 30 a **57 OK**. Problemas: E26, E27, E28, E29.

---

### Paso 41 — Contrato v1 en código (2026-10-10)
- **Qué se hizo:** [`src/race/contract.py`](../../src/race/contract.py), el "idioma común" de la política de carrera
  entre el entrenamiento, la demo de 3 carriles y el NAO real (vía PenaltyStack):
  - **orden de las 26 articulaciones de B-Human**, copiado de PenaltyStack (`motion_contract.py`, commit `9c08a41`);
  - **tiempos:** ciclo de 12 ms y política cada 24 ms;
  - **observación de 54 valores** armada desde un `frame` con el formato del `SensorAdapter` de PenaltyStack:
    - gravedad proyectada desde el cuaternión de la IMU;
    - giroscopio;
    - error de rumbo;
    - **`d`, `psi` y válido de la cámara**;
    - ángulos y velocidades de las 13 articulaciones;
    - acción anterior;
    - carga de cada pie desde los 8 FSR;
    - reloj de marcha;
    - `vx_cmd`;
  - **acción de 13 ángulos:** HipYawPitch ±0.10 y **HipRoll asimétrico** (0.25 hacia afuera, 0.07 hacia adentro, por
    E16), y la salida `angles[26]` + `stiffness[26]` para PenaltyStack, con RHipYawPitch = LHipYawPitch;
  - **`EstadoCamara`:** última medición cruda, mantenida entre fotos, y válido < 300 ms (diseño, sección 6.7).
- **De dónde sale cada dato:**
  - orden de articulaciones y ciclo: PenaltyStack;
  - formato del `frame`: `SensorAdapter` de PenaltyStack;
  - pose `home` y rangos articulares: modelo V6 (keyframe `home` de `nao.xml`, generado desde el RSI3 de B-Human);
  - observación, acción y escalas: diseño, secciones 6.1, 6.2 y 6.7.
- **Restricción de diseño:** compatible con **Python 2.7 y sin numpy**, porque corre a bordo del NAO (NAOqi 2.8).
- **Verificación:** `scripts/check_contract.py` → **RESULTADO: OK** en la primera corrida. Comprueba:
  - nombres idénticos a PenaltyStack;
  - 54 valores con la cámara en las posiciones 7–9;
  - `POSE_HOME` = keyframe `home` en los 23 actuadores y los 13 límites dentro del rango articular;
  - con un frame real de MuJoCo (robot de pie girado 10°): gravedad igual a la del simulador, error de rumbo de
    −10.00°, carga de los pies 0.50 + 0.50, ángulos respecto a `home` < 0.021 rad;
  - gravedad y rumbo correctos en 50 orientaciones al azar;
  - acción 0 = `home`, ±1 = límites, recorte fuera de [−1, 1];
  - salida de 26 valores con RHipYawPitch copiado;
  - reglas de la cámara;
  - revisión estática de compatibilidad con Python 2.7: sin f-strings, sin anotaciones, solo `math`.
- **Errores:** ninguno en consola.
- **Pendiente:** el PC no tiene Python 2.7 (`py -0` solo lista 3.12). La prueba en el intérprete 2.7 real se hace en
  el NAO, en el paso 69.

### Paso 46 — Valores del modelo V6 en lugar de los del modelo aproximado (2026-10-10)
- **Revisión previa de la documentación** (regla de `CLAUDE.md`):
  - 23 `.md`, 0 enlaces o anclas rotas;
  - se encontró y corrigió un hueco: el contrato del paso 41 copia datos de PenaltyStack y no estaba en
    `fuentes_y_repositorios.md`.
- **Decisión:** no se cambió `src/envs/nao_walk_env.py`. Lo usa la política del sprint en la demo de 3 carriles, y
  cambiarle las escalas o el ciclo la rompería. Los valores del V6 van en `src/race/contract.py`, porque también los
  usa el robot, y en `src/race/valores_v6.py`, que son solo de la simulación.
- **Medición** (`scripts/check_valores_v6.py`, nuevo, sin PyTorch):
  1. **Altura de cadera en `home`:** 232 mm sobre la suela. B-Human camina con 230 mm, así que la pose `home` se
     mantiene.
  2. **Choque entre piernas:** 20,000 acciones al azar más los extremos, con distancia entre la pierna izquierda y la
     derecha medida con `mj_geomDistance`:
     - límites viejos: **23.9 %** de cruces (hasta −7.5 cm);
     - límites por articulación del contrato: **2.2 %** (E40);
     - con el **presupuesto lateral combinado**: **0 %**.
  3. **Altura de caída:** agachado al máximo dentro de los límites, el torso queda a 291.6 mm, así que la altura de
     caída es **0.24 m** (antes 0.22).
  4. **Altura objetivo:** de pie, asentado, 315.9 mm, así que **0.316 m** (antes 0.31).
  5. **Ciclo:** 12 × 2 ms = **24 ms**.
- **Además:**
  - período de marcha de 0.6 a **0.5 s** (2 pasos de 250 ms, como B-Human), también como parámetro del barrido
    (0.4–0.7);
  - `check_contract.py` ampliado con las pruebas del presupuesto lateral.
- **Verificación:**
  - `check_valores_v6.py` → OK;
  - `check_contract.py` → OK;
  - `check_standing.py` → OK en el V6: 10 s de pie, 20 de 20 con ruido, empujones de 15–20 N.
- **Errores:** E40, con su salida de consola y el cambio de criterio registrado. E16 queda resuelto.
- **De dónde salen los datos:**
  - modelo V6 (RSI3 de B-Human);
  - parámetros del WalkingEngine de B-Human (230 mm y 250 ms) en la config incluida en PenaltyStack;
  - contrato del paso 41.

### Paso 42 — Políticas compartidas en el repo (2026-10-11)
- **Qué se hizo:**
  - `scripts/guardar_politica.py` guarda una política en `policies/<nombre>/` (modelo, normalización, config,
    metadatos y README con su origen);
  - `src/train.py --continuar` sigue entrenando desde una política guardada y registra `continua_de`;
  - `env_id` configurable para el entorno de carrera.
- **Verificación:** ciclo guardar → evaluar → continuar probado con el run de humo. OK.
- **Errores:** ninguno.

### Paso 43 — Rendimiento de entrenamiento en este PC (2026-10-11)
- **Medición** (`scripts/benchmark_envs.py`, V6, fricción aleatoria, 16 entornos):
  - 3,725 pasos/s de entrenamiento;
  - 7,465 pasos/s de simulación pura;
  - 5.0 GB de RAM.
- **Consecuencia:** ~65–70M pasos en una noche de 6 h con el entorno de carrera, y ~22–27 h para el barrido de 100
  agentes.
- **Errores:** ninguno.

### Paso 44 — Validación de la física del V6 contra el RSI3 (2026-10-11)
- **Qué se hizo:** `scripts/check_modelo_v6.py` lee el RSI3 de B-Human por separado y compara con el modelo compilado:
  masas, centros de masa, inercias, posiciones, ejes y rangos de las articulaciones, y servos.
- **Resultado:**
  - todo idéntico, con diferencias del orden de 1e-15;
  - **masa total de 5.35975 kg**, igual a la del URDF oficial de Aldebaran (`NAOH25V60.urdf`), que es un control
    independiente.
- **Documentos:** `assets/nao/SOURCE.md` (V6) y la sección 10 del README.
- **Errores:** ninguno.

### Paso 45 — Diagnóstico de caídas al pausar y choque entre piernas (2026-10-11)
- **Qué se hizo:** `scripts/diag_caidas.py` reproduce sin visor las pausas de la demo, con 4 modos de pausa y 30
  episodios cada uno. También mide el choque entre piernas con acciones al azar, con la política del sprint y con una
  política entrenada desde cero en el V6.
- **Resultado:**
  - En el V6 la pausa de la demo tumba al robot en el **45 % de las pausas**, sobre todo durante la pausa.
    - Motivo: inclinación. Articulación con más error: RAnklePitch.
    - En el V5 eran 1 de 400.
  - El reloj de marcha no es la causa. Pausar en la pose de pie da 5.6 %.
  - Choque entre piernas:
    - 0 % con la política del sprint;
    - 0.16 % con una desde cero en el V6;
    - 1.06 % con acciones al azar del contrato v1, solo al caer.
- **Consecuencia:** el episodio de carrera arranca desde quieto y castiga el choque entre piernas.
- **Errores:** E42 (hallazgo); E44 (herramienta, paso 44).

### Paso 49 — Contactos, de pie y barrido articular con el V6 (2026-10-11, parte automática)
- **Resultado:** `check_contacts`, `check_standing` y `joint_sweep` en OK con el V6. Los topes del barrido son choques
  reales entre partes del cuerpo.
- **Pendiente:** revisión visual del usuario de `videos/joint_sweep.mp4`.
- **Errores:** ninguno.

### Pasos 53–58 — Entorno de carrera `NaoRace-v0` (2026-10-11)
- **Qué se hizo:** `src/envs/nao_race_env.py` implementa el diseño de las secciones 6–8.
  - Contrato v1: 54 observaciones y 13 acciones cada 24 ms.
  - Recompensa con las faltas, con los pesos de `configs/carrera/pesos.yaml`.
  - Episodio desde quieto con error de colocación y 0.5 s de medición de la visión.
  - Cámara simulada con ruido, retardo y pérdidas.
  - Pérdida de rectitud: asimetrías, empujones, suelo inclinado y deriva de la IMU.
- **Verificación:**
  - `scripts/check_race_env.py`: OK, 30/30. La observación es idéntica a la del contrato.
  - `scripts/check_camara_sim.py`: OK. La cámara renderizada da el mismo signo, con error de 1.05 cm / 0.72°, dentro
    del rango simulado.
- **Pendiente:** video del episodio revisado por el usuario (56), prueba de rectitud de 100 episodios (58) y orden de
  comportamientos de la recompensa (55), cuando haya una política que camine.
- **Errores:** E43, dos umbrales mal puestos en la prueba.

### Paso 58b — La política de carrera en los 3 carriles (2026-10-11, en curso)
- **Qué se hizo:**
  - `CorredorRLCarrera` en `carrera_vivo.py`: el RL corre con su propia cámara renderizada (d y psi crudos), sin el
    truco del giroscopio.
  - `scripts/eval_carrera.py` evalúa con la misma batería y las mismas métricas que el benchmark.
- **Pendiente:** verlo con una política que camine.

### Paso 59 — `carrera_v01` (2026-10-11, en curso)
- **Qué se hizo:** lanzado a las 00:26 con 60M pasos (~2,300 pasos/s), fricción aleatoria, perturbaciones y
  `vx_cmd` de 0.15 a 0.5 m/s.

### Paso 48b — Choques entre robots de carriles vecinos (2026-10-11)
- **Qué se hizo:** `demo/caminatas/choques.py` detecta contactos entre los 3 robots en la escena de 3 carriles. Cada
  robot sigue en su propia física y se copian sus poses. `carrera_vivo` lo usa.
- **Verificación:** `scripts/check_choques_robots.py`: OK. El choque con el vecino aparece 9 cm después de que el pie
  sale del carril.
- **Simplificación:** sin empujones entre robots después del contacto.
- **Errores:** ninguno.

### Paso 51 — Benchmark completo de los 3 carriles (2026-10-11)
- **Qué se hizo:** 150 corridas (3 caminatas × visión sí/no × 5 fricciones × 5 semillas) con
  `demo/caminatas/benchmark.py`.
- **Resultado con visión** (todas 25/25 sin faltas): B-Human 16.2–18.3 s, NAOqi 45.3–49.9 s, RL del sprint
  24.2–24.3 s. Sin visión, cerca del 45 % de salidas en las tres.
- **Errores:** ninguno.

### Paso 52 — Métricas de carrera unificadas (2026-10-11)
- **Qué se hizo:** el benchmark de 3 carriles evalúa la política de carrera con la misma función que
  `scripts/eval_carrera.py` (`--rl-carrera`).
- **Verificación:** mismas corridas → 9 métricas idénticas.
- **Errores:** ninguno.

### Paso 59 — `carrera_v01` (2026-10-11)
- **Qué se hizo:** PPO desde cero en `NaoRace-v0`, con fricción aleatoria, perturbaciones y cámara simulada. Se
  detuvo en 15.3M pasos (1 h 35 min).
- **Resultado (15M):** con visión, 10/10 metas sin faltas en 10.5–10.6 s (B-Human: 16.2–18.3 s), con desvío máximo
  de 3.4–5.6 cm; con perturbaciones, 20/20. Sin visión se cae o se sale (E45).
- **Errores:** E45 (dependencia de la cámara), E46 (`--continuar` con checkpoints).

### Paso 59b — `carrera_v02`: más pérdida de visión (2026-10-11, en curso)
- **Hipótesis:** con episodios sin cámara y apagones largos, la política deja de caerse al perder la visión.
- **Qué se hizo:** continúa desde `v01` a 15M; 40M pasos.

### Paso 60 — Lanzador de barridos (2026-10-11)
- **Qué se hizo:** `scripts/barrido.py` sortea pesos, fricción, velocidad, ruido de la cámara y semilla por agente;
  entrena en cola desde la base, evalúa con la batería, puntúa (sección 11.4) y es reanudable.
- **Verificación:** prueba completa con 4 agentes (`results/barridos/prueba_paso60/`).
- **Errores:** ninguno.

### Paso 55 — Recompensa con las faltas (2026-10-11): `[!]`
- **Qué se hizo:** recompensa implementada; pesos y rangos en `configs/carrera/pesos.yaml`; prueba de orden de
  comportamientos `scripts/check_recompensa_carrera.py`.
- **Resultado:** con −200, salirse justo antes de la meta da más retorno que ir lento; hace falta < −271 (E47).
  Queda para el paso 55b. El filtro duro de la selección cubre el riesgo mientras tanto.

### Pasos 59 y 59b — Resultado de la noche (2026-10-11)
- **`carrera_v01`** (15M): con visión le gana a B-Human por ~3–6 s sin faltas; sin visión se cae.
- **`carrera_v02`** (15M sobre `v01`): igual con visión y, sin visión, 89/100 sin caídas. Entrenar hasta 40M empeoró
  la robustez (E48); se eligió por batería.
- **Verificación:** baterías de 100 episodios con perturbaciones y lazo cerrado con la cámara renderizada (36/36).

## Trabajo de documentación (sin número de paso, 2026-10-10)

Pedido por el usuario para el paper. Commits `441dcb0`, `a266095` y el de la revisión previa al paso 41.

1. **Carpeta `docs/paper/`:** este historial, el registro de errores, el capítulo de la visión y su índice.
2. **`fuentes_y_repositorios.md`:** procedencia verificada con Git de cada pieza externa. Cubre B-Human, el RSI3,
   PenaltyStack, SabanaHerons2026, nao_linea y el origen de la cámara en este repo.
3. **Salida de consola textual en el registro de errores**, y dos errores nuevos: E38 (lectura del PDF del
   reglamento) y E39 (`KeyError` en `check_vision.py`).
4. **Regla nueva en `CLAUDE.md`:** al empezar **cada** paso se revisa toda la documentación con una lista fija.
   Primera revisión, antes del paso 41:
   - 23 archivos `.md`, 0 enlaces rotos y 0 anclas rotas;
   - sin datos contradictorios con lo decidido;
   - avisos agregados en `assets/nao/SOURCE.md` (describía el V5) y en `docs/variables_rl.md` (describe la
     política del sprint).

## Siguiente

Paso 41, el contrato v1 en código, dentro de la ruta crítica del RL: 41 → 46 → 53–58 → 58b → 59 → 60–63.
