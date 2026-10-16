# Visión de carril: método, desarrollo y resultados

Capítulo para el paper sobre cómo el NAO **ve el carril con su propia cámara** para no salirse.

**Créditos:**
- **Método original:** Daniel, en [danielpaya/nao_linea](https://github.com/danielpaya/nao_linea) (9–10 de
  octubre de 2026). Su propuesta completa estaba en el documento `docs/fase_p_camara.md` de la rama
  `fase-p-camara-carril`. Esa rama no se usa, pero su contenido se resume aquí.
- **Integración en este repo**, cámara de cada robot en los 3 carriles, colores y verificación: pasos 40 y
  48, 10 de octubre.

Los errores de este capítulo están en el [registro](registro_errores.md): E24–E27 y E30–E37.

**Origen.** La cámara nació en **este repo**: el 9 de octubre Daniel abrió la rama `fase-p-camara-carril` sobre
nuestro commit `4ca136d`. Esa misma noche la separó en su propio repo, `nao_linea`, con copias idénticas de
nuestro `src/`, `checkpoints/` y `assets/`. El 10 de octubre agregó las caminatas de los baselines y la carrera
de 3 carriles, y ese mismo día se integró de vuelta en nuestro `main` (paso 40). Cronología verificada en
[`fuentes_y_repositorios.md`](fuentes_y_repositorios.md#4-nao_linea-la-visión-de-carril-que-salió-de-este-repo).

---

## 1. El problema: la IMU no ve el carril

La política de caminata mantiene el rumbo con la IMU, pero la IMU solo sabe **cuánto giró el robot desde
que arrancó**, no dónde están las líneas.

| Causa de desvío | ¿La ve la IMU? | ¿La ve la cámara? |
|---|---|---|
| Asimetría entre piernas que hace girar | Sí | Sí |
| Empujón de giro | Sí | Sí |
| **Robot colocado chueco en la salida** | **No:** ese rumbo pasa a ser el "recto" | **Sí** |
| **Robot colocado corrido del centro** | **No** | **Sí** |
| **Deslizamiento lateral del pie** | **No** | **Sí** |
| **Deriva del propio sensor de rumbo** | **No** | **Sí** |

**Cuánto importa, por geometría.** El operador coloca el robot a mano en la salida. En 5 m:
- un error de colocación de **3°** desvía **26 cm**, casi todo el margen del carril;
- un error de **5°** saca al robot del carril.

**Evidencia en simulación** (lazo cerrado con la cámara renderizada; política del sprint inicial sin
reentrenar; 9 colocaciones de ±10 cm y ±8° por 2 semillas):

| | Llegan a la meta | Desvío máximo (peor) | Tiempo medio en 5 m |
|---|---|---|---|
| Solo RL | **3 / 18** | Fuera del carril | 24.8 s |
| RL + visión | **18 / 18** | 14.5 cm | 24.2 s |

Incluso con la salida perfectamente centrada, sin cámara se salió en 1 de 2 corridas
([`results/camara/lazo_cerrado.md`](../../results/camara/lazo_cerrado.md)).

---

## 2. El método

**Entradas:**
- una imagen de la **cámara inferior** del NAO V6: QVGA (320×240), RGB, **10 FPS**, la misma suscripción
  que usa PenaltyStack;
- la **pose de la cámara**, que sale de la cinemática del propio robot (`ALMotion.getTransform` en el NAO
  real).

**Pasos:**
1. **Buscar la cinta.** En 1 de cada 3–4 filas se marcan los píxeles bastante más oscuros (o más claros) que
   el **fondo local**, una media móvil de 41 px. Comparar con el entorno hace que funcione con poca luz,
   con reflejos y con luz no uniforme (E34).
2. **Quedarse con lo que tiene el ancho de la cinta.** Como se sabe a qué distancia queda cada fila del
   piso, se sabe cuántos píxeles debe medir una cinta de 1.9 cm: ~10 px cerca, ~3 px lejos. Se descartan:
   - la veta de la madera, demasiado delgada;
   - la franja de salida y las sombras, demasiado anchas.
3. **Proyectar al piso.** El centro de cada tramo se proyecta al plano del suelo con la pose de la cámara,
   y resulta una nube de puntos en metros, sin perspectiva.
4. **Ajustar las rectas.**
   - RANSAC encuentra las rectas y se elige el par paralelo separado 72 cm que encierra al robot.
   - Si solo se ve una línea, se usa el ancho conocido del carril; con la cámara cerca del piso pasa en
     ~40 % de las fotos.
5. **La meta.** La franja de meta se detecta por color, con saturación y continuidad por fila (E35), y da
   su distancia a los pies.

**Salida**, que es justo lo que recibe la política (ver la sección 6.7 del
[diseño](../plan_rl_carrera.md)):

| Salida | Significado |
|---|---|
| `d` | Distancia al centro del carril, en metros. + = robot a la izquierda |
| `psi` | Ángulo respecto a las líneas, en radianes. + = girado a la izquierda |
| `válido` | Hubo medición en los últimos 300 ms |

**Implementaciones:**
- [`carril/lane_estimator.py`](../../carril/lane_estimator.py), con numpy: **2 ms** por imagen en PC;
- [`carril/lane_estimator_puro.py`](../../carril/lane_estimator_puro.py), en **Python puro** compatible con
  Python 2.7, para el NAO si no tiene numpy: **13 ms** por imagen en PC. Se estiman 40–110 ms en el Atom del
  NAO, dentro de los 100 ms entre fotos; está **por medir**.

Las dos dan la misma estimación, con una diferencia de 0.1 cm.

---

## 3. Precisión

Imágenes sintéticas, 150 por condición, con 1.5° de error en la pose de la cámara
([`results/camara/modelo_error.md`](../../results/camara/modelo_error.md)):

| Condición | σ de `d` | σ de `psi` | Mediciones malas |
|---|---|---|---|
| Normal | 1.6 cm | 1.2° | 0 % |
| Poca luz | 1.6 cm | 1.1° | 0 % |
| Reflejos en la duela | 1.7 cm | 1.3° | 0 % |
| Cinta gastada | 1.6 cm | 1.2° | 0 % |
| Robot vecino tapando una línea | 4.8 cm | 4.1° | 2 % |

**El error lo domina la pose de la cámara, no la detección:**

| Error de pose | 0° | 0.5° | 1° | 1.5° | 2° | 3° |
|---|---|---|---|---|---|---|
| σ de `d` | 0.5 cm | 0.7 cm | 1.1 cm | 1.6 cm | 2.0 cm | 3.0 cm |

Corregir la pose con el paralelismo de las líneas **no funcionó** (E36). Las mejoras con más impacto son:
1. sincronizar la imagen con la pose usando el sello de tiempo de la imagen;
2. corregir el roll y el pitch de la cámara con la IMU.

**Verificación en este repo** (`scripts/check_vision.py`, 2026-10-10): 50 posiciones conocidas con la cámara
renderizada en MuJoCo, 100 % de mediciones válidas.

| Error de pose | Error medio de `d` | Error medio de `psi` |
|---|---|---|
| Ninguno | 0.19 cm | 0.03° |
| 1.5° | 1.27 cm | 0.86° |

---

## 4. Colores de la pista

La organización avisa **poco antes del evento** los colores de las líneas y del piso. La solución (paso 48):

- **Un solo archivo,** [`config/pista.yaml`](../../config/pista.yaml). El comando
  `scripts/cambiar_colores.py` lo cambia, regenera la escena y verifica la visión en menos de 1 minuto. El
  NAO recibe los colores en `config/pista_robot.json`.
- **La política de RL no ve colores:** solo `d`, `psi` y válido. Cambiar colores no obliga a reentrenar.
- **Dos modos de visión:**
  - **brillo**, si la línea es más oscura o más clara que el piso;
  - **color**, si el brillo es parecido pero el color no. En ese caso cada píxel se proyecta sobre la
    dirección de color "línea − piso" (E24, E25).
- **Matriz de 63 combinaciones** de piso × línea
  ([`results/camara/matriz_colores.md`](../../results/camara/matriz_colores.md)): de **30 OK** solo con
  brillo a **57 OK** con los dos modos.
  - Fallan colores casi iguales, como gris sobre gris o verde sobre verde, y combinaciones **NO APTAS**
    (contraste < 30), como negro sobre negro (E26).
  - Gris sobre blanco falla porque la cámara simulada no tiene autoexposición (E27).

---

## 5. Tres carriles: cada robot con su cámara

En la demo principal (`uv run python demo/run_demo.py --live`), los tres robots corren a la vez:
- B-Human, verde (baseline 2);
- RL, azul;
- NAOqi, naranja (baseline 1).

Cada uno se corrige con **su propia cámara renderizada**
([`demo/caminatas/vision_camara.py`](../../demo/caminatas/vision_camara.py)), con la ley de giro
w = −(1.2·psi + 2.0·d). La ventana "Lo que ve cada NAO" muestra las tres cámaras con las líneas detectadas.

**Resultado** (colocados a +10 cm y −6°, μ = 1.0):

| Caminata | Con su cámara | Sin visión |
|---|---|---|
| RL (sprint inicial) | META en 24.6 s | META en 24.8 s |
| Baseline 2: tipo B-Human | META en 16.2 s | Se sale a los 9.0 s |
| Baseline 1: tipo NAOqi | META en 49.8 s | META en 49.9 s |

**Benchmark corto** (visión simulada con el error medido, μ = 0.6 y 1.0): sin visión se salen tipo B-Human
con μ = 0.6 y tipo NAOqi con μ = 1.0. **Con visión llegan todas.**

---

## 6. Cómo entra la cámara al RL

**Hoy**, con la política del sprint inicial, la corrección entra por un **truco**: se suma una señal falsa al
giroscopio de la política, y con señales grandes se invierte (E37).

**Con la política nueva:**
- `d`, `psi` y válido **son parte de la observación** (contrato v1, 54 valores);
- en el entrenamiento, la cámara se **simula** sin renderizar: valor real + ruido gaussiano (σ = 1.6 cm y
  1.2°, hasta 3 veces más) + retardo + pérdidas, a 10 Hz;
- en la demo y en la selección de agentes se usa la cámara renderizada (paso 58b);
- en el NAO real:
  - `robot/race_nao.py` en el carril NAOqi;
  - **desde el 2026-10-15, dentro de `bhuman`** en los carriles RL y B-Human: el módulo `CopaLanePerceptor` corre
    el mismo estimador portado a C++ (`bhuman/Src/Tools/CopaRace/CopaRace.h`) sobre la cámara inferior a 10 FPS, con
    los intrínsecos calibrados de B-Human y la pose real de la cámara. La paridad con el código Python es exacta
    (10⁻¹²) en 16 imágenes sintéticas que cubren los tres modos: oscura, clara y color
    ([`docs/despliegue/02_PLAN_E_IMPLEMENTACION.md`](../despliegue/02_PLAN_E_IMPLEMENTACION.md), sección 3.2);
- **la señal es la misma en los tres lugares** (sección 6.7 del diseño).

---

## 7. Limitaciones y pendientes

- **Todo está medido en simulación.** Falta medir la precisión en una pista réplica con el robot y una cinta
  métrica (paso 70, guía en [`robot/LUNES.md`](../../robot/LUNES.md)).
- El tiempo de la visión a bordo y su compatibilidad real con Python 2.7 están por verificar (paso 69). En
  `bhuman` la visión es C++; falta medir su tiempo en el robot (paso 68d).
- Los colores llegan al robot desde `config/pista_robot.json` en el despliegue: polaridad y, en modo color, el
  `color_ref` (E64).
- Con un robot vecino tapando una línea, el error sube a σ(`d`) = 4.8 cm.
- Las caminatas de los baselines en simulación son réplicas del esquema de NAOqi y de B-Human, no el código
  original.
