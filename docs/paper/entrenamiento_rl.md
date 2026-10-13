# Capítulo: el entrenamiento por RL de la caminata de carrera

Regla del capítulo: **mejor que sobre documentación a que falte.** Aquí está todo lo necesario para explicar y
reproducir el entrenamiento: qué ve la política, qué hace, qué se premia y castiga (con fórmulas y pesos), qué se
sortea, con qué algoritmo y parámetros, cómo evolucionó, cómo se probó, cómo se eligió y qué salió mal.

Cada número tiene su archivo de origen entre corchetes o en la columna "Fuente".

**Generaciones documentadas:**

| Generación | Fecha | Pasos | Parte de | Política guardada |
|---|---|---|---|---|
| `carrera_v01` | 2026-10-11, 00:26–02:00 | 15.3M | cero | [`policies/carrera_v01/`](../../policies/carrera_v01/) (checkpoint de 15M) |
| `carrera_v02` | 2026-10-11, 02:05–05:53 | 40M | `v01` a 15M | [`policies/carrera_v02/`](../../policies/carrera_v02/) (checkpoint de 15M) |
| `carrera_v03` | 2026-10-11, 12:40–14:18 | 20M | `v02` a 15M, con el paso 58c | [`policies/rl_v1.0/`](../../policies/rl_v1.0/) (checkpoint de 5M; antes `policies/carrera_v03/`) |

Antes de esto, la política del sprint (`checkpoints/best_model.zip`, entorno `NaoWalk-v0`, modelo aproximado V5)
caminaba a 0.20 m/s sin cámara. Se describe en la bitácora (etapa 1) y no se repite aquí.

---

## 1. Resumen en una página

- **Problema:** caminar 5 m por un carril de 70 cm, lo más rápido posible, sin caerse ni salirse, con un NAO V6. La
  política solo puede usar sensores del NAO y la cámara inferior, que entrega `d` (corrimiento lateral) y `psi`
  (ángulo respecto a las líneas).
- **Método:** PPO (Stable-Baselines3) en MuJoCo, con el entorno `NaoRace-v0`.
  - Observación de 54 valores y acción de 13 ángulos cada 24 ms.
  - Cámara simulada con ruido, retardo y pérdidas.
  - Fricción aleatoria y perturbaciones.
  - Recompensa de 17 términos.
  - 16 entornos en paralelo en una laptop Ryzen 7 5800H, solo CPU, ~2,700–2,900 pasos/s.
- **Resultado (simulación):**
  - con visión, 100/100 carreras sin faltas en **13.0–13.2 s** (`vx_cmd` 0.40) o ~10.5 s (`vx_cmd` 0.5);
  - B-Human, en la misma batería: 16.2–18.3 s;
  - `carrera_v02`, además, llega sin visión en 89/100 y nunca se cae;
  - funciona igual con la cámara renderizada y la visión real del pipeline: 36/36.
- **Lo que hay que saber explicar:**
  - la velocidad, el ritmo de pasos y el rumbo explican casi toda la recompensa;
  - se aprendió en ~5M pasos (~30 min);
  - entrenar más no siempre mejora (E48);
  - la política usa varias acciones en su límite (brazos fijos, caderas hacia adentro; E49).

---

## 2. Qué ve la política: observación de 54 valores

Definida en [`src/race/contract.py`](../../src/race/contract.py) (contrato v1, compatible con Python 2.7 para el NAO).
La calcula `NaoRaceEnv._obs`; la prueba `scripts/check_race_env.py` comprueba que es **idéntica** (diferencia 0.0)
a `contract.armar_observacion`, que es lo que usará el robot.

| # | Variable | Dim. | Escala | De qué sensor del NAO sale | En simulación |
|---|---|---|---|---|---|
| 0–2 | Gravedad proyectada | 3 | — | IMU (orientación del torso) | Rotación del torso; sin ruido |
| 3–5 | Giroscopio | 3 | ×0.25 | IMU | Sensor `gyro` + ruido σ 0.02 rad/s (con perturbaciones) |
| 6 | Error de rumbo de la IMU | 1 | rad, recortado a ±π/2 | `AngleZ` | Rumbo objetivo (el de la IMU al arrancar) − rumbo de la IMU. La IMU deriva 0.003 rad/√s y tiene ruido σ 0.005 rad |
| 7 | `d` de la cámara | 1 | m, + = robot a la izquierda | Visión de carril | Cámara simulada (sección 5) |
| 8 | `psi` de la cámara | 1 | rad, + = girado a la izquierda | Visión de carril | Cámara simulada |
| 9 | Válido | 1 | 0/1 | Visión de carril | 1 si hubo medición en los últimos 300 ms |
| 10–22 | Ángulos de las 13 articulaciones − pose de pie | 13 | rad | Encoders | qpos − calibración + ruido σ 0.002 rad |
| 23–35 | Velocidades articulares | 13 | ×0.05 | Encoders | qvel |
| 36–48 | Acción anterior | 13 | [−1, 1] | (memoria de la política) | — |
| 49–50 | Carga de cada pie | 2 | kg / 5.36, recortado a [0, 2] | 8 FSR | Fuerza normal pie-suelo / g |
| 51–52 | Reloj de marcha | 2 | sen, cos | (reloj interno) | Período 0.5 s; empieza en 0 al arrancar |
| 53 | `vx_cmd` | 1 | m/s | (comando) | Sorteado (sección 4) |

**No usa:** velocidad lineal, posición global ni nada que el NAO no mida (regla de compatibilidad con PenaltyStack).

**Normalización (`VecNormalize`):** cada observación se centra y escala con media y desviación móviles, y se recorta
a ±10. Valores de las políticas guardadas [`results/carrera/analisis_politicas.json`]:

| Variable | `v01`: media / desv. | `v02`: media / desv. | Comentario |
|---|---|---|---|
| Error de rumbo de la IMU | −0.011 / 0.126 | −0.006 / 0.095 | — |
| `d` | 0.008 / 0.091 | −0.003 / 0.094 | — |
| `psi` | 0.010 / 0.134 | 0.004 / 0.103 | — |
| **Válido** | **0.982 / 0.131** | **0.890 / 0.312** | En `v01`, `válido = 0` se normaliza a **−7.5**: fuera de distribución, causa de E45. En `v02`, a −2.9 |
| `vx_cmd` | 0.322 / 0.101 | 0.323 / 0.100 | — |

---

## 3. Qué hace la política: acción de 13 ángulos cada 24 ms

Cada 24 ms (2 ciclos de 12 ms de PenaltyStack; `FRAME_SKIP` = 12 pasos de física de 2 ms), la política entrega 13
números en [−1, 1]. `contract.accion_a_objetivos` los convierte en ángulos objetivo para los servos PD:
- objetivo = pose de pie + acción × límite (el límite superior si la acción es positiva, el inferior si es negativa);
- lo demás (cabeza, codos, muñecas) se queda en la pose de pie;
- `RHipYawPitch` copia a `LHipYawPitch`, porque en el NAO las mueve un solo motor.

| Articulación | Límite [rad] (−1 / +1) | Nota |
|---|---|---|
| LHipYawPitch | −0.10 / +0.10 | Gira las dos caderas |
| LHipRoll | −0.07 (adentro) / +0.25 (afuera) | **Asimétrico**: solo hay 3 cm entre las piernas del V6 |
| RHipRoll | −0.25 (afuera) / +0.07 (adentro) | Ídem |
| L/R HipPitch | ±0.5 | — |
| L/R KneePitch | ±0.5 | — |
| L/R AnklePitch | ±0.4 | — |
| L/R AnkleRoll | ±0.25 | — |
| L/R ShoulderPitch | ±0.5 | Brazos |

**Presupuesto lateral (paso 46):** si la suma de lo que van hacia adentro las caderas, los tobillos y HipYawPitch
supera 0.09 rad equivalentes de cadera, esas componentes se escalan juntas. Con esto, 0 cruces de piernas en 20,000
acciones al azar.

**Pose de pie (`home`):** cadera −0.4, rodilla 0.8, tobillo −0.4 y hombros 1.57 rad. El torso queda a 0.316 m.

---

## 4. El episodio

| Elemento | Valor | Archivo |
|---|---|---|
| Pista | Carril centrado en y = 0, de ±0.35 m interiores; salida en x = 0, meta en x = 5 m | `nao_race_env.py` |
| Colocación inicial | y ~ N(0, 2 cm) recortada a ±10 cm; rumbo ~ N(0, 2°) recortado a ±8°; ángulos de pie con ruido U(±0.01 rad) | ídem |
| De pie antes de arrancar | 0.5 s en la pose de pie (21 pasos), dentro de `reset`: la cámara toma sus primeras fotos | ídem |
| Duración | Hasta 30 s de marcha (1250 pasos); **sigue después de la meta**, para que no aprenda a frenar | `src/envs/__init__.py` |
| `vx_cmd` | U(0.15, 0.50) m/s por episodio; en el 30 % de los episodios cambia una vez, entre 3 y 20 s | config |
| Fricción | μ ~ U(0.4, 1.2) por episodio; cada pie ±0.05 (asimetría de 0.1): por pie entre 0.35 y 1.25 | config |
| Termina por | Salida de carril, caída (torso < 0.24 m, inclinación > 40° o algo que no es el pie toca el suelo) o inestabilidad numérica | `falta()` |

**Perturbaciones** (`perturbaciones: true` en las dos generaciones), sorteadas por episodio:

| Perturbación | Valor |
|---|---|
| Ganancia de los servos | kp de cada pierna × U(0.85, 1.15) |
| Calibración | U(±1.5°) por articulación: el servo va a objetivo + error, y el sensor reporta sin el error |
| Centro de masa del torso | ±1 cm en x e y |
| Suelo inclinado | ±1° en x e y (se inclina la gravedad) |
| Empujones | Cada 2–6 s, durante 50–150 ms: hasta ±6 N en x e y y ±0.4 N·m de giro |
| IMU | Deriva del rumbo de 0.003 rad/√s; ruido de 0.005 rad |
| Sensores | Giroscopio σ 0.02 rad/s; ángulos σ 0.002 rad |
| Apagones de visión | Ver sección 5 |

---

## 5. La cámara en el entrenamiento

No se renderizan imágenes (sería ~100 veces más lento). Se simula **la salida** de la visión, con la convención de la
sección 6.7 del diseño:
- una foto cada 100 ms, con fase aleatoria;
- cada foto mide la `d` y la `psi` **reales** de hace un retardo, más ruido gaussiano;
- puede perderse (no se actualiza, y `válido` cae a 0 a los 300 ms) o salir mala (con un error extra).

| Parámetro (por episodio) | `carrera_v01` | `carrera_v02` |
|---|---|---|
| σ de `d` | U(1, 5) cm | U(1, 5) cm |
| σ de `psi` | U(1, 4)° | U(1, 4)° |
| Retardo | U(50, 250) ms | U(50, 250) ms |
| Fotos perdidas | U(0, 30) % | U(0, 30) % |
| Mediciones malas | U(0, 8) %, hasta ±15 cm | ídem |
| Apagón (tramo sin visión) | 30 % de los episodios, de 0.5–2 s, empezando entre 0.5 y 20 s | **60 %, de 1–8 s, empezando entre 0 y 20 s** |
| **Episodios enteros sin cámara** | **0 %** | **15 %** |

**Validación de la cámara simulada:** `scripts/check_camara_sim.py` comparó con la cámara renderizada y la visión de
`carril/` en 25 poses de la pista. Mismo signo; error real rms de 1.05 cm y 0.72°, menor que el simulado. El
entrenamiento es conservador [`results/camara/camara_sim_vs_render.json`].

---

## 6. La recompensa: 17 términos

Fuente: [`configs/carrera/pesos.yaml`](../../configs/carrera/pesos.yaml) (un solo archivo con pesos y rangos del
barrido); cálculo en `NaoRaceEnv.terminos_recompensa`. **Las dos generaciones usaron los pesos iniciales sin
cambios.**

Cada término se calcula por paso de 24 ms con valores **reales** del simulador (no los de la cámara) y se multiplica
por su peso. El aporte medio por paso se midió en TensorBoard [`results/carrera/carrera_v0N/curvas_entrenamiento.csv`].

| Término | Fórmula (por paso) | Peso | Aporte medio por paso al final de `v01` (13–15.3M) | Al final de `v02` (35–40M) |
|---|---|---|---|---|
| **seguimiento_vx** | exp(−((vx − vx_cmd)/0.1)²); vx = velocidad del torso hacia la meta | +1.0 | **+0.793** | +0.781 |
| **patron_marcha** | Fracción de pies (0, ½, 1) cuyo contacto coincide con el reloj (período 0.5 s, 60 % de apoyo por pie) | +0.5 | **+0.460** | +0.458 |
| **rumbo** | exp(−(psi/0.1)²), psi real del torso | +0.5 | **+0.446** | +0.373 |
| vivo | 1 | +0.1 | +0.100 | +0.100 |
| meta | 1 una vez, cuando la punta de un pie llega a x ≥ 5 m | +20 | +0.015 | +0.015 |
| vel_giro | ωz² (giro del torso en el mundo) | −0.5 | −0.047 | −0.049 |
| barrera_margen | Σ por pie ((0.10 − margen)/0.10)² si el margen a la línea es < 10 cm | −5 | −0.045 | **−0.222** |
| torque | Σ τ² de los 13 servos | −0.001 | −0.035 | −0.036 |
| vel_lateral | vy² | −10 | −0.032 | −0.049 |
| centrado | d² | −2 | −0.014 | −0.028 |
| cambio_accion | ‖aₜ − aₜ₋₁‖² | −0.02 | −0.014 | −0.013 |
| caida | 1 al caer (termina) | −100 | −0.014 | −0.005 |
| inclinacion | gx² + gy² | −2 | −0.008 | −0.014 |
| choque_piernas | 1 si una pierna toca la otra | −1 | −0.007 | −0.017 |
| salida_carril | 1 si una esquina de un pie pasa la línea (termina) | −200 | −0.005 | −0.035 |
| altura | (z − 0.316)² | −50 | −0.002 | −0.003 |
| choque_robot | Siempre 0 en el entrenamiento (sin robots vecinos; se mide en la selección) | −400 | 0 | 0 |

**Cómo leer la tabla:**
- Los tres primeros términos, más `vivo`, son ~95 % de la recompensa positiva.
- Los castigos de la política final son pequeños **porque la política ya los evita**, no porque no importen.
  Al principio dominaban: en los primeros 0.5M pasos, `vel_giro` aportaba −0.77 por paso y `caida` −1.17 por paso
  (99.6 % de episodios con falta).
- `caida` y `salida_carril` se cobran una vez y terminan el episodio. Además cuestan toda la recompensa futura
  (~1.85 por paso), así que pesan más de lo que muestra su aporte medio.
- Que haya aporte (por ejemplo, `vivo` o `patron_marcha` de pie) no prueba que el peso sea necesario. No se hizo un
  estudio de ablación (sección 12).

**Limitación conocida (E47):** con −200, salirse justo antes de la meta (a 4.8–4.9 m) da más retorno que caminar
lento todo el episodio. Haría falta que `salida_carril` < −271. Con descuento 0.99, salirse después de ~4 s "vale
más" que ir lento. Lo cubre el filtro duro de la selección; se corrige en el paso 55b
[`results/carrera/orden_recompensa.json`, `scripts/check_recompensa_carrera.py`].

---

## 7. El algoritmo y los parámetros

| Elemento | Valor | Nota |
|---|---|---|
| Algoritmo | PPO, Stable-Baselines3 2.9.0, `MlpPolicy` | — |
| Red | Actor y crítico **separados**, 2 capas de 256, activación ELU | ~163k parámetros: actor 83,213, crítico 80,129 y 13 de `log_std` |
| Distribución de la acción | Gaussiana diagonal, `log_std_init` = −1 (σ = 0.37) | σ medio: 0.37 → 0.096 al final de `v01`; ~0.10 en `v02` |
| Entornos | 16 en paralelo (`SubprocVecEnv`) | — |
| `n_steps` | 512 por entorno | 8,192 pasos por actualización |
| `batch_size` | 2048 | — |
| `n_epochs` | 5 | — |
| `learning_rate` | 3e-4, **constante** | Posible causa de E48 |
| `gamma` / `gae_lambda` | 0.99 / 0.95 | Horizonte efectivo de ~100 pasos (2.4 s) |
| `clip_range` | 0.2 | — |
| `ent_coef` / `vf_coef` / `max_grad_norm` | 0.0 / 0.5 / 1.0 | — |
| Normalización | Observaciones y recompensa (`VecNormalize`), recorte de 10 | — |
| Semilla | `v01`: 0; `v02`: 2 | — |
| Hilos de torch | 4 | Del sprint: con 8, 35 % más lento |
| Checkpoints | Cada 5M pasos, con su normalización | — |
| Evaluación interna | Cada 1M pasos, 5 episodios deterministas | Solo para `best_model`; **no se usó para elegir** (E48) |

**Máquina y versiones** [`runs/<run>/metadata.yaml`]: laptop Ryzen 7 5800H, Windows 11 (10.0.26300), Python 3.12.10,
MuJoCo 3.14.0, Gymnasium 1.3.0, Stable-Baselines3 2.9.0, torch 2.14.0+cpu.

**Velocidad:**
- `v01`: 2,710 pasos/s de media, 15.29M pasos en 1.57 h.
- `v02`: 2,918 pasos/s de media, 40.0M pasos en 3.81 h.
- El entorno tarda 0.61 ms por paso (la física sola, 0.34 ms).

**Versión del código.** Los dos runs registran `git_commit: ea5e992-modificado`: el código del entorno no estaba
confirmado al entrenar. Lo que cambió entre los dos lanzamientos (bitácora del 2026-10-11):
- `v01` se lanzó con `NaoRaceEnv` ya optimizado (`_medir`, tabla de búsqueda) y con `pesos.yaml` en formato plano
  (mismos valores).
- Antes de `v02` se agregaron:
  - `options` en `reset` (colocación y `vx_cmd` fijos, solo para evaluar);
  - `escena` (solo para la demo);
  - `sin_vision_prob` y `camara.apagon_inicio_s` (el cambio de `v02`; por defecto dejan a `v01` igual);
  - las secciones `pesos` y `rangos` en el YAML.
- `check_race_env.py` dio OK con las dos versiones. La primera versión confirmada del código será la del commit que
  haga el usuario con estos cambios.

---

## 8. Cómo aprendió: etapas de `carrera_v01` (desde cero)

Medias por tramo de las curvas de TensorBoard [`results/carrera/carrera_v01/curvas_entrenamiento.csv` y `.png`].
"Con falta" cuenta caídas **y** salidas.

| Tramo | Episodio medio | Retorno medio | Con falta | Salidas | Metas | seguim. vx | rumbo | vel_giro | σ acción |
|---|---|---|---|---|---|---|---|---|---|
| 0–0.5M | 3.2 s | −176 | 99.6 % | 5 % | 0 % | 0.09 | 0.13 | −0.77 | 0.34 |
| 0.5–1M | 19.2 s | −289 | 59 % | 19 % | 0 % | 0.09 | 0.12 | −0.46 | 0.30 |
| 1–2M | 27.7 s | +340 | 15 % | 17 % | 0 % | 0.14 | 0.36 | −0.32 | 0.27 |
| 2–3M | 28.6 s | +826 | 11 % | 14 % | 57 % | 0.28 | 0.42 | −0.22 | 0.22 |
| 3–5M | 29.3 s | +1,415 | 5 % | 15 % | 96 % | 0.55 | 0.43 | −0.14 | 0.17 |
| 5–7M | 29.3 s | +1,846 | 4 % | 16 % | 95 % | 0.73 | 0.45 | −0.07 | 0.13 |
| 7–9M | 29.4 s | +1,944 | 5 % | 17 % | 95 % | 0.78 | 0.45 | −0.05 | 0.11 |
| **9–10M** | 26.1 s | +1,695 | 24 % | 23 % | 82 % | 0.79 | 0.45 | −0.05 | 0.10 |
| **10–11M** | 25.2 s | +1,299 | 29 % | 29 % | 80 % | 0.76 | 0.40 | −0.06 | 0.10 |
| 11–13M | 26.5 s | +1,556 | 23 % | 21 % | 84 % | 0.75 | 0.41 | −0.06 | 0.10 |
| 13–15.3M | 27.0 s | +1,781 | 18 % | 16 % | 86 % | 0.79 | 0.45 | −0.05 | 0.10 |

**Fases:**
1. **0–1M, aprender a no caerse.** El castigo por caída y el giro dominan. A 1M pasos la política se queda de pie
   casi 30 s, pero no camina: `seguimiento_vx` está en 0.09, porque de pie solo cobra algo cuando `vx_cmd` es bajo.
2. **1–3M, aprender a caminar recto.** Primero sube `rumbo` (0.12 → 0.42), después `seguimiento_vx`. Las primeras
   metas aparecen a los ~2.5M.
3. **3–9M, aprender velocidad.** `seguimiento_vx` 0.55 → 0.78; 95 % de metas. El checkpoint de 5M ya llega en 9.6 s
   con visión.
4. **9–11M, retroceso.** Las salidas suben al 29 % y el retorno cae a ~1,300. Coincide con que el checkpoint de 10M
   se desvía 17–21 cm en la evaluación.
5. **11–15M, recuperación.** El checkpoint de 15M es el más recto: desvío máximo de 3.4–5.6 cm.

En el entrenamiento, el episodio sigue 30 s (~15 m a 0.5 m/s), así que muchas "salidas" ocurren después de los 5 m.
Por eso las tasas de salida del entrenamiento son mayores que las de la batería, que para en la meta.

## 9. Etapas de `carrera_v02` (continúa de `v01` a 15M, con más pérdida de visión)

[`results/carrera/carrera_v02/curvas_entrenamiento.csv` y `.png`]

| Tramo | Episodio medio | Retorno | Con falta | Salidas | Metas | seguim. vx | rumbo | barrera | Válido (media) |
|---|---|---|---|---|---|---|---|---|---|
| 0–2M | 26.1 s | 1,500 | 25 % | 18 % | 73 % | 0.67 | 0.41 | −0.06 | — |
| 2–5M | 26.6 s | 1,506 | 24 % | 26 % | 83 % | 0.74 | 0.41 | −0.13 | — |
| 5–10M | 28.0 s | 1,803 | 15 % | 22 % | 91 % | 0.80 | 0.44 | −0.09 | — |
| 10–15M | 26.5 s | 1,550 | 27 % | 29 % | 85 % | 0.79 | 0.43 | −0.18 | — |
| 15–20M | 27.5 s | 1,739 | 19 % | 24 % | 90 % | 0.81 | 0.43 | −0.12 | — |
| 20–25M | 27.5 s | 1,691 | 19 % | 24 % | 89 % | 0.80 | 0.44 | −0.14 | — |
| 25–30M | 25.8 s | 1,381 | 31 % | 30 % | 82 % | 0.77 | 0.43 | −0.21 | — |
| 30–35M | 27.1 s | 1,566 | 23 % | 26 % | 88 % | 0.80 | 0.43 | −0.16 | — |
| 35–40M | 26.3 s | 1,372 | 29 % | 31 % | 84 % | 0.78 | 0.37 | −0.22 | 0.890 al final |

Al principio la política de `v01` pierde ~10 % de metas, porque ahora hay episodios sin cámara. A los 5M ya se
recuperó. **Después de ~20M no mejora:** oscila, y la barrera de margen y las salidas crecen (E48).

---

## 10. Cómo se probó: baterías y resultados

**Herramienta:** [`scripts/eval_carrera.py`](../../scripts/eval_carrera.py).
- Usa la misma colocación por semilla (`benchmark.inicio`), la misma meta (centro de la suela en x ≥ 5 m) y las
  mismas métricas que el benchmark de 3 carriles.
- `benchmark.py --rl-carrera` usa la misma función; el paso 52 comprobó que dan números idénticos.
- La política es determinista. `vx_cmd` es fijo y sin cambios durante la corrida.

**Baterías:**

| Batería | Fricciones | Semillas | Visión | Perturbaciones | Para qué |
|---|---|---|---|---|---|
| Nominal | 0.4, 0.6, 0.8, 1.0, 1.2 | 2 | sí y no | no | Cada checkpoint |
| Perturbada | ídem | 4 | sí y no | sí | Cada checkpoint, con `vx_cmd` 0.5 y 0.40 |
| Grande (selección / rectitud, paso 58) | ídem | 20 | sí y no | sí | 100 episodios por condición |
| Cámara renderizada (paso 58b) | 0.4, 0.8, 1.2 | 3 | cámara real / sin cámara | no | Lazo cerrado con la visión de `carril/` |

**Todos los resultados:** [`results/carrera/resumen.md`](../../results/carrera/resumen.md) (`scripts/resumen_carrera.py`).
Los principales:

| Política | Batería | Con visión | Sin visión |
|---|---|---|---|
| `v01` 5M | Nominal 0.5 | 10/10, 9.6 s | 0/10 (10 caídas) |
| `v01` 5M | Perturbada 0.5 / 0.40 / 0.30 | 16/20 (4 caídas) / **20/20, 12.35 s** / 20/20, 16.8 s | — |
| `v01` 10M | Perturbada 0.5 | 9/20 (1 caída, 10 salidas) | — |
| **`v01` 15M** | Perturbada 0.5 / 0.40 | **20/20, 11.15 s** / 20/20, 13.6 s | — |
| **`v01` 15M** | **Grande 0.40** | **100/100, 13.2 ± 0.7 s, desvío ~8 cm** | 0/100 (45 caídas, 47 salidas) |
| `v01` 15M | Cámara renderizada 0.40 / 0.5 | 9/9 12.7 s / 9/9 10.3–10.5 s | — |
| `v02` 5M | Perturbada 0.5 | 20/20, 10.25 s | 9/20, **0 caídas** |
| **`v02` 15M** | Perturbada 0.5 / 0.40 | **20/20, 10.85 s** / 20/20, 13.1 s | 10/20 / 14/20 |
| **`v02` 15M** | **Grande 0.40** | **100/100, 13.0 ± 0.5 s** | **89/100, 0 caídas** |
| `v02` 15M | Cámara renderizada | 18/18 (12.7 s y 10.5–10.7 s) | 18/18 (13.5–13.7 s y 11.0 s) |
| `v02` 20M | Grande 0.40 | 100/100, 12.5 ± 0.55 s | 86/100, 0 caídas |
| `v02` 20M / 25M / 30M / 35M / 40M | Perturbada 0.5 | 15/20 / 14/20 / 19/20 / 15/20 / 15/20 | — |
| **B-Human (réplica)** | Benchmark de 3 carriles (5 semillas, sin perturbaciones) | 25/25, 16.2–18.3 s | 14/25 |
| NAOqi (réplica) | ídem | 25/25, 45.3–49.9 s | 14/25 |

## 11. Cómo se eligió

Criterio de la sección 11.4 del diseño:
1. **Filtro duro:** cualquier caída, salida o choque descarta.
2. Entre los que pasan: menor tiempo medio + 1σ.
3. Desempate: menor desvío.

- **`v01`: checkpoint de 15M.** Es el único de `v01` que pasa la batería perturbada a `vx_cmd` 0.5. El de 5M tuvo 4
  caídas.
- **`v02`: checkpoint de 15M.**
  - Con la batería grande a 0.40, 15M y 20M pasan el filtro. Por tiempo + 1σ, 20M es mejor (13.05 contra 13.5 s).
  - Se eligió 15M porque también pasa a `vx_cmd` 0.5 (20/20 contra 15/20): da margen para subir la perilla de
    velocidad en el robot real.
  - Sin visión, 15M es igual o algo mejor (89 contra 86/100).
- **No se eligió por el `best_model` interno ni por el último checkpoint.** La evaluación interna (5 episodios sin
  perturbaciones) no ve las faltas raras (E48).

**Velocidad recomendada:** `vx_cmd` 0.40, con 0 faltas en todas las baterías con visión. A 0.5 m/s es ~2.5 s más
rápida, con menos margen.

---

## 12. Qué aprendió a hacer la política (análisis de la marcha)

[`results/carrera/analisis_politicas.json`]: μ 0.8, `vx_cmd` 0.40, 3 semillas, 500 pasos por semilla, sin
perturbaciones.

| Métrica | `v01` | `v02` |
|---|---|---|
| Doble apoyo / un pie / vuelo | 20.5 % / 79.5 % / 0 % | 24.3 % / 75.7 % / 0 % |
| Altura máxima del pie | 55 / 49 mm | 52 / 53 mm |
| Pasos por segundo por pie | 2.0 | 2.06 (el reloj es de 2.0) |

Marcha real con pasos, al ritmo del reloj de marcha y sin fases de vuelo. Tira de imágenes:
`results/carrera/carrera_v01/marcha_lado_5M.png`.

**Uso de cada acción** (media, desviación y % del tiempo saturada, |a| > 0.98):

| Acción | `v01` media ± desv. (sat.) | `v02` media ± desv. (sat.) | Lectura |
|---|---|---|---|
| LHipYawPitch | +0.34 ± 0.19 (1 %) | −0.27 ± 0.16 (0 %) | Giro constante de ~±0.03 rad |
| LHipRoll | −0.78 ± 0.21 (37 %) | −0.78 ± 0.26 (42 %) | **Hacia adentro**, cerca del límite (−0.07 rad) |
| RHipRoll | +0.84 ± 0.16 (25 %) | **+1.00 ± 0.00 (99.6 %)** | **Hacia adentro, en el límite** (+0.07 rad) |
| L/R HipPitch | +0.47 ± 0.42 / +0.05 ± 0.49 | +0.50 ± 0.43 / +0.37 ± 0.47 | Son las que dan el paso |
| L/R KneePitch | −0.07 ± 0.70 / +0.26 ± 0.56 | +0.15 ± 0.66 / +0.35 ± 0.56 | Son las que dan el paso |
| L/R AnklePitch | −0.22 ± 0.29 / −0.32 ± 0.33 | −0.30 ± 0.24 / −0.47 ± 0.19 | — |
| L/R AnkleRoll | +0.17 / −0.34 | +0.03 / −0.44 | **Hacia afuera**: compensa las caderas |
| LShoulderPitch | +0.95 ± 0.08 (57 %) | **+1.00 ± 0.00 (99.7 %)** | Brazo izquierdo **fijo atrás** (2.07 rad) |
| RShoulderPitch | −0.85 ± 0.20 (52 %) | **−1.00 ± 0.01 (99.8 %)** | Brazo derecho **fijo adelante** (1.07 rad) |

**Hallazgos (E49):**
1. **Los brazos no se balancean.** Quedan fijos y asimétricos, uno adelante y otro atrás, probablemente como
   contrapeso y para compensar el giro. Corrige la entrada de la bitácora de la madrugada que decía "brazos que se
   balancean": eso era la tira de 5M de `v01`, que todavía tenía algo de movimiento (desv. 0.08–0.20).
2. **Pisada lo más estrecha posible:** las dos caderas hacia adentro, contra el límite asimétrico y el presupuesto
   lateral, con los tobillos hacia afuera. El espacio de 3 cm entre las piernas del V6 es la restricción activa.
   `choque_piernas` aporta −0.007 a −0.017 por paso: las piernas se rozan a veces.
3. **Giro constante con HipYawPitch**, de signo distinto en cada generación. No es simétrico, y probablemente
   compensa la asimetría de los brazos.

**¿Es aprendido? Sí, y la política lo necesita.** Prueba con la misma política y los hombros forzados a la pose de
pie (acción 0) [`results/carrera/prueba_brazos_home.json`]:

| Política | Brazos | Sin perturbaciones | Con perturbaciones | Rumbo medio |
|---|---|---|---|---|
| `v01` | Los aprendidos | 12/12, 12.8 s | 12/12, 13.6 s | +0.5° |
| `v01` | Forzados a la pose de pie | 12/12, **17.5 s** | 12/12, **20.6 s** | **+3.5°** |
| `v02` | Los aprendidos | 12/12, 12.7 s | 12/12, 13.1 s | −1.5° |
| `v02` | Forzados a la pose de pie | **0/12, se cae** | **0/12, se cae** | +4.3° |

**Por qué lo aprendió:**
- ningún término premia balancear los brazos ni la simetría;
- moverlos cuesta (`cambio_accion`, `torque`);
- fijos, adelante y atrás, sirven de contrapeso y compensan el giro: sin ellos `v01` se tuerce +3.5° y `v02` no se
  sostiene;
- además llegan al tope de ±0.5 rad.

En el sprint (0.2 m/s, sin perturbaciones ni cámara) la política sí balanceaba los brazos sin pedírselo. A 0.4–0.5 m/s,
con empujones y deriva, le convino usarlos como contrapeso fijo.

**Por qué importa:** en el robot real, operar en el límite de las acciones deja poco margen. Si el modelo y el robot
difieren, por ejemplo en la holgura de la cadera, las piernas pueden chocar. Los brazos fijos y asimétricos pueden
verse raros. Antes de la sesión real conviene considerar una generación con premio a la simetría o al balanceo de
brazos, o límites revisados. No se cambió nada esta noche: un cambio por generación.

---

### 12b. Salidas malas (E50)

| Colocación | Con visión | Sin visión |
|---|---|---|
| Recto (0°), corrido 0, ±10 o ±15 cm | 10/10, 12.7–13.0 s | 10/10, 13.7 s |
| +8° | 6/10 (solo con y = 0, −10 y −15 cm) | 0/10 |
| −8° | 0/10, salidas | 0/10 |
| ±15° y ±25° | 0/20, salidas a los 2–5 s | 0/20 |

Con el rumbo objetivo de la IMU alineado al carril (rumbo al arrancar − `psi` de la cámara), la misma política llega en
12/12 salidas torcidas hasta ±25° [`results/carrera/carrera_v02/rumbo_objetivo_carril.json`]. Detalle en E50 y en el
paso 58c.

### 12c. Paso 58c: rumbo objetivo de la IMU = dirección del carril

Cambio en el entorno y en el contrato (no es una generación):
- de pie, la cámara mide `psi`;
- al arrancar, rumbo objetivo = rumbo de la IMU − `psi` medio (`contract.rumbo_objetivo_inicial`, también para el
  robot).

Batería de 70 salidas malas con `v02` sin reentrenar (`scripts/eval_salida_mala.py`, μ 0.8, `vx_cmd` 0.40, 2 semillas
por celda) [`results/carrera/carrera_v02/salida_mala_model_{arranque,carril}.md`]:

| Rumbo objetivo de la IMU | Con visión (70 salidas) | Sin visión (70) |
|---|---|---|
| `arranque` (como se entrenó `v02`) | 16/70 metas, 54 salidas | 10/70 (solo las salidas rectas) |
| **`carril` (paso 58c)** | **69/70 metas**, 1 caída (y −15 cm, rumbo −25°), 0 salidas; 12.7–13.5 s | 10/70 (solo las salidas rectas) |

Sin visión no se puede corregir una salida torcida: sin la cámara, el robot no sabe que arrancó torcido.

## 12d. `carrera_v03`: salidas torcidas en el entrenamiento (paso 59c)

- **Config:** `configs/carrera_v03.yaml`.
- **Igual que `v02` salvo un cambio:** colocación del entrenamiento con σ 6 cm / 10°, máximo ±15 cm / ±25° (antes, σ
  2 cm / 2°, máximo ±10 cm / ±8°).
- **Base y entorno:** usa el rumbo objetivo del paso 58c (`carril`). La referencia de comparación es "`v02` + 58c",
  evaluada con el mismo entorno.
- **Corrida:** semilla 3, 20M pasos desde `policies/carrera_v02` en 1.65 h (3,375 pasos/s).
- **Hipótesis:** viendo salidas malas, las corrige también con perturbaciones y fricción baja, sin perder velocidad.

**Etapas** [`results/carrera/carrera_v03/curvas_entrenamiento.csv` y `.png`]:

| Tramo | Episodio medio | Retorno | Con falta | Salidas | Metas | seguim. vx | rumbo | barrera | σ acción |
|---|---|---|---|---|---|---|---|---|---|
| 0–2M | 26.0 s | 1,692 | 20 % | 24 % | 82 % | 0.81 | 0.45 | −0.08 | 0.100 |
| 2–5M | 25.7 s | 1,686 | 21 % | 23 % | 83 % | 0.81 | 0.45 | −0.07 | 0.097 |
| 5–10M | 25.6 s | 1,661 | 23 % | 24 % | 81 % | 0.82 | 0.45 | −0.10 | 0.095 |
| 10–15M | 26.0 s | 1,682 | 23 % | 26 % | 83 % | 0.82 | 0.44 | −0.11 | 0.096 |
| 15–20M | 25.7 s | 1,635 | 22 % | 24 % | 82 % | 0.81 | 0.44 | −0.11 | 0.100 |

Las medias casi no cambian: el entrenamiento parte de una política que ya camina. Lo que mejora se ve en las
baterías.

**Evaluación de los checkpoints** [`results/carrera/carrera_v03/`; batería grande en `seleccion_100/`]:

| Checkpoint | Salidas malas, sin perturb. (70) | Salidas malas, con perturb. (140) | Batería grande, con visión (100) | Batería grande, sin visión (100) |
|---|---|---|---|---|
| `v02` + 58c (referencia) | 69/70 (1 caída) | 128/140 (12 caídas) | 100/100, 13.0 s | 89/100 |
| **`v03` 5M (elegido)** | **70/70** | 135/140 (5 caídas) | **100/100, 12.8 ± 0.4 s, desvío 7.4 cm** | 82/100, 0 caídas |
| `v03` 10M | 70/70 | 137/140 (3 caídas) | 98/100 (2 salidas) | 87/100 |
| `v03` 15M | 70/70 | 122/140 (18 salidas) | — | — |
| `v03` 20M (final) | 69/70 (1 salida) | 133/140 (3 caídas, 4 salidas) | — | — |

**Elegido: 5M.** Es el único que pasa el filtro duro de la batería grande, y es más rápido y más recto que `v02`. Con
la cámara renderizada real, en salidas malas (y 0/±15 cm × rumbo 0/±15/±25° × μ 0.4/1.2): **30/30 metas** en
12.3–12.9 s [`results/carrera/carrera_v03/camara_renderizada_salida_mala.json`].

**Hipótesis cumplida en parte:**
- sin perturbaciones, todas las salidas malas;
- con perturbaciones, las caídas bajan de 12 a 5, todas en el mismo caso extremo (E52).

Entrenar más de 5M volvió a oscilar (15M y 20M peores), como en E48.

**Qué aprendió (uso de las acciones):** igual que `v02`.
- Brazos fijos (99–100 % saturados);
- RHipRoll hacia adentro, en el límite (99.4 %);
- marcha con 28.5 % de doble apoyo, 2.03 pasos/s por pie y pies que suben 46–49 mm
  [`results/carrera/analisis_politicas.json`].

Lo de E49 sigue igual, como era de esperar: no se cambió nada de eso.

## 12e. Entrenamiento por población: ronda 1 de 100 agentes (paso 61)

**Cómo:** `scripts/barrido.py --nombre ronda1 --agentes 100 --pasos 1000000 --eval-semillas 2`.
- Cada agente parte de `policies/carrera_v03` (hoy `policies/rl_v1.0`) con `configs/carrera_v03.yaml` y sortea, con su semilla:
  - los 14 pesos dentro de `rangos` (`salida_carril` en [−400, −300] desde el paso 55b);
  - fricción mínima U(0.3, 0.5) y máxima U(1.0, 1.3);
  - `vx_max` U(0.40, 0.60);
  - σ máximos de la cámara U(3, 6) cm y U(3, 5)°;
  - semilla de PPO.
- **Batería corta,** con visión, perturbaciones y `vx_cmd` 0.45:
  - μ 0.4–1.2 × 2 semillas;
  - 4 salidas torcidas a μ 0.6.
- **Puntaje (sección 11.4):** filtro duro y luego tiempo medio + 1σ.
- **Datos:** `results/barridos/ronda1/` (config, log y resultado de cada agente; `tabla.md`, `analisis.md`,
  `mejores.json`, `base_carrera_v03.json`).

| Resultado | Valor |
|---|---|
| Agentes | 100 (1M pasos cada uno desde `carrera_v03`), 14:36 → 23:40 (9 h 04 min, ~5.4 min por agente), 0 errores |
| Pasan el filtro duro (0 faltas en 14 corridas) | **70/100** |
| Superan a la base (12.41 s) | **49** |
| Puntaje de los que pasan | mejor **11.43 s** (`agente_045`), mediana 12.26 s, peor 13.54 s |
| Faltas de los descartados (48 corridas) | 26 caídas y 5 salidas en las salidas torcidas; 13 caídas y 5 salidas en la batería normal |

**Qué parámetros se asocian a un mejor puntaje** (Spearman entre los 70 que pasan; negativo = valor más alto, menos
tiempo):

| Parámetro | Media, pasan (70) | Media, descartados (30) | Media, 20 mejores | Spearman con el puntaje |
|---|---|---|---|---|
| `vx_max` | 0.515 | 0.501 | **0.535** | **−0.28** |
| peso `seguimiento_vx` | 1.26 | 1.27 | **1.37** | **−0.23** |
| peso `inclinacion` | −2.74 | −2.63 | −2.46 | **−0.23** |
| peso `rumbo` | 0.591 | 0.609 | 0.58 | **+0.22** |
| `friccion_max` | 1.14 | 1.15 | 1.14 | +0.15 |
| peso `caida` | −171 | −188 | −191 | +0.11 |
| peso `patron_marcha` | 0.584 | 0.574 | 0.635 | −0.10 |
| Los otros 11 | casi iguales | casi iguales | — | \|ρ\| ≤ 0.09 |

**Lectura:**
- **No hay un peso que domine.** La correlación más fuerte es de 0.28: entrenar pidiendo más velocidad (`vx_max`) y
  premiarla más (`seguimiento_vx`) da algo más de velocidad; más peso al rumbo, algo menos.
- Las medias de los que pasan y de los descartados son casi iguales en todos los parámetros. **Pasar o no pasar el
  filtro no depende de los pesos** sino, sobre todo, de la variación de cada entrenamiento (semilla) y del ruido de
  una batería de solo 14 corridas.
- Con 1M pasos desde una base fuerte, los pesos apenas alcanzan a mover la política. La ronda 2 (5M pasos y batería
  de 44 corridas) dirá si las diferencias se sostienen.

## 12f. Ronda 2: los 20 mejores con 5M pasos (paso 62)

**Cómo:** `scripts/ronda_siguiente.py --anterior ronda1 --nombre ronda2 --pasos 5000000`.
- Cada uno de los 20 mejores sigue **con su propia config** desde su modelo final de la ronda 1.
- **Batería completa** (44 corridas, con visión, perturbaciones y `vx_cmd` 0.45):
  - μ 0.4–1.2 × 4 semillas;
  - 12 salidas torcidas (y 0/±10 cm × rumbo ±15/±25°) × μ 0.4 y 1.0.
- **Se evalúa cada checkpoint (1M–5M) y se elige el mejor** (E54): el modelo final del primer agente había empeorado
  (6 caídas), y su checkpoint de 4M pasaba.
- **Tiempo:** 23:41 → 07:05, pausa a pedido del usuario, y 19:05 → 21:38.
- **Velocidad:** ~3,400 pasos/s antes de la pausa y ~2,100–2,800 después, con el mismo número de entornos; la causa
  probable es la temperatura del procesador.

**Resultado** [`results/barridos/ronda2/tabla.md` y `analisis.md`]: 17/20 pasan; 16 superan a la base. Los 5 mejores:

| # | Agente | Checkpoint elegido | Puntaje (44 corridas) | Desvío máx. |
|---|---|---|---|---|
| 1 | `agente_071` | 3M | **11.38 s** | 25.2 cm |
| 2 | `agente_026` | 4M | 11.51 s | 21.0 cm |
| 3 | `agente_062` | 5M | 11.58 s | **13.2 cm** |
| 4 | `agente_081` | 5M | 11.64 s | 14.2 cm |
| 5 | `agente_004` | 3M | 11.72 s | 26.3 cm |
| — | Base `carrera_v03` | — | 12.54 s | 20.9 cm |

**Qué pesos ganan** (Spearman entre los 17 que pasan; con 5M pasos la señal es mucho más clara que en la ronda 1):

| Parámetro | Media, pasan (17) | Media, 5 mejores | Spearman con el puntaje | Lectura |
|---|---|---|---|---|
| peso `seguimiento_vx` | 1.36 | **1.84** | **−0.64** | Premiar más la velocidad da más velocidad |
| peso `barrera_margen` | −9.7 | −7.6 | **−0.57** | Barrera más fuerte, mejor puntaje |
| peso `cambio_accion` | −0.060 | −0.080 | **+0.54** | Castigar más los cambios bruscos, mejor puntaje |
| peso `salida_carril` | −354 | −331 | **−0.53** | Castigo más fuerte, mejor puntaje |
| peso `caida` | −184 | −140 | −0.38 | — |
| peso `choque_piernas` | −2.75 | −3.36 | +0.33 | — |
| peso `patron_marcha` | 0.63 | 0.59 | +0.32 | — |
| `vx_max` | 0.538 | 0.561 | −0.21 | — |

Descartes: 7 caídas en salidas torcidas y 1 en la batería normal.

**Contra los otros carriles,** con la batería del benchmark (con visión, sin perturbaciones, μ 0.4–1.2 × 5 semillas,
`vx_cmd` 0.45) [`results/barridos/ronda2/comparacion_3_carriles/`, `results/benchmark/`]:

| Carril | Política | Metas | Tiempo en 5 m | Desvío máx. medio |
|---|---|---|---|---|
| **RL** | `agente_071` (ronda 2, 3M) | 25/25 | **10.68–10.78 s** | 5.5 cm (máx. 13.3) |
| **RL** | `agente_062` (ronda 2, 5M) | 25/25 | 10.73–11.40 s | **4.0 cm** (máx. 7.6) |
| RL | `carrera_v03` | 25/25 | 11.16–11.26 s | 4.9 cm (máx. 10.2) |
| RL | Sprint inicial (`v2_brazos`) | 25/25 | 24.2–24.3 s | ~7 cm |
| Baseline 2 | B-Human (réplica) | 25/25 | 16.2–18.3 s | ~3 cm |
| Baseline 1 | NAOqi (réplica) | 25/25 | 45.3–49.9 s | ~2.4 cm |

## 13. Fallos y callejones de este entrenamiento

| ID | Qué pasó | Qué se hizo |
|---|---|---|
| E43 | `check_race_env.py` falló por dos umbrales mal puestos en la prueba | Umbrales corregidos |
| E45 | `v01` se cae sin visión: `válido = 0` normalizado a −7.5 | `carrera_v02` |
| E46 | `--continuar` no encontraba la normalización de un checkpoint | Corregido en `src/train.py` |
| E47 | Con −200, salirse justo antes de la meta da más retorno que ir lento | Paso 55b; filtro duro mientras tanto |
| E48 | Entrenar más (25–40M) empeoró la robustez de `v02`; `v01` tuvo un retroceso a los 9–11M | Elegir por batería externa; considerar una tasa de aprendizaje decreciente |
| E49 | La política usa acciones saturadas (brazos fijos, caderas al límite) | Documentado; candidato a una generación propia |
| E50 | No se recupera si arranca torcida ≥ 8°: la IMU le pide mantener el ángulo con que arrancó | Paso 58c: rumbo objetivo = dirección del carril medida por la cámara al arrancar |
| E51 | Prueba de `check_contract.py` comparaba ángulos con `==` | Tolerancia |
| E52 | `v03`: 5 caídas en un solo caso extremo de salida mala con perturbaciones (−25°, μ 0.4) | Aceptado; opción 59d |
| E53 | El peso de salida que garantiza "salirse es peor que ir lento" depende de la política | Filtro duro; prueba con la política que se usa |
| E54 | Ronda 2: el modelo final de un agente empeoró con 5M pasos más (6 caídas); su checkpoint de 4M pasa | Se evalúa cada checkpoint y se elige el mejor |

Detalle y salidas de consola en [`registro_errores.md`](registro_errores.md).

**Otras decisiones de la noche:**
- `v01` se detuvo en 15.3M (de 60M planeados), porque ya cumplía con visión. El problema pendiente (sin visión) no
  se iba a resolver con más de lo mismo.
- Se detuvo con `taskkill`; por eso `v01` no tiene `final_model.zip`, solo checkpoints.

## 14. Lo que NO se hizo (y conviene hacer)

- **Ablación de pesos:** no se probó quitar o cambiar pesos uno por uno. Saber qué pesos realmente importan es el
  objetivo de los pasos 61–62 (100 agentes con pesos sorteados; lanzador listo, `scripts/barrido.py`).
- **Varias semillas por generación:** cada generación tiene una sola semilla de entrenamiento. No se sabe cuánto
  cambia el resultado con otra.
- **Tasa de aprendizaje decreciente, o parar por la batería** en lugar de por pasos fijos.
- **Fricción fuera del rango y asimétrica en la evaluación:**
  - se entrenó con μ por pie entre 0.35 y 1.25 y se evaluó con μ fijo e igual en los dos pies (0.4, 0.6, 0.8, 1.0 y
    1.2);
  - no se probó μ < 0.35 ni fricción distinta en cada pie en la evaluación;
  - en ese rango la política es casi insensible a μ: con `vx_cmd` 0.40 y perturbaciones, 13.2–13.3 s (`v01`) y
    12.9–13.1 s (`v02`), contra 16.2–18.3 s de B-Human, que pierde ~2 s con μ 0.4;
  - el μ real de la duela se mide en el paso 69; si diera < 0.4, hay que ampliar el rango y reentrenar.
- **Robots vecinos en el entrenamiento:** `choque_robot` siempre es 0; el choque solo se mide en la escena de 3
  carriles (paso 48b).
- **Prueba en el robot real** (fase O), exportación a Python 2.7 (paso 66) e integración en PenaltyStack (paso 67).

## 15. Cómo reproducirlo

```bash
uv run python -m src.train --config configs/carrera_v01.yaml --run-name carrera_v01
```

```bash
uv run python -m src.train --config configs/carrera_v02.yaml --continuar runs/carrera_v01/checkpoints/model_15000000_steps.zip --run-name carrera_v02
```

```bash
uv run python -m src.train --config configs/carrera_v03.yaml --continuar policies/carrera_v02 --run-name carrera_v03
```

```bash
uv run python scripts/eval_salida_mala.py --modelo policies/rl_v1.0/model.zip --perturbaciones --mu 0.4 1.2
```

```bash
uv run python scripts/eval_carrera.py --modelo policies/carrera_v02/model.zip --vx 0.40 --semillas 20 --perturbaciones
```

```bash
uv run python scripts/exportar_curvas.py --run carrera_v02
```

```bash
uv run python scripts/resumen_carrera.py
```

`v01` se entrenó 15.3M pasos y se detuvo a mano. Para reproducirlo igual, cortar en el checkpoint de 15M (o
`--total-timesteps 15000000`, aunque la curva del programa de PPO no depende del total, porque la tasa es constante).

**Huellas SHA-256 de las políticas guardadas:**

| Archivo | SHA-256 |
|---|---|
| `policies/carrera_v01/model.zip` | `a42284a3ae17d06bd52debade6943d0eb39bb91d416b20a300885b9a669d703f` |
| `policies/carrera_v01/model_vecnormalize.pkl` | `a60675a1251f9530e39e70b9e6ad30ddbfaea7fe0dbf846a9ab7a0468653cf1f` |
| `policies/carrera_v02/model.zip` | `1491947356c9937f63aee6a7d22d9a85c977ff74af5e7b5f69812df4f16dc728` |
| `policies/carrera_v02/model_vecnormalize.pkl` | `6e667e792b84fd9d79da673994c4d4ddb225d1d72661af922ab302f58ef983bf` |
| `policies/rl_v1.0/model.zip` (antes `carrera_v03`) | `73ba8474fc3bb17eaf55c9602db71daf7ed59f9efe78f5224136c54c371af818` |
| `policies/rl_v1.0/model_vecnormalize.pkl` | `67fc03eb4a77a69b34290cb205fbaf5e215c8bcddfd8c57fc8906e22a5f1304c` |

## 16. Índice de archivos

| Qué | Dónde |
|---|---|
| Entorno | `src/envs/nao_race_env.py`, `src/envs/__init__.py` (`NaoRace-v0`) |
| Contrato (observación y acción) | `src/race/contract.py`, `src/race/valores_v6.py` |
| Pesos y rangos | `configs/carrera/pesos.yaml` |
| Configs | `configs/carrera_v01.yaml`, `configs/carrera_v02.yaml` |
| Entrenamiento | `src/train.py`, `src/utils/env_factory.py`, `src/utils/callbacks.py` |
| Pruebas del entorno | `scripts/check_race_env.py`, `check_camara_sim.py`, `check_recompensa_carrera.py`, `check_choques_robots.py` |
| Evaluación | `scripts/eval_carrera.py`, `scripts/resumen_carrera.py`, `demo/caminatas/benchmark.py --rl-carrera` |
| Curvas | `scripts/exportar_curvas.py` → `results/carrera/carrera_v0N/curvas_entrenamiento.{csv,png}` |
| Resultados | `results/carrera/` (cada evaluación en `.md` y `.json`; `resumen.md`; `analisis_politicas.json`; `orden_recompensa.json`) |
| Políticas | `policies/carrera_v01/`, `policies/carrera_v02/` (modelo, normalización, config, metadatos y README) |
| Diario | `docs/bitacora.md`, entradas del 2026-10-11 |
