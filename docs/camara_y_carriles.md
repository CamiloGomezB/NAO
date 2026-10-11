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
| `demo/pista.yaml` | **Colores** de piso, línea y meta |
| `demo/run_demo.py` | Demo con la política de RL y la cámara: interactiva (`--live`) o en video (`--video`) |
| `demo/caminatas/` | Caminatas de los **baselines** (`naoqi_like.py`, `bhuman_like.py`), simulador del carril (`simular.py`), **carrera de 3 carriles en vivo** (`carrera_vivo.py`), **benchmark** (`benchmark.py`) y video (`video_carrera.py`) |
| `robot/` | Kit para el **NAO real**: `diagnostico.py`, `race_nao.py` (visión a bordo, prueba en seco y medición), `replay.py` y la guía [`robot/LUNES.md`](../robot/LUNES.md) |
| `scripts/check_vision.py` | **Verificación de la visión** en la pista simulada: robot en 50 posiciones conocidas. No necesita PyTorch |
| `results/camara/`, `results/benchmark/` | Resultados de la visión y del benchmark |

---

## 2. Comandos

Todos se corren desde la raíz del repo.

### Ver la cámara funcionando con el RL actual

```bash
uv run python demo/run_demo.py --live
```

**Qué se abre:**
- el visor 3D;
- la ventana **"Lo que ve el NAO"**, con las líneas detectadas en celeste;
- un panel con la posición inicial, la visión sí o no, los botones Correr y Detener, y los colores.

**Para mostrarlo:**
1. Pon corrido 15 y girado −10.
2. Desmarca la visión y presiona Correr: se sale del carril.
3. Marca la visión y vuelve a correr: mide dónde quedó, se centra y llega.

**Otras variantes:**

```bash
uv run python demo/run_demo.py --live --inicio-d 12 --inicio-psi 8 --sin-camara   # sin la ventana de la cámara
uv run python demo/run_demo.py --video videos/demo_camara.mp4 --inicio-psi 8     # video comparativo (3-5 min)
uv run python demo/run_demo.py --inicio-d 12 --inicio-psi 8                      # sin ventanas: imprime el resultado
```

### Los tres carriles

```bash
uv run python -m demo.caminatas.carrera_vivo                         # los 3 NAOs a la vez en el visor, con visión
uv run python -m demo.caminatas.carrera_vivo --sin-vision --mu 0.6   # sin visión y piso resbaloso
uv run python -m demo.caminatas.simular --caminata bhuman --vivo     # una sola caminata
uv run python -m demo.caminatas.benchmark --rapido                   # benchmark corto (~1 min)
uv run python -m demo.caminatas.benchmark                            # completo: 3 caminatas x 5 fricciones x 5 salidas x con/sin visión
```

En `carrera_vivo`, el carril izquierdo es B-Human (baseline 2), el central el RL y el derecho NAOqi
(baseline 1). Cada robot va en su propia física: todavía no pueden chocar entre sí (paso 48).

### Verificar la visión (sin PyTorch)

```bash
uv run python scripts/check_vision.py                     # colores actuales
uv run python scripts/check_vision.py --pose-noise 1.5    # con error de pose de la cámara
```

Termina con `RESULTADO: OK` si las 50 mediciones son válidas y el error medio es ≤ 3 cm y ≤ 3°.

### Cambiar los colores de la pista

**Desde el panel de la demo:** listas **Piso ▼** y **Línea ▼**, y el botón **Aplicar colores**.

**Desde la terminal:**

```bash
uv run python demo/run_demo.py --live --piso gris_oscuro --linea blanco
```

**Permanente:** editar [`demo/pista.yaml`](../demo/pista.yaml). Desde el paso 48 se centraliza en un solo
archivo para todo el repo.

**Colores con nombre:**
- **Pisos:** `madera_clara`, `madera_oscura`, `duela_roja`, `gris`, `gris_oscuro`, `blanco`, `negro`, `verde`,
  `azul`.
- **Líneas:** `negro`, `blanco`, `amarillo`, `rojo`, `azul`, `verde`, `gris`.
- También acepta cualquier código `#rrggbb`.

La visión decide sola si la línea es más oscura o más clara que el piso.

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
- **Los robots de `carrera_vivo` no se tocan entre sí.** La escena con física compartida llega en el paso 48.
