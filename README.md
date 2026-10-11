# Caminata con Reinforcement Learning para NAO V6 (MuJoCo + PPO)

Política de locomoción para el robot humanoide **NAO**, entrenada con **PPO** (Stable-Baselines3) en
simulación **MuJoCo**. El robot aprende desde cero a caminar hacia adelante; no hay trayectorias
articulares programadas a mano.

## Proyecto actual: Carrera Individual — Copa NAO CCM MX 2026

> **Estado (2026-10-11, madrugada):** **primera política de carrera que le gana a B-Human en simulación.**
>
> - **`carrera_v01`** ([`policies/carrera_v01/`](policies/carrera_v01/)): entrenada desde cero en el entorno de carrera
>   `NaoRace-v0` (contrato v1, cámara simulada, fricción aleatoria, perturbaciones).
>   - Con visión llega en **10.5 s** (`vx_cmd` 0.5) o **12.7 s** (0.40) contra **16.2–18.3 s** de B-Human, con 0 faltas;
>     también con la cámara renderizada de verdad (18/18).
>   - **Sin visión no sirve** (E45).
> - **`carrera_v02`** ([`policies/carrera_v02/`](policies/carrera_v02/)), con más pérdida de visión en el entrenamiento:
>   igual de rápida con visión (13.0 s a 0.40 m/s, 100/100) y **sin visión llega en 89/100 sin caerse**.
> - Hechos: 40–48b, 51–54, 57 y 60. Revisión del usuario pendiente en 49, 56 y 58b. 50 bloqueado (faltan VS Build
>   Tools). 55 con hallazgo (E47 → 55b).
>
> **¿Buscas algo?** Todo está enlazado en [Dónde está toda la información](#dónde-está-toda-la-información).

### Dónde está toda la información

Cada archivo tiene su enlace y una línea que dice qué contiene. Se mantiene al día en cada paso.

**Para empezar**

| Archivo | Qué tiene |
|---|---|
| [`PLAN.md`](PLAN.md) | Los pasos del proyecto con su criterio de aceptación, su estado (`[ ]` pendiente, `[~]` en curso, `[x]` hecho, `[!]` fallido o bloqueado), una nota con el resultado de cada uno y el **paso actual** |
| [`docs/bitacora.md`](docs/bitacora.md) | **Diario de trabajo**, en orden cronológico: qué se hizo en cada sesión, resultados con números, problemas, decisiones y siguiente paso |
| [`CLAUDE.md`](CLAUDE.md) | Reglas del proyecto (protocolo de trabajo, convenciones, compatibilidad con PenaltyStack, robot real) para el equipo y los asistentes de IA |

**Diseño**

| Archivo | Qué tiene |
|---|---|
| [`docs/plan_rl_carrera.md`](docs/plan_rl_carrera.md) | **Diseño del RL de carrera**: reglamento y faltas, observación de 54 valores, acción de 13 ángulos, recompensa con pesos y rangos, cámara simulada, fricción, 100 agentes, valores del V6 e implementación del entorno (§6.8) |
| [`docs/integracion_penaltystack.md`](docs/integracion_penaltystack.md) | Qué exige el repo final del equipo (PenaltyStack): sensores, orden de articulaciones, ciclo de 12 ms, arranque y paro, despliegue a bordo |
| [`docs/camara_y_carriles.md`](docs/camara_y_carriles.md) | La cámara y la demo de 3 carriles: cómo se usan |
| [`docs/variables_rl.md`](docs/variables_rl.md) | Variables de la **política del sprint inicial** (histórico, sin cámara). Para la de carrera, ver el capítulo del entrenamiento |

**Material del paper** ([`docs/paper/`](docs/paper/README.md))

| Archivo | Qué tiene |
|---|---|
| [`docs/paper/entrenamiento_rl.md`](docs/paper/entrenamiento_rl.md) | **Capítulo del entrenamiento por RL**: qué ve y hace la política, cada término de la recompensa (fórmula, peso y aporte medido), PPO y sus parámetros, etapas del aprendizaje, todas las pruebas, cómo se eligió, qué aprendió la política, fallos y cómo reproducirlo |
| [`docs/paper/historial_pasos.md`](docs/paper/historial_pasos.md) | Resumen de cada paso: qué se hizo, cómo se verificó y resultado |
| [`docs/paper/registro_errores.md`](docs/paper/registro_errores.md) | **Todos los errores y callejones** (E01, E02, …), con síntoma, causa, solución y la salida de consola textual |
| [`docs/paper/fuentes_y_repositorios.md`](docs/paper/fuentes_y_repositorios.md) | De dónde sale cada pieza externa (modelo V6 de B-Human, PenaltyStack, nao_linea), con commit o SHA-256, y por qué se usa |
| [`docs/paper/vision_carril.md`](docs/paper/vision_carril.md) | Capítulo de la visión de carril: método, precisión, colores y cómo entra al RL |

**Resultados y datos** ([`results/`](results/))

| Archivo o carpeta | Qué tiene |
|---|---|
| [`results/carrera/resumen.md`](results/carrera/resumen.md) | **Tabla de todas las evaluaciones** de las políticas de carrera (metas, caídas, salidas, tiempo, desvío) con la referencia de B-Human |
| [`results/carrera/carrera_v01/`](results/carrera/carrera_v01/) y [`carrera_v02/`](results/carrera/carrera_v02/) | Por generación: cada evaluación de cada checkpoint (`eval_*.md` legible y `.json` con cada corrida), las **curvas completas del entrenamiento** (`curvas_entrenamiento.csv` y `.png`), pruebas con la cámara renderizada, la prueba de rectitud de 100 episodios (`rectitud_58/`) y la batería de selección (`seleccion_100/`) |
| [`results/carrera/analisis_politicas.json`](results/carrera/analisis_politicas.json) | Qué aprendió cada política: normalización de las 54 observaciones, uso de cada acción y métricas de la marcha |
| [`results/carrera/orden_recompensa.json`](results/carrera/orden_recompensa.json) | Prueba de si salirse siempre es peor que ir lento (E47) |
| [`results/carrera/prueba_brazos_home.json`](results/carrera/prueba_brazos_home.json) | Prueba de la política con los brazos forzados a la pose de pie (E49) |
| [`results/carrera/carrera_v02/salida_mala.json`](results/carrera/carrera_v02/salida_mala.json) y [`rumbo_objetivo_carril.json`](results/carrera/carrera_v02/rumbo_objetivo_carril.json) | Salidas malas (corrida hasta ±15 cm, torcida hasta ±25°) y la prueba de alinear la IMU con el carril (E50) |
| [`results/benchmark/benchmark.md`](results/benchmark/benchmark.md) | **Benchmark de los 3 carriles** (RL del sprint, B-Human, NAOqi): 150 corridas, 5 fricciones, con y sin visión; datos en `benchmark.json` y `corridas.csv` |
| [`results/diagnostico_45.md`](results/diagnostico_45.md) | Diagnóstico de las caídas al pausar la demo y del choque entre piernas en el V6 |
| [`results/camara/`](results/camara/) | Validación de la visión: modelo de error, matriz de colores, lazo cerrado, cámara simulada contra renderizada |
| [`results/barridos/`](results/barridos/) | Barridos de agentes (por ahora, la prueba del lanzador con 4) |
| [`results/comparison.md`](results/comparison.md), [`results/metrics.json`](results/metrics.json) | Resultados de la política del sprint inicial (septiembre) |

**Políticas y configuraciones**

| Archivo o carpeta | Qué tiene |
|---|---|
| [`policies/carrera_v02/`](policies/carrera_v02/README.md) | **Política de carrera recomendada**: modelo, normalización, config, metadatos y README con su origen y resultados |
| [`policies/carrera_v01/`](policies/carrera_v01/README.md) | Primera política de carrera (la más recta; se cae sin visión) |
| [`configs/carrera_v01.yaml`](configs/carrera_v01.yaml), [`configs/carrera_v02.yaml`](configs/carrera_v02.yaml) | Config completa de cada generación, con su hipótesis escrita |
| [`configs/carrera/pesos.yaml`](configs/carrera/pesos.yaml) | Pesos de la recompensa y rangos para el barrido de agentes (un solo archivo) |
| [`config/pista.yaml`](config/pista.yaml) | Colores de la pista; se cambian con `scripts/cambiar_colores.py` |

**Fuera de git (solo en el PC que entrena)**
- `runs/`: cada entrenamiento completo (checkpoints, TensorBoard, log de consola). Lo importante se copia a
  `results/` y `policies/`.
- `videos/`: videos de las demos y de las pruebas.

**Objetivo.** Entrenar por RL una caminata para que un **NAO V6 real** recorra el carril de **5 m × 70 cm**
de la Carrera Individual **más rápido que los dos baselines, NAOqi (1) y B-Human (2)**, sin salirse del carril y
sin caer. Reglamento V1.0, sección 3.2; evento el **3 de noviembre de 2026**.

Este repo se dedica al RL de la caminata. La visión de carril y el simulador de la pista vienen de
[danielpaya/nao_linea](https://github.com/danielpaya/nao_linea) (Daniel) y se integran aquí. La versión final se
lleva a [PenaltyStack](https://github.com/Limao0521/PenaltyStack), el repo final del equipo.

**Cómo funciona** (detalle en [`docs/plan_rl_carrera.md`](docs/plan_rl_carrera.md)):

```mermaid
flowchart LR
    CAM["Cámara inferior"] --> VIS["Visión de carril"]
    PISTA["config/pista.yaml<br/>(colores)"] -.-> VIS
    VIS -- "d, psi, válido" --> POL["Política de RL<br/>(PPO, cada 24 ms)"]
    SENS["IMU, ángulos y velocidades<br/>articulares, 8 FSR"] --> POL
    VX["Velocidad vx_cmd"] --> POL
    POL -- "13 ángulos objetivo" --> NAO["Servos del NAO V6"]
```

1. **Política de RL.**
   - Observa 54 valores medibles en el NAO, incluidos los de la cámara: desplazamiento lateral `d`, ángulo
     `psi` y válido.
   - Controla 13 articulaciones.
2. **Faltas del reglamento.** Salirse del carril, caerse y chocar con otro robot terminan el episodio con
   castigos grandes, y **descartan** al agente en la selección. La comunicación externa queda imposible por
   diseño.
3. **Cámara simulada con ruido gaussiano.** En el entrenamiento no se renderizan imágenes: la salida de la
   visión se simula con el error medido (σ = 1.6 cm y 1.2°), hasta 3 veces peor.
4. **Fricción aleatoria** entre 0.4 y 1.2 al entrenar. Batería fija de pruebas: 0.4, 0.6, 0.8, 1.0 y 1.2.
5. **Colores de la pista en un solo archivo.** La política no ve colores, así que cambiarlos antes del
   evento no obliga a reentrenar.
6. **100 agentes.** Desde una base común se entrenan 100 variantes con distintos pesos y fricciones, y se
   eliminan por rondas con la misma batería.

**Tres carriles de comparación.** Simulación: carril de 5 m, batería común. Robot real: pista réplica.
Se actualiza con cada resultado:

| Carril | Caminata | Tiempo 5 m (sim) | Velocidad (sim) | Faltas (sim) | Tiempo 5 m (real) | Faltas (real) | Fuente |
|---|---|---|---|---|---|---|---|
| **Baseline 1: NAOqi** | Réplica tipo NAOqi (ZMP), con visión | 45.3–49.9 s (25/25 metas) | ~0.10 m/s | 0 | pendiente | pendiente | [`results/benchmark/`](results/benchmark/benchmark.md): 5 fricciones × 5 semillas (paso 51, 2026-10-11) |
| **Baseline 2: B-Human** | Réplica tipo B-Human (parámetros de PenaltyStack), con visión | 16.2–18.3 s (25/25; 18.3 s con mu 0.4) | ~0.27–0.31 m/s | 0 | pendiente | pendiente | [`results/benchmark/`](results/benchmark/benchmark.md) (paso 51). Sin visión: 14/25 metas, 11 salidas |
| **Baseline 2: B-Human** | WalkingEngine original (PenaltyStack) | pendiente (~18.7 s teórico) | — | — | — | — | Pasos 50 y 73 |
| RL | `v2_brazos` del sprint inicial, con visión (truco del giroscopio) | 24.2–24.3 s (25/25) | ~0.20 m/s | 0 | — | — | [`results/benchmark/`](results/benchmark/benchmark.md) (paso 51) |
| **RL** | **`carrera_v01`** (15M pasos, NaoRace-v0, cámara simulada, fricción aleatoria), con visión, `vx_cmd` 0.5 | **10.5–10.6 s** (10/10); con perturbaciones 11.2 s (20/20) | ~0.47 m/s | 0 | — | — | [`results/carrera/carrera_v01/`](results/carrera/carrera_v01/) (paso 59). **Sin visión se cae o se sale** (E45) |
| **RL** | **`carrera_v02`** (15M pasos sobre `v01`, más pérdida de visión), con visión y perturbaciones, `vx_cmd` 0.40 | **13.0 s** (100/100) | ~0.38 m/s | 0 | — | — | [`results/carrera/carrera_v02/`](results/carrera/carrera_v02/) (paso 59b). **Sin visión: 89/100 metas, 0 caídas.** Cámara renderizada: 36/36 |

**Cambiar los colores de la pista** (los avisan poco antes del evento): `uv run python scripts/cambiar_colores.py --piso <color> --linea <color>`.

**Ver la carrera en MuJoCo:** `uv run python demo/run_demo.py --live`. Se ven los 3 carriles con sus 3 robots:
- B-Human (verde, izquierda, baseline 2);
- RL (azul, centro);
- NAOqi (naranja, derecha, baseline 1).

Aparte se abre la ventana **"Lo que ve cada NAO"**, con la cámara de cada robot. Solo el RL con panel de
controles: `--live --solo-rl`. Guía completa: [`docs/camara_y_carriles.md`](docs/camara_y_carriles.md).

**Material para el paper:** [`docs/paper/`](docs/paper/README.md). Contiene el historial paso a paso, el registro
de los 37 errores encontrados con su solución, y el capítulo de la visión de carril.

**Para el equipo:** antes de trabajar, lean [`CLAUDE.md`](CLAUDE.md) (convenciones y protocolo de
documentación), el paso actual en [`PLAN.md`](PLAN.md) y las últimas entradas de la
[bitácora](docs/bitacora.md).

> El resto de este README documenta la **Etapa 1**: el sprint inicial en el que el NAO aprendió a caminar
> en simulación (pasos 1–32). Se conserva como línea base y se irá actualizando al avanzar la carrera.

![Demo: el NAO caminando con la política entrenada](media/demo.gif)

**Resultado de la política entregada** (`checkpoints/best_model.zip`, evaluada en 20 episodios con semillas fijas):

| Distancia en 20 s | Velocidad media | Caídas | Doble apoyo | Desviación lateral | Inclinación máx. del torso |
|---|---|---|---|---|---|
| **4.00 m** | **0.200 m/s** (objetivo 0.2) | **0 %** | 20 % del tiempo | 5 cm | 3.5° |

Entrenada en **~22 min en CPU** (5M pasos). Camina alternando los pies con una fase de doble apoyo,
como una marcha humana, y **balancea los brazos en oposición a las piernas**, un comportamiento que la
política descubrió sola. Detalles y comparación de variantes en la [sección 6](#6-experimentos-y-resultados).

### Inicio rápido

Requiere Python 3.12, Git y [uv](https://docs.astral.sh/uv/getting-started/installation/). No hace falta entrenar: el modelo viene incluido.

```bash
git clone https://github.com/CamiloGomezB/NAO.git
cd NAO
uv sync
uv run python -m src.evaluate --model checkpoints/best_model.zip --episodes 2 --render
```

El último comando abre el visor 3D con el NAO caminando. Para una demo en la que se puede **parar y
reanudar** la caminata con la barra espaciadora: `uv run python scripts/demo_interactive.py`.
Instalación con pip y más opciones en las secciones [1](#1-instalación) y [2](#2-demo-rápida-sin-entrenar).

---

## Contenido

0. [Dónde está toda la información](#dónde-está-toda-la-información)
1. [Instalación](#1-instalación)
2. [Demo rápida (sin entrenar)](#2-demo-rápida-sin-entrenar)
3. [Entrenamiento](#3-entrenamiento)
4. [Evaluación y evidencia](#4-evaluación-y-evidencia)
5. [Diseño del problema de RL](#5-diseño-del-problema-de-rl)
6. [Experimentos y resultados](#6-experimentos-y-resultados)
7. [Estructura del repositorio](#7-estructura-del-repositorio)
8. [Reproducibilidad](#8-reproducibilidad)
9. [Limitaciones y siguientes pasos](#9-limitaciones-y-siguientes-pasos)
10. [Modelo del robot, créditos y licencias](#10-modelo-del-robot-créditos-y-licencias)

---

## 1. Instalación

**Requisitos:** Python **3.12** y Git. No se necesita GPU: todo corre en CPU.
Probado en Windows 11 (Ryzen 7 5800H, 14 GB de RAM utilizable). Las dependencias también funcionan en Linux y macOS.

### Opción A: con [uv](https://docs.astral.sh/uv/) (recomendada)

```bash
git clone https://github.com/CamiloGomezB/NAO.git
cd NAO
uv sync
```

`uv sync` crea el entorno virtual `.venv` con las versiones exactas de `uv.lock`.
Todos los comandos siguientes se ejecutan con el prefijo `uv run`.

### Opción B: con pip

```bash
git clone https://github.com/CamiloGomezB/NAO.git
cd NAO
python -m venv .venv
# Windows:      .venv\Scripts\activate
# Linux/macOS:  source .venv/bin/activate
pip install -r requirements.txt
```

Con pip, omite el prefijo `uv run` en los comandos de abajo.

> **Windows y rutas largas:** si pip falla con `OSError ... Windows Long Path support`, clona el
> repositorio en una ruta corta (por ejemplo `C:\NAO`) o
> [habilita las rutas largas](https://pip.pypa.io/warnings/enable-long-paths). Algunos archivos de
> PyTorch superan el límite de 260 caracteres de Windows. `uv` (opción A) no tiene este problema.

### Versiones principales

| Paquete | Versión |
|---|---|
| Python | 3.12 |
| MuJoCo | 3.14.0 |
| Gymnasium | 1.3.0 |
| Stable-Baselines3 | 2.9.0 |
| PyTorch | 2.14.0 (CPU) |

Todas las dependencias están fijadas en [`pyproject.toml`](pyproject.toml), [`uv.lock`](uv.lock) y [`requirements.txt`](requirements.txt).

### Verificar la instalación

```bash
uv run python scripts/inspect_model.py
```

Debe terminar con `OK: el modelo carga y pasa las verificaciones basicas.`

---

## 2. Demo rápida (sin entrenar)

El repositorio incluye la política entrenada en [`checkpoints/`](checkpoints/). Para ver al NAO caminando
en el visor 3D de MuJoCo:

```bash
uv run python -m src.evaluate --model checkpoints/best_model.zip --episodes 2 --render
```

Para grabar un video en lugar de abrir el visor:

```bash
uv run python -m src.evaluate --model checkpoints/best_model.zip --episodes 1 --video videos/demo.mp4
```

> Controles del visor: clic izquierdo + arrastrar = rotar, clic derecho = desplazar, rueda = zoom.
> La ventana se cierra sola al terminar los episodios.

**Demo interactiva (parar y reanudar):**

```bash
uv run python scripts/demo_interactive.py
```

**Espacio** detiene o reanuda la caminata y **Enter** reinicia. La política se entrenó para caminar
siempre hacia adelante y no tiene una orden de "parar". Para detenerse, el script espera a que ambos
pies estén en el suelo (~60 ms) y congela la postura en ese instante. Tras reanudar, una nueva parada se
aplaza hasta llevar 2 s caminando, porque parar y reanudar muy seguido desestabiliza la marcha. Con
pulsaciones rápidas simuladas: **399/400 paradas sin caída**. Otras estrategias (volver a la pose de pie,
frenar gradualmente o acomodarse hacia la pose de pie una vez detenido) hacían caer al robot en un
40–100% de los casos. Una parada que junte los pies requeriría entrenar a la política con una orden
de velocidad (ver siguientes pasos).

### Problemas frecuentes

| Situación | Solución |
|---|---|
| **macOS:** el visor falla al abrir (`--render` o `demo_interactive.py`) | En macOS el visor de MuJoCo debe ejecutarse con `mjpython`, que viene con el paquete `mujoco`: `uv run mjpython -m src.evaluate --model checkpoints/best_model.zip --render` y `uv run mjpython scripts/demo_interactive.py` |
| **Linux sin pantalla** (servidor, SSH): el visor no abre o el video falla | Usa `--video` en lugar de `--render` y activa el render sin pantalla: `MUJOCO_GL=egl uv run python -m src.evaluate --model checkpoints/best_model.zip --video videos/demo.mp4` (o `MUJOCO_GL=osmesa` si no hay GPU) |
| Aviso `VIRTUAL_ENV=... does not match the project environment` | Inofensivo: aparece si hay otro entorno virtual activo en la terminal. `uv` usa igual el `.venv` del proyecto. Para quitarlo: `deactivate` o abrir una terminal nueva |
| **Windows + pip:** `OSError ... Windows Long Path support` | Clonar en una ruta corta (por ejemplo `C:\NAO`) o usar `uv` (ver [sección 1](#1-instalación)) |
| El entrenamiento va lento o el equipo se queda sin memoria | Menos entornos en paralelo: `--n-envs 8` (cada entorno usa ~250 MB de RAM). Cierra programas pesados mientras entrena |
| **El visor de MuJoCo se ve negro, con la escena aplastada en una franja** (laptops con dos GPU) | El visor estaba usando la GPU integrada (AMD) en lugar de la NVIDIA. Los scripts del repo ya piden la NVIDIA con `SHIM_MCCOMPAT=0x800000001`. Si aun asi pasa, en Configuracion de Windows → Pantalla → Graficos, asignar "Alto rendimiento" a `python.exe` (ver bitacora, 2026-10-10) |
| La ventana del visor no responde a Espacio o Enter | Haz clic sobre la vista 3D para darle el foco antes de usar el teclado |

> Probado en Windows 11. Las dependencias tienen versiones oficiales para Linux y macOS, pero en esos
> sistemas no se ejecutó la demo completa.

---

## 3. Entrenamiento

```bash
uv run python -m src.train --config configs/ppo_brazos_friccion.yaml --total-timesteps 5000000 --run-name mi_entrenamiento
```

- **Fricción aleatoria obligatoria (desde el paso 47).** No se sabe qué piso habrá en la competencia, así que
  todo entrenamiento sortea la fricción pie-suelo en cada episodio:
  - μ entre 0.4 y 1.2 (`friction_range`);
  - hasta 0.1 de diferencia entre pies (`friction_asym`).

  `src.train` rechaza una config con fricción fija (`friction`), salvo que se pase `--friccion-fija`. Esa
  opción existe solo para reproducir el sprint inicial. Verificación: `uv run python scripts/check_friction.py`.
- Todos los hiperparámetros, la semilla y los parámetros del entorno están en la config, por ejemplo
  [`configs/ppo_brazos_friccion.yaml`](configs/ppo_brazos_friccion.yaml).
- La salida queda en `runs/<run-name>/`: la configuración usada, versiones y commit, checkpoints
  periódicos, `best_model.zip`, `final_model.zip` y logs de TensorBoard.
- **Duración de referencia:** 5M pasos en **~22 min** (Ryzen 7 5800H, 16 entornos en paralelo, ~3,800 pasos/s).
  Con `--n-envs` se ajusta el número de procesos si el equipo tiene menos núcleos.
- Se puede interrumpir con `Ctrl+C`: guarda el modelo actual antes de salir.

Las variantes del sprint inicial comparadas en la [sección 6](#6-experimentos-y-resultados) usaban μ = 1.0
fijo. Se reproducen con `configs/ppo.yaml`, `configs/ppo_natural.yaml` o `configs/ppo_brazos.yaml` agregando
`--friccion-fija`.

**Reproducir la política entregada** (V2 brazos) y copiarla a `checkpoints/`:

```bash
uv run python -m src.train --config configs/ppo_brazos.yaml --total-timesteps 5000000 --run-name ppo_brazos_5M --friccion-fija
uv run python scripts/export_model.py --run ppo_brazos_5M
```

### Seguimiento con TensorBoard

```bash
uv run tensorboard --logdir runs
```

Abrir http://localhost:6006. Además de las métricas de PPO, se registra la media de **cada término
de la recompensa** (`reward_terms/*`) y la **tasa y motivo de caídas** (`episodes/*`).

---

## 4. Evaluación y evidencia

`src/evaluate.py` es independiente del entrenamiento. Carga un modelo, junto con la normalización de
observaciones y la configuración del entorno que se detectan automáticamente, y lo evalúa en N
episodios con semillas fijas:

```bash
uv run python -m src.evaluate --model checkpoints/best_model.zip --episodes 20 --json results/metrics.json --mu 1.0
```

`--mu` fija la fricción pie-suelo. Sin `--mu`, se sortea en cada episodio y el μ de cada uno queda en las
métricas. `results/metrics.json` del sprint inicial corresponde a μ = 1.0.

Métricas por episodio y agregadas (media ± desviación estándar): distancia recorrida, velocidad media,
duración, tasa de caídas, retorno, desviación lateral, inclinación máxima del torso y esfuerzo
(media de Σ τ²).

**Evidencia incluida en el repositorio:**

| Archivo | Contenido |
|---|---|
| [`results/metrics.json`](results/metrics.json) | Evaluación de la política entregada en 20 episodios |
| [`results/comparison.md`](results/comparison.md) | Comparación de las variantes con las mismas métricas |
| [`results/training_curves.png`](results/training_curves.png) | Curvas de entrenamiento de las variantes |
| [`media/demo.gif`](media/demo.gif) | Demo de la política entregada (8 s) |
| [`media/demo.mp4`](media/demo.mp4) | Episodio completo de la política entregada (20 s) |

Para regenerarlos: `scripts/compare_runs.py` (comparación), `scripts/plot_training.py` (curvas) y
`scripts/make_gif.py` (GIF a partir del video). Los tres requieren los runs en `runs/`, es decir,
reentrenar.

---

## 5. Diseño del problema de RL

> **Explicación sin código ni matemáticas:** [`docs/variables_rl.md`](docs/variables_rl.md) describe qué
> variables usa el aprendizaje (física, observación, acción, recompensa, reglas y parámetros de PPO),
> cuáles se dejaron fuera y por qué, y qué cambiaría para enseñarle otra habilidad, por ejemplo saltar.

Entorno Gymnasium `NaoWalk-v0` en [`src/envs/nao_walk_env.py`](src/envs/nao_walk_env.py).

| Elemento | Diseño |
|---|---|
| **Frecuencia** | La política actúa a **50 Hz**; la física corre a 500 Hz (`timestep` = 2 ms) |
| **Acción** (10) | Desviación en [-1, 1] × escala, sumada a la pose de pie `home`, para HipRoll, HipPitch, KneePitch, AnklePitch y AnkleRoll de cada pierna. Servos PD (kp=30, kv=0.5) con los límites de torque del NAO |
| **Fijas** | HipYawPitch en 0 (inclina mucho el torso y no aporta a caminar recto); cabeza y brazos en `home` en la versión base |
| **Observación** (43) | Gravedad proyectada (inclinación, IMU), velocidad angular (giroscopio), velocidad lineal del torso, ángulos y velocidades de las 10 articulaciones, acción anterior, contacto de cada pie y un reloj de marcha (sin/cos de un ciclo de 0.6 s) |
| **Terminación** | Caída: torso < 0.22 m, inclinación > 40° o cualquier parte que no sea un pie tocando el suelo |
| **Truncamiento** | 1000 pasos (20 s) |
| **Política entregada (V2)** | Además controla **LShoulderPitch y RShoulderPitch** (±0.5 rad), lo que da 12 acciones y 49 observaciones; velocidad objetivo 0.2 m/s y cada pie apoya el 60% del ciclo de marcha (20% de doble apoyo). Ver [sección 6](#6-experimentos-y-resultados) |

**Recompensa por paso** (pesos en `REWARD_WEIGHTS`, configurables desde el YAML):

| Término | Peso | Propósito |
|---|---|---|
| Velocidad de avance: exp(−((vx − v_obj)/0.1)²), v_obj = 0.15 m/s (0.2 en V1 y V2) | +1.0 | Avanzar a la velocidad objetivo, sin premiar lanzarse |
| Patrón de marcha (contactos vs reloj) | +0.5 | Alternar los pies al ritmo del reloj (con 20% de doble apoyo en V1 y V2) |
| Vivo | +0.1 | Pequeño premio por no caer |
| Inclinación (gx² + gy²) | −2.0 | Torso erguido |
| Altura ((z − 0.31)²) | −50 | Sin agacharse ni gatear |
| Velocidad lateral (vy²) y giro (ωz²) | −10, −0.5 | Caminar recto |
| Cambio de acción (‖aₜ − aₜ₋₁‖²) | −0.02 | Movimientos suaves |
| Torque (Σ τ²) | −0.001 | Esfuerzo moderado |
| Caída | −10 | Evitar caerse |

**Algoritmo:** PPO de Stable-Baselines3, como recomienda el enunciado. Red 256×256 (ELU) para
política y valor, 16 entornos en paralelo, 8,192 pasos por actualización, normalización de
observaciones y recompensas (`VecNormalize`) y exploración inicial moderada (`log_std_init = −1`).

**Por qué este stack:** MuJoCo + PPO/SB3 es el stack recomendado. Se usa en CPU y en Windows nativo:
la alternativa en GPU (MJX/JAX) requiere WSL/Linux y complica la reproducibilidad, mientras que en CPU
cualquier persona puede instalar y ejecutar el proyecto con los mismos comandos.

---

## 6. Experimentos y resultados

Se entrenaron tres variantes con el mismo algoritmo, hiperparámetros, semilla (0) y presupuesto
(**5M pasos, ~22 min cada una**). Cada variante se diseñó a partir de lo observado en la anterior:

| Variante | Config | Cambios respecto a la anterior | Motivación |
|---|---|---|---|
| **Base** | [`ppo.yaml`](configs/ppo.yaml) | — | Primer diseño (sección 5) |
| **V1 natural** | [`ppo_natural.yaml`](configs/ppo_natural.yaml) | Cada pie apoya el 60% del ciclo (`stance_fraction: 0.6`, 20% de doble apoyo); velocidad objetivo 0.2 m/s | La base caminaba con "pasitos de soldado": nunca apoyaba ambos pies a la vez |
| **V2 brazos** ✅ | [`ppo_brazos.yaml`](configs/ppo_brazos.yaml) | La política también controla los hombros (`control_arms: true`, 12 acciones, 49 observaciones) | En V1 los brazos seguían rígidos |

**Evaluación** (20 episodios, semillas 1000–1019, acciones deterministas; media ± desviación estándar;
tabla completa en [`results/comparison.md`](results/comparison.md)):

| Variante | Caídas | Distancia [m] | Velocidad [m/s] | Desv. lateral [m] | Doble apoyo [%] | Altura pie izq./der. [cm] | Esfuerzo Σ τ² | Brazos |
|---|---|---|---|---|---|---|---|---|
| Base | 0 % | 3.02 ± 0.00 | 0.151 | −0.13 ± 0.02 | 0.2 | 4.1 / 2.5 | 12.8 | fijos |
| V1 natural | 0 % | 3.98 ± 0.00 | 0.199 | −0.04 ± 0.03 | 20.1 | 3.7 / 3.3 | 12.3 | fijos |
| **V2 brazos** | **0 %** | **4.00 ± 0.00** | **0.200** | +0.05 ± 0.03 | **20.0** | 3.7 / 4.1 | 14.3* | **se balancean** |

\* Incluye el esfuerzo de los motores de los hombros, que las otras variantes no usan.

![Curvas de entrenamiento de las tres variantes](results/training_curves.png)

**Observaciones:**

- **Las tres variantes caminan sin caerse** en los 20 episodios y alcanzan su velocidad objetivo con
  gran precisión. Las curvas muestran que el robot primero aprende a no caerse (~0.5M pasos) y
  después a avanzar.
- **V1 corrige la "marcha de soldado".** Permitir el doble apoyo en el reloj de marcha dio pasos más
  largos y fluidos (evaluación visual) y, sin buscarlo directamente, **simetría entre piernas**: altura de
  los pies 3.7/3.3 cm frente a 4.1/2.5 cm, y **3 veces menos desviación lateral**.
- **V2 aprende a balancear los brazos de forma natural.** El hombro izquierdo oscila ~46° y el
  derecho ~30°, **en fase con la pierna contraria** (correlación hombro izquierdo–cadera derecha
  = +0.85), igual que al caminar una persona. No hay ninguna recompensa que lo pida explícitamente.
  Aprende algo más lento (más articulaciones que coordinar), pero a los 5M pasos iguala a V1.

**Política entregada: V2 brazos.** Empata con V1 en todas las métricas de caminata (0% caídas,
0.200 m/s, 20% de doble apoyo, desviación lateral de ~5 cm) y es la única que resuelve también la rigidez
de los brazos. Su costo es un esfuerzo algo mayor, por los motores de los hombros. V1 queda como
alternativa igual de válida si se prefiere mantener los brazos quietos.

**Otros hallazgos del proceso:**

- **Reproducibilidad:** dos entrenamientos con la misma configuración y semilla dieron curvas y
  políticas idénticas, episodio por episodio.
- **Rendimiento en CPU (Windows):** 16 entornos en paralelo con **4 hilos de PyTorch** es la mejor
  configuración (~3,800 pasos/s de entrenamiento). Con 8 hilos, PyTorch compite con los procesos de
  simulación y el entrenamiento es ~35% más lento. El cuello de botella es la comunicación entre
  procesos, no la física (`scripts/benchmark_envs.py`).
- **Robustez observada:** en la demo en vivo, al reiniciar la simulación desde el visor (Backspace),
  que deja al robot en una pose neutra que nunca vio en el entrenamiento, la política se recupera y
  sigue caminando.
- **Ajuste por plazo:** el plan original ([`PLAN.md`](PLAN.md)) contemplaba un entrenamiento largo
  de la base. Como la base ya caminaba a los 5M pasos, ese tiempo se usó en las dos variantes, que
  atacan lo observado en ella.

---

## 7. Estructura del repositorio

```
NAO/
├── assets/nao/          # Modelo MuJoCo del NAO (nao.xml, scene.xml), pista de la carrera con cámara (scene_carril.xml, nao_cam.xml) y SOURCE.md
├── carril/              # Visión de carril (de nao_linea): cámara → d, psi, válido
├── demo/                # Pista configurable, demo RL + cámara y caminatas de los baselines (3 carriles)
├── robot/               # Kit para probar la visión en el NAO real
├── config/              # pista.yaml: colores de la pista (único lugar) y pista_robot.json para el NAO
├── configs/             # Configuraciones de entrenamiento (base y variantes)
├── src/
│   ├── envs/            # NaoWalkEnv (Gymnasium) y registro de NaoWalk-v0
│   ├── utils/           # Entornos paralelos, callbacks de entrenamiento, video
│   ├── train.py         # Entrenamiento (CLI)
│   └── evaluate.py      # Evaluación, demo en vivo, video y métricas (CLI)
├── scripts/             # Verificaciones y utilidades (ver tabla abajo)
├── checkpoints/         # Política entregada: modelo, normalización, config y metadatos
├── results/             # Métricas, comparación y curvas de entrenamiento
├── media/               # GIF de la demo
├── docs/                # Variables del RL, diseño del RL de carrera, guía de cámara y carriles, integración con PenaltyStack y bitácora
├── third_party/         # Contrato de articulaciones de PenaltyStack (repo final), copia de referencia
├── CLAUDE.md            # Convenciones del equipo y protocolo de documentación (también para asistentes de IA)
├── PLAN.md              # Plan de trabajo paso a paso (sprint inicial + carrera)
└── pyproject.toml / uv.lock / requirements.txt
```

**Scripts de verificación.** Cada uno termina en `RESULTADO: OK` o `FALLA`:

| Script | Qué verifica |
|---|---|
| `scripts/inspect_model.py` | Carga del modelo, masas (5.360 kg en el V6), articulaciones y actuadores |
| `scripts/check_modelo_v6.py` | El modelo V6 es idéntico al RSI3 de B-Human; masa igual al URDF de Aldebaran (paso 44) |
| `scripts/check_valores_v6.py` | Valores del V6 para la carrera; las piernas no se cruzan con ninguna acción (paso 46) |
| `scripts/check_contract.py` | Contrato de observación y acción (54 valores, 13 acciones, formato PenaltyStack) (pasos 41 y 46) |
| `scripts/check_friction.py` | Fricción explícita y aleatoria por episodio (paso 47) |
| `scripts/check_vision.py` | Visión de carril con la cámara renderizada en 50 posiciones conocidas (pasos 40 y 48) |
| `scripts/check_contacts.py` | Contacto pie-suelo: penetración, rebote, deslizamiento |
| `scripts/check_standing.py` | Estabilidad de pie con los servos PD, con ruido y empujones |
| `scripts/joint_sweep.py` | Cada articulación recorre su rango, sin atravesar el cuerpo (genera video) |
| `scripts/check_env.py` | API de Gymnasium y SB3, semillas reproducibles |
| `scripts/inspect_obs.py` | Signos y marcos de referencia de las observaciones |
| `scripts/inspect_actions.py` | Mapeo acción → articulación y límites |
| `scripts/inspect_termination.py` | Detección de caída sin falsos positivos ni negativos |
| `scripts/inspect_reward.py` | La recompensa ordena correctamente los comportamientos |
| `scripts/benchmark_envs.py` | Velocidad con distintos números de entornos en paralelo |

Utilidades: `scripts/view_model.py` (visor interactivo del modelo; Enter reinicia),
`scripts/render_episode.py` (videos con políticas de prueba), `scripts/compare_runs.py` (tabla
comparativa de variantes), `scripts/plot_training.py` (gráficas), `scripts/make_gif.py` (GIF de la demo)
y `scripts/export_model.py` (copia un modelo de `runs/` a `checkpoints/`).

---

## 8. Reproducibilidad

- **Semillas:** cada entrenamiento usa la semilla de su YAML (`seed: 0`); el entorno `i` usa `seed + i`
  y la evaluación usa semillas fijas (1000, 1001…).
- **Determinismo verificado:** dos entrenamientos independientes con la misma configuración y semilla
  produjeron **exactamente** las mismas curvas y la misma política (mismas métricas episodio a episodio).
- **Trazabilidad:** cada run guarda `config.yaml` y `metadata.yaml` (commit de Git, versiones de
  Python, MuJoCo, Gymnasium, SB3 y PyTorch, y el comando ejecutado). Los de la política entregada están
  en `checkpoints/best_model_config.yaml` y `checkpoints/best_model_metadata.yaml`. Se entrenó con el
  commit `1bc49f6`; el código del entorno y del entrenamiento no cambió después, y los cambios
  posteriores son solo de evaluación y documentación.
- **Sin rutas absolutas:** todas las rutas se resuelven relativas a la raíz del repositorio.
- **Sin reentrenar:** la política final se incluye en `checkpoints/`, así que la demo funciona recién clonado.

---

## 9. Limitaciones y siguientes pasos

### Limitaciones

- **Solo simulación.** No se probó en el robot físico. La política no se entrenó con aleatorización de
  dinámica (masas, fricción, retrasos, ruido de sensores), así que no se espera que funcione
  directamente en el NAO real.
- **Modelo aproximado.** Es un NAO V5 con geometrías simplificadas; la dinámica de los servos reales
  (retrasos, límites de velocidad, calentamiento) no está modelada, solo un PD ideal con límites de torque.
- **Observación privilegiada.** La velocidad lineal del torso se lee directamente de la simulación;
  en el robot real habría que estimarla.
- **Tarea acotada.** Camina solo hacia adelante, en línea recta, a una velocidad fija (sin comandos
  de giro ni de velocidad), sobre suelo plano y sin perturbaciones.
- **Estilo de marcha.** La política base caminaba con pasos cortos, sin fase de doble apoyo ("marcha de
  soldado") y con los brazos fijos. Las variantes V1 y V2 de la sección 6 corrigieron estos puntos, pero
  la marcha sigue siendo de pasos cortos (~4 cm de altura de pie).
- **Presupuesto de cómputo.** Cada variante se entrenó 5M pasos (~22 min en CPU) por el plazo del
  sprint; no hubo búsqueda de hiperparámetros ni varias semillas por variante.

- **Asimetrías residuales en la política entregada:** el balanceo de brazos no es simétrico (~46° vs
  ~30°) y un pie se levanta algo más que el otro (3.7 vs 4.1 cm). Cada variante se entrenó con una sola
  semilla, así que no se midió la variabilidad entre semillas.

### Siguientes pasos

1. **Robustez:** aleatorización de dominio (masas, fricción, ganancias PD, retraso de acciones),
   empujones durante el entrenamiento y terreno irregular.
2. **Comandos:** velocidad (incluida velocidad 0, para detenerse juntando los pies) y giro como entrada de la política, para caminar en cualquier dirección y parar de forma natural.
3. **Marcha más natural:** recompensas de altura de pie y longitud de paso, simetría entre piernas y
   balanceo de brazos coordinado.
4. **Hacia el robot real (sim-to-real):** modelar la dinámica de los servos del NAO (retrasos y límites
   de velocidad), quitar observaciones privilegiadas, ejecutar la política a través de NAOqi/LoLA y
   probar primero con el robot suspendido. Los ángulos ya usan la convención de NAOqi, lo que facilita
   este paso.
5. **Escala:** entrenar en GPU con MuJoCo MJX (miles de entornos en paralelo) para explorar más
   variantes y semillas.

---

## 10. Modelo del robot, créditos y licencias

- **Modelo actual: NAO V6 de B-Human.**
  - `assets/nao/nao.xml` se genera con `scripts/build_nao_v6.py` desde `NaoV6H25.rsi3` de
    [bhuman/BHumanCodeRelease](https://github.com/bhuman/BHumanCodeRelease) (revisión `d89d603`), el mismo archivo que
    usa PenaltyStack.
  - **Validado** con `scripts/check_modelo_v6.py`: cuerpos, articulaciones y servos idénticos al RSI3, y masa de
    5.35975 kg, igual al URDF oficial de Aldebaran.
  - Detalle en [`assets/nao/SOURCE.md`](assets/nao/SOURCE.md); procedencia en
    [`docs/paper/fuentes_y_repositorios.md`](docs/paper/fuentes_y_repositorios.md).
- **Modelo del sprint inicial (histórico):** un NAO V5 derivado de
  [nico-bohlinger/one_policy_to_run_them_all](https://github.com/nico-bohlinger/one_policy_to_run_them_all) (MIT), con
  datos de [ros-naoqi/nao_robot](https://github.com/ros-naoqi/nao_robot) (BSD-3). La política de `checkpoints/` se
  entrenó con él.
- **Referencias:**
  - N. Bohlinger et al., *One Policy to Run Them All: an End-to-end Learning Approach to Multi-Embodiment
    Locomotion*, CoRL 2024;
  - B-Human, *Team Report and Code Release*, licencia en `assets/nao/bhuman/License.md`.
