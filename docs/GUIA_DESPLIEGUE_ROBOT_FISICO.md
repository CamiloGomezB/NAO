# Guía: desplegar la carrera en un NAO físico

Esta guía es para una persona del equipo que **no participó en el desarrollo** y necesita dejar uno o varios NAO V6
listos para la **Carrera Individual** de la *Copa NAO CCM MX 2026*. Sigue los pasos en orden. Los detalles técnicos
están en [docs/despliegue/](despliegue/01_AUDITORIA.md).

> **Estado (2026-10-15):** el programa compila, sus cálculos coinciden con los de Python (políticas, visión,
> filtro) y el despliegue se probó en simulacro. **Todavía no se ha ejecutado en un robot físico.** La primera
> prueba de cada robot y de cada política se hace **con el robot suspendido o con arnés** (regla del repo), con
> alguien listo para detenerlo.

---

## 1. Cómo funciona (en 2 minutos)

```
 PC con Windows                         Cable Ethernet                 NAO V6
┌──────────────────────────────┐                                  ┌───────────────────────────┐
│ Ventana de despliegue        │                                  │ /home/nao/Config/         │
│ (DeployCarreraNAO.bat)       │   copia binario + configuración  │   bhuman  (el programa)   │
│        │                     │ ───────────────────────────────► │   Config  (carril,        │
│        ▼                     │   ssh / rsync, red 192.168.49.x  │     política, vx, visión) │
│ WSL (Ubuntu): compila bhuman │                                  │ servicio bhuman: arranca  │
│ para el NAO y lo envía       │                                  │ solo al encender el robot │
└──────────────────────────────┘                                  └───────────────────────────┘
```

- **El robot decide solo.** Corre el sistema de B-Human (el que el equipo usa en RoboCup) con un escenario propio,
  `CopaNAORace`. Ese escenario trae:
  - la visión de carril;
  - la política RL de este repo, que mueve las articulaciones cada 24 ms;
  - como alternativa, la caminata original de B-Human corregida con la visión.

  Durante la carrera no hay PC, red ni Wi-Fi.
- **El PC solo prepara al robot.** Compila el programa en WSL (Linux dentro de Windows) y lo copia por cable con
  la configuración de cada robot:
  - el **carril**: `RL` o `B-Human`;
  - la **política RL** (`rl_v1.2.1` es la recomendada);
  - `vx_cmd`;
  - el modo de arranque;
  - los colores de la pista;
  - el número de jugador.

  Además apaga el Wi-Fi del robot (regla 2.7: solo cable).
- **En la pista el robot se maneja con sus botones.** El pecho lo pone de pie, el botón medio de la cabeza arranca
  y el pecho o el botón trasero (mantenidos) lo detienen. La sección 7 tiene el protocolo completo.

> `robot/race_nao.py` es otra cosa: el carril **NAOqi** (baseline 1), que corre con NAOqi y Python 2.7 y no usa este
> despliegue. No lo corras junto con `bhuman`: los dos manejarían los motores.

---

## 2. Qué necesitas

**Hardware**
- PC con Windows 10 u 11 y puerto Ethernet (sirve un adaptador USB-Ethernet).
- Cable Ethernet. Si vas a conectar varios robots a la vez, un switch.
- NAO V6 con batería cargada, **ya preparado con el sistema B-Human del equipo**. Los robots de Sabana Herons ya lo
  están. Un NAO de fábrica (solo NAOqi) primero necesita la instalación de B-Human (`bhuman/Install/`, wiki de
  B-Human 2023), que esta guía no cubre.
- Para las primeras pruebas: **arnés o soporte** para tener el robot suspendido.

**Software**
- Git y [uv](https://docs.astral.sh/uv/) (el repo se instala con `uv sync`, ver el README).
- Visual Studio 2022 Build Tools (C++), **solo** si vas a correr la prueba de paridad.
- WSL con Ubuntu 24.04 (se instala en el paso 3.2).

**Robots que reconoce la ventana** (salen de `bhuman/Config/Robots/<nombre>/network.cfg`):

| Robot | IP por cable | Robot | IP por cable |
| :--- | :--- | :--- | :--- |
| ronaoldinho | 192.168.49.2 | ospinao | 192.168.49.7 |
| loki | 192.168.49.3 | Heron | 192.168.49.8 |
| falcanao | 192.168.49.4 | naonaldo | 192.168.49.9 |
| juan | 192.168.49.5 | naonel | 192.168.49.10 |
| iniesnao | 192.168.49.6 | | |

---

## 3. Preparar el PC (solo la primera vez)

### 3.1 Descargar el repositorio

```bash
git clone https://github.com/CamiloGomezB/NAO.git
```

```bash
cd NAO
```

```bash
uv sync
```

### 3.2 Instalar WSL con Ubuntu 24.04

En PowerShell **como administrador**:

```powershell
wsl --install -d Ubuntu-24.04
```

Reinicia el PC si lo pide. Al abrir *Ubuntu 24.04* por primera vez crea un usuario y una contraseña de Linux.

### 3.3 Instalar las herramientas de compilación del NAO

Dentro de la terminal de Ubuntu, si tienes `sudo`:

```bash
sudo apt update
```

```bash
sudo apt install -y clang mold cmake ccache ninja-build rsync openssh-client
```

Sin `sudo`, desde la carpeta del repositorio en Windows (instala en tu usuario de WSL; si ya lo instalaste para
PenaltyStack, sirve el mismo):

```bash
uv run python scripts/compilar_bhuman.py --install-toolchain
```

Comprueba que no falte nada (todas las líneas deben decir `ok`):

```bash
uv run python scripts/compilar_bhuman.py --check
```

Si tu distribución de WSL no se llama `Ubuntu-24.04`, define la variable de entorno `PENALTYSTACK_WSL_DISTRO` con
su nombre (`wsl -l -v` lo muestra).

### 3.4 Poner el PC en la red de los robots

El puerto Ethernet del PC debe tener una IP fija en la subred `192.168.49.x`. Usa `192.168.49.100`, que no es de
ningún robot.

- **Con la interfaz gráfica**: Configuración → Red e Internet → Ethernet → *Asignación de IP* → Editar → Manual →
  IPv4. Dirección `192.168.49.100`, longitud de prefijo `24`, puerta de enlace y DNS vacíos.
- **Con PowerShell como administrador** (el adaptador suele llamarse `Ethernet`; `Get-NetAdapter` lo muestra):

```powershell
New-NetIPAddress -InterfaceAlias "Ethernet" -IPAddress 192.168.49.100 -PrefixLength 24
```

---

## 4. Compilar el programa del robot

```bash
uv run python scripts/compilar_bhuman.py
```

La primera vez tarda entre 10 y 20 minutos; las siguientes, segundos o pocos minutos. Al final aparece
`BHUMAN_BINARY=...` y el hash del binario. También se puede compilar con el botón **Compilar** de la ventana.

Solo hace falta recompilar si cambia el código. Si solo cambia la configuración (sección 8), basta con desplegar
sin compilar.

**Antes de una competencia**, corre también estas dos revisiones; las dos deben terminar sin errores:

```bash
uv run python scripts/check_grafo_modulos.py
```

```bash
uv run python scripts/check_paridad_robot.py
```

---

## 5. Conectar y desplegar

### 5.1 Conectar el robot

1. Enciende el NAO con un toque corto al botón del pecho. El arranque tarda alrededor de un minuto. **No mantengas
   el pecho presionado**: más de 3 s lo apaga.
2. Conecta el cable Ethernet al puerto trasero de la cabeza y al PC (o al switch).
3. **Seguridad:** durante el despliegue el programa del robot se detiene y el robot **pierde la rigidez**. Despliega
   con el robot sentado, sujetado o suspendido.

### 5.2 Abrir la ventana

Doble clic en **`DeployCarreraNAO.bat`**, en la raíz del repositorio (o `uv run python deploy/deploy_dialog.py`).

La ventana comprueba sola qué robots responden: la columna **Conexión** dice `● responde` en verde o
`● sin respuesta` en rojo. Se repite con **Comprobar conexion**.

### 5.3 Configurar

**Configuración general** (vale para todos los robots que despliegues):

| Opción | Qué poner |
| :--- | :--- |
| Compilacion | `Release`. |
| Compilar antes de desplegar | Marcado la primera vez o si cambió el código. |
| Equipo # | El número de equipo asignado (0 = no cambiarlo). |
| Volumen % | 70; el robot habla al cambiar de estado. |
| Arranque | **Botón medio de la cabeza** (recomendado). Las opciones con silbato pueden arrancar con silbatos de otras pistas. |
| Apagar Wi-Fi | **Siempre marcado** en competencia (regla 2.7). |
| Iniciar bhuman al terminar | Marcado. |
| Visión de la línea | **Según `config/pista_robot.json`** (recomendado): toma la polaridad y el modo color de los colores de la pista. Las otras dos opciones fuerzan línea oscura o clara por brillo. |
| Simulacro | Muestra lo que haría sin tocar los robots. Útil para practicar. |

**Tabla de robots** (una fila por robot):
1. Marca la casilla de cada robot que vas a desplegar.
2. **Carril**: `RL (politica)` para la caminata de este repo; `B-Human + vision` para el baseline 2. Se puede
   cambiar después en el robot (sección 6).
3. **Política RL**: `rl_v1.2.1` es la recomendada (motores ≤ 80 % y recta). Al elegir una aparecen su estado y
   sus resultados debajo de la tabla. `rl_v1.1` es la más rápida, pero exige los motores por encima del 80 %.
4. **vx_cmd**: `0.0` usa el recomendado de la política (0.45 m/s en las `rl_v1.x`). Para las primeras pruebas
   conviene bajarlo, por ejemplo a `0.30`.
5. **Jugador**: un número distinto por robot.

### 5.4 Desplegar

1. Pulsa **Desplegar seleccionados** y confirma el resumen.
2. El registro de abajo muestra cada paso por robot:
   1. detiene `bhuman`;
   2. activa el perfil Wi-Fi `NONE` (Wi-Fi apagado);
   3. copia el programa y la configuración;
   4. ajusta el volumen;
   5. verifica el hash del binario en el robot;
   6. arranca `bhuman`.
3. Termina bien cuando **Resultado** dice `OK` y el registro muestra `DEPLOY_OK <robot> ... sha256=...`.
4. Pulsa **Estado** con el robot seleccionado. Debe decir `bhuman: active` y mostrar el manifiesto del despliegue:
   carril, política, `vx_cmd`, arranque, visión, Wi-Fi y fecha.

Lo mismo por línea de comandos:

```bash
uv run python deploy/robot_deploy.py --deploy falcanao:rl loki:bhuman --team 49
```

---

## 6. Primera prueba de cada robot (suspendido)

Con el robot desplegado, `bhuman` activo y el robot **suspendido** en el arnés:

1. Recién arrancado está **sin rigidez**. Es normal.
2. **Toque al pecho**: toma la pose de salida y dice "learned walk ready" (carril RL) o "b human walk ready".
3. **Mantén el botón delantero 2 s**: cambia el carril y lo anuncia. Déjalo en el carril que vas a probar.
4. **Toque al botón medio**: arranca. Suspendido, las piernas deben hacer la marcha sin sacudidas.
5. **Mantén el pecho 0.3 s**: se detiene de pie y dice "stop". Repite con el **botón trasero 0.5 s**.
6. **Toque al botón delantero**: se rearma.
7. **Paro por inclinación**: arranca otra vez e inclina el arnés con cuidado más de ~35°. Debe decir "safety stop" y
   quedarse de pie.
8. **Mantén los tres botones de la cabeza 1 s**: pierde la rigidez.

Después baja los logs (**Descargar logs** → `data/real/logs_robot/<robot>/`) y guárdalos en `data/real/sesion_NN/`
con el manifiesto y el video. Busca las líneas `[CopaRace]` (la lista está en
[03_OPERACION.md](despliegue/03_OPERACION.md#5-lo-que-queda-en-el-log)). Si la marcha no arranca, revisa que diga
`politica ... cargada`.

Solo cuando todo esto funciona se pasa al piso: arnés → 1 m → 5 m, subiendo `vx_cmd` (paso 72 del plan).

---

## 7. En la competencia: protocolo por carrera

Reglas clave (reglamento V1.0, sección 3.2):
- ambos pies en la franja de salida;
- activación por un sensor del NAO hasta 10 s después del silbato, **nunca antes**;
- no se toca el robot una vez activado;
- se sale del carril = carrera anulada; 3 minutos como máximo.

| Momento | Qué hace el operador | Qué hace el robot |
| :--- | :--- | :--- |
| Antes de entrar | Desconectar el cable Ethernet. El Wi-Fi ya quedó apagado. | — |
| Colocación | Pies en la franja de salida, mirando a lo largo del carril. Toque al pecho si está sin rigidez. | Toma la pose de salida y espera ("… ready"). |
| Cambio de carril (si hace falta) | Mantener el botón delantero 2 s. | Anuncia el carril. |
| Silbato del juez | **Toque al botón medio de la cabeza**, antes de 10 s. | Arranca (en el carril RL, después de medir el rumbo de pie 0.5 s). |
| Durante la carrera | **No tocar.** | Corrige con la cámara; al ver la meta roja sigue 0.45 m y se detiene. |
| Emergencia (va a salirse o a caer) | Mantener el pecho 0.3 s (o el botón trasero 0.5 s). | Se detiene de pie ("stop"). |
| Fin | Esperar a que el juez autorice retirar el robot. | Queda de pie e inmóvil. |
| Otra carrera | Recolocar y dar un toque al botón delantero. | Se rearma. |

---

## 8. Ajustes en la sede, sin recompilar

Se cambian en el PC y se vuelve a desplegar con **Compilar antes de desplegar** desmarcado.

- **Colores de la pista** (los avisan poco antes del evento):

  ```bash
  uv run python scripts/cambiar_colores.py --piso <color> --linea <color>
  ```

  Regenera `config/pista_robot.json` y verifica la visión en simulación. Con *Visión: según
  config/pista_robot.json*, la ventana pasa sola la polaridad o el modo color al robot.
- **Umbrales de la visión**: `bhuman/Config/Scenarios/CopaNAORace/copaLanePerceptor.cfg`. Ajústalos con fotos
  reales de la zona de calibración (reglamento 2.10).
- **Meta y topes**: `copaRaceTactics.cfg`. **Gestos y 3 minutos**: `copaRaceController.cfg`. **Transición a la
  pose y paros de seguridad**: `copaRLWalkEngine.cfg`. Todos en la misma carpeta.

El carril, la política, `vx_cmd`, el arranque y la visión **no se tocan a mano**: se eligen en la ventana.

---

## 9. Problemas frecuentes

| Síntoma | Causa probable | Solución |
| :--- | :--- | :--- |
| `● sin respuesta` | El robot no terminó de arrancar, el cable está suelto o el PC no tiene la IP `192.168.49.x`. | Esperar, revisar el cable y repetir el paso 3.4. |
| Responde en la ventana, pero el despliegue no conecta | WSL no alcanza la red cableada (VPN o firewall). | Desactivar la VPN; `wsl --shutdown` y reintentar. Si persiste, `%UserProfile%\.wslconfig` con `[wsl2]` y `networkingMode=mirrored`. |
| `Toolchain incompleto` al compilar | Faltan herramientas en WSL. | Paso 3.3 y `uv run python scripts/compilar_bhuman.py --check`. |
| `Estado` no muestra `bhuman: active` | El programa no arrancó. | **Validar escenario** (0 errores), descargar logs y redesplegar. |
| Dice "walking policy missing" | Falta el `.cfg` de la política. | Redesplegar; `uv run python scripts/exportar_politicas_robot.py` si se borró. |
| No se pone de pie con el pecho | `bhuman` no está corriendo. | **Estado** o **Iniciar bhuman**. |
| En el carril B-Human camina torcido o lento | No ve la línea (`[CopaRace]` sin `meta a la vista`, visión inválida). | Revisar los colores (sección 8) y los umbrales con fotos reales. |
| "safety stop" al arrancar | Inclinación > 0.6 rad o motor de pierna caliente (≥ 75 °C). | Dejar enfriar; revisar el log `PARO de seguridad: …`. |
| Arrancó sin que nadie tocara el botón | Modo silbato con ruido de otra pista. | Redesplegar con *Arranque: Botón medio de la cabeza*. |

---

## 10. Para saber más

- [docs/despliegue/01_AUDITORIA.md](despliegue/01_AUDITORIA.md): qué había, qué faltaba y cómo se cumple el
  reglamento.
- [docs/despliegue/02_PLAN_E_IMPLEMENTACION.md](despliegue/02_PLAN_E_IMPLEMENTACION.md): arquitectura a bordo y
  verificaciones.
- [docs/despliegue/03_OPERACION.md](despliegue/03_OPERACION.md): referencia rápida.
- Código: `bhuman/Src/Modules/*/Copa*`, `bhuman/Src/Tools/CopaRace/CopaRace.h`, `deploy/` y
  `scripts/compilar_bhuman.py`.
