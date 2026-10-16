# Despliegue en el NAO real — 1. Auditoría

*2026-10-15. Escrita por Claude Code a pedido de Luis Mario (autor de PenaltyStack). Es la misma auditoría que se
hizo para el penal en PenaltyStack (rama `despliegue/copa-nao-ccm-2026`, `docs/robot/01_AUDITORIA.md`), aplicada a
este repo, que es un fork reducido de PenaltyStack para la caminata.*

Documentos de esta serie:

1. **Auditoría** (este): qué había en el repo para llegar al robot, qué faltaba y qué exige el reglamento.
2. [Plan e implementación](02_PLAN_E_IMPLEMENTACION.md): la arquitectura a bordo y cómo se verificó.
3. [Operación](03_OPERACION.md): referencia rápida de comandos, gestos y archivos.
4. [Guía para otra persona](../GUIA_DESPLIEGUE_ROBOT_FISICO.md): el procedimiento paso a paso.

---

## 1. Qué había en el repo (antes del 2026-10-15)

| Pieza | Dónde | Estado |
|---|---|---|
| Políticas de carrera | `policies/rl_v1.2.1/` (recomendada), `rl_v1.2/`, `rl_v1.1/`, `rl_v1.0/`, `carrera_v02/`, `carrera_v01/` | SB3 (`model.zip`) + `VecNormalize` (`.pkl`). Solo corren en Python 3 con torch |
| Contrato v1 | `src/race/contract.py` | Arma las 54 observaciones desde el `frame` de PenaltyStack y devuelve `angles[26]` + `stiffness[26]`. Python 2.7/3, sin numpy |
| Visión de carril | `carril/lane_estimator_puro.py`, `carril/lane_filter.py`, `carril/controller.py` | Python puro (sirve en el NAO con NAOqi). Colores en `config/pista.yaml` → `config/pista_robot.json` |
| Ejecutor a bordo | `robot/race_nao.py` | **Carril NAOqi** (baseline 1): visión + `ALMotion.moveToward`, Python 2.7. Arranque por el táctil frontal 0.25 s, paro por el pecho 0.3 s, paro por inclinación |
| Herramientas del robot | `robot/diagnostico.py`, `robot/replay.py`, `robot/LUNES.md` | Diagnóstico y repetición de imágenes con NAOqi |
| Plan | `PLAN.md`, fase N (66–68b) | 66 (exportar), 67 (simulador de PenaltyStack) y 68 (ejecutor a bordo) **sin empezar** |

### 1.1 Qué faltaba para correr la política RL en el robot

1. **La política no podía correr a bordo.** El NAO V6 con NAOqi 2.8 tiene Python 2.7, sin torch. El paso 66 pedía
   exportar los pesos a JSON o `.npz` y escribir la inferencia en Python 2.7. Nunca se hizo.
2. **No había forma de mandar ángulos cada 12 ms.** `ALMotion` no está pensado para ángulos articulares a 41.7 Hz
   con la rigidez del contrato. Además, `ALMotion` y el proceso `bhuman` no pueden manejar los motores a la vez
   (`docs/integracion_penaltystack.md`, sección 3).
3. **No había framework B-Human en el repo.** El baseline 2 (WalkingEngine de B-Human) solo existía como réplica
   en MuJoCo. No había cómo correrlo en el robot (paso 73).
4. **No había herramienta de despliegue**: ni compilación cruzada, ni copia por Ethernet, ni selección de robots.
5. **Arranque y paro**: solo existían en `race_nao.py`, que no corre la política RL.

## 2. Qué aporta PenaltyStack

La rama `despliegue/copa-nao-ccm-2026` de [PenaltyStack](https://github.com/Limao0521/PenaltyStack) (commits
`c8aadf8` y `17b5c03`) ya resolvió lo mismo para el penal:

- **Framework B-Human 2023** de SabanaHerons2026 (`2360ab1`) importado con su procedencia (SHA-256 por archivo).
- **Compilación cruzada** para el NAO V6 en WSL (clang 18 + mold + sysroot V6 + ccache + ninja), instalable sin
  `sudo`.
- **Escenario propio** sin GameController, con los gestos del equipo, el silbato opcional y el apagado del Wi-Fi.
- **Despliegue** por Ethernet (rsync/ssh, servicio `bhuman.service`) con una ventana como el DeployDialog de
  Sabana Herons: selección de robots en red, opciones por robot y simulacro.
- **Verificación sin robot**: revisión del grafo de módulos y paridad de los cálculos contra Python.

Los robots del equipo (Sabana Herons) **ya tienen instalado el sistema B-Human** (`bhuman.service`). Basta con
copiar el binario y la configuración.

## 3. Lo que pide el reglamento (V1.0) y cómo se cumple

| Regla | Exigencia | Cómo se cumple en el despliegue |
|---|---|---|
| 2.7 | Sin comunicación inalámbrica; solo cable para cargar el programa | El despliegue activa el perfil `NONE` (Wi-Fi apagado) por defecto; la ventana pide confirmación si se desmarca |
| 2.9 | Activación ≤ 10 s después del silbato; no antes | Botón medio de la cabeza (toque). El silbato automático es opcional y está apagado por defecto (paso 68b sigue pendiente de decisión) |
| 3.2.3 | Paro manual con un sensor que **no** esté en las piernas | Pecho mantenido 0.3 s (como `race_nao.py`) **o** botón trasero de la cabeza mantenido 0.5 s (como PenaltyStack) |
| 3.2.5 | 3 minutos por carrera | `maxRunMs = 180000`: al vencer, se detiene de pie |
| 3.2.6 | Faltas: salir del carril, choque, comunicación externa | Visión de carril a bordo (la misma de Daniel, portada a C++), todo corre en el robot, sin red |
| — (seguridad del repo) | Paro por táctil de la cabeza y por inclinación antes de correr nada | Botón trasero, pecho, paro por inclinación (> 0.6 rad) y por temperatura de las piernas (≥ 75 °C) en la marcha RL |

## 4. Decisión: la política RL corre en C++ dentro de `bhuman`

**Antes** (paso 68 del plan): ejecutor en Python 2.7 con NAOqi. **Ahora**: un módulo del framework B-Human, en el
hilo Motion (ciclo de 12 ms, el de LoLA), que evalúa la política cada 2 ciclos (24 ms, el contrato v1).

Motivos:

1. **El contrato se cumple tal cual.** En el entrenamiento la política actúa cada 24 ms sobre ángulos articulares
   con rigidez 100. En `bhuman` el hilo Motion corre exactamente a 12 ms y escribe ángulos y rigidez por LoLA.
2. **Un solo proceso maneja los motores.** No hay competencia entre `ALMotion` y `bhuman`.
3. **Los dos carriles reales en el mismo binario.** El carril B-Human (WalkingEngine original + visión) queda listo
   para el paso 73 sin otro despliegue: se cambia de carril con un gesto en el robot.
4. **El mismo mecanismo que PenaltyStack**, el repo final: la integración del paso 78 es copiar módulos, no
   reescribir un ejecutor.
5. **Inferencia rápida**: 65 µs por decisión en el PC (la red es 54 → 256 → 256 → 13); hay margen de sobra en el
   Atom del NAO para 24 ms.

`robot/race_nao.py` **no se toca**: sigue siendo el carril NAOqi (baseline 1).

## 5. Riesgos que quedan abiertos

| Riesgo | Por qué | Cómo se mitiga |
|---|---|---|
| **Nada se ha probado en un robot físico** | No hubo robot en esta sesión | Paso 68d: primera prueba con el robot suspendido, con todos los paros activos |
| Diferencias sim-to-real de la marcha RL | Servos, fricción y retardos reales | Pasos 69–74 del plan; la marcha RL arranca en la pose `home` del entrenamiento con transición suave de 1.5 s |
| Cámara real distinta de la simulada | Exposición, intrínsecos, altura | El perceptor usa los intrínsecos calibrados de B-Human (`CameraInfo`) y la pose real (`CameraMatrix`). Paso 70 mide la precisión |
| Odometría del carril RL | La marcha RL no estima su odometría | El avance se estima con `vx_cmd`; tope de seguridad `rlMaxDistance = 7.5 m` y tiempo máximo de 3 min |
| Silbato con ruido de otras canchas | 4 carriles y público | Arranque por botón por defecto; el silbato es opcional |
