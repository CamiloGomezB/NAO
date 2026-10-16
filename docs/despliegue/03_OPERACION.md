# Despliegue en el NAO real — 3. Operación (referencia rápida)

*2026-10-15. El procedimiento completo, para quien lo hace por primera vez, está en la
[guía](../GUIA_DESPLIEGUE_ROBOT_FISICO.md). Aquí van los comandos, los gestos y los archivos.*

## 1. Comandos (desde la raíz del repo)

| Para qué | Comando |
|---|---|
| Abrir la ventana de despliegue | `DeployCarreraNAO.bat` (doble clic) o `uv run python deploy/deploy_dialog.py` |
| Instalar el toolchain del NAO en WSL (una vez, sin `sudo`) | `uv run python scripts/compilar_bhuman.py --install-toolchain` |
| Revisar el toolchain | `uv run python scripts/compilar_bhuman.py --check` |
| Compilar `bhuman` (Release) | `uv run python scripts/compilar_bhuman.py` |
| Revisar el escenario sin robot | `uv run python scripts/check_grafo_modulos.py` |
| Paridad C++ ↔ Python | `uv run python scripts/check_paridad_robot.py` |
| Volver a exportar las políticas (solo si cambia una política o la visión) | `uv run python scripts/exportar_politicas_robot.py` |
| Robots y políticas conocidos | `uv run python deploy/robot_deploy.py --list` |
| ¿Responden? | `uv run python deploy/robot_deploy.py --ping falcanao loki` |
| Desplegar | `uv run python deploy/robot_deploy.py --deploy falcanao:rl loki:bhuman --team 49` |
| Desplegar sin compilar, en simulacro | `uv run python deploy/robot_deploy.py --deploy falcanao --no-build --dry-run` |
| Estado (servicio y manifiesto) | `uv run python deploy/robot_deploy.py --status falcanao` |
| Detener o iniciar `bhuman` | `uv run python deploy/robot_deploy.py --stop falcanao` / `--start falcanao` |
| Bajar los logs del robot | `uv run python deploy/robot_deploy.py --logs falcanao` → `data/real/logs_robot/falcanao/` |

Opciones de `--deploy`: `--policy rl_v1.2.1`, `--vx 0.45` (0 = el de la política), `--start-mode buttonOnly |
whistleOnly | buttonOrWhistle`, `--vision pista | oscura | clara`, `--first-player 1`, `--team`, `--volume`,
`--keep-wifi` (prohibido en competencia), `--no-build`, `--dry-run`, `--config Release | Develop | Debug`.

## 2. Gestos en el robot

| Gesto | Cuándo | Efecto |
|---|---|---|
| Toque al pecho | Sin rigidez (recién arrancado) | Se pone de pie en la pose de salida y dice el carril ("learned walk ready" o "b human walk ready") |
| Botón delantero de la cabeza mantenido 2 s | Esperando | Cambia el carril RL ↔ B-Human |
| **Toque al botón medio de la cabeza** | Esperando | **Arranca la carrera** |
| **Pecho mantenido 0.3 s** o **botón trasero mantenido 0.5 s** | Corriendo | **Paro manual**: se queda de pie ("stop") |
| Toque al botón delantero | Terminada o detenida | Rearma para otra carrera |
| Los tres botones de la cabeza 1 s | Siempre | Sin rigidez ("joints off") |

Paros automáticos: meta (franja roja + 0.45 m), tope de distancia, 3 minutos, inclinación > 0.6 rad o motor de pierna
≥ 75 °C (estos dos solo en el carril RL; el robot dice "safety stop").

## 3. Qué se escribe en cada robot

`deployCopaRace` prepara una copia de `Config` por robot (no modifica el árbol compartido) y cambia:

| Archivo | Valores |
|---|---|
| `settings.cfg` | `scenario = CopaNAORace`, `location = Default`, `playerNumber`, `teamNumber` |
| `Scenarios/CopaNAORace/copaRaceController.cfg` | `lane`, `startMode` |
| `Scenarios/CopaNAORace/copaRLWalkEngine.cfg` | `policy`, `vxCmd` |
| `Scenarios/CopaNAORace/copaRaceTactics.cfg` | `rlVxCmd` (= `vxCmd`) |
| `Scenarios/CopaNAORace/copaLanePerceptor.cfg` | `lightLine`, `colorMode`, `colorAxis`, `colorMean` (de `config/pista_robot.json`) |
| `carrera_deploy.json` (nuevo) | Manifiesto: robot, carril, política y su SHA-256, `vx_cmd`, arranque, visión, Wi-Fi, SHA-256 del binario y fecha |

Además: detiene `bhuman`, activa el perfil inalámbrico `NONE` (Wi-Fi apagado), copia el binario, `libonnxruntime` y
`Config` a `/home/nao/Config`, ajusta el volumen, **verifica el hash del binario en el robot** e inicia `bhuman`.
Termina con `DEPLOY_OK <robot> …`.

## 4. Ajustes en la sede sin recompilar

Se editan en el PC y se redespliega con **Compilar antes de desplegar** desmarcado:

| Qué | Dónde |
|---|---|
| Colores de la pista | `config/pista.yaml` → `uv run python scripts/cambiar_colores.py --piso <color> --linea <color>` (regenera `config/pista_robot.json`). La ventana lo toma con *Visión: según config/pista_robot.json* |
| Umbrales de la visión | `bhuman/Config/Scenarios/CopaNAORace/copaLanePerceptor.cfg` |
| Meta y topes | `copaRaceTactics.cfg` (`finishTrigger`, `postFinish`, `maxDistance`, `rlMaxDistance`) |
| Tiempos de los gestos, 3 min | `copaRaceController.cfg` |
| Transición a `home`, paros de seguridad | `copaRLWalkEngine.cfg` (`interpolationMs`, `settleMs`, `maxTilt`, `maxLegTemperature`) |

El carril, la política, `vx_cmd`, el arranque y la visión **no se tocan a mano**: se eligen en la ventana.

## 5. Lo que queda en el log

`Descargar logs` copia `/home/nao/logging/` del robot. Las líneas de la carrera empiezan con `[CopaRace]`:

```
[CopaRace] politica rl_v1.2.1 cargada vx_cmd=0.45 ...
[CopaRace] t=... fase unstiff -> waiting carril=learned walk
[CopaRace] t=... arranque headButton intento 1 carril=learned walk
[CopaRace] t=... marcha RL: 5 psi de pie, rumbo objetivo ...
[CopaRace] t=... meta a la vista a 0.33 m
[CopaRace] t=... fin finishLine tiempo=...
[CopaRace] t=... PARO de seguridad: inclinacion (inclinacion ...)
```

Las sesiones con el robot real se guardan en `data/real/sesion_NN/` (regla del repo), con estos logs, el manifiesto
`carrera_deploy.json` y el video.
