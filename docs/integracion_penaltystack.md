# Integración con PenaltyStack (repo final): solo lo que necesita la caminata

**PenaltyStack** ([Limao0521/PenaltyStack](https://github.com/Limao0521/PenaltyStack)) es el repositorio final
del equipo. Este repo (NAO) se dedica **solo al RL de la caminata**. Todo lo que hagamos aquí tiene que
poder pasarse allá y funcionar.

**De PenaltyStack usamos únicamente lo que sirve para caminar.** No usamos nada de penales: ni pelota, ni
portería, ni patada, ni portero.

Este documento resume el análisis de PenaltyStack del 2026-10-08, rama `feat/bhuman-simulation` (commit
`9c08a41`), limitado a la caminata. La única copia de código está en
[`third_party/penaltystack/`](../third_party/penaltystack/README.md): el orden de articulaciones.

> **Actualización del 2026-10-15 (fase N2):** el despliegue en el robot ya no sigue las secciones 3 (filas "A bordo",
> "Arranque", "Paro" y "Despliegue") y 6 tal como están escritas. Se tomaron de PenaltyStack el framework B-Human y
> sus herramientas de despliegue (rama `despliegue/copa-nao-ccm-2026`), y la política corre en C++ dentro de
> `bhuman`. Ver la [sección 7](#7-actualización-del-2026-10-15-despliegue-con-el-framework-b-human).

---

## 1. Qué parte de PenaltyStack nos interesa

- **Modelo del robot.** PenaltyStack usa el NAO V6 de B-Human convertido desde `NaoV6H25.rsi3`. Es **el
  mismo archivo** del que sale nuestro `assets/nao/nao.xml`, con el mismo SHA-256 `73f8c9a7…`, así que no
  hay que convertir nada.
- **Caminata.** PenaltyStack ejecuta en MuJoCo el **WalkingEngine original de B-Human**, en C++
  (`bhuman_motion.exe`, compilado con MSVC), con la física cada 2 ms y el motor cada 12 ms. **Es nuestro
  baseline.**
- **Interfaz con el robot real.** PenaltyStack define qué sensores se leen, cómo arranca y para el robot y
  cómo se despliega por Ethernet.

## 2. El baseline: la caminata de B-Human

**Decisión, confirmada con el autor de PenaltyStack el 2026-10-08:** el baseline es la caminata ya
establecida en PenaltyStack, el **WalkingEngine de B-Human**.

Desde el 2026-10-10 la comparación es de **tres carriles**: RL, B-Human y NAOqi. Ver
[`plan_rl_carrera.md`, sección 4](plan_rl_carrera.md#4-los-tres-carriles-qué-comparamos-y-cómo). Esta sección
describe el B-Human original, que valida la réplica tipo B-Human del benchmark.

**Parámetros del WalkingEngine** (config de B-Human incluida en PenaltyStack, `baseline/bhuman/Config/Robots/`):

| Parámetro | Valor | Archivo |
|---|---|---|
| Velocidad máxima hacia adelante (NAO) | 300 mm/s | `Nao/Nao/walkingEngine.cfg` |
| Velocidad máxima por defecto | 250 mm/s (`walkSpeedParams` hasta 350 mm/s) | `Default/walkingEngine.cfg` |
| Velocidad máxima de giro | 120 °/s | ídem |
| Aceleración máxima hacia adelante | 75 mm/s² | `Default/walkingEngineCommon.cfg` |
| Duración base de un paso | 250 ms | ídem |
| Altura de cadera al caminar | 230 mm | ídem |
| Altura de levantamiento del pie | 13 mm | ídem |
| Separación de caderas (`yHipOffset`) | 50 mm | `Default/robotDimensions.cfg` |

**Tiempo teórico en 5 m a 300 mm/s:** tarda 4 s en acelerar hasta 0.3 m/s y recorre 0.6 m en ese tiempo.
Los 4.4 m restantes llevan 14.7 s, así que el total es **~18.7 s**. **Es el tiempo a vencer**, pendiente
de medirlo.

**Evidencia en PenaltyStack:** la única prueba de marcha registrada es de **0.469 m en 5 s**, con orden de
avance de 0.06 m/s (`docs/SIMULACION.md`). Hay que medir el baseline a velocidades de carrera.

**Cómo se mide:**
- **En simulación** (paso 50): con el simulador de PenaltyStack sin ventana y la marcha original
  (`python -m penalty.simulator --headless --mode manual --action walk --forward <v> --seconds <s>`).
  Hay que compilar antes su runtime con VS 2022 Build Tools. Se mide con el mismo protocolo que
  nuestras políticas:
  - tiempo en 5 m;
  - deriva lateral;
  - rumbo máximo;
  - caídas.
- **En el robot real** (paso 73): la caminata de B-Human corriendo en el NAO con el framework de B-Human.
  En el robot ya existe un proceso `bhuman`, según `deploy/run.sh` de PenaltyStack. Se mide con el mismo
  protocolo en la pista marcada. Hay que confirmar en la sesión 1 que el framework está instalado y cómo
  se le ordena caminar recto a una velocidad fija.

## 3. Condiciones que impone PenaltyStack a nuestra política

| Tema | Condición en PenaltyStack | Qué cambia en nuestro diseño |
|---|---|---|
| Modelo | Mismo RSI3 V6, 23 servos, HipYawPitch acoplado | Usamos el mismo modelo; no hay que convertir nada |
| Nombres y orden de articulaciones | 26 entradas del enum `Joints` de B-Human (`third_party/penaltystack/motion_contract.py`) | La política exporta un mapa nombre ↔ índice con ese orden |
| Ciclo de control | Física 2 ms, motor 12 ms (también es el ciclo de LoLA en el robot) | La política actúa cada **24 ms** (2 ciclos, ~41.7 Hz). Hoy actúa cada 20 ms y hay que cambiarlo |
| Sensores disponibles | `angles[26]`, `velocity[26]`, `gyro[3]` (rad/s), `acc[3]` (m/s²), `orientation` (cuaternión wxyz), `fsr[8]` (kg) | La observación se arma **solo** con esto. Se quita la velocidad lineal del torso y los contactos de los pies salen de los FSR |
| FSR | 4 por pie, en kg, en el orden izq. fl/fr/bl/br y der. fl/fr/bl/br. Posiciones (m, marco del pie), izquierdo: (0.070, 0.030), (0.070, −0.023), (−0.030, 0.030), (−0.030, −0.019); derecho: espejo | Carga por pie = suma de sus 4 FSR / peso del robot |
| IMU | Sitio a (−0.008, 0.006, 0.027) m del torso, igual que en nuestro modelo | Ya coincide |
| Salida al motor | `angles[26]` + `stiffness[26]` (0–100) | La política da ángulos de las articulaciones que controla; el resto se mantiene y la rigidez es 100 |
| Autocolisiones | Desactivadas en su simulador | Nosotros **sí** simulamos los choques entre piernas, porque en el robot real chocan. Se evalúan aquí, porque allá no se detectan |
| A bordo | Python 2.7 + `qi` (NAOqi 2.8), sin MuJoCo ni torch. Su código a bordo está escrito en Python puro, sin numpy | La inferencia de la red debe correr en Python 2.7 puro. Que haya numpy a bordo está **por verificar**. Esto limita el tamaño de la red |
| Arranque | Táctil **frontal de la cabeza** sostenido **0.25 s** (`Device/SubDeviceList/Head/Touch/Front/Sensor/Value`), que el operador presiona tras el silbato | Se reutiliza. Cumple el reglamento: activación por sensor del NAO dentro de 10 s |
| Paro | **Botón del pecho** sostenido **0.3 s** (`Device/SubDeviceList/ChestBoard/Button/Sensor/Value`), enclavado | Se reutiliza. Cumple el reglamento: sensor que no está en las piernas |
| Actuadores | No se puede correr junto al proceso `bhuman`: ALMotion y LoLA no deben competir por los motores | La interfaz para mandar ángulos (ALMotion o LoLA) se decide con mediciones en el robot |
| Despliegue | Paquete con hashes copiado por SSH y Ethernet a `/home/nao/PenaltyStack/releases/<hash>` | Nuestro ejecutor se integra a ese mecanismo dentro de PenaltyStack |

## 4. Silbato

- PenaltyStack **no detecta el silbato**. El operador lo escucha y presiona el táctil frontal de la
  cabeza 0.25 s. Esto cumple el reglamento: activación por un sensor del NAO, como máximo 10 s después
  del silbato.
- La activación manual se mantiene. Ya se discutió el 2026-10-08 (ver la bitácora): un detector de
  silbato arriesga falsos positivos con 4 carriles y público.

## 5. Cámara y ruido gaussiano

- El simulador de PenaltyStack **no simula la cámara**. En el robot real la cámara se lee suscribiéndose a
  `ALVideoDevice`: cámara inferior, QVGA, RGB, **10 FPS**. Esa suscripción no existe en simulación.
- **Método de cámara (2026-10-10):** la visión de carril de Daniel, de
  [danielpaya/nao_linea](https://github.com/danielpaya/nao_linea), integrada en `carril/`. Usa la **misma suscripción** que
  PenaltyStack (cámara inferior, QVGA, RGB, 10 FPS) y entrega `d`, `psi` y válido. Tiene una versión en
  Python puro para el NAO.
- En el entrenamiento, su salida se simula sin renderizar imágenes:

  > estimación del carril = valor real del simulador + **ruido gaussiano** + retardo + pérdidas, actualizada a 10 Hz

  Es el mismo patrón que PenaltyStack ya usa para simular percepción. Ver
  [`plan_rl_carrera.md`](plan_rl_carrera.md#7-cámara-simulada-con-ruido-gaussiano).

## 6. Cómo se pasará la política a PenaltyStack

1. **Exportar la política a un formato liviano:** pesos y normalización en JSON o `.npz`, con la versión
   del contrato de observación y acción.
2. **El contrato** [`src/race/contract.py`](../src/race/contract.py) (paso 41) ya arma la observación desde el `frame`
   de PenaltyStack y devuelve `angles[26]` + `stiffness[26]` en el orden de B-Human. Es Python 2.7/3 y no usa numpy.
3. **Un módulo de inferencia** compatible con Python 2.7 y 3, sin dependencias o con numpy opcional. Recibe
   los sensores con el formato de PenaltyStack (sección 3) y devuelve ángulos en el orden de
   `motion_contract.py`.
4. **Probarla primero dentro del simulador de PenaltyStack**, en lugar del WalkingEngine de B-Human. Así
   se comparan las dos caminatas en el mismo simulador.
5. **Ejecutor a bordo** con el bucle de 24 ms y el arranque y paro de la sección 3, desplegado con el
   mecanismo de PenaltyStack.

Estos pasos son la Fase N del [`PLAN.md`](../PLAN.md).

## 7. Actualización del 2026-10-15: despliegue con el framework B-Human

Luis Mario hizo en PenaltyStack el despliegue del penal en robots reales (rama `despliegue/copa-nao-ccm-2026`,
commits `c8aadf8` y `17b5c03`) y pidió hacer lo mismo aquí con la carrera. Es la fase N2 del `PLAN.md`.

| Tema | Antes (secciones 3 y 6) | Ahora |
|---|---|---|
| A bordo | Python 2.7 + NAOqi, inferencia en Python puro | Framework B-Human (`bhuman/`, SabanaHerons2026 `2360ab1`). La política corre en C++ en el hilo Motion (12 ms), cada 24 ms; la visión, en el hilo de la cámara inferior |
| Exportación | Pesos en JSON o `.npz` | `.cfg` de B-Human en `bhuman/Config/NeuralNets/CopaRace/` (`scripts/exportar_politicas_robot.py`); paridad con SB3 4.6 × 10⁻⁷ |
| Arranque | Táctil frontal 0.25 s | Toque al botón medio de la cabeza (gestos del penal de PenaltyStack); silbato opcional |
| Paro | Pecho 0.3 s | Pecho mantenido 0.3 s **o** botón trasero mantenido 0.5 s; además, paros por inclinación y por temperatura |
| Actuadores | ALMotion o LoLA, por decidir | LoLA a través de `bhuman` (un solo proceso maneja los motores) |
| Despliegue | Paquete en `/home/nao/PenaltyStack/releases/<hash>` | `bhuman` + `Config` en `/home/nao/Config` por rsync/ssh, con la ventana `DeployCarreraNAO.bat`; Wi-Fi apagado y hash verificado |
| Baseline 2 en el robot | Por confirmar en la sesión 1 | El mismo binario trae el carril B-Human (WalkingEngine original + visión); se elige al desplegar o con un gesto |

**Lo que no cambia:** el contrato v1 (observación, acción, orden de articulaciones, 24 ms) y los sensores. De
PenaltyStack sigue sin tomarse nada del penal.

**Para pasarlo a PenaltyStack (paso 78):** los módulos de la carrera (`bhuman/Src/Modules/*/Copa*`, las
representaciones y `Tools/CopaRace/CopaRace.h`) usan el mismo framework que `robot/` de PenaltyStack, así que se
copian como módulos, con un escenario propio junto a `CopaNAOPenalty`.

Documentos: [auditoría](despliegue/01_AUDITORIA.md), [plan e implementación](despliegue/02_PLAN_E_IMPLEMENTACION.md),
[operación](despliegue/03_OPERACION.md) y [guía](GUIA_DESPLIEGUE_ROBOT_FISICO.md).
