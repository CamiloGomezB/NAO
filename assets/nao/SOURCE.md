# Origen y licencia del modelo NAO V6

Procedencia completa y verificada: [`docs/paper/fuentes_y_repositorios.md`](../../docs/paper/fuentes_y_repositorios.md).

## Fuente

`nao.xml` y `meshes/*.obj` se **generan** con [`scripts/build_nao_v6.py`](../../scripts/build_nao_v6.py) a partir de:

| Campo | Valor |
|---|---|
| Archivo | [`bhuman/NaoV6H25.rsi3`](bhuman/NaoV6H25.rsi3), **sin modificar** |
| Origen | [bhuman/BHumanCodeRelease](https://github.com/bhuman/BHumanCodeRelease), `Config/Scenes/Includes/NaoV6H25.rsi3`, revisión `d89d603f0388208cecd1c3144b6e8eb92aef4a93` |
| SHA-256 | `73f8c9a78b35fbdd18e6e407193924b2d1996812ff78cd405377cc57b0981369` (el script lo verifica antes de generar) |
| Cómo llegó | Por PenaltyStack, el repo final del equipo, que usa exactamente el mismo archivo |
| Licencia | La de B-Human, en [`bhuman/License.md`](bhuman/License.md): permite redistribuir con aviso y tiene condiciones para el uso en RoboCup |

**Qué es el RSI3.** Es la descripción de escenas de SimRobot, el simulador de B-Human, que usa MuJoCo como motor.
`NaoV6H25.rsi3` describe el NAO V6 completo:
- 25 cuerpos con masas e inercias;
- 24 articulaciones con ejes y límites;
- primitivas de colisión;
- mallas visuales;
- servos (P, D y fuerza máxima).

## Qué se conserva del RSI3

- **Sin cambios:** cuerpos, posiciones y ejes de las articulaciones, rangos, masas, centros de masa e inercias,
  cajas y esferas de colisión, mallas visuales y parámetros de los servos.
- **Verificación:** `uv run python scripts/check_modelo_v6.py` (paso 44) compara el modelo compilado con el RSI3 leído
  por separado:
  - 25 cuerpos, 24 articulaciones y 23 servos idénticos (diferencias del orden de 1e-15);
  - masa total de **5.35975 kg**, la misma del URDF oficial de Aldebaran (`NAOH25V60.urdf`).

## Qué agrega el script para el RL

1. **Raíz libre** y un sitio `imu` en la posición del acelerómetro del RSI3.
2. **HipYawPitch acoplado.** En el NAO real las dos HipYawPitch las mueve un solo motor. Se agrega una restricción de
   igualdad (`RHipYawPitch = LHipYawPitch`) y solo la izquierda tiene actuador: 23 actuadores.
3. **Servos de posición de MuJoCo** con los kp, kv y fuerza máxima del RSI3. Las articulaciones tienen el
   amortiguamiento y la armadura que fija SimRobotCore3 (0.01).
4. **Grupos de colisión:**
   - suelo = 1, torso/cabeza/caderas = 2, brazos = 4, piernas y pies = 8;
   - las piernas chocan entre sí, igual que en el robot real;
   - se excluyen solo los pares que se solapan por construcción (en la pose cero o en `home`) y los de las
     articulaciones intermedias (brazo-antebrazo y tibia-pie).
5. **Pose `home`** (cadera −0.4, rodilla 0.8, tobillo −0.4, brazos abajo), con la suela a 0.5 mm del suelo. La cadera
   queda a 232 mm de la suela; B-Human camina con 230 mm (paso 46).
6. **Sitios en el centro de cada suela** (`left_foot`, `right_foot`) y sensores: orientación, giroscopio,
   acelerómetro y velocidad (`local_linvel`; esta última solo la usa el entorno del sprint, porque el NAO real no la
   mide).
7. **Fricción:** no se fija en el modelo. La pone el entorno, aleatoria por episodio (paso 47).

**La cámara inferior** del NAO, para la visión de carril, no está en este archivo. La agrega
`demo/build_scene.py` en `nao_cam.xml`, con la pose y el campo de visión del modelo de B-Human.

---

## Histórico: el modelo V5 del sprint inicial (septiembre de 2026)

Hasta el 7 de octubre, `nao.xml` era un NAO **V5** derivado de
[nico-bohlinger/one_policy_to_run_them_all](https://github.com/nico-bohlinger/one_policy_to_run_them_all)
(`environments/nao_v5/data/nao.xml`, commit `7c18194`, MIT), con datos de
[ros-naoqi/nao_robot](https://github.com/ros-naoqi/nao_robot) (BSD-3).

**Cambios que se le hicieron:**
- primitivas en lugar de mallas, porque las mallas tienen licencia CC BY-NC-ND;
- sin dedos;
- HipYawPitch acoplado;
- **ejes corregidos a la convención NAOqi**: el original invertía HipRoll, AnkleRoll, ShoulderRoll, ElbowYaw y el
  pitch derecho;
- muñecas fijas;
- autocolisiones;
- servos de posición con kp = 30 y kv = 0.5.

Masa total: 5.305 kg.

Con ese modelo se entrenó la política del sprint (`checkpoints/best_model.zip`). La evaluación lo rechazó por ser una
aproximación del V5 (registro de errores, E12), y se reemplazó por el V6 de este archivo.
