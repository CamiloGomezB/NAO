# Cámara, pista y tres carriles: guía de uso

Esta guía explica cómo usar en este repo:
- la **pista de la carrera en MuJoCo**;
- la **cámara inferior del NAO** y la **visión de carril**;
- la **carrera de los tres carriles**: baseline 1 NAOqi, baseline 2 B-Human y nuestro RL.

**Origen.** Todo esto viene de [danielpaya/nao_linea](https://github.com/danielpaya/nao_linea) (autor: Daniel,
commit `f8e0cc6`, 2026-10-10). Se integró en `main` en el paso 40 del [`PLAN.md`](../PLAN.md). El diseño y
las decisiones están en [`plan_rl_carrera.md`](plan_rl_carrera.md).

---

## 1. Qué hay y dónde

| Ruta | Qué es |
|---|---|
| `carril/` | **Visión de carril.** Modelo de cámara, estimador (`lane_estimator.py` con numpy y `lane_estimator_puro.py` en Python puro para el NAO), filtro visión + odometría y controlador |
| `demo/build_scene.py` | Genera la **pista** (`assets/nao/scene_carril.xml`): carril de 5 m × 70 cm, líneas de 1.9 cm, carriles vecinos, salida y meta. También genera el **NAO con su cámara inferior** (`assets/nao/nao_cam.xml`): 39.7° hacia abajo, 54.7° × 42.5°, 320×240 |
| `config/pista.yaml` | **Colores** de piso, línea, salida y meta: el único lugar donde se definen |
| `config/pista_robot.json` | Colores, polaridad y modo de la visión para el NAO; lo genera `demo/build_scene.py` |
| `scripts/cambiar_colores.py` | Cambia los colores, regenera la pista y verifica la visión (procedimiento antes de la competencia) |
| `demo/run_demo.py` | **Entrada principal.** `--live` abre los 3 carriles con sus cámaras; `--live --solo-rl` abre solo el RL con el panel; `--video` graba un video |
| `demo/caminatas/vision_camara.py` | Visión con la cámara **renderizada** de cada robot (10 Hz), usada en la carrera de 3 carriles |
| `demo/caminatas/` | Caminatas de los **baselines** (`naoqi_like.py`, `bhuman_like.py`), simulador del carril (`simular.py`), **carrera de 3 carriles en vivo** (`carrera_vivo.py`), **benchmark** (`benchmark.py`) y video (`video_carrera.py`) |
| `robot/` | Kit para el **NAO real**: `diagnostico.py`, `race_nao.py` (visión a bordo, prueba en seco y medición), `replay.py` y la guía [`robot/LUNES.md`](../robot/LUNES.md) |
| `scripts/check_vision.py` | **Verificación de la visión** en la pista simulada: robot en 50 posiciones conocidas. No necesita PyTorch |
| `results/camara/`, `results/benchmark/` | Resultados de la visión y del benchmark |

---

## 2. Comandos

Todos se corren desde la raíz del repo.

### Ver la carrera: 3 carriles con sus cámaras (entrada principal)

```bash
uv run python demo/run_demo.py --live
```

**Qué se abre:**
- **El visor 3D de MuJoCo**, visto desde atrás de la salida, con la pista de 3 carriles. La salida y la meta
  están en los tres, y cada robot va en su carril:

  | Carril | Robot | Color |
  |---|---|---|
  | Izquierdo | **Baseline 2: tipo B-Human** | Verde |
  | Centro | **RL del equipo** | Azul |
  | Derecho | **Baseline 1: tipo NAOqi** | Naranja |

  Cada carril tiene una marca de su color en el piso, antes de la salida y después de la meta. Arriba a la
  derecha se ven el tiempo y la distancia o el resultado de cada uno.
- **La ventana "Lo que ve cada NAO"**, con la cámara inferior de cada robot, las líneas detectadas en
  celeste y la posición estimada por la visión (`d`, `psi`) frente a la real.

Cada robot corrige su rumbo con **su propia cámara renderizada** y la visión de `carril/`.

**Variantes:**

```bash
uv run python demo/run_demo.py --live --sin-vision                   # sin visión: se ve cómo se desvían
uv run python demo/run_demo.py --live --inicio-d 12 --inicio-psi -8  # los 3 colocados chuecos
uv run python demo/run_demo.py --live --piso gris_oscuro --linea blanco
uv run python -m demo.caminatas.carrera_vivo --mu 0.6                # otra fricción (y más opciones: --help)
uv run python -m demo.caminatas.carrera_vivo --vision simulada       # visión simulada con el modelo de error
```

### Solo el RL, con panel de controles

```bash
uv run python demo/run_demo.py --live --solo-rl
```

**Qué se abre:**
- el visor con el RL;
- la ventana "Lo que ve el NAO";
- un panel con la posición inicial, la visión sí o no, Correr y Detener, y los colores.

**Para mostrarlo:**
1. Pon corrido 15 y girado −10.
2. Desmarca la visión y presiona Correr: se sale.
3. Marca la visión y vuelve a correr: se centra y llega.

**Sin ventanas o en video:**

```bash
uv run python demo/run_demo.py --inicio-d 12 --inicio-psi 8                      # sin ventanas: imprime el resultado
uv run python demo/run_demo.py --video videos/demo_camara.mp4 --inicio-psi 8     # video comparativo (3-5 min)
```

### Otras herramientas de los carriles

```bash
uv run python -m demo.caminatas.simular --caminata bhuman --vivo     # una sola caminata
uv run python -m demo.caminatas.benchmark --rapido                   # benchmark corto (~1 min, visión simulada)
uv run python -m demo.caminatas.benchmark                            # completo: 3 caminatas x 5 fricciones x 5 salidas x con/sin visión
```

### Verificar la visión (sin PyTorch)

```bash
uv run python scripts/check_vision.py                     # colores actuales
uv run python scripts/check_vision.py --pose-noise 1.5    # con error de pose de la cámara
```

Termina con `RESULTADO: OK` si las 50 mediciones son válidas y el error medio es ≤ 3 cm y ≤ 3°.

### Cambiar los colores de la pista (antes de la competencia)

La organización avisa los colores definitivos de las líneas y del piso **poco antes del evento**. Están en
**un solo archivo**, [`config/pista.yaml`](../config/pista.yaml), y se cambian con un solo comando:

```bash
uv run python scripts/cambiar_colores.py --piso madera_oscura --linea blanco
```

**Qué hace:**
1. guarda los colores en `config/pista.yaml`, conservando los comentarios;
2. regenera la pista de MuJoCo (`assets/nao/scene_carril.xml`) y `config/pista_robot.json`, que es lo que lee
   la visión a bordo del NAO;
3. verifica la visión con la cámara renderizada en 50 posiciones conocidas, con 1.5° de error de pose;
4. guarda el resultado en [`results/camara/verificacion_vision.md`](../results/camara/verificacion_vision.md)
   y termina con `RESULTADO: OK` o `FALLA`.

**Si da OK, no hay que reentrenar:** la política de RL no ve colores, solo `d`, `psi` y válido. Después hay
que **copiar `config/pista_robot.json` al robot** (ver [`robot/LUNES.md`](../robot/LUNES.md)).

**Variantes:**

```bash
uv run python scripts/cambiar_colores.py                                        # verificar los colores actuales del archivo
uv run python scripts/cambiar_colores.py --piso gris --linea amarillo --probar  # probar SIN guardar nada
uv run python scripts/cambiar_colores.py --piso "#3a2a1a" --linea "#f5f5f5" --sin-veta
uv run python scripts/cambiar_colores.py --linea blanco --salida negro --meta rojo   # salida y meta por separado
uv run python scripts/cambiar_colores.py --matriz                               # todas las combinaciones (~30 s)
```

**Colores con nombre:**
- **Pisos:** `madera_clara`, `madera_oscura`, `duela_roja`, `gris`, `gris_oscuro`, `blanco`, `negro`, `verde`,
  `azul`.
- **Líneas:** `negro`, `blanco`, `amarillo`, `rojo`, `azul`, `verde`, `gris`.
- También acepta cualquier código `#rrggbb`.
- La franja de salida usa por defecto el mismo color que las líneas (`salida: null`).

**Cómo decide la visión** (`demo/build_scene.py`, función `describe`):

| Modo | Cuándo | Cómo detecta la línea |
|---|---|---|
| **brillo** | La línea pasa la prueba del detector por brillo: más oscura que el 62 % del piso (o más clara en la misma proporción) y al menos 45 niveles de diferencia | Escala de grises; busca la cinta más oscura o más clara que el fondo local. Es el modo validado por Daniel |
| **color** | El brillo no alcanza, pero el color sí distingue la línea (p. ej. verde o amarilla sobre madera) | Proyecta cada píxel sobre la dirección de color "línea − piso", así que la línea siempre queda más clara que el piso |

Si el contraste efectivo es menor que 30 de 255, la combinación queda **NO APTA**: en una pista real no se
vería, aunque en la simulación, que no tiene ruido, se detecte.

**Matriz de colores** ([`results/camara/matriz_colores.md`](../results/camara/matriz_colores.md)): de las 63
combinaciones con nombre, **57 dan OK**. Las que fallan son colores casi iguales:
- gris sobre gris y verde sobre verde;
- negro sobre negro y blanco sobre blanco, que salen NO APTO;
- tres casos al límite: gris sobre madera clara, rojo sobre gris y gris sobre blanco.

Si la organización elige una de esas combinaciones, hay que avisar y ajustar la visión con fotos reales en
la zona de calibraciones.

**Desde el panel de la demo** también se pueden probar colores (listas **Piso ▼** y **Línea ▼**, botón
**Aplicar colores**), o con `uv run python demo/run_demo.py --live --piso gris_oscuro --linea blanco`.
Esto no modifica `config/pista.yaml`.

### En el NAO real

Seguir [`robot/LUNES.md`](../robot/LUNES.md): diagnóstico, prueba en seco moviendo el robot a mano y
medición con cinta métrica.

---

## 3. Resultados heredados de nao_linea (a regenerar)

| Prueba | Resultado | Archivo |
|---|---|---|
| Precisión de la visión (imágenes sintéticas) | σ(d) = 1.6 cm y σ(psi) = 1.2° con 1.5° de error de pose; 4.8 cm con un robot vecino tapando | [`results/camara/modelo_error.md`](../results/camara/modelo_error.md) |
| Lazo cerrado RL + cámara renderizada | Solo RL llega en 3 de 18; RL + visión en 18 de 18 | [`results/camara/lazo_cerrado.md`](../results/camara/lazo_cerrado.md) |
| Benchmark de 3 carriles | Tipo B-Human 16.2–18.3 s, RL 24.2–24.3 s, tipo NAOqi 45–50 s en 5 m, con visión | [`results/benchmark/`](../results/benchmark/). **Ojo:** el `benchmark.md` guardado es la versión corta, de 12 corridas. La completa se regenera en el paso 51 |
| Verificación en este repo (2026-10-10) | 50 posiciones, 100 % válidas, error medio de 1.27 cm y 0.86° con 1.5° de error de pose | [`results/camara/verificacion_vision.md`](../results/camara/verificacion_vision.md) |

---

## 4. Limitaciones

- **Las caminatas de los baselines son réplicas del esquema** de NAOqi y de B-Human, no el código
  original:
  - la de **B-Human** usa los parámetros de la config de B-Human incluida en PenaltyStack: pasos de 250 ms,
    levantamiento del pie de 13 mm, 0.3 m/s;
  - el **WalkingEngine original** se mide en el simulador de PenaltyStack en el paso 50;
  - en el robot real se comparan las caminatas originales en el paso 73.
- **La demo corrige el rumbo del RL actual con un truco:** suma una señal falsa al giroscopio. La política
  nueva recibe `d` y `psi` como observación (Fase L).
- **Los robots de `carrera_vivo` no se tocan entre sí.** La escena con física compartida llega en el paso 48b.
