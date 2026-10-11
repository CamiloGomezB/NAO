# Registro de errores, fallos y soluciones

Catálogo de **todos** los problemas que aparecieron en el proyecto, en orden cronológico. Para cada uno se
registra:
- qué se observó (síntoma);
- por qué pasó (causa);
- cómo se resolvió (solución);
- dónde está la evidencia.

Es material directo para la sección de lecciones aprendidas del paper.

**Reglas**
- Cada error nuevo se agrega aquí con el siguiente número (`E38`, `E39`, …), **además** de su entrada en la
  [bitácora](../bitacora.md).
- No se borran errores. Si una solución resulta mala, se agrega un error nuevo que lo diga.
- **Si el error salió en consola, se copia el texto exacto** (traceback, mensaje de git o del sistema) en un
  bloque de código, y después cómo se solucionó. Si la salida no se conservó, se dice.
- **Estado:** ✅ resuelto · ⚠️ resuelto parcialmente o mitigado · ⏳ pendiente (con el paso del plan donde se
  resuelve) · ℹ️ hallazgo o limitación documentada.

**Categorías**
- **Modelo:** modelo del robot.
- **Sim:** simulación.
- **RL:** entrenamiento.
- **Visión.**
- **Entorno:** software y sistema operativo.
- **Integración:** entre repositorios.
- **Proceso:** herramientas y flujo de trabajo.

**Errores del sprint inicial (E01–E12):** la salida de consola de esos días no se conservó. Se reconstruyeron
a partir de los commits, `assets/nao/SOURCE.md`, el README y las notas de las sesiones.

Fuentes: historial de Git, [`PLAN.md`](../../PLAN.md), [`bitacora.md`](../bitacora.md), README, `assets/nao/SOURCE.md` y,
para la visión, el trabajo de Daniel en [danielpaya/nao_linea](https://github.com/danielpaya/nao_linea).

---

## Resumen

| ID | Fecha | Paso | Categoría | Problema | Estado |
|---|---|---|---|---|---|
| E01 | 2026-09-29 | 5–6 | Modelo | El modelo base invertía los ejes de varias articulaciones respecto a NAOqi | ✅ |
| E02 | 2026-09-29 | 5–6 | Modelo | Las mallas del modelo base tienen licencia que no permite redistribuirlas | ✅ |
| E03 | 2026-09-29 | 9 | Sim | Reiniciar el visor dejaba al robot en una pose cero y caía | ✅ |
| E04 | 2026-09-29 | 10 | Modelo | Partes del cuerpo se atravesaban entre sí | ✅ |
| E05 | 2026-09-29 | 10–13 | RL | HipYawPitch y los rangos completos generan movimientos peligrosos | ✅ |
| E06 | 2026-09-30 | 17–21 | Entorno | Con 8 hilos de PyTorch el entrenamiento era ~35 % más lento | ✅ |
| E07 | 2026-09-30 | 24 | RL | "Pasitos de soldado": la marcha base nunca apoyaba los dos pies | ✅ |
| E08 | 2026-09-30 | 24 | RL | Brazos rígidos | ✅ |
| E09 | 2026-09-30 | 24–25 | RL | Marcha asimétrica y deriva lateral de 13 cm en 3 m | ⚠️ |
| E10 | 2026-09-30 | 31 | Entorno | `pip` falla en Windows por rutas largas (PyTorch) | ✅ |
| E11 | 2026-09-30 | Demo | RL | Parar y reanudar la caminata hacía caer al robot | ⚠️ |
| E12 | 2026-09-30 | 33–35 | Modelo | El modelo entregado era un V5 aproximado: rechazado | ⚠️ |
| E13 | 2026-10-08 | 39 | Entorno | DLL de MuJoCo bloqueado (`WinError 4551`) dentro del sandbox de Claude Code | ✅ |
| E14 | 2026-10-08 | 39 | Entorno | Clonar PenaltyStack falla en Windows: "Filename too long" | ✅ |
| E15 | 2026-10-08 | 39 | Proceso | Un script de diagnóstico no terminaba nunca | ✅ |
| E16 | 2026-10-08 | 39 | Modelo | En el V6 solo hay 3 cm entre las piernas; valores heredados permiten cruzarlas | ⏳ 45–46 |
| E17 | 2026-10-08 | 39 | RL | En la demo interactiva el robot se cae al reanudar (V6) | ⏳ 45 |
| E18 | 2026-10-08 | 39 | Sim | La fricción era 1.0 por defecto de MuJoCo, sin que nadie la eligiera | ✅ 47 |
| E19 | 2026-10-10 | 40 | Integración | El benchmark guardado en nao_linea era la versión corta | ⏳ 51 |
| E20 | 2026-10-10 | 40 | Integración | nao_linea traía archivos que no deben versionarse | ✅ |
| E21 | 2026-10-10 | 40 | Entorno | Smart App Control de Windows bloqueó PyTorch | ✅ |
| E22 | 2026-10-10 | 47 | Proceso | La prueba "de pie con μ = 0.4" falló por una causa que no era la fricción | ✅ |
| E23 | 2026-10-10 | 47 | Sim | `condim` 3 vs 4: comparación no concluyente | ⏳ 51 |
| E24 | 2026-10-10 | 48 | Visión | La visión solo miraba el brillo: 30 de 63 combinaciones de colores | ✅ |
| E25 | 2026-10-10 | 48 | Visión | La regla para elegir el modo de visión fallaba con verde sobre madera | ✅ |
| E26 | 2026-10-10 | 48 | Visión | La simulación "detecta" negro sobre negro porque no tiene ruido | ✅ |
| E27 | 2026-10-10 | 48 | Visión | Gris sobre blanco falla: el piso blanco se satura | ℹ️ |
| E28 | 2026-10-10 | 48 | Proceso | Los parches escritos con heredocs de Bash rompieron dos archivos | ✅ |
| E29 | 2026-10-10 | 48 | Proceso | Archivos generados con finales de línea CRLF y comentarios desalineados | ✅ |
| E30 | 2026-10-10 | 40 | Sim | El visor no mostraba bien los 3 carriles | ✅ |
| E31 | 2026-10-10 | 40 | Sim | La cámara del visor miraba desde la meta hacia la salida | ✅ |
| E32 | 2026-10-10 | 40 | Entorno | El visor de MuJoCo se dibujaba roto: usaba la GPU integrada AMD | ✅ |
| E33 | 2026-10-10 | 40 | Proceso | La captura de la ventana tomó lo que estaba encima en la pantalla | ✅ |
| E34 | 2026-10-09 | Visión | Visión | Con poca luz solo el 67 % de las imágenes eran válidas | ✅ |
| E35 | 2026-10-09 | Visión | Visión | Falsos positivos de la meta roja sobre madera oscura | ✅ |
| E36 | 2026-10-09 | Visión | Visión | La autocorrección de la pose de la cámara no mejoró | ℹ️ |
| E37 | 2026-10-09 | Visión | RL | El "truco del giroscopio" se invierte con señales grandes | ⚠️ 58b |
| E38 | 2026-10-08 | 39 | Proceso | No se podía leer el PDF del reglamento desde el asistente | ✅ |
| E39 | 2026-10-10 | 40 | Proceso | `scripts/check_vision.py` falló en su primera corrida con `KeyError` | ✅ |

---

## Detalle

### E01 — El modelo base invertía los ejes de varias articulaciones
- **Fecha / paso:** 2026-09-29, pasos 5–6 (commit `6f55cb9`).
- **Síntoma:** en el modelo MuJoCo de partida, *one_policy_to_run_them_all*, `nao_v5`, un mismo ángulo no
  significaba lo mismo que en NAOqi.
- **Causa:** el original invertía el eje y el rango de HipRoll, AnkleRoll, ShoulderRoll, ElbowYaw y de todas
  las articulaciones de pitch del lado derecho.
- **Solución:** se restauró la convención oficial de Aldebaran (NAOqi). Se verificó en el paso 10 moviendo
  cada articulación por separado.
- **Por qué importa:** sin esto, una política entrenada en simulación mandaría ángulos con el signo
  equivocado al robot real.
- **Evidencia:** `assets/nao/SOURCE.md` (modelo V5), `scripts/joint_sweep.py`.

### E02 — Mallas con licencia que no permite redistribuirlas
- **Fecha / paso:** 2026-09-29, pasos 5–6.
- **Síntoma:** las mallas 3D del modelo base parecían venir de `ros-naoqi/nao_meshes`, que tiene licencia
  CC BY-NC-ND 4.0.
- **Solución:** se reemplazaron por primitivas: cápsulas, cajas y esferas. Además, la simulación de
  colisiones se volvió más rápida.
- **Consecuencia posterior:** el robot se veía "aproximado", y eso contribuyó a E12.

### E03 — Reiniciar el visor dejaba al robot en una pose cero y caía
- **Fecha / paso:** 2026-09-29, paso 9 (commit `5ad65cd`, "reinicio robusto del visor").
- **Síntoma:** al pulsar Backspace o el botón Reset del visor, el robot quedaba con los brazos al frente y
  las piernas rectas, y se caía.
- **Causa:** el Reset del visor ejecuta `mj_resetData`, que pone todo en cero en lugar de usar la pose
  `home`, y vuelve a aplicar los controles que guarda internamente.
- **Solución:** el visor detecta que el tiempo de la simulación retrocedió, vuelve a la pose `home` y fija
  los servos en `home`.
- **Evidencia:** `scripts/view_model.py`.

### E04 — Partes del cuerpo se atravesaban entre sí
- **Fecha / paso:** 2026-09-29, paso 10 (commit `6b0c7d9`).
- **Síntoma:** en el barrido articular con video, la mano atravesaba el muslo y un pie al otro.
- **Causa:** el modelo no tenía autocolisiones.
- **Solución:** grupos de colisión (`contype`/`conaffinity`) para que brazos, torso, cabeza y piernas choquen
  entre sí. Solo se excluye el par bíceps-antebrazo, que se tocan en el codo.
- **Evidencia:** `scripts/joint_sweep.py`, `assets/nao/SOURCE.md`.

### E05 — HipYawPitch y los rangos completos generan movimientos peligrosos
- **Fecha / paso:** 2026-09-29, pasos 10–13.
- **Síntoma:** el usuario señaló que HipYawPitch, que mueve las dos caderas a la vez, puede abrir las
  piernas y hacer caer al NAO real.
- **Prueba en el suelo**, una articulación a la vez desde `home` (seguro = no cae y el torso se inclina
  < 20°):

  | Articulación | Rango seguro |
  |---|---|
  | HipRoll y AnkleRoll | ±0.5 rad (inclinación ≤ 7°) |
  | HipPitch | −0.4 / +0.3 |
  | KneePitch | −0.3 / +0.2 |
  | AnklePitch (la más sensible) | −0.3 / +0.1 |
  | HipYawPitch | ±0.3–0.4, pero inclina el torso ~18° |

- **Solución:**
  - las acciones son **desviaciones pequeñas alrededor de `home`**: HipRoll 0.25, HipPitch 0.5,
    KneePitch 0.5, AnklePitch 0.4 y AnkleRoll 0.25 rad;
  - **HipYawPitch fija en 0**;
  - castigo por cambios bruscos y por torque.
- **Nota:** para la carrera se plantea volver a habilitar HipYawPitch con un rango pequeño (±0.10) para poder
  girar (paso 54).

### E06 — Con 8 hilos de PyTorch el entrenamiento era ~35 % más lento
- **Fecha / paso:** 2026-09-30, pasos 17–21.
- **Causa:** PyTorch competía por la CPU con los 16 procesos de simulación. El cuello de botella es la
  comunicación entre procesos, no la física.
- **Solución:** `torch_threads: 4` con 16 entornos, a ~3,800 pasos/s de entrenamiento.
- **Evidencia:** `scripts/benchmark_envs.py`, README (sección 6).

### E07 — "Pasitos de soldado"
- **Fecha / paso:** 2026-09-30, paso 24.
- **Síntoma:** la política base (`ppo_base_5M`) camina estable a 0.151 m/s, pero **nunca apoya los dos
  pies** (0 % de doble apoyo) y da pasos cortos. Esa fue la observación del usuario al ver el video.
- **Causa:** el reloj de marcha de la recompensa (`stance_fraction: 0.5`) premiaba que cada pie estuviera
  exactamente medio ciclo en el aire.
- **Solución (V1):**
  - `stance_fraction: 0.6`, que da 20 % de doble apoyo;
  - velocidad objetivo de 0.2 m/s.

  Resultado: 0.199 m/s, 20 % de doble apoyo, marcha fluida según el usuario.

### E08 — Brazos rígidos
- **Fecha / paso:** 2026-09-30, paso 24.
- **Causa:** los brazos estaban fijos en `home` y no formaban parte de la acción.
- **Solución (V2):** la política también controla `LShoulderPitch` y `RShoulderPitch` (±0.5 rad). **Aprendió
  sola a balancearlos en oposición a las piernas:** la correlación entre el hombro izquierdo y la cadera
  derecha es +0.85, sin ninguna recompensa que lo pida.

### E09 — Marcha asimétrica y deriva lateral
- **Fecha / paso:** 2026-09-30, pasos 24–25.
- **Síntoma:** en la política base, el pie izquierdo se levantaba 4.0 cm y el derecho 2.4 cm, y el robot se
  desviaba **13 cm a la derecha en 3 m**.
- **Solución parcial:** V1 lo redujo a 3.7/3.3 cm y −4.5 cm. En V2 la deriva es de ~+5 cm en 4 m.
- **Estado:** ⚠️ La deriva sin corrección sigue existiendo. Es la razón de fondo de la visión de carril y de
  la "pérdida de rectitud simulada" (paso 58).

### E10 — `pip` falla en Windows por rutas largas
- **Fecha / paso:** 2026-09-30, paso 31, prueba de instalación limpia (commit `c388b50`).
- **Salida de consola** (textual):
  ```text
  OSError ... Windows Long Path support
  (solo se conservó este fragmento del mensaje de pip, citado en el README)
  ```
- **Síntoma:** `OSError ... Windows Long Path support` al instalar PyTorch con `pip`.
- **Causa:** algunos archivos de PyTorch superan el límite de 260 caracteres de Windows.
- **Solución:** nota en el README: clonar en una ruta corta (`C:\NAO`), habilitar las rutas largas o usar
  `uv`, que no tiene el problema.

### E11 — Parar y reanudar la caminata hacía caer al robot
- **Fecha / paso:** 2026-09-30, demo interactiva (commit `468e562`).
- **Síntoma:** la política no tiene una orden de "parar". Volver a la pose de pie, frenar gradualmente o
  acomodarse hacia la pose de pie hacía caer al robot en el **40–100 %** de los casos.
- **Solución:**
  - esperar a que ambos pies estén en el suelo (~60 ms) y **congelar** la postura;
  - no permitir otra parada hasta llevar 2 s caminando.

  Resultado: **399 de 400** paradas sin caída (en el modelo V5).
- **Estado:** ⚠️ En el modelo V6 vuelve a fallar "a veces" (ver E17).

### E12 — El modelo entregado era un V5 aproximado: rechazado
- **Fecha / paso:** 2026-09-30, retroalimentación tras la entrega (Fase H, pasos 33–35).
- **Síntoma:** la evaluación pidió el **NAO V6 completo**, no una aproximación del V5 con primitivas.
- **Investigación:** se buscó el URDF oficial V6, `NAOH25V60.urdf`, publicado por Aldebaran en el grupo
  `ros-sig-aldebaran`, y las mallas del SDK 2.8.7.4. Entre V5 y V6 solo cambia la cabeza:
  - masa 0.660 kg en lugar de 0.605 kg;
  - masa total 5.360 kg en lugar de 5.305 kg.
- **Solución:** el modelo V6 se generó desde la descripción de **B-Human**, `NaoV6H25.rsi3`, con el script
  `scripts/build_nao_v6.py` (commit `d9207ec`). Es el mismo archivo que usa PenaltyStack, el repo final, así
  que los dos repos tienen el mismo robot. El plan original apuntaba al URDF; el motivo del cambio de fuente
  no quedó registrado en ese momento.
- **Procedencia verificada (2026-10-10):**
  - el RSI3 es `Config/Scenes/Includes/NaoV6H25.rsi3` de BHumanCodeRelease, revisión `d89d603`;
  - PenaltyStack lo agregó el 6 de octubre (`21dbb16`) y este repo el 7 (`d9207ec`), con el mismo SHA-256;
  - el script de conversión de este repo es propio.

  Ver [`fuentes_y_repositorios.md`](fuentes_y_repositorios.md#23-b-human-y-su-naov6h25rsi3-el-modelo-v6-actual-desde-el-7-de-octubre).
- **Estado:** ⚠️ El modelo está generado pero **no validado** (paso 44), y sus valores heredados (E16)
  siguen pendientes.

### E13 — DLL de MuJoCo bloqueado dentro del sandbox de Claude Code
- **Fecha / paso:** 2026-10-08, paso 39.
- **Salida de consola** (textual):
  ```text
  Traceback (most recent call last):
    File "<string>", line 2, in <module>
    File "C:\Users\camil\Documents\GitHub\NAO\.venv\Lib\site-packages\mujoco\__init__.py", line 254, in <module>
      _load_all_bundled_plugins()
    File "C:\Users\camil\Documents\GitHub\NAO\.venv\Lib\site-packages\mujoco\__init__.py", line 247, in _load_all_bundled_plugins
      PLUGIN_HANDLES.append(ctypes.CDLL(os.path.join(directory, filename)))
  OSError: [WinError 4551] Una directiva de Control de aplicaciones bloqueó este archivo
  ```
- **Síntoma:** `OSError: [WinError 4551] Una directiva de Control de aplicaciones bloqueó este archivo` al
  importar `mujoco` desde el asistente.
- **Causa:** el bloqueo ocurría solo dentro del entorno aislado del asistente.
- **Solución:** fuera de ese entorno, MuJoCo cargaba bien. Ver E21 para el bloqueo real que llegó después.

### E14 — Clonar PenaltyStack falla en Windows: "Filename too long"
- **Fecha / paso:** 2026-10-08, paso 39.
- **Salida de consola** (textual):
  ```text
  error: unable to create file baseline/bhuman/Src/Modules/MotionControl/KeyframeMotionEngine/KeyframeMotionLibs/KeyframePhaseJointCompensationImpl.cpp: Filename too long
  fatal: unable to checkout working tree
  warning: Clone succeeded, but checkout failed.
  You can inspect what was checked out with 'git status'
  and retry with 'git restore --source=HEAD :/'
  ```
- **Segundo problema:** después de `git config core.longpaths true` y `git restore --source=HEAD :/`, `git ls-files`
  devolvía 0 archivos y `git status` mostraba todos los archivos como `deleted` en el área de preparación.
  Se resolvió con `git reset --hard HEAD` en el clon temporal.
- **Causa:** el código de B-Human incluido en PenaltyStack tiene rutas que superan los 260 caracteres.
- **Solución:** `git config core.longpaths true` antes del checkout. Lo mismo se usó con nao_linea.

### E15 — Un script de diagnóstico no terminaba nunca
- **Fecha / paso:** 2026-10-08, paso 39.
- **Salida de consola** (textual):
  ```text
  Command did not complete within its 300s timeout and was moved to the background
  (mensaje de la herramienta del asistente; el script no imprimió ningún error, simplemente no terminaba)
  ```
- **Síntoma:** al evaluar la política sobre el V6 con un script propio, el primer episodio no terminaba.
- **Causa:** `NaoWalkEnv`, creado directamente y no con `gym.make`, **no tiene límite de duración**. El límite
  de 1000 pasos lo pone el registro de Gymnasium. Como el robot no se caía, el episodio seguía para siempre.
- **Solución:** tope explícito de 1000 pasos (20 s) en el script.
- **Lección:** al usar el entorno sin `gym.make`, hay que poner el límite de tiempo a mano.

### E16 — En el V6 solo hay 3 cm entre las piernas
- **Fecha / paso:** 2026-10-08, paso 39.
- **Medición:**
  - en la pose de pie hay 3.0 cm entre muslos y tibias y 3.1 cm entre pies;
  - las cajas de colisión reales del V6 miden 7–7.5 cm de ancho;
  - un HipRoll hacia adentro de ~0.075 rad por pierna cierra ese espacio.
- **Causa:** las escalas de acción (HipRoll ±0.25, simétrica), la altura objetivo, la altura de caída y el
  período de marcha **se heredaron del modelo aproximado**, que tenía piernas más delgadas.
- **Estado:** ⏳ Pasos 45 (diagnóstico) y 46 (valores del V6, HipRoll asimétrico).
- **Dato:** la política de septiembre en el V6, caminando de corrido, hizo 0 caídas y 0 choques entre piernas
  en 3 episodios de 20 s.

### E17 — En la demo interactiva el robot se cae al reanudar (V6)
- **Fecha / paso:** observado por el usuario y reportado el 2026-10-08.
- **Síntoma:** en `scripts/demo_interactive.py`, al pausar y reanudar, "a veces se cae".
- **Causa probable:** la política nunca aprendió a arrancar desde una postura quieta. En el V6 eso empeora
  (E11, E16).
- **Relevancia:** la carrera **empieza desde quieto**. Por eso el episodio de carrera siempre arranca así
  (paso 56).
- **Estado:** ⏳ Paso 45.

### E18 — La fricción era 1.0 por defecto, sin que nadie la eligiera
- **Fecha / paso:** 2026-10-08 (detectado al preguntar el usuario), resuelto en el paso 47.
- **Causa:** ni `nao.xml` ni `scene.xml` definían la fricción. MuJoCo usa 1.0 por defecto y combina dos
  contactos con el **mayor** de los dos coeficientes. La duela real probablemente está entre 0.5 y 0.8.
- **Solución:** fricción explícita en el suelo y en los pies:
  - **aleatoria por episodio** en [0.4, 1.2], con asimetría entre pies;
  - `src.train` rechaza fricción fija;
  - `scripts/check_friction.py` lo verifica.
- **Hallazgo:** **sin visión, la misma caminata llega o se sale del carril según la fricción.**

### E19 — El benchmark guardado en nao_linea era la versión corta
- **Fecha / paso:** 2026-10-10, revisión de nao_linea.
- **Síntoma:** el README de nao_linea cita 150 corridas, pero `resultados/benchmark/benchmark.md` tiene 12,
  una por celda: es el `--rapido`.
- **Estado:** ⏳ Paso 51: regenerar el benchmark completo. La versión corta sí se reprodujo idéntica en este
  repo.

### E20 — nao_linea traía archivos que no deben versionarse
- **Síntoma:** `__pycache__/*.pyc`, `MUJOCO_LOG.TXT`, `fase-p-camara-carril.bundle`, `rama_fase_p_camara.zip`.
- **Solución:** no se copiaron al integrar (paso 40), y `.gitignore` ahora ignora `robot/logs/`,
  `MUJOCO_LOG.TXT` y `*.bundle`.

### E21 — Smart App Control de Windows bloqueó PyTorch
- **Fecha / paso:** 2026-10-10, paso 40.
- **Salida de consola** (textual):
  ```text
  Traceback (most recent call last):
    File "C:\Users\camil\Documents\GitHub\NAO\demo\run_demo.py", line 32, in <module>
      from stable_baselines3 import PPO
    ...
    File "C:\Users\camil\Documents\GitHub\NAO\.venv\Lib\site-packages\torch\__init__.py", line 292, in _load_dll_libraries
      raise err
  OSError: [WinError 4551] Una directiva de Control de aplicaciones bloqueó este archivo. Error loading "C:\Users\camil\Documents\GitHub\NAO\.venv\Lib\site-packages\torch\lib\torch_python.dll" or one of its dependencies.
  
  Registro de Windows (Microsoft-Windows-CodeIntegrity/Operational), 10/10/2026 10:09:31 p. m.:
    Id 3118  Smart App Control Block Deteails
    Id 3077  Code Integrity determined that a process (\Device\HarddiskVolume3\Users\camil\AppData\Local\Programs\Python\Python312\python.exe) attempted to load \Device\HarddiskVolume3\Users\camil\Documents\GitHub\NAO\.venv\Lib\site-...
  VerifiedAndReputablePolicyState = 1
  ```
- **Síntoma:** `OSError: [WinError 4551] ... torch_python.dll`. Pasaba también fuera del entorno del
  asistente, desde Bash y desde PowerShell. El 2026-10-08 PyTorch sí cargaba en el mismo PC.
- **Diagnóstico:**
  - registro de Code Integrity de Windows: eventos 3077 y 3118, "Smart App Control Block";
  - valor `VerifiedAndReputablePolicyState = 1`, es decir, activado.
- **Causa:** Smart App Control decide por reputación en la nube. Las DLL de PyTorch pasaron a estar
  bloqueadas.
- **Solución:** **el usuario desactivó Smart App Control.** El asistente no cambia configuraciones de
  seguridad. Las alternativas documentadas eran usar WSL2 o esperar.
- **Impacto:** mientras duró, no se podía cargar ni entrenar ninguna política. Lo que no usa PyTorch, como
  MuJoCo, la visión y las caminatas de los baselines, sí se pudo verificar.

### E22 — La prueba "de pie con μ = 0.4" falló por otra causa
- **Fecha / paso:** 2026-10-10, paso 47.
- **Salida de consola** (textual):
  ```text
  4. De pie con mu = 0.4 (piso resbaloso)
     3 s de pie: caida = None, deslizamiento maximo de los pies 4.97 mm -> FALLA
  
  RESULTADO: FALLA
  
  Medicion de control (ruido inicial 0.02):  mu=0.4 -> 4.97 mm | mu=0.6 -> 4.67 mm | mu=1.0 -> 4.46 mm | mu=1.2 -> 4.44 mm
  Medicion de control (ruido inicial 0.0):   mu=0.4 -> 0.03 mm | mu=0.6 -> 0.02 mm | mu=1.0 -> 0.01 mm | mu=1.2 -> 0.02 mm
  ```
- **Síntoma:** 4.97 mm de deslizamiento de los pies en 3 s de pie con μ = 0.4, cuando el criterio era < 2 mm.
- **Diagnóstico:** con μ = 1.2 el deslizamiento era casi igual, 4.44 mm. Sin ruido en la pose inicial, era de
  0.01–0.03 mm con cualquier μ.
- **Causa:** el movimiento venía de **cómo se acomoda la postura** por el ruido de la pose inicial
  (`reset_noise`), no de la fricción.
- **Solución:** la prueba de fricción se hace sin ruido inicial.
- **Lección:** antes de culpar a la variable que se está probando, hay que barrer un valor de control.

### E23 — `condim` 3 vs 4: comparación no concluyente
- **Fecha / paso:** 2026-10-10, paso 47.
- **Prueba:** caminatas de los baselines con μ de 0.4, 0.6 y 1.0, sin visión, **una corrida por caso**.
  - Tipo B-Human con `condim` 3 se sale con μ = 0.6 y 1.0; con `condim` 4 llega en los tres casos.
  - Con una sola corrida, la variabilidad de la deriva no permite concluir.
- **Decisión:** mantener `condim` 3, igual que el entrenamiento previo y el benchmark.
- **Estado:** ⏳ Repetir con varias semillas en el paso 51.

### E24 — La visión solo miraba el brillo
- **Fecha / paso:** 2026-10-10, paso 48.
- **Salida de consola** (textual):
  ```text
  (primera corrida de scripts/cambiar_colores.py --matriz, extracto)
    piso verde         linea azul      contraste    26: **FALLA** (0 % validas)
    piso verde         linea verde     contraste     4: **FALLA** (0 % validas)
    piso azul          linea rojo      contraste     7: **FALLA** (0 % validas)
  | madera_clara | OK 1.4 cm | OK 1.4 cm | OK 1.5 cm | OK 1.4 cm | OK 1.4 cm | **FALLA** (0 % validas) | **FALLA** (0 % validas) |
  ```
- **Síntoma:** en la matriz de 63 combinaciones de piso × línea, **solo 30 daban OK**. Por ejemplo, línea verde
  o gris sobre madera clara daba 0 % de mediciones válidas.
- **Causa:** el detector convierte la imagen a escala de grises. Una línea de color con brillo parecido al
  del piso no se distingue.
- **Solución:** **modo "color"** en los dos estimadores, el de numpy y el de Python puro para el NAO.
  - Como los colores de la pista se conocen por `config/pista.yaml`, cada píxel se proyecta sobre la
    dirección de color "línea − piso", y la línea queda siempre más clara que el piso.
  - Resultado: **57 de 63 OK**.
- **Por qué importa:** la organización avisa los colores poco antes del evento.

### E25 — La regla para elegir el modo fallaba con verde sobre madera
- **Salida de consola** (textual):
  ```text
  (segunda corrida de la matriz, con la primera regla del modo color)
  | madera_clara | OK 1.4 cm | OK 1.4 cm | OK 1.4 cm (color) | OK 1.4 cm | OK 1.4 cm | **FALLA** (0 % validas) | **FALLA** (89 % validas (color)) |
  ```
- **Síntoma:** la primera regla, "modo color si el contraste de brillo es < 45", dejaba verde sobre madera
  clara en modo brillo (contraste 54), y daba 0 % de detecciones.
- **Causa:** el detector por brillo no solo exige contraste: exige que la línea sea más oscura que el 62 %
  del piso.
- **Solución:** usar el brillo **solo si pasa la misma prueba que aplica el detector**; si no, usar color.

### E26 — La simulación "detecta" negro sobre negro
- **Causa:** la imagen renderizada no tiene ruido de cámara. Un contraste de 25 de 255 se detecta en la
  simulación pero no se vería en una pista real.
- **Solución:** criterio **NO APTO** si el contraste efectivo es < 30.

### E27 — Gris sobre blanco falla: el piso blanco se satura
- **Causa:** la cámara simulada no tiene autoexposición. El piso blanco aparece en 255 y la línea gris queda
  demasiado clara.
- **Estado:** ℹ️ Limitación de la simulación. La cámara real ajusta la exposición, así que se verifica con
  fotos reales (paso 70).

### E28 — Los parches con heredocs de Bash rompieron dos archivos
- **Fecha:** 2026-10-10.
- **Salida de consola** (textual):
  ```text
    File "C:\Users\camil\Documents\GitHub\NAO\scripts\check_vision.py", line 130
      return "
             ^
  SyntaxError: unterminated string literal (detected at line 130)
  
      meta_rgb=list(info["meta_rgb"])), indent=2, ensure_ascii=False) + "
                                                                        ^
  SyntaxError: unterminated string literal (detected at line 193)        <- demo/build_scene.py
  
  /usr/bin/bash: -c: line 1: unexpected EOF while looking for matching `''   <- 2026-10-08, al reescribir PLAN.md
  /usr/bin/bash: -c: line 136: unexpected EOF while looking for matching `'' <- 2026-10-10, parche de documentación
  
  AssertionError:           f"maximo {MAX_EPISODE_STEPS * env.unwrapped.dt:.0f   <- reemplazo que no encontró el texto por los escapes
  <stdin>:3: SyntaxWarning: invalid escape sequence '\S'
  AssertionError: no
  ```
- **Dato:** ningún parche roto llegó a un commit. Antes de cada commit se verificó la sintaxis con
  `ast.parse` y los parches fallidos abortaban antes de escribir, gracias a los `assert`.
- **Síntoma:** `SyntaxError: unterminated string literal` en `scripts/check_vision.py` y
  `demo/build_scene.py`.
- **Causa:** las secuencias `\n` del código, escritas dentro de un heredoc de Bash que a su vez contenía un
  script de Python, llegaron como saltos de línea reales. Otros heredocs largos fallaron con
  `unexpected EOF`.
- **Solución:**
  - verificar con `ast.parse` después de cada parche;
  - escribir los parches largos como archivos y ejecutarlos.

### E29 — Finales de línea CRLF y comentarios desalineados
- **Salida de consola** (textual):
  ```text
  warning: in the working copy of 'PLAN.md', LF will be replaced by CRLF the next time Git touches it
  (aviso de git, inofensivo; aparece en casi todos los commits en Windows)
  
  diff pista_backup.yaml config/pista.yaml
  1,22c1,22      <- las 22 lineas "distintas" solo por el final de linea
  ```
- **Síntoma:** `config/pista.yaml`, reescrito por `cambiar_colores.py`, aparecía completo como distinto en
  `diff`, y los comentarios quedaban desalineados.
- **Causa:** `Path.write_text` en Windows escribe CRLF, y el reemplazo de valores no conservaba la columna de
  los comentarios.
- **Solución:** `newline="\n"` en los archivos generados, y el reemplazo conserva la columna del comentario.
  Al revertir, el archivo queda idéntico al original.

### E30 — El visor no mostraba bien los 3 carriles
- **Fecha / paso:** 2026-10-10, paso 40 (reportado por el usuario).
- **Síntomas:**
  1. `run_demo.py --live` mostraba un solo robot;
  2. la vista de 3 carriles (`carrera_vivo`) no tenía cámara;
  3. la meta roja solo estaba en el carril central;
  4. los 3 robots eran iguales.
- **Solución:**
  - `run_demo.py --live` abre los 3 carriles;
  - cada robot usa **su cámara renderizada** (`demo/caminatas/vision_camara.py`);
  - cada robot tiene su color (B-Human verde, RL azul, NAOqi naranja), con marcas en el piso;
  - meta en los 3 carriles;
  - ventana "Lo que ve cada NAO".

### E31 — La cámara del visor miraba desde la meta hacia la salida
- **Síntoma:** en la primera corrección, los robots caminaban hacia la cámara y los carriles se veían
  invertidos.
- **Causa:** el ángulo azimut del visor estaba en 200° en lugar de ~15°.
- **Solución:** se detectó en una captura sin pantalla y se corrigió antes de entregarlo.

### E32 — El visor de MuJoCo se dibujaba roto: usaba la GPU integrada AMD
- **Fecha / paso:** 2026-10-10, paso 40 (reportado por el usuario, con captura).
- **Salida de consola** (textual):
  ```text
  (no hubo error en consola: el visor abria, pero dibujaba mal)
  Diagnostico con GLFW + PyOpenGL:
  GL_VENDOR  : ATI Technologies Inc.
  GL_RENDERER: AMD Radeon(TM) Graphics
  GL_VERSION : 4.6.0 Compatibility Profile Context 22.20.44.221025
  Con SHIM_MCCOMPAT=0x800000001:
  GL_RENDERER: NVIDIA GeForce RTX 3060 Laptop GPU/PCIe/SSE2
  ```
- **Síntoma:** la ventana del visor se veía negra, con la escena aplastada en una franja arriba a la
  izquierda.
- **Diagnóstico, por eliminación:**
  - el fallo aparecía **con cualquier escena**, incluida la original del sprint;
  - aparecía con o sin cámaras, con o sin matplotlib y con o sin texto;
  - aparecía también en la versión de nao_linea;
  - las capturas sin pantalla (`mujoco.Renderer`) sí salían bien.
- **Causa:** la laptop tiene dos GPU, una NVIDIA RTX 3060 y una AMD Radeon integrada. El OpenGL de Python
  usaba la **AMD**, con driver 22.20.44 de 2022, y su ventana dibuja mal el visor.
- **Solución:** la variable de entorno `SHIM_MCCOMPAT=0x800000001`, fijada al inicio de los scripts con
  visor, hace que el driver de NVIDIA tome el OpenGL de ese proceso. No se cambió ninguna configuración de
  Windows.
- **Ajustes de presentación:** visor sin paneles laterales y texto arriba a la izquierda.

### E33 — La captura de la ventana tomó lo que estaba encima en la pantalla
- **Salida de consola** (textual):
  ```text
  ventanas del proceso:      <- primer intento: lista vacia
  ```
- **Primer problema:** el script buscaba la ventana por el número del proceso, pero `.venv\Scripts\python.exe` de
  `uv` lanza un proceso hijo, el intérprete real, que es el dueño de la ventana. Se pasó a buscar por el título
  ("MuJoCo").
- **Causa:** `CopyFromScreen` copia la región de la pantalla. Como la ventana de MuJoCo no estaba al frente,
  capturó la ventana que la tapaba.
- **Solución:** `PrintWindow`, que captura el contenido de la ventana aunque esté tapada y sin tomar nada más
  de la pantalla.

### E34 — Visión con poca luz: 67 % de imágenes válidas
- **Fecha:** 2026-10-09, desarrollo de la visión (Daniel, nao_linea).
- **Causa:** el umbral para detectar la cinta se calculaba contra el brillo de toda la fila.
- **Solución:** **fondo local**, una media móvil de 41 px a lo largo de la fila, con contraste relativo.
  Ahora 100 % válidas.

### E35 — Falsos positivos de la meta roja sobre madera oscura
- **Fecha:** 2026-10-09 (Daniel).
- **Síntoma:** 20 de 40 imágenes de madera oscura "veían" la meta roja.
- **Solución:** exigir saturación de color y una franja continua por fila. Ahora 0 de 40.

### E36 — La autocorrección de la pose de la cámara no mejoró
- **Fecha:** 2026-10-09 (Daniel).
- **Idea:** corregir el pitch y el roll de la cámara usando que las dos líneas deben ser paralelas y estar a
  72 cm.
- **Resultado:** no mejoró. El roll desplaza todo el carril de lado por igual y no se detecta con las líneas.
- **Decisión:** desactivada (`refine=False`).
- **Hallazgo relacionado:** **el error de la visión lo domina la pose de la cámara**. σ(d) va de 0.5 cm con
  la pose perfecta a 3.0 cm con 3° de error.

### E37 — El "truco del giroscopio" se invierte con señales grandes
- **Fecha:** 2026-10-09 (Daniel).
- **Contexto:** la política actual no tiene orden de giro. Para corregir el rumbo con la visión, la demo le
  suma una señal falsa a la observación del giroscopio, y la política "la compensa" girando.
- **Síntoma:** con un sesgo de 0.5 la respuesta se invierte y la política gira hacia el lado equivocado.
- **Mitigación:** sesgo limitado a ±0.35.
- **Solución definitiva:** ⏳ La política nueva recibe `d` y `psi` como observación (pasos 53 y 58b) y el
  truco desaparece.

### E38 — No se podía leer el PDF del reglamento desde el asistente
- **Fecha / paso:** 2026-10-08, paso 39.
- **Salida de consola** (textual):
  ```text
  pdftoppm is not installed. Install poppler-utils (e.g. `brew install poppler` or `apt-get install poppler-utils`) to enable PDF page rendering.
  
  ModuleNotFoundError: No module named 'pypdf'
  
  FileNotFoundError: [Errno 2] No such file or directory: '/c/Users/camil/AppData/Local/Temp/claude/.../scratchpad/regl_flat.txt'
  ```
- **Causa:**
  1. El lector de PDF del asistente necesita `pdftoppm`, que no está instalado en Windows.
  2. `pypdf` no estaba en el entorno.
  3. La terminal volvía a la carpeta del repo entre comandos, y una ruta relativa apuntaba a otro lugar.
- **Solución:**
  1. `pypdf` instalado **en una carpeta temporal**, fuera del proyecto (`uv pip install --target …/pylib pypdf`),
     para no tocar las dependencias del repo.
  2. Texto del PDF extraído (21 páginas).
  3. Rutas absolutas.
- **Impacto:** ninguno en el repo. El resumen del reglamento está en `docs/plan_rl_carrera.md`, sección 1.

### E39 — `scripts/check_vision.py` falló en su primera corrida
- **Fecha / paso:** 2026-10-10, paso 40.
- **Salida de consola** (textual):
  ```text
  Traceback (most recent call last):
    File "C:\Users\camil\Documents\GitHub\NAO\scripts\check_vision.py", line 135, in <module>
      sys.exit(main())
    File "C:\Users\camil\Documents\GitHub\NAO\scripts\check_vision.py", line 107, in main
      f"Generado por `scripts/check_vision.py`. Pista: piso `{info['piso']}`, linea `{info['linea']}`, "
                                                              ~~~~^^^^^^^^
  KeyError: 'piso'
  ```
- **Causa:** `build_scene.build()` devuelve los colores en RGB (`piso_rgb`, …), no sus nombres. El informe usaba el
  diccionario equivocado.
- **Solución:** los nombres se toman de la configuración (`cfg`), y los RGB y la polaridad de `info`. La segunda
  corrida dio `RESULTADO: OK`.
