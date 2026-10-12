# Bitácora del proyecto

Registro cronológico de **todo** lo que se hace en el proyecto: avances, resultados, errores, callejones
sin salida y cómo se resolvieron. Tiene tres usos:

- que cualquier persona del equipo, y su asistente de IA, sepa en qué punto estamos y por qué;
- que alguien externo pueda reconstruir el proceso completo;
- que sea la fuente para escribir el paper.

**Reglas**

1. Se escribe **una entrada por paso del [`PLAN.md`](../PLAN.md)** al terminarlo, o antes si falla o se
   bloquea. También se escribe una entrada por cada sesión con el robot real y por cada generación de RL
   entrenada.
2. Las entradas nuevas van **al final**. Las anteriores **no se editan**. Si algo resultó estar mal, se
   corrige en una entrada nueva que haga referencia a la vieja.
3. Los fallos se documentan con el mismo detalle que los éxitos: qué se esperaba, qué pasó, causa y
   solución. Si no hubo solución, también se anota.
4. Los números van con su fuente: archivo de métricas, run o log.

**Plantilla**

```markdown
### AAAA-MM-DD — Paso NN: título corto
- **Autor:** nombre (equipo: laptop / torre / robot real)
- **Objetivo:** qué se quería lograr.
- **Qué se hizo:** cambios, comandos, configs.
- **Resultado:** métricas y evidencia (rutas a results/, policies/, data/real/, videos).
- **Problemas y solución:** qué falló, causa, cómo se resolvió (o "sin resolver").
- **Decisiones:** qué se decidió y por qué.
- **Siguiente:** próximo paso.
- **Commit:** hash o mensaje.
```

---

## Etapa 1 — Sprint inicial: caminata en simulación (pasos 1–32)

*Entrada retrospectiva escrita el 2026-10-08 a partir del historial de Git, el README y `results/`.*

### 2026-09-29 / 2026-09-30 — Pasos 1–32: primera política de caminata
- **Autor:** Camilo (laptop Ryzen 7 5800H).
- **Objetivo:** entrenar desde cero una política que haga caminar al NAO en simulación, en un sprint de 48 h.
- **Qué se hizo:**
  - **Stack:** MuJoCo 3.14 + Stable-Baselines3 2.9 (PPO), en Windows nativo y CPU.
  - **Modelo NAO:** derivado de *one_policy_to_run_them_all* (V5, MIT) con primitivas de colisión,
    HipYawPitch acoplado, ejes en la convención NAOqi y autocolisiones.
  - **Entorno `NaoWalkEnv`:**
    - 10 acciones de piernas a 50 Hz;
    - 43 observaciones (incluye la velocidad lineal del torso, una observación privilegiada);
    - recompensa por términos;
    - caída por altura, inclinación o contacto no-pie.
- **Resultado:** tres variantes de 5M pasos cada una (~22 min). Detalle en `results/comparison.md`.

  | Variante | Velocidad | Caídas | Desv. lateral | Observación |
  |---|---|---|---|---|
  | Base | 0.151 m/s | 0 % | −13 cm | "Pasitos de soldado", sin doble apoyo |
  | V1 natural | 0.199 m/s | 0 % | −4 cm | 20 % de doble apoyo, más simétrica |
  | **V2 brazos** (entregada) | 0.200 m/s | 0 % | +5 cm | Balancea los brazos en fase con la pierna contraria sin recompensa explícita |

- **Problemas y solución:**
  - **Marcha de soldado** en la versión base: el reloj de marcha no permitía doble apoyo. Se resolvió
    en V1 con `stance_fraction: 0.6`.
  - **Brazos rígidos:** se resolvió en V2 dejando que la política controle los hombros.
  - **Rendimiento en CPU:** con 8 hilos de PyTorch el entrenamiento era ~35 % más lento que con 4, porque
    PyTorch compite con los procesos de simulación. Se fijó `torch_threads: 4`.
  - **Parar y reanudar en la demo:** volver a la pose de pie hacía caer al robot en el 40–100 % de los
    casos. Se resolvió congelando la postura cuando ambos pies tocan el suelo (399/400 paradas sin caída).
- **Decisiones:** CPU en lugar de MJX/GPU, por reproducibilidad y cero riesgo de instalación. Política
  entregada: V2 brazos.
- **Limitaciones conocidas al cierre:**
  - solo simulación;
  - modelo V5 aproximado;
  - observación privilegiada;
  - sin domain randomization;
  - sin comandos de giro ni de velocidad.
- **Commits:** `cd92f6d` … `5ef27c7`.

## Etapa 2 — Correcciones tras la entrega

### 2026-10-07 — Pasos 33–35: modelo NAO V6 desde B-Human
- **Autor:** Camilo.
- **Objetivo:** reemplazar la aproximación del V5 por el modelo **V6** completo, como pidió la
  retroalimentación, y documentar las variables del RL sin código.
- **Qué se hizo:**
  - `docs/variables_rl.md`: explicación de las variables del RL sin código ni matemáticas (paso 33).
  - `scripts/build_nao_v6.py`: genera `assets/nao/nao.xml` y las mallas `.obj` a partir de
    `assets/nao/bhuman/NaoV6H25.rsi3`, la descripción del V6 de B-Human, verificada por SHA-256. Del RSI3
    conserva cuerpos, ejes, rangos, masas, inercias, colisiones, mallas y parámetros de servos (p, d,
    fuerza máxima).
- **Resultado:** el modelo V6 carga en el visor con las mallas oficiales.
- **Pendiente:**
  - validar la física (masa, contactos, de pie, barrido);
  - ninguna política se ha entrenado con el V6: `checkpoints/best_model.zip` es del modelo anterior;
  - `SOURCE.md` y la sección 10 del README todavía describen el V5.
- **Commit:** `d9207ec`.

## Etapa 3 — Carrera Individual, Copa NAO CCM MX 2026

### 2026-10-08 — Paso 39: replanificación hacia la competencia
- **Autor:** Camilo, con Claude Code.
- **Contexto:**
  - El director propuso un roadmap de 3 semanas para Laberinto, Carrera y Penales. **Este repo se enfoca
    solo en la Carrera**: caminata autónoma, rápida y estable.
  - Reglamento: *Reglamento Copa NAO CCM MX 2026 V1.0*, sección 3.2. Carril de 5 m × 70 cm sobre duela,
    gana el menor tiempo, salir del carril anula la carrera. Evento el 3 de noviembre de 2026.
- **Datos del equipo:**
  - **Robot:** NAO V6 con NAOqi 2.8.
  - **Acceso al robot:** 2–3 sesiones por semana.
  - **Experiencia previa:** Choregraphe y Python/NAOqi.
  - **Equipos para entrenar:** laptop Ryzen 7 5800H y torre Ryzen + RTX 5060.
  - **Personas:** dos en el frente de RL, trabajando en este mismo repo.
  - **Tiempo de referencia:** no hay. La meta es ser lo más rápidos posible.
  - **Caminata existente en el robot real:** ninguna, salvo la política de este repo, que solo existe en
    simulación.
- **Decisiones:**
  1. **Arquitectura:** RL + corrección externa. La cámara **no** entra a la red. Un detector de líneas y
     un controlador de carril generan una orden de giro (`wz_cmd`) que la política aprende a obedecer en
     simulación. Motivo: renderizar en el entrenamiento lo haría unas 100 veces más lento en CPU y
     agregaría la diferencia entre imágenes simuladas y reales.
  2. La política recibe además un **comando de velocidad** (`vx_cmd`). Sirve como perilla para elegir en
     la pista real la mayor velocidad estable.
  3. **Solo observaciones disponibles en el NAO real.** Se quita la velocidad lineal del torso.
  4. **Medir el robot real antes de entrenar para él:** servos, latencia, ruido e inferencia a bordo.
  5. **Baseline y plan B:** la caminata de fábrica ALMotion se mide como baseline y es el plan B. La
     prioridad sigue siendo el RL, iterado por generaciones.
  6. Los pasos 36–38 se reestructuran dentro de las fases J y M.
  7. **Documentación obligatoria y continua:** `CLAUDE.md`, esta bitácora, `docs/plan_rl_carrera.md` y
     la sección de la carrera en el README.
- **Qué se hizo:**
  - `PLAN.md` reestructurado, con los pasos 39–73 de las fases I a P.
  - `docs/plan_rl_carrera.md`: diseño del sistema, para presentar.
  - Esta bitácora.
  - `CLAUDE.md`: instrucciones para el equipo y sus asistentes.
  - Sección "Proyecto actual: Carrera" en el README.
- **Problemas observados:**
  - Al importar `mujoco` desde la sesión de Claude Code, Windows bloqueó un DLL de plugins de MuJoCo:
    `OSError: [WinError 4551] Una directiva de Control de aplicaciones bloqueó este archivo`.
  - **Sin resolver.** Hay que verificar si también ocurre en una terminal normal y en la torre. Si
    ocurre, es probable que lo cause Smart App Control o una política de control de aplicaciones de
    Windows, y bloquearía el entrenamiento.
- **Siguiente:** confirmar el paso 39 y pasar al paso 40 (políticas compartidas en el repo).

### 2026-10-08 — Paso 39 (revisión): PenaltyStack como repo final y baseline
- **Autor:** Camilo, con Claude Code.
- **Contexto (indicaciones del administrador):**
  1. El repo final es **PenaltyStack** ([Limao0521/PenaltyStack](https://github.com/Limao0521/PenaltyStack)).
     Este repo hace **solo el RL de la caminata**, y lo que se haga debe poder pasarse allá y funcionar.
  2. **El baseline es la caminata ya establecida en PenaltyStack.** Reemplaza al baseline ALMotion
     decidido en la entrada anterior.
  3. **La cámara queda vacía por ahora.** El método para saber si el robot va recto lo definirá el equipo
     aparte.
  4. La caminata debe ser **lo más recta posible**. Como el simulador no permite suscribirse a la cámara,
     hay que buscar estrategias para simular la pérdida de rectitud sin cámara.
  5. Hay que **definir y explicar** los pesos, las entradas y los espacios de observación y acción, para
     presentarlos al administrador.
  6. El equipo observó que, con el modelo V6, las piernas mantienen la separación del modelo aproximado,
     **se chocan y el robot se cae mucho**. El código sigue usando valores del modelo aproximado.
  7. Hay que tener en cuenta el silbato y traer de PenaltyStack lo necesario.
  8. **Ruido gaussiano:** es la forma de simular en MuJoCo el error de la cámara real. Se tiene en
     cuenta en el diseño, pero no se implementa todavía.
- **Qué se hizo:**
  - **Análisis completo de PenaltyStack:** rama `feat/bhuman-simulation` (`9c08a41`, 686 archivos) y rama
    `feat/rl-contracts` (`9682fe0`). Hallazgos en `docs/integracion_penaltystack.md`:
    - **Su caminata es el WalkingEngine original de B-Human** en C++, ejecutado en MuJoCo.
      - Parámetros: 300 mm/s máximo, 75 mm/s² de aceleración, pasos de 250 ms, cadera a 230 mm.
      - Tope teórico en 5 m: ~18.7 s.
      - Prueba registrada en su simulador: solo 0.469 m en 5 s, a 0.06 m/s.
      - En el robot real su adaptador usa `ALMotion.moveToward` con velocidades provisionales.
    - **Usa el mismo modelo V6 que nosotros:** `NaoV6H25.rsi3` con el mismo SHA-256.
    - Ciclo de 12 ms.
    - Sensores con formato fijo, incluidos 8 FSR en kg.
    - Python 2.7 a bordo, sin numpy en su código.
    - Despliegue por Ethernet.
    - **Silbato:** no hay detector. El operador presiona el táctil frontal de la cabeza 0.25 s después
      del silbato, y el ABORT es el botón del pecho 0.3 s. Esto cumple el reglamento.
    - La rama de RL tiene `PerceptionNoiseWrapper`, con ruido gaussiano, pérdidas y retardo para
      simular percepción. Es el patrón para la cámara.
  - **Copias de referencia** sin modificar en `third_party/penaltystack/`:
    - contrato de articulaciones;
    - `SensorAdapter`;
    - carga del modelo;
    - adaptador NAOqi;
    - despliegue;
    - perfil;
    - wrappers de ruido.

    Cada una con su procedencia en el README de la carpeta.
  - **`docs/plan_rl_carrera.md` reescrito:**
    - nuevo baseline;
    - contrato v1 con observación de 51 valores y acción de 13 articulaciones cada 24 ms;
    - pesos iniciales de la recompensa;
    - seis estrategias de pérdida de rectitud sin cámara;
    - ranura reservada para la cámara con ruido gaussiano;
    - análisis de la separación de piernas del V6.
  - **`PLAN.md` reestructurado:** pasos 39–76, fases I a Q, con la cámara aislada en la Fase P para que
    no bloquee.
  - `CLAUDE.md` y el README actualizados.
- **Mediciones:**
  - **Separación de piernas en el V6**, en la pose de pie: 3.0 cm entre muslos y tibias y 3.1 cm entre
    pies. Los centros de los pies están en y = ±0.053 m y las cajas miden 7–7.5 cm de ancho. Un HipRoll
    hacia adentro de ~0.075 rad por pierna cierra ese espacio, y la escala actual permite ±0.25 rad.
  - **La política de septiembre** (entrenada en el modelo aproximado) **en el V6:** 3 episodios de 20 s
    (semillas 1000–1002, deterministas): **0 caídas y 0 pasos con choque entre piernas**. La caída que
    vio el equipo **no se reproduce con esa política**. Se medirá en el paso 44 en el caso donde se vio,
    por ejemplo en un entrenamiento desde cero en el V6. Script de diagnóstico, temporal y fuera del
    repo: carga `checkpoints/best_model.zip`, evalúa con `NaoWalkEnv` y cuenta los contactos entre
    geometrías de la pierna izquierda y la derecha.
- **Problemas y solución:**
  - El error del DLL de MuJoCo (`WinError 4551`) de la entrada anterior **queda resuelto**. Ocurría solo
    dentro del sandbox de la sesión de Claude Code. Fuera del sandbox, MuJoCo carga bien en la laptop:
    masa del modelo 5.360 kg. No afecta al entrenamiento.
  - Clonar PenaltyStack en Windows falla con `Filename too long`, porque B-Human tiene rutas muy largas.
    Se resuelve con `git config core.longpaths true` antes del checkout, o clonando en una ruta corta.
- **Decisiones:**
  1. **Baseline:** el WalkingEngine de B-Human de PenaltyStack, medido en su simulador (paso 47) y en el
     robot (paso 67).
  2. **El rumbo lo corrige la política misma** con el error de rumbo de la IMU, y HipYawPitch entra como
     acción. Se descarta el controlador externo de giro `wz_cmd` de la entrada anterior.
  3. **Cámara:** entrada reservada (contrato v2) que no se implementa. Cuando se defina, se simulará con
     ruido gaussiano, retardo y pérdidas a 10 Hz.
  4. **Ciclo de 24 ms** (2 × 12 ms) para ser compatible con PenaltyStack y el NAO.
  5. **Choques entre piernas:** HipRoll asimétrico, penalización por choque y diagnóstico antes de
     cambiar valores.
- **Preguntas abiertas:**
  - **Baseline en el robot real:** ¿la caminata de PenaltyStack en el NAO es `ALMotion.moveToward`, que
    es lo que corre hoy su adaptador, o el WalkingEngine de B-Human corriendo en el framework de B-Human
    del robot?
  - **Licencia:** confirmar con el autor de PenaltyStack que sus archivos pueden copiarse en este repo
    público.
  - **Caídas por choque de piernas:** ¿en qué caso se vieron?
- **Siguiente:** confirmar el paso 39 y pasar al paso 40 (contrato v1 en código).

### 2026-10-08 — Paso 39 (ajuste): alcance solo caminata y respuestas del equipo
- **Autor:** Camilo, con Claude Code.
- **Respuestas a las preguntas abiertas de la entrada anterior:**
  1. **Baseline:** Luis Mario, autor de PenaltyStack, indicó que el baseline es la caminata ya
     establecida en su repo, la **caminata de B-Human**.
     - **En simulación:** el WalkingEngine en el simulador de PenaltyStack.
     - **En el robot real:** la caminata de B-Human con el framework de B-Human en el NAO. Falta
       confirmar en la sesión 1 que está instalado y cómo ordenarle caminar recto.
  2. **Caídas:** las vio Camilo en la **demo interactiva** (`scripts/demo_interactive.py`), al **pausar
     y reanudar** la caminata. "A veces" el robot se cae.
     - La demo congela la postura al pausar, y al reanudar la política tiene que arrancar desde quieta.
     - En el sprint inicial, con el modelo aproximado, esto funcionaba en 399 de 400 paradas.
     - Caminando de corrido, sin pausas, la medición anterior dio 0 caídas y 0 choques en 3 episodios.
     - Se mide en el paso 44, ampliado para reproducir las pausas sin visor.
  3. **Licencia:** el equipo indica que no hay problema en usar material de PenaltyStack. Se quita de
     los riesgos.
- **Indicación nueva:** de PenaltyStack **solo se usa lo que sirve para la caminata**. No se trae nada de
  penales.
- **Qué se hizo:**
  - **`third_party/penaltystack/`:** se borraron las copias de penales (adaptador NAOqi de penales,
    carga de la escena de penales, simulador de penales, despliegue, perfil de tirador y wrappers de
    percepción de pelota). Queda **solo `motion_contract.py`**, con el orden de articulaciones y el ciclo
    de 12 ms, que la política necesita para integrarse.
  - **`docs/integracion_penaltystack.md` reescrito** solo con lo de la caminata:
    - modelo;
    - baseline de B-Human y cómo medirlo;
    - formato de sensores, con las posiciones de los FSR;
    - teclas de arranque y paro;
    - despliegue;
    - silbato;
    - cámara y ruido gaussiano.

    Los datos que antes estaban en las copias quedaron escritos en el documento.
  - `docs/plan_rl_carrera.md`, `PLAN.md` y `CLAUDE.md` actualizados:
    - baseline en el robot real;
    - caídas de la demo y su relevancia para la carrera;
    - sin referencias a archivos de penales.
- **Decisión:** las caídas al reanudar muestran que la política **no sabe arrancar desde quieto**, y la
  carrera empieza justo así. El episodio de carrera arranca siempre desde quieto (paso 51).
- **Siguiente:** confirmar el paso 39 y pasar al paso 40 (contrato v1 en código).

### 2026-10-10 — Replanificación: cámara, tres carriles, fricción, faltas y 100 agentes
- **Autor:** Camilo, con Claude Code.
- **Contexto (indicaciones del equipo):**
  1. Revisar [danielpaya/nao_linea](https://github.com/danielpaya/nao_linea), basado en este repo, que
     trae la implementación de la cámara.
  2. **Tres carriles de comparación:** el RL del equipo, B-Human y NAOqi. Lo esperado:
     - NAOqi, la más lenta;
     - B-Human, más rápida;
     - el RL tiene que ser **el más rápido**.
  3. Replantear el RL con la cámara, el camino y las dos comparaciones.
  4. Pruebas con **distintos coeficientes de fricción**.
  5. Pesos importantes para las faltas del reglamento (3.2.6):
     - salir del carril (carrera anulada);
     - choque con otro robot (descalificación del equipo);
     - comunicación externa o control remoto (descalificación).
  6. **Los colores de líneas y piso se avisan poco antes del evento**: tienen que ser fáciles de cambiar.
  7. **~100 agentes** en pruebas distintas, variando pesos y fricción, para sacar el mejor RL.
- **Revisión de nao_linea** (commit `f8e0cc6`, 2026-10-10, autor Daniel):
  - **Visión de carril completa:**
    - busca la cinta por contraste local y filtra por su ancho;
    - proyecta al piso y ajusta las rectas con RANSAC;
    - devuelve `d`, `psi`, válido y la distancia a la meta.
  - **Precisión en simulación:** σ(d) = 1.6 cm y σ(psi) = 1.2°, con 1.5° de error de pose. Con un robot
    vecino tapando, σ(d) = 4.8 cm. Tiene versión en Python puro: 13 ms por imagen en PC.
  - **Lazo cerrado con la cámara renderizada:** solo RL llega en 3 de 18 corridas; RL + visión, en 18 de 18.
  - **Pista con colores configurables** (`demo/pista.yaml`). La visión decide sola si la línea es más
    oscura o más clara que el piso.
  - **Sí tiene los tres carriles** (`demo/caminatas/`):
    - **tipo B-Human:** réplica del esquema Walk2014, pasos de 250 ms, 0.30 m/s;
    - **RL:** la política del sprint inicial, 0.20 m/s;
    - **tipo NAOqi:** réplica de ZMP + control preview, 0.10–0.12 m/s.

    Están en `carrera_vivo.py` (los 3 en el visor) y `benchmark.py`. Resultados con visión, en 5 m:

    | Caminata | Tiempo en 5 m |
    |---|---|
    | Tipo B-Human | 16.2–18.3 s |
    | RL | 24.2–24.3 s |
    | Tipo NAOqi | 45–50 s |

    **Hoy el RL pierde contra B-Human.**
  - **Kit para el robot real** (`robot/`): diagnóstico, `race_nao.py --dry-run` y `--medir`, y guía
    `LUNES.md`.
  - La propuesta para **este** repo viene en `fase-p-camara-carril.bundle`: rama `fase-p-camara-carril`,
    3 commits sobre nuestro `4ca136d`, con `camara/`, `docs/fase_p_camara.md` y `results/camara/`.
    Todavía no está en GitHub.
- **Limitaciones encontradas en nao_linea:**
  - Las caminatas tipo B-Human y tipo NAOqi son **reimplementaciones**, no el código original, y su
    velocidad la impone el comando.
  - El `resultados/benchmark/benchmark.md` guardado es la **versión corta** (12 corridas). Las 150 que cita
    el README no están guardadas.
  - La corrección del rumbo usa un **truco** (sesgo en el giroscopio) que se invierte con señales grandes.
  - El RL usado es el del modelo aproximado, sin fricción aleatoria.
  - Cada robot va en su propia física, así que **los choques entre robots no se pueden medir** ahí.
  - Hay archivos que no deberían versionarse: `__pycache__`, `MUJOCO_LOG.TXT`, `.bundle` y `.zip`.
- **Qué se hizo:**
  - **`docs/plan_rl_carrera.md` reescrito:**
    - faltas del reglamento con su tratamiento en recompensa, selección y diseño;
    - tres carriles con protocolo común;
    - contrato v1 con **54 observaciones** (suma `d`, `psi` y válido de la cámara) y 13 acciones;
    - pesos iniciales **con rangos** para el barrido;
    - cámara simulada con ruido gaussiano (nominal de nao_linea, rango hasta 3×);
    - fricción;
    - colores en un solo archivo;
    - entrenamiento por población de 100 agentes con puntaje de selección.
  - **`PLAN.md` reestructurado:** pasos 40–80, fases I a P, con una tabla de equivalencias con la
    numeración anterior, para leer la rama de Daniel.
  - README, `CLAUDE.md` y `docs/integracion_penaltystack.md` actualizados.
- **Decisiones:**
  1. **La política recibe `d`, `psi` y válido como observación** (contrato v1 con cámara). Reemplaza el
     truco del giroscopio y el controlador externo de giro. La visión sigue fuera de la red.
  2. **Faltas en dos capas:**
     - en la recompensa, salida −200, caída −100 y choque −400 de referencia, todas terminales, más una
       barrera de margen a menos de 10 cm de la línea;
     - en la selección, cualquier falta en la batería descarta al agente.

     La comunicación externa no es un peso: queda imposible por diseño, porque solo hay sensores propios,
     todo corre a bordo y no hay Wi-Fi, y se verifica con una lista de chequeo (paso 76).
  3. **Fricción:** entrenamiento en [0.4, 1.2] con asimetría entre pies; batería de 0.4, 0.6, 0.8, 1.0 y
     1.2, la misma de nao_linea; μ de la duela medido en el robot.
  4. **Colores:** un solo archivo `config/pista.yaml` para la escena, la visión y el benchmark. La política
     no ve colores y se entrena con ruido de visión hasta 3×, así que cambiar colores no obliga a
     reentrenar. Procedimiento de menos de 1 hora (paso 75).
  5. **100 agentes:**
     - base común `carrera_v01`;
     - ronda 1: 100 agentes × ~2M pasos;
     - ronda 2: 20 × ~10M;
     - ronda 3: 5 × ~30M;
     - campeón.

     Varían pesos, rango de fricción, velocidad máxima, ruido de cámara y semilla. Estimado: 2–3 noches
     con las dos máquinas, a medir en el paso 43.
  6. **Meta de velocidad:** < 15 s en 5 m (≥ 0.35 m/s de media), para superar a la réplica de B-Human
     (16.2–18.3 s).
  7. **Plan B:** B-Human + visión, que en simulación ya llega siempre.
- **Siguiente:** paso 40, integrar el trabajo de Daniel en `main`.

### 2026-10-10 — Ajustes a la replanificación: baselines, un solo PC, solo `main`
- **Autor:** Camilo, con Claude Code.
- **Indicaciones:**
  1. **Baseline 1:** la caminata de **NAOqi**. **Baseline 2:** la de **B-Human**, sacada de PenaltyStack.
     Las dos se comparan contra nuestro RL.
  2. La cámara tiene que quedar integrada en el MuJoCo de este repo, para ver cómo funciona con el RL ya
     entrenado. **El MuJoCo de la pista es el de nao_linea.**
  3. **Todos los entrenamientos corren en el PC de Camilo** (laptop Ryzen 7 5800H). La torre con RTX 5060
     no está disponible.
  4. **Todo va en `main`.** La rama de cámara que se creó en este repo fue un error y no se usa. Camilo
     trabaja solo.
  5. **Todo entrenamiento de RL usa fricciones distintas**, porque no se sabe qué piso habrá.
  6. El cambio de colores antes de la competencia tiene que quedar implementado.
- **Cambios en el plan:**
  - Pasos 40 (integrar nao_linea), 43 (rendimiento en un solo PC), 60 (cola de agentes reanudable en este
    PC) y 65 (reducir costo, sin la torre) reescritos.
  - **Rondas del barrido acortadas para un solo PC:** 100 × 1M, 20 × 5M y 5 × 20M pasos. Son ~7.5 h cada
    una, unas 3 noches en total. Reemplaza el 100 × 2M / 20 × 10M / 5 × 30M de la entrada anterior.
  - Baselines nombrados como **baseline 1 (NAOqi)** y **baseline 2 (B-Human)** en el diseño, el README y
    `CLAUDE.md`.
  - `CLAUDE.md`: una sola persona, solo `main`, un solo PC. El asistente queda autorizado a hacer el commit
    de cada paso en `main`; el push, solo cuando se pida.
- **Siguiente:** paso 40, integrar nao_linea en `main`.

### 2026-10-10 — Paso 40: integrar nao_linea en `main` (bloqueado en la parte del RL)
- **Autor:** Camilo, con Claude Code (laptop Ryzen 7 5800H).
- **Objetivo:** dejar en este repo el MuJoCo de la pista con la cámara del NAO, la visión de carril y las
  caminatas de los baselines, para ver la cámara funcionando con el RL ya entrenado.
- **Qué se hizo:**
  - Copiado desde [danielpaya/nao_linea](https://github.com/danielpaya/nao_linea) (commit `f8e0cc6`),
    **sin** `__pycache__`, `MUJOCO_LOG.TXT`, `.bundle`, `.zip` ni el `src/` y `checkpoints/` (que eran
    idénticos a los nuestros). Se copiaron:
    - `carril/`;
    - `demo/`: `build_scene.py`, `run_demo.py`, `pista.yaml` y `caminatas/`;
    - `robot/`;
    - la escena y la textura de la pista en `assets/nao/`;
    - resultados en `results/camara/` y `results/benchmark/`;
    - figuras en `docs/img/`;
    - GIFs y el video de la carrera en `media/`.
  - **Ajustes:**
    - el benchmark escribe en `results/benchmark/` en lugar de `resultados/`;
    - `.gitignore` ignora `robot/logs/`, `MUJOCO_LOG.TXT` y `*.bundle`.
  - **Dependencias:** `pyproject.toml` y `uv.lock` de nao_linea son idénticos a los nuestros. No hubo que
    instalar nada.
  - **Nuevo `scripts/check_vision.py`:** coloca al NAO en 50 posiciones conocidas (x = 0.5 y 2.5 m; d de
    −15 a +15 cm; psi de −10 a +10°), renderiza la cámara inferior y compara la visión con la posición real.
    No necesita PyTorch.
  - **Nueva guía `docs/camara_y_carriles.md`**, con el crédito a Daniel.
- **Resultado:**
  - Pista regenerada con `demo/build_scene.py`: madera clara, línea negra, meta roja, contraste 141.
  - **Visión** (`results/camara/verificacion_vision.md`), 100 % de mediciones válidas en los dos casos:

    | Error de pose de la cámara | Error medio de d | Error medio de psi |
    |---|---|---|
    | Ninguno | 0.19 cm | 0.03° |
    | 1.5° | 1.27 cm (máx. 4.0 cm) | 0.86° (máx. 3.2°) |

    Coincide con el modelo de error de nao_linea (σ = 1.6 cm y 1.2°).
  - **Caminatas de los baselines** (`demo.caminatas.simular`, μ = 0.8, velocidades por defecto del
    script). Las dos llegan a la meta:

    | Caminata | Tiempo en 5 m | Velocidad | Desvío máximo |
    |---|---|---|---|
    | Tipo NAOqi | 58.4 s | 0.086 m/s | 7.9 cm |
    | Tipo B-Human | 23.1 s | 0.215 m/s | 5.3 cm |

    Estas no son las velocidades del benchmark, que pide 0.12 y 0.30 m/s.
- **Problemas y solución:**
  - **Bloqueante, sin resolver.** **Smart App Control de Windows** (estado 1 = activado) **bloquea
    PyTorch** en este PC: `OSError: [WinError 4551] Una directiva de Control de aplicaciones bloqueó este
    archivo ... torch_python.dll`.
    - Pasa dentro y fuera del sandbox de Claude Code, desde Bash y desde PowerShell.
    - El registro de Code Integrity de Windows muestra el bloqueo: eventos 3077 y 3118, "Smart App Control
      Block", a las 22:09 del 2026-10-10.
    - El 2026-10-08 PyTorch sí cargaba en este mismo PC, porque se evaluó la política en el V6. Smart App
      Control decide por reputación en la nube, así que su decisión puede cambiar.
    - **Consecuencia:** no se puede cargar la política de RL (`demo/run_demo.py`, el carril del RL en
      `carrera_vivo`, `src/evaluate.py`) **ni entrenar**. MuJoCo y todo lo que no usa PyTorch funciona.
    - **Opciones para el usuario.** Es una configuración de seguridad; el asistente no la cambia.
      1. Desactivar Smart App Control (Seguridad de Windows → Control de aplicaciones y navegador →
         Smart App Control). **Ojo:** Windows no permite volver a activarlo sin reinstalar el sistema.
      2. Correr el proyecto en **WSL2 (Ubuntu)**, donde Smart App Control no aplica.
      3. Esperar y reintentar, por si la reputación cambia.
  - Clonar nao_linea en Windows requiere `core.longpaths`, igual que PenaltyStack.
- **Estado del paso:** `[!]` bloqueado. La integración está hecha y verificada salvo la demo con el RL,
  que depende de que PyTorch vuelva a cargar.
- **Siguiente:** resolver el bloqueo de PyTorch (decisión del usuario). Mientras tanto se avanza con los
  pasos 47 (fricción) y 48 (colores), que se pueden verificar sin PyTorch.

### 2026-10-10 — Paso 47: fricción explícita y aleatoria en todo entrenamiento
- **Autor:** Camilo, con Claude Code (laptop Ryzen 7 5800H).
- **Objetivo:** que todo entrenamiento de RL use fricciones distintas, porque no se sabe qué piso habrá en
  la competencia, y dejar de depender del μ = 1.0 por defecto de MuJoCo.
- **Qué se hizo:**
  - **`src/envs/nao_walk_env.py`:**
    - Nuevos parámetros `friction` (μ fijo, para evaluar con un piso conocido), `friction_range`
      (por defecto [0.4, 1.2]) y `friction_asym` (por defecto 0.1).
    - Sin `friction`, cada `reset()` sortea μ uniforme y separa los pies hasta 0.1. El sorteo va
      **después** del ruido de la pose inicial, para no cambiar la secuencia aleatoria de antes.
    - `set_friction()` deja todas las geometrías (suelo incluido) en el menor de los dos μ y cada pie en
      el suyo. Como MuJoCo combina con el **mayor** de los dos coeficientes, el contacto de cada pie con el
      suelo usa el μ de ese pie.
    - `reset()` devuelve el μ usado en `info["friccion"]`.
  - **`src/train.py`:** rechaza una config con fricción fija, salvo con `--friccion-fija`, que existe solo
    para reproducir el sprint inicial.
  - **`src/evaluate.py`:** opción `--mu` para evaluar con fricción fija; el μ de cada episodio queda en
    las métricas.
  - **Configs:**
    - `configs/ppo.yaml`, `ppo_natural.yaml` y `ppo_brazos.yaml` fijan `friction: 1.0` explícito (es lo
      que usó el sprint inicial).
    - Nueva `configs/ppo_brazos_friccion.yaml`: V2 con fricción aleatoria, lista para entrenar.
  - **Prueba nueva `scripts/check_friction.py`.**
  - Los scripts de nao_linea (`benchmark`, `carrera_vivo`) fijan μ **después** de `reset()`, así que
    siguen funcionando igual.
- **Resultado:** `scripts/check_friction.py` → **RESULTADO: OK**:
  - con μ fijo de 0.4, 0.8 y 1.2, los 8 contactos pie-suelo usan exactamente ese μ;
  - **aleatorio, 200 semillas:** μ medio entre 0.413 y 1.199 (media 0.824); diferencia entre pies de 0.047
    de media y 0.099 como máximo;
  - el μ efectivo de cada pie coincide con el pedido;
  - el sorteo es reproducible con la misma semilla y cambia entre semillas;
  - de pie con μ = 0.4, el pie se desliza 0.03 mm en 3 s.
- **Problemas y solución:**
  - La primera versión de la prueba de "de pie con μ = 0.4" falló: 4.97 mm de deslizamiento.
  - Medición con distintos μ: el movimiento es casi igual con μ = 1.2 (4.44 mm) y viene de cómo se acomoda
    la postura por el **ruido de la pose inicial** (`reset_noise`), no de la fricción. Sin ese ruido, el
    deslizamiento es de 0.01–0.03 mm con cualquier μ.
  - La prueba se hace ahora sin ruido inicial.
- **`condim` 3 vs 4** (fricción torsional del pie). Prueba con las caminatas de los baselines, porque el RL
  no carga por el bloqueo de PyTorch: μ de 0.4, 0.6 y 1.0, sin visión, **una corrida por caso**.
  - Con `condim` 3, tipo B-Human llega con μ = 0.4 y **se sale** con 0.6 y 1.0. Con `condim` 4 llega en los
    tres.
  - Tipo NAOqi se sale con μ = 1.0 y `condim` 3, y llega en los demás casos.
  - Con una sola corrida, la diferencia no es concluyente: la deriva sin visión cambia mucho de una corrida
    a otra.
  - **Decisión:** mantener `condim` 3, igual que el entrenamiento previo y el benchmark de nao_linea, y
    repetir la comparación con varias semillas en el benchmark completo (paso 51).
  - **Lo que sí muestra:** **sin visión, la misma caminata llega o se sale según la fricción.** Eso
    confirma que hay que entrenar con fricción variable y usar la cámara.
- **Siguiente:** paso 48, colores de la pista en un solo archivo.

### 2026-10-10 — Paso 48: colores de la pista en un solo archivo, con verificación automática
- **Autor:** Camilo, con Claude Code (laptop Ryzen 7 5800H).
- **Objetivo:** que cambiar los colores de las líneas y del piso, que la organización avisa poco antes del
  evento, sea un solo comando con verificación, sin tocar código ni reentrenar.
- **Qué se hizo:**
  - **`config/pista.yaml`**, movido desde `demo/pista.yaml`, es el **único lugar** con los colores: piso,
    veta, línea, salida y meta.
    - `salida: null` significa "mismo color que las líneas", como en el reglamento V1.0.
  - **`demo/build_scene.py`:**
    - lee `config/pista.yaml`;
    - acepta `--salida`;
    - genera **`config/pista_robot.json`** (polaridad, modo y colores) para la visión a bordo del NAO, que
      no tiene PyYAML.
  - **`robot/race_nao.py`** toma la polaridad y el modo de `pista_robot.json`; antes la polaridad era
    "oscura" fija. `robot/LUNES.md` explica que hay que copiar ese JSON al robot.
  - **`scripts/check_vision.py`** ahora expone las funciones `verificar()` e `informe()` y exige además un
    contraste mínimo.
  - **Nuevo `scripts/cambiar_colores.py`:** guarda los colores conservando los comentarios del YAML,
    regenera la escena, verifica la visión (50 posiciones, 1.5° de error de pose) y escribe el informe.
    Tiene `--probar` (sin guardar) y `--matriz` (todas las combinaciones con nombre).
- **Problema encontrado y solución: la visión solo miraba el brillo.**
  - **Primera matriz** (63 combinaciones de piso × línea con nombre): **solo 30 OK.** Fallaban todas las
    líneas de color con brillo parecido al piso; por ejemplo, verde o gris sobre madera clara daba 0 %
    de mediciones válidas.
  - **Solución, un modo "color" en los dos estimadores** (`carril/lane_estimator.py` con numpy y
    `carril/lane_estimator_puro.py` para el NAO):
    - como los colores de la pista se conocen por la configuración, cada píxel se proyecta sobre la
      dirección de color "línea − piso";
    - con eso, la línea queda siempre más clara que el piso.
  - **Cuándo se usa cada modo:**
    - se usa **brillo** si la línea pasa la misma prueba que aplica el detector (más oscura que el 62 % del
      piso, o más clara en la misma proporción, con al menos 45 niveles de diferencia);
    - si no, se usa **color**.
    - Con la pista actual (negro sobre madera clara) se sigue usando brillo: el modo validado no cambia.
  - Se agregó un criterio **NO APTO** para contraste efectivo < 30 de 255. La imagen simulada no tiene ruido
    y "detecta" negro sobre negro, cosa que en una pista real no pasaría.
- **Resultado:**
  - **Pista actual** (madera clara, línea negra), visión por brillo: **RESULTADO: OK**, 100 % válidas,
    error medio de 1.27 cm y 0.86°. Idéntico a antes del cambio
    (`results/camara/verificacion_vision.md`).
  - **Cambio real y vuelta atrás** (gris oscuro con línea `#f2f2f2` y sin veta → madera clara con línea
    negra):
    - con los colores nuevos: OK, error de 1.26 cm, polaridad "clara";
    - al volver, `config/pista.yaml` queda idéntico al original.
  - **`--probar`** no modifica ningún archivo (verificado con md5).
  - **Matriz final:** **57 de 63 OK** (`results/camara/matriz_colores.md`).
    - **NO APTO:** negro sobre negro y blanco sobre blanco.
    - **Fallan:** gris sobre gris y verde sobre verde; y, al límite, gris sobre madera clara (89 %), rojo
      sobre gris (89 %) y gris sobre blanco (0 %).
    - Gris sobre blanco falla por una limitación de la simulación: la cámara simulada no tiene
      autoexposición y el piso blanco se satura a 255.
- **Problemas menores:**
  - Al escribir parches con heredocs de Bash, las secuencias `
` se convirtieron en saltos de línea
    reales y rompieron dos archivos. Se detectó con `ast.parse` y se corrigió.
  - Path.write_text en Windows guarda con CRLF; los archivos generados ahora se escriben con LF.
- **Decisión:** la escena de 3 carriles con física compartida (choques entre robots) pasa a un paso
  propio, el **48b**, para no mezclarla con los colores.
- **Siguiente:**
  - resolver el bloqueo de PyTorch (decisión del usuario, ver la entrada del paso 40);
  - después, pasos 41 (contrato v1), 44–46 (modelo V6) y 48b.

### 2026-10-10 — Paso 40 (continuación): PyTorch desbloqueado, demo RL + cámara verificada
- **Autor:** Camilo, con Claude Code (laptop Ryzen 7 5800H).
- **Qué pasó:** el usuario **desactivó Smart App Control** de Windows. PyTorch 2.14.0 y Stable-Baselines3
  vuelven a cargar. Se resuelve el bloqueo de la entrada del paso 40.
- **Verificaciones con el RL actual** (`checkpoints/best_model.zip`, el del sprint inicial):
  - **Demo RL + cámara sin ventanas** (`demo/run_demo.py --inicio-d 12 --inicio-psi 8`, robot 12 cm
    corrido y 8° girado):
    - **solo RL:** se sale del carril a los 2.8 s (0.54 m), con un desvío de 27.1 cm;
    - **RL + visión:** mide de pie d = +12.3 cm y psi = +7.6° (los reales son +12.0 cm y +8.0°), se centra
      a los 12.1 s (2.47 m) y **llega a la meta en 24.2 s**, con un desvío máximo de 15.2 cm.
  - **Benchmark corto de 3 carriles** (`demo.caminatas.benchmark --rapido`: μ = 0.6 y 1.0, con y sin
    visión, una semilla): **números idénticos a los de nao_linea**.

    | Caminata, con visión | Tiempo en 5 m |
    |---|---|
    | Tipo B-Human | 16.2–16.9 s |
    | RL | 24.3–24.5 s |
    | Tipo NAOqi | 47.8–49.8 s |

    Sin visión se salen: tipo B-Human con μ = 0.6 y tipo NAOqi con μ = 1.0. La integración reproduce los
    resultados originales.
  - **Entrenamiento de humo con fricción aleatoria:** `configs/ppo_brazos_friccion.yaml`, 40,000 pasos,
    4 entornos.
    - Corre a ~1,570 pasos/s y guarda el modelo.
    - Una config con fricción fija (`configs/ppo.yaml`) se rechaza sin crear el run.
    - `src.evaluate` informa la fricción aleatoria de cada episodio.
    - El modelo de humo se cae, como se espera con tan pocos pasos.
- **Estado del paso:** `[~]`. Falta la revisión visual del usuario de la demo en vivo y de la carrera de 3
  carriles.
- **Siguiente:** revisión visual del usuario; después, pasos 41, 44–46 y 48b.

### 2026-10-10 — Paso 40 (corrección): el visor muestra bien los 3 carriles con sus cámaras
- **Autor:** Camilo, con Claude Code.
- **Problema reportado por el usuario:** en MuJoCo no se veía bien. La idea es ver **los 3 carriles**, con el
  RL, NAOqi y B-Human, y la cámara.
- **Diagnóstico**, con capturas sin pantalla del visor:
  1. `run_demo.py --live` mostraba **un solo robot**, el RL.
  2. `carrera_vivo` mostraba los 3 robots, pero **sin cámara**: su visión era la simulada con ruido.
  3. **La meta roja solo estaba en el carril central.**
  4. **Los 3 robots eran iguales**, sin forma de saber cuál era cuál.
- **Qué se hizo:**
  - **`demo/build_scene.py`:** franja de meta en los 3 carriles (`meta`, `meta_izq`, `meta_der`).
  - **Nuevo `demo/caminatas/vision_camara.py`:** visión con la **cámara renderizada** de cada robot a
    10 Hz, más el control proporcional de giro de `run_demo` y el benchmark.
  - **`demo/caminatas/carrera_vivo.py`:**
    - cada robot usa su propia cámara (`--vision camara` por defecto; también `simulada` y `no`);
    - **cada robot tiene su color:** B-Human verde, RL azul, NAOqi naranja. Hay marcas del mismo color en el
      piso de cada carril;
    - **nueva ventana "Lo que ve cada NAO"** con las 3 cámaras, las líneas detectadas y d/psi estimados
      frente a los reales;
    - colocación configurable con `--inicio-d` y `--inicio-psi`, y opciones de colores;
    - **el visor mira desde atrás de la salida hacia la meta.** En la primera corrección miraba al revés;
      se detectó en la captura y se corrigió;
    - modo `--captura` para revisar sin pantalla.
  - **`demo/run_demo.py --live`** abre ahora esta carrera de 3 carriles. El modo anterior, solo RL con
    panel, queda con `--live --solo-rl`.
- **Resultado:**
  - Capturas revisadas: los 3 robots con color en sus carriles, la meta en los 3, y las 3 cámaras
    detectando las dos líneas.
  - **Carrera completa sin ventanas**, colocados +10 cm y −6°, μ = 1.0:

    | Caminata | Con la cámara de cada robot | Sin visión |
    |---|---|---|
    | RL | META en 24.6 s | META en 24.8 s |
    | B-Human | META en 16.2 s | **sale del carril** a los 9.0 s |
    | NAOqi | META en 49.8 s | META en 49.9 s |

  - **Sin cambios en lo anterior:**
    - `run_demo.py` sin ventanas: solo RL se sale a 0.54 m; RL + visión llega en 24.2 s;
    - `scripts/check_vision.py`: OK.
- **Siguiente:** revisión en vivo del usuario. No se toca el RL hasta que el MuJoCo esté aprobado.

### 2026-10-10 — Visor de MuJoCo roto en la laptop: era la GPU integrada AMD
- **Autor:** Camilo, con Claude Code.
- **Problema reportado por el usuario,** con captura: el visor de los 3 carriles se veía negro, con la escena
  aplastada en una franja arriba a la izquierda. Pidió verlo "como se veía caminando en grande, los 3 en
  perspectiva".
- **Diagnóstico.** Se abrió el visor brevemente y se capturó solo su ventana con `PrintWindow`:
  - **Mismo fallo con visión simulada,** sin cámaras renderizadas ni matplotlib, y **sin texto
    superpuesto**. No era la cámara ni la ventana de las cámaras.
  - **Mismo fallo con la versión anterior de `carrera_vivo`** (la de nao_linea), con la pista de un solo
    robot (`scene_carril.xml`) y con la escena original del sprint (`scene.xml`). El patrón era idéntico
    en todos los casos. No era la escena ni los cambios recientes.
  - **Causa.** La laptop tiene dos GPU, una NVIDIA GeForce RTX 3060 Laptop y una AMD Radeon integrada.
    El contexto OpenGL de Python se creaba en la **AMD**, con driver 22.20.44 de 2022, y su ventana GLFW
    dibuja mal el visor de MuJoCo. Las capturas sin pantalla (`mujoco.Renderer`) sí salían bien.
- **Solución.**
  - La variable de entorno `SHIM_MCCOMPAT=0x800000001` hace que el driver de NVIDIA tome el OpenGL de ese
    proceso. Con ella, `GL_RENDERER` pasa a ser `NVIDIA GeForce RTX 3060 Laptop GPU`. Funciona también
    si se fija dentro del programa, antes de crear la ventana.
  - Se agregó `os.environ.setdefault("SHIM_MCCOMPAT", "0x800000001")` al inicio de los scripts con
    visor: `demo/run_demo.py`, `demo/caminatas/carrera_vivo.py`, `simular.py`, `video_carrera.py`,
    `scripts/view_model.py`, `scripts/demo_interactive.py`, `scripts/test_viewer.py` y `src/evaluate.py`.
    En PCs sin NVIDIA no tiene efecto. **No se cambió ninguna configuración de Windows.**
- **Ajustes de presentación:**
  - el visor abre **sin los paneles laterales**; se muestran con Tab y Shift+Tab;
  - el texto con tiempo y avance va **arriba a la izquierda**: abajo tapaba la meta o se cortaba.
- **Resultado** (`run_demo.py --live` lanzado sin nada externo y capturado a los 11 s):
  - **visor:** pista de 3 carriles en perspectiva desde atrás de la salida, los 3 robots grandes y con su
    color, y la meta en los 3 carriles;
  - **ventana "Lo que ve cada NAO":** las cámaras detectando las líneas en vivo.
- **Siguiente:** revisión del usuario en vivo.

### 2026-10-10 — Paso 40 cerrado y ajuste del plan del RL
- **Autor:** Camilo, con Claude Code.
- **Paso 40 aprobado por el usuario.** Funcionan bien:
  - los 3 carriles en el visor;
  - la cámara;
  - la distancia `d` y el ángulo `psi`;
  - la fricción, con μ = 1.0 en la demo.
- **Indicación:** el RL tiene que ir variando esos valores (fricción y pesos) y tener en cuenta los pesos
  importantes de las faltas del reglamento (`docs/plan_rl_carrera.md`, secciones 1.2 y 6.4) y los nuevos
  `d` y `psi` de la cámara, para que no nos descalifiquen.
- **Revisión del plan.** Ya estaban cubiertos:
  - fricción aleatoria en todo entrenamiento (paso 47, hecho);
  - pesos de las faltas con rangos para el barrido (pasos 55 y 60);
  - `d` y `psi` en la observación (paso 53);
  - selección de agentes con filtro duro de faltas (sección 11.4).
- **Huecos encontrados y corregidos en el plan:**
  1. **Faltaba un paso para correr la política nueva en los 3 carriles con su propia cámara.** Hoy el RL
     de `carrera_vivo` y del benchmark usa el truco del giroscopio. Nuevo **paso 58b**. La selección final
     de agentes usa este mismo camino.
  2. **No estaba definido cómo llegan `d` y `psi` a la política.** Nueva **sección 6.7 del diseño**:
     - signos (+ = robot a la izquierda o girado a la izquierda);
     - última medición cruda, mantenida entre fotos a 10 Hz;
     - `válido` con una ventana de 300 ms;
     - la misma señal en entrenamiento, demo y robot.

     El paso 57 ahora exige comprobar que la cámara simulada y la renderizada dan la misma señal.
  3. **Los pesos vivían solo en el documento.** El paso 55 ahora pide un solo archivo
     `configs/carrera/pesos.yaml`, con los pesos iniciales y los rangos del barrido, del que leen el entorno
     y el lanzador.
- **Ruta crítica del RL, agregada al plan:** 41 → 46 → 53–58 → 58b → 59 → 60–63 → 77–78. Los demás pasos se
  intercalan mientras haya entrenamientos corriendo.
- **Siguiente:** paso 41, contrato v1 en código.

### 2026-10-10 — Material para el paper: historial, registro de errores y capítulo de visión
- **Autor:** Camilo, con Claude Code.
- **Indicación:** guardar todo, incluidos todos los errores y fallos, cómo se solucionaron y el paso a paso
  exacto, porque de esto sale un paper. Revisar los pasos anteriores e incluir la visión (cámara).
- **Revisión de los pasos 1–40:**
  - 1–33, 39 y 40 completos;
  - 34–35 hechos pero sin validar (la validación pasó al paso 44);
  - 36–38 reubicados en la replanificación;
  - 47 y 48 completos, adelantados.
- **Qué se hizo.** Nueva carpeta **`docs/paper/`**:
  - **`historial_pasos.md`:** cada paso del 1 al 40, más el 47 y el 48, con qué se hizo, cómo se verificó,
    resultado y commit. Reconstruido del historial de Git, el plan, el README, `SOURCE.md`, `results/`, la
    bitácora y las notas de las sesiones del sprint. **No se inventaron cifras:** donde no hay dato, no se
    pone.
  - **`registro_errores.md`:** **37 errores** (E01–E37) con síntoma, causa, solución, estado y evidencia.
    - Incluye errores del sprint que no estaban en la bitácora: ejes invertidos del modelo base, reinicio
      del visor, autocolisiones, rangos peligrosos, rutas largas de `pip`.
    - Incluye los del desarrollo de la visión de Daniel: poca luz, falsos positivos de la meta,
      autocorrección de pose, truco del giroscopio.
    - Incluye errores de herramientas: heredocs, CRLF, captura de ventanas.
  - **`vision_carril.md`:** capítulo de la visión (problema, método, precisión, colores, 3 carriles, cómo
    entra al RL y pendientes), con crédito a Daniel.
  - **`README.md`:** índice y cuándo se actualiza cada documento.
- **Protocolo:** `CLAUDE.md` ahora exige que todo error vaya también al registro (con su ID `E##`) y que cada
  paso cerrado se resuma en el historial.
- **Pendiente detectado al reconstruir:** el plan original de los pasos 34–35 usaba el URDF oficial V6
  (`NAOH25V60.urdf`), pero el modelo se generó desde el RSI3 de B-Human. El motivo del cambio no quedó
  registrado en su momento (ver E12).
- **Siguiente:** paso 41.

### 2026-10-10 — Procedencia de todas las piezas externas (fuentes y repositorios)
- **Autor:** Camilo, con Claude Code.
- **Indicación:** de aquí en adelante, aclarar en cada paso qué se hizo, cómo, de dónde se sacó, y si hubo
  errores o no. Explicar lo que se sacó de otros repositorios, cómo funcionan y por qué se usan; en
  particular el modelo de B-Human y la cámara. La cámara salió de este repo como un apartado, que otro
  compañero (Daniel) desarrolló en otro repositorio.
- **Qué se verificó, con el historial de Git de cada repo:**
  - **Modelo V6:**
    - `NaoV6H25.rsi3` es `Config/Scenes/Includes/NaoV6H25.rsi3` de **bhuman/BHumanCodeRelease**, revisión
      `d89d603`;
    - PenaltyStack lo agregó el **6 de octubre** (commit `21dbb16`, Luis Mario) y este repo el **7 de
      octubre** (`d9207ec`), con el **mismo SHA-256** `73f8c9a7…`. Llegó por PenaltyStack;
    - nuestro `scripts/build_nao_v6.py` es propio, distinto de `tools/build_bhuman_model.py` de PenaltyStack.
  - **PenaltyStack** deriva de **SabanaHerons2026** (`2360ab11`), basado en B-Human, del que conserva 559
    archivos del motor de movimiento.
  - **nao_linea:**
    - empezó el **9 de octubre a las 21:06** como la rama `fase-p-camara-carril` de **este** repo, sobre
      nuestro `4ca136d` (3 commits);
    - a las **21:47** pasó al repo de Daniel, con `src/`, `checkpoints/` y `assets/` idénticos a los
      nuestros;
    - el **10 de octubre a las 00:11** agregó las caminatas tipo NAOqi y tipo B-Human y la carrera de 3
      carriles;
    - se integró en nuestro `main` el **10 de octubre a las 22:12** (paso 40).
- **Qué se hizo:**
  - **Nuevo `docs/paper/fuentes_y_repositorios.md`:** mapa de fuentes y, para cada una, qué es, cómo
    funciona, qué se tomó (commit o SHA-256), por qué y qué se cambió. Cubre one_policy_to_run_them_all,
    el URDF de Aldebaran, B-Human y el RSI3, SabanaHerons2026, PenaltyStack, nao_linea, cómo funcionan las
    réplicas de los baselines, el reglamento y el software. Incluye una tabla de procedencia por archivo.
  - Se agregó la cronología del origen en `vision_carril.md` y la procedencia verificada en E12 del
    registro.
  - **`CLAUDE.md`:** todo lo que se tome de otra fuente se registra en `fuentes_y_repositorios.md`.
- **Sigue sin registro:** por qué los pasos 34–35 usaron el RSI3 de B-Human en lugar del URDF oficial que
  decía el plan.
- **Errores en este paso:** ninguno.
- **Siguiente:** paso 41.

### 2026-10-10 — Revisión de la documentación antes del paso 41, y errores con su salida de consola
- **Autor:** Camilo, con Claude Code.
- **Indicación:**
  - cada vez que empiece un paso nuevo, revisar todo lo documentado para el paper;
  - si salió un error en consola, poner el error textual y cómo se solucionó.
- **Qué se hizo:**
  - **`docs/paper/registro_errores.md`:**
    - se agregó la **salida de consola textual** en los errores que la tuvieron: E10, E13, E14, E15, E21,
      E22, E24, E25, E28, E29, E32, E33. Se dice explícitamente que la de E01–E12 no se conservó;
    - errores nuevos que no estaban registrados: **E38** (no se podía leer el PDF del reglamento:
      `pdftoppm is not installed`, `ModuleNotFoundError: No module named 'pypdf'`, `FileNotFoundError` por una
      ruta relativa) y **E39** (`KeyError: 'piso'` en la primera corrida de `scripts/check_vision.py`);
    - E14 completado: además del "Filename too long", `git restore` dejó el clon con todos los archivos
      marcados como borrados, y se resolvió con `git reset --hard HEAD`;
    - E33 completado: la primera captura no encontró la ventana porque el `python.exe` de uv lanza un proceso
      hijo.
  - **`CLAUDE.md`:**
    - nueva sección "**Revisión de la documentación al empezar CADA paso**", con una lista de 6 puntos;
    - la regla de copiar el texto exacto de consola de cada error.
  - **Revisión completa, primera aplicación de la regla:**
    - **chequeo automático de los 23 `.md`:** 0 enlaces rotos a archivos y 0 anclas de sección rotas;
    - **búsqueda de datos viejos** (cámara "pendiente", 51 observaciones, numeración vieja, dos personas o
      máquinas, `wz_cmd`, baseline ALMotion): sin contradicciones. Las coincidencias que quedan son
      históricas y correctas;
    - **dos documentos que inducían a error**, ahora con un aviso al inicio:
      - `assets/nao/SOURCE.md` describía el modelo V5 como si fuera el actual (se reescribe en el paso 44);
      - `docs/variables_rl.md` describe la política del sprint, no la de carrera;
    - el `historial_pasos.md` ahora registra también el trabajo de documentación de hoy.
- **Errores en este paso:** ninguno nuevo.
- **Siguiente:** paso 41, contrato v1 en código.

### 2026-10-10 — Paso 41: contrato v1 en código
- **Autor:** Camilo, con Claude Code (laptop Ryzen 7 5800H).
- **Revisión previa de la documentación** (regla nueva de `CLAUDE.md`): hecha justo antes, en la entrada anterior. 0
  enlaces rotos, sin contradicciones y avisos agregados en `SOURCE.md` y `variables_rl.md`.
- **Objetivo:** escribir en código la observación de 54 valores, que incluye `d`, `psi` y válido de la cámara, y la
  acción de 13 ángulos, con el formato de PenaltyStack, para que entrenamiento, demo y robot usen exactamente lo mismo.
- **Qué se hizo:**
  - **`src/race/contract.py`:**
    - orden de articulaciones de B-Human;
    - tiempos de 12 y 24 ms;
    - `armar_observacion(frame, …)`, `accion_a_objetivos`, `objetivos_a_salida_bhuman` y `EstadoCamara`;
    - compatible con Python 2.7 y sin numpy.
  - **`scripts/check_contract.py`:** 8 grupos de pruebas.
  - **De dónde sale cada dato:**
    - orden y ciclo: PenaltyStack (`third_party/penaltystack/motion_contract.py`, `9c08a41`);
    - formato del frame: `SensorAdapter` de PenaltyStack;
    - `home` y rangos: modelo V6 (RSI3 de B-Human);
    - observación y acción: diseño, secciones 6.1, 6.2 y 6.7.
- **Resultado:** `RESULTADO: OK` en la primera corrida. Datos clave con un frame real de MuJoCo (robot de pie, girado
  10°):
  - error de rumbo −10.00°;
  - carga de los pies 0.50 / 0.50;
  - gravedad proyectada igual a la del simulador (tolerancia 1e-9);
  - HipRoll asimétrico verificado (afuera 0.25, adentro 0.07).
- **Errores:** ninguno en consola.
- **Pendiente:** en el PC no hay Python 2.7 (`py -0` → solo `-V:3.12`). La compatibilidad se verificó con una revisión
  estática (sin f-strings, sin anotaciones, solo `math`). La prueba real va en el paso 69, en el NAO.
- **Decisiones:**
  - el contrato no importa numpy ni MuJoCo, para poder copiarlo tal cual a PenaltyStack;
  - los valores "(a validar)" (`home`, período de marcha, límites de HipYawPitch y HipRoll) se revisan en el paso 46.
- **Cambio de regla de commits:** el usuario indicó que el asistente **no haga commits**; él los hace manualmente
  cuando decida. Este paso queda **sin commit**. `CLAUDE.md` se actualizó; la autorización del 2026-10-10 queda
  retirada.
- **Siguiente:** paso 46 (ruta crítica), quitar los valores del modelo aproximado. Según la regla, antes se revisa toda la
  documentación.

### 2026-10-10 — Paso 46: valores del modelo V6 (y las piernas ya no se cruzan)
- **Autor:** Camilo, con Claude Code (laptop Ryzen 7 5800H).
- **Revisión previa de la documentación:**
  - 23 `.md`, 0 enlaces o anclas rotas, estados coherentes;
  - **hueco corregido:** `fuentes_y_repositorios.md` no registraba que el contrato del paso 41 copia el orden de
    articulaciones y el ciclo de PenaltyStack.
- **Objetivo:** reemplazar los valores heredados del modelo aproximado V5 por valores medidos en el V6.
- **Decisión:** `src/envs/nao_walk_env.py` (el entorno del sprint) no se toca, porque la política del sprint lo usa en
  la demo. Los valores nuevos van en `src/race/contract.py` (también del robot) y `src/race/valores_v6.py` (solo de la
  simulación).
- **Qué se hizo y qué salió:**
  - **Nuevo `scripts/check_valores_v6.py`.**
    - Cadera en `home` a 232 mm, igual que B-Human (230 mm).
    - Altura de caída 0.24 m: el torso agachado al máximo queda a 291.6 mm, menos 5 cm.
    - Altura objetivo 0.316 m.
    - Ciclo de 24 ms.
  - **Primera corrida → FALLA** (E40). Las piernas se cruzaban con los límites del paso 41 en el 2.19 % de las
    acciones. El diagnóstico mostró que eran pie contra pie, con las dos caderas y los dos tobillos hacia adentro a la
    vez. Achicar los límites de cada articulación no lo resolvía.
  - **Solución: presupuesto lateral combinado** en el contrato, de 0.09 rad equivalentes de cadera, con pesos medidos
    (HipRoll 22.1 cm/rad, AnkleRoll 3.85, HipYawPitch +10.6/−5.4). **0 cruces** en 20,000 acciones (antes 23.9 %
    con los límites viejos).
  - **Cambio de criterio:** de "margen ≥ 0.30 cm" a "ningún cruce y margen > 0.10 cm". El 0.30 era arbitrario y bajar
    el presupuesto no subía el peor margen (0.20 cm). Registrado en E40.
  - **Período de marcha** de 0.6 a 0.5 s (como B-Human), y agregado al barrido (0.4–0.7).
  - **`check_contract.py`:** pruebas del presupuesto (las dos piernas adentro se escalan exactamente a 0.090 rad, el
    pitch no se toca y hacia afuera no hay límite combinado).
- **Resultado:** `check_valores_v6.py` OK; `check_contract.py` OK; `check_standing.py` OK en el V6 (10 s de pie, 20/20
  con ruido, empujones de 15–20 N).
- **Documentos actualizados:**
  - `PLAN.md` (paso actual: 53);
  - README;
  - diseño (secciones 6.2, 11.1 y 12);
  - `docs/paper/` (historial, E40, E16 resuelto, fuentes).
- **Errores en consola:** solo el `RESULTADO: FALLA` de la primera corrida (E40).
- **Siguiente:** paso 53 (entorno de carrera: observación de 54 valores), según la ruta crítica. Antes, la revisión de
  la documentación.

### 2026-10-10/11 (noche) — Noche de trabajo autónomo; E41; pasos 42 y 43
- **Autor:** Claude Code, trabajando solo con autorización del usuario hasta las 7:00. Sin commits.
- **Indicaciones del usuario para la noche:**
  - avanzar bastante en el RL, con documentación;
  - **meta: que el RL sea al menos igual de rápido que B-Human** (hoy 16–17 s en 5 m con visión, ~0.30 m/s);
  - el entrenamiento tiene que tener **cambio de fricción** y ser **pesado** (~7 h disponibles).
- **E41 (pasos saltados):** se eliminó la "ruta crítica" del `PLAN.md` y los pasos vuelven al orden numérico. Detalle en el
  registro de errores.
- **Paso 42, políticas compartidas:**
  - **`scripts/guardar_politica.py`:** copia `model.zip`, `model_vecnormalize.pkl`, `config.yaml`, `metadata.yaml` y un
    README a `policies/<nombre>/`;
  - **`src/train.py --continuar`:** acepta una carpeta de `policies/` o un `.zip` de un run, carga el modelo y su
    normalización (que se sigue actualizando) y anota `continua_de` en los metadatos;
  - **`env_id` en la config:** para el entorno de carrera (`src/train.py` y `src/utils/env_factory.py`);
  - **prueba:** guardar el run de humo → `src.evaluate` detecta la normalización y la config solas → `src.train
    --continuar` 20,000 pasos → OK. Las carpetas de prueba se borraron.
- **Paso 43, rendimiento** (`scripts/benchmark_envs.py --envs 16 --ppo-envs 16`):
  - simulación pura: 7,465 pasos/s, 5.0 GB de RAM;
  - **entrenamiento PPO: 3,725 pasos/s**, es decir 45 min cada 10M pasos;
  - con el ciclo de 24 ms del entorno de carrera se estiman 3,100–3,300 pasos/s: **~65–70M pasos en 6 h**;
  - el barrido de 100 agentes (300M pasos) tomaría ~22–27 h en este PC.
- **Errores en consola:** ninguno.
- **Siguiente:** paso 44, validar la física del V6.

### 2026-10-11 ~00:00 — Paso 44: el modelo V6 es idéntico al de B-Human
- **Autor:** Claude Code (noche autónoma). Sin commits.
- **Qué se hizo:** nuevo `scripts/check_modelo_v6.py`. Lee `NaoV6H25.rsi3` **por su cuenta**, sin pasar por el MJCF
  generado, y lo compara con `assets/nao/nao.xml` compilado en MuJoCo.
- **Resultado: RESULTADO: OK.**
  - 25 cuerpos: masa (dif. máx. 2.8e-17 kg), centro de masa (3.5e-18 m) e inercias principales (dif. relativa
    2.2e-15).
  - 24 articulaciones: posición (6.9e-18 m), eje (0) y rango (4.8e-10 rad).
  - 23 servos con los kp, kv y fuerza del RSI3; RHipYawPitch acoplado sin actuador propio.
  - **Masa total: RSI3 5.35975 kg = MJCF 5.35975 kg = URDF oficial de Aldebaran 5.35975 kg.** Es un control
    independiente: el URDF de Aldebaran y el RSI3 de B-Human dan la misma masa.
- **Consecuencia:** las mediciones del paso 46 (alturas, cruce de piernas) se hicieron sobre un modelo correcto. No
  hay que repetirlas (ver E41).
- **Documentos:**
  - `assets/nao/SOURCE.md` reescrito para el V6 (fuente, qué se conserva, qué se agrega para el RL); el V5 queda como
    sección histórica;
  - sección 10 del README reescrita;
  - tabla de scripts del README con los 5 scripts nuevos (`check_modelo_v6`, `check_valores_v6`, `check_contract`,
    `check_friction`, `check_vision`);
  - `scripts/inspect_model.py` (que ya esperaba 5.360 kg): OK.
- **Errores en consola:** ninguno.
- **Siguiente:** paso 45, diagnóstico de las caídas al reanudar.

### 2026-10-11 ~00:00–00:30 — Paso 45: diagnóstico de las caídas al pausar y del choque entre piernas
- **Autor:** Claude Code (noche autónoma). Sin commits.
- **Qué se hizo:** nuevo `scripts/diag_caidas.py`, que reproduce sin visor la lógica de pausa de
  `scripts/demo_interactive.py`.
  - Pausas al azar: marcha de 2–5 s y pausa de 0.5–3 s, en 30 episodios de 30 s.
  - Cuatro modos de pausa: el de la demo, el de la demo con el reloj de marcha detenido, congelar en cuanto se pide y
    la pose de pie.
  - Por cada caída guarda el motivo, el momento (en pausa o al reanudar), la articulación con más error de seguimiento
    y si hubo choque entre piernas.
  - También mide la distancia y los choques entre piernas con acciones al azar y con dos políticas.
  - Para eso se entrenó una política desde cero en el V6 con `NaoWalk-v0`: `runs/diag45_desde_cero_2M`, 2M pasos,
    10 min, fricción aleatoria. Termina con un episodio medio de 19.4 s.
- **Resultado** (`results/diagnostico_45.md` y `.json`):
  - **Pausa de la demo en el V6: se cae en el 45 % de las pausas** (28/62), y no en 1 de cada 400 como en el V5.
    - 19 caídas fueron **durante** la pausa y 9 al reanudar.
    - Todas por inclinación; la articulación con más error es RAnklePitch (20/28).
  - Detener el reloj de marcha no ayuda (48 %). Pausar en la pose de pie baja a **5.6 %**.
  - **Piernas:**

    | Fuente | Pasos con choque | Penetración máxima |
    |---|---|---|
    | Política del sprint | 0 % | separación mínima de 1.5 mm |
    | Desde cero en el V6 | 0.16 % | 1.2 mm |
    | Al azar, escalas del sprint | 7.7 % | 12.8 mm |
    | Al azar, contrato v1 | 1.06 %, solo al caer | 4.3 mm |
- **Decisiones:**
  - La carrera no pausa y arranca siempre desde quieto: así lo hace `NaoRace-v0` (paso 56).
  - La recompensa castiga el choque entre piernas.
  - La demo del sprint no se toca: se reemplaza con la política de carrera en el paso 58b.
  - Detalle en el registro de errores, **E42**.
- **Errores en consola:** ninguno. En el paso 44 hubo un rechazo de la herramienta de escritura, que se registra como
  **E44**.
- **Siguiente:**
  - de acuerdo con el orden de la noche, el entorno de carrera (53–58) y el entrenamiento pesado del 59;
  - el paso 49 se corre mientras entrena.

### 2026-10-11 ~00:30 — Paso 49: contactos, de pie y barrido articular con el V6 (parte automática)
- **Autor:** Claude Code (noche autónoma). Sin commits.
- **Resultado:**
  - **`check_contacts`: OK.**
    - Penetración en reposo de 0.39 mm.
    - Penetración máxima de 4.79 mm al soltarlo desde 3 cm.
    - Rebote de 0.37 mm; 4 contactos por pie; solo los pies tocan el suelo.
  - **`check_standing`: OK.**
    - 10 s de pie con 1.7° de inclinación máxima.
    - 20/20 de pie con ruido de ±0.05 rad.
    - Resiste empujones de 0.1 s de 20 N hacia adelante, izquierda y derecha, y de 15 N hacia atrás.
  - **`joint_sweep`: OK.**
    - Las 23 articulaciones recorren su rango.
    - Las que no llegan al 100 % las detiene un choque real: hombro con la cadera (76 %), HipRoll con la otra pierna
      (87 %) y rodilla con la cadera (94 %).
    - Video: `videos/joint_sweep.mp4`.
- **Falta, para marcar `[x]`:** la revisión visual del usuario. Qué observar en `videos/joint_sweep.mp4`:
  1. cada articulación se mueve en el sentido que dice el letrero (convención de NAOqi);
  2. ninguna parte atraviesa a otra; los choques se ven como topes;
  3. HipRoll hacia adentro: las piernas se tocan antes del límite, como en el NAO real;
  4. los brazos no atraviesan el torso.
- **Errores en consola:** ninguno.

### 2026-10-11 ~00:05–00:45 — Pasos 53–58: entorno de carrera `NaoRace-v0`; 58b; lanzamiento de `carrera_v01`
- **Autor:** Claude Code (noche autónoma). Sin commits.
- **Qué se hizo: `src/envs/nao_race_env.py`, registrado como `NaoRace-v0`** (máximo 1250 pasos = 30 s).
  - **Observación (53):** los 54 valores del contrato v1, calculados con las funciones de `src/race/contract.py`.
  - **Acción (54):** 13 ángulos cada 24 ms (`FRAME_SKIP = 12`) con `contract.accion_a_objetivos`, presupuesto
    lateral incluido.
  - **Recompensa (55):**
    - 17 términos, con los pesos de `configs/carrera/pesos.yaml`, que ahora tiene `pesos` y `rangos` del barrido;
    - usa la `d`, la `psi` y la velocidad **reales**;
    - la salida de carril se mide con las esquinas de las suelas contra el borde interior de la línea (±35 cm);
    - la meta se mide con la punta del pie en x ≥ 5 m.
  - **Episodio (56):**
    - desde quieto, con colocación normal de σ 2 cm / 2° recortada a ±10 cm / ±8°;
    - **0.5 s de pie dentro de `reset`** para que la cámara mida; el reloj de marcha arranca en 0 al terminar;
    - el rumbo objetivo de la IMU es el que mide al arrancar;
    - fricción por pie sorteada;
    - sigue después de la meta.
  - **Cámara simulada (57):**
    - verdad + ruido gaussiano, retardo, pérdidas, mediciones malas y apagones, a 10 Hz;
    - se mantiene el último valor, con `EstadoCamara` del contrato;
    - cada episodio sortea sus parámetros dentro del rango de la sección 7.
  - **Pérdida de rectitud (58):** asimetrías por episodio, empujones, suelo inclinado, deriva y ruido de la IMU, y
    ruido de sensores (valores en la nota del paso 58 del `PLAN.md`).
- **Pruebas:**
  - **`scripts/check_race_env.py`: RESULTADO: OK, 30/30.**
    - Observación igual a `contract.armar_observacion`, con diferencia 0.0.
    - Acciones iguales al contrato.
    - Faltas y meta correctas.
    - Colocación con σ medida de 1.9 cm y 2.1°.
    - Reproducible con semilla.
    - Signos de la cámara correctos; estadística del ruido igual a la sorteada.
  - En la primera corrida dio FALLA por dos umbrales mal puestos en la prueba; ver **E43**.
  - **`scripts/check_camara_sim.py`: RESULTADO: OK.**
    - Cámara renderizada con la visión de carril/ en 25 poses de la pista (125 fotos, todas válidas).
    - Mismo signo que la convención.
    - Error rms de 1.05 cm y 0.72°, por debajo de lo que simula el entrenamiento: el entrenamiento es conservador.
- **Rendimiento:**
  - la primera versión hacía 3 pasadas por los contactos y `np.isin` por paso: ~0.95 ms por paso;
  - con una sola pasada (`_medir`) y una tabla de búsqueda: **0.61 ms por paso** (la física sola, 0.34 ms);
  - entrenamiento: ~2,300 pasos/s con 16 entornos, frente a 3,700 de `NaoWalk-v0`.
- **58b, la política nueva en los 3 carriles:**
  - `CorredorRLCarrera` en `demo/caminatas/carrera_vivo.py` (opción `--rl`). Por defecto usa
    `policies/carrera_v01/model.zip` si existe.
  - La política recibe `d` y `psi` **crudos** de su `VisionCamara`; se agregaron `d_crudo` y `psi_crudo`.
  - En la captura sin pantalla la cámara del RL estimó d = −2.1 cm con −2.2 cm reales.
  - `scripts/eval_carrera.py` evalúa con la colocación, el criterio de meta y las métricas de
    `demo/caminatas/benchmark.py`, para comparar directo con B-Human.
- **Paso 59, `carrera_v01` lanzado a las 00:26** (`configs/carrera_v01.yaml`, 60M pasos, fricción aleatoria,
  perturbaciones, `vx_cmd` 0.15–0.5).
  - A 1.9M pasos: 0 caídas y episodios de 29 s, pero **todavía no camina** (se queda de pie; seguimiento de vx de
    0.2).
  - Se revisa a los ~5M pasos.
- **Errores en consola:** E43 (umbrales de la prueba).
- **Decisiones:**
  1. `NaoWalkEnv` no se toca: lo usa la política del sprint en la demo.
  2. La meta del evaluador es la del benchmark (sitio del pie en x ≥ 5 m), para comparar con B-Human; la del
     entorno (punta del pie) se guarda como `t_meta_punta`.

### 2026-10-11 ~00:45–00:55 — Paso 48b: choques entre robots de carriles vecinos
- **Autor:** Claude Code (noche autónoma). Sin commits.
- **Qué se hizo:**
  - **`demo/caminatas/choques.py`** (`DetectorChoques`): las poses de los 3 robots, cada uno con su propia física, se
    copian a la escena de 3 carriles que ya usaba el visor para dibujar (`escena_tres`). `mj_forward` calcula los
    contactos, y todo contacto entre geometrías de robots distintos es un choque.
  - **`carrera_vivo`** lo revisa en cada cuadro y marca al robot como "CHOQUE CON OTRO ROBOT".
- **Simplificación:** no es física compartida completa. La detección es exacta, pero después del choque los robots
  no se empujan entre sí. Basta para la selección de agentes, porque un solo contacto ya descarta al agente.
- **Prueba (`scripts/check_choques_robots.py`): RESULTADO: OK.**
  - De pie en sus carriles: sin choques, a 34.8 cm entre RL y B-Human.
  - Corriendo al RL de a 1 cm: el choque aparece a los 35 cm. Su pie ya tocaba la línea a los 25.9 cm: **la salida
    de carril siempre llega antes que el choque**, como supone el diseño (sección 1.2).
- **Errores en consola:** ninguno.

### 2026-10-11 ~00:55 — Paso 50 bloqueado: faltan las herramientas para compilar el WalkingEngine original
- **Autor:** Claude Code (noche autónoma).
- **Qué se revisó:** compilar el runtime de PenaltyStack necesita CMake y Visual Studio 2022 Build Tools.
  - `which cmake cl` no los encuentra.
  - No existe `C:/Program Files*/Microsoft Visual Studio`.
- **Estado:** `[!]` en el `PLAN.md`. Instalarlos es una descarga y un cambio en el sistema, así que lo decide el
  usuario.
- **Mientras tanto:** la comparación contra B-Human usa la réplica tipo B-Human del benchmark: 16.2–16.9 s en 5 m con
  visión, ~0.30 m/s.

### 2026-10-11 ~00:45–01:05 — Paso 51: benchmark completo de los 3 carriles (150 corridas)
- **Autor:** Claude Code (noche autónoma). Sin commits.
- **Qué se hizo:** `uv run python -m demo.caminatas.benchmark --procesos 2`, en paralelo con el entrenamiento de
  `carrera_v01`.
  - Con solo 2 procesos para no quitarle CPU al entrenamiento: 3 caminatas × con/sin visión × μ (0.4, 0.6, 0.8, 1.0,
    1.2) × 5 semillas (1000–1004).
  - Resultados en `results/benchmark/` (`benchmark.md`, `benchmark.json`, `corridas.csv`, `trayectorias.png`).
- **Resultado:**
  - **Con visión, 25/25 metas sin faltas** para las tres:

    | Caminata | Tiempo a la meta | Velocidad |
    |---|---|---|
    | B-Human | **16.2–18.3 s** (el más lento, 18.3 s con μ 0.4) | ~0.27–0.31 m/s |
    | NAOqi | 45.3–49.9 s | ~0.10 m/s |
    | RL del sprint | 24.2–24.3 s | ~0.20 m/s |

  - **Sin visión:** B-Human 14/25, NAOqi 14/25, RL 15/25 metas; el resto son salidas de carril. Muestra otra vez que
    la cámara es imprescindible.
- **Meta de la noche:** el RL de carrera tiene que bajar de **16.2–18.3 s** con visión en las 5 fricciones.
- **Choques entre robots:** cada robot corre en su propia física. Por el paso 48b, un choque solo puede pasar después
  de salirse del carril, así que las salidas ya lo cubren.
- **Paso 52 (preparación):** `benchmark.py` tiene una caminata nueva, `rl_carrera` (`--rl-carrera <modelo>`), que
  usa la misma función que `scripts/eval_carrera.py` (`correr`). Las dos herramientas dan las mismas métricas con
  el mismo código. Se comprueba con un checkpoint.
- **Errores en consola:** ninguno.

### 2026-10-11 ~00:58–01:15 — `carrera_v01` a 5M pasos: ya le gana a B-Human con visión; E45; paso 52
- **Autor:** Claude Code (noche autónoma). Sin commits.
- **Evaluación del checkpoint de 5M** (`scripts/eval_carrera.py`, `vx_cmd` = 0.5, μ 0.4–1.2, semillas 1000–1001,
  colocación del benchmark; `results/carrera/carrera_v01/`):
  - **Con visión: 10/10 metas, 0 caídas, 0 salidas, en 9.2–10.2 s (~0.52 m/s).**
    - B-Human tarda 16.2–18.3 s en la misma batería.
    - Desvío máximo de 7–17 cm, rumbo máximo de 1.7–4.2°.
  - **Con perturbaciones** (asimetrías, empujones, suelo inclinado, deriva de la IMU), con visión, 4 semillas:
    **16/20 metas, 4 caídas, 0 salidas**, media de 9.9 s.
  - **Sin visión: 10/10 caídas a los 2.4–7.1 s.** Ver **E45**: `válido = 0` normalizado da −7.6, porque en
    entrenamiento la cámara casi nunca falta.
- **Decisión: `carrera_v02`** (`configs/carrera_v02.yaml`), con un solo cambio: más pérdida de visión.
  - 15 % de episodios sin cámara;
  - apagones en el 60 % de los episodios, de 1–8 s.

  Continúa desde un checkpoint de `v01` (el de 15M si sigue mejorando) y entrena el resto de la noche. Para eso, el
  entorno tiene `sin_vision_prob` y `camara.apagon_inicio_s`, que por defecto dejan a `v01` igual.
- **Paso 52:** `benchmark.py --rl-carrera` y `eval_carrera.py` dan las mismas 9 métricas, idénticas, para las mismas
  corridas (5M, μ 1.0 y 0.4).
- **Errores en consola:** ninguno.

### 2026-10-11 ~01:15–01:55 — `carrera_v01`: marcha, 10M pasos y perilla de velocidad
- **Autor:** Claude Code (noche autónoma). Sin commits.
- **Cómo camina el checkpoint de 5M** (μ 0.8, `vx_cmd` 0.5; `results/carrera/carrera_v01/marcha_lado_5M.png`):
  - pasos de verdad: levanta los pies 5–6 cm, ~2.1 pasos/s por pie (coincide con el reloj de 0.5 s);
  - 30 % de doble apoyo y 1 % de "vuelo";
  - torso erguido, brazos que se balancean;
  - 0.53 m/s.
- **Video de 3 carriles** (`demo/caminatas/video_carrera.py --rl-carrera <modelo>`), con μ 1.0 y semilla 1000:
  RL 9.2 s, B-Human 16.2 s, NAOqi 49.8 s.
- **Checkpoint de 10M** (misma batería):

  | Condición | Metas | Caídas | Salidas | Tiempo |
  |---|---|---|---|---|
  | Con visión | 9/10 | 0 | 1 (μ 0.4) | 10.0–10.3 s |
  | Sin visión | 0/10 | **0** | 10 | — |
  | Con perturbaciones y visión | 9/20 | 1 | 10 | — |

  - Sin visión ya no se cae (camina a ~0.3 m/s), pero se desvía y se sale.
  - Con visión el centrado empeoró respecto a 5M: desvío máximo de 17–21 cm contra 7–17 cm.
  - En el entrenamiento el episodio sigue 30 s (~15 m), así que muchas salidas pasan después de la meta.
- **Perilla de velocidad** (`vx_cmd`, sección 6.3), checkpoint de 5M, con perturbaciones y visión, 4 semillas × 5
  fricciones:

  | `vx_cmd` | Metas | Caídas | Salidas | Tiempo medio | Mejor |
  |---|---|---|---|---|---|
  | 0.50 | 16/20 | 4 | 0 | 9.9 s | — |
  | **0.40** | **20/20** | **0** | **0** | **12.35 s** | 12.0 s |
  | 0.30 | 20/20 | 0 | 0 | 16.8 s | 16.25 s |

  **Con 0.40 m/s ya hay una política que le gana a B-Human (16.2–18.3 s) sin faltas, incluso con perturbaciones.**

### 2026-10-11 ~01:58–02:10 — `carrera_v01` a 15M: el mejor; se detiene y arranca `carrera_v02`
- **Autor:** Claude Code (noche autónoma). Sin commits.
- **Checkpoint de 15M** (`results/carrera/carrera_v01/eval_model_15000000_steps_*`):

  | Condición | Metas | Faltas | Tiempo | Desvío máximo |
  |---|---|---|---|---|
  | Con visión, `vx_cmd` 0.5 | **10/10** | 0 | **10.5–10.6 s** | **3.4–5.6 cm** (5M: 7–17 cm) |
  | Con perturbaciones, `vx_cmd` 0.5 | **20/20** | 0 | 11.15 s de media (mejor 10.7 s) | — |
  | Con perturbaciones, `vx_cmd` 0.40 | 20/20 | 0 | 13.6 s | — |
  | Sin visión | 0/10 | 6 caídas, 4 salidas | — | — (avanza apenas 0.03–0.11 m/s) |

  Con visión, este checkpoint pasa el filtro duro de la sección 11.4 también con perturbaciones; el de 5M no (4
  caídas). **Se guarda el de 15M en `policies/carrera_v01/`**, reemplazando al de 5M que se había guardado a las
  02:00.
- **Decisión: detener `carrera_v01` en 15.3M pasos** (`taskkill` del árbol de procesos; los checkpoints de 5, 10 y
  15M están guardados) y dedicar el resto de la noche a `carrera_v02`.
  - Motivo: con visión ya le gana a B-Human por ~6 s, con 0 faltas.
  - Lo que falta es no depender de la cámara (E45). Seguir con `v01` no lo arregla: en `v01` la cámara casi nunca
    falta.
- **`carrera_v02` lanzado a las 02:05** desde el checkpoint de 15M de `v01`: 40M pasos, ~2,800 pasos/s, ~4 h.
  - Un solo cambio respecto a `v01`: 15 % de episodios sin cámara; apagones en el 60 % de los episodios, de 1–8 s,
    desde el arranque.
  - Semilla 2.
  - El primer intento falló por **E46** (`--continuar` no reconocía la normalización de un checkpoint), corregido en
    `src/train.py`.
- **Visor y video:** `carrera_vivo.py` y `video_carrera.py` usan la política de carrera con `--rl-vx` (por defecto
  0.40, el valor sin faltas con perturbaciones).

### 2026-10-11 ~02:10 — Paso 58: prueba de rectitud de 100 episodios con `carrera_v01` (15M)
- **Autor:** Claude Code (noche autónoma). Sin commits.
- **Qué se hizo:** `scripts/eval_carrera.py --modelo policies/carrera_v01/model.zip --vx 0.40 --semillas 20
  --perturbaciones`.
  - Con perturbaciones: asimetrías, empujones, suelo inclinado, deriva de la IMU.
  - 5 fricciones × 20 semillas = 100 episodios con visión y 100 sin visión.
  - Resultados en `results/carrera/carrera_v01/rectitud_58/`.
- **Resultado:**

  | Condición | Metas | Caídas | Salidas | Tiempo | Desvío máximo medio | Rumbo máximo medio |
  |---|---|---|---|---|---|---|
  | **Con visión** | **100/100** | 0 | 0 | **13.2 ± 0.7 s** | **7.8–8.6 cm** | 5.7–6.1° |
  | Sin visión | 0/100 | 45 | 47 | — | 15–17 cm | 16.5–19.2° |

  Sin visión, la política casi no avanza (0.03–0.05 m/s) y termina cayéndose o saliéndose. La "deriva sin visión"
  todavía no es una medida de la marcha, sino del problema E45. Se repite con `carrera_v02`.
- **Lectura:** con visión, la política es rápida y robusta. Le sobran ~3–5 s contra B-Human aun con `vx_cmd` 0.40 y
  perturbaciones.

### 2026-10-11 ~02:12–02:20 — Paso 58b: la política de carrera con la cámara renderizada, en lazo cerrado
- **Autor:** Claude Code (noche autónoma). Sin commits.
- **Qué se hizo:** `CorredorRLCarrera` (el mismo que usa `run_demo.py --live`), corrido sin pantalla hasta el final.
  - La política recibe `d`, `psi` y válido **crudos** de su cámara inferior renderizada y de la visión de `carril/`,
    a 10 Hz.
  - Sin cámara simulada ni truco del giroscopio.
  - 18 corridas: μ 0.4/0.8/1.2 × semillas 1000–1002 × `vx_cmd` 0.40 y 0.5.
  - Resultados en `results/carrera/carrera_v01/camara_renderizada_58b.json`.
- **Resultado: 18/18 metas, 0 faltas.**
  - 12.7–12.8 s con `vx_cmd` 0.40 y 10.3–10.5 s con 0.5.
  - Desvío máximo de 1.4–8.8 cm.
  - La política entrenada con la cámara simulada funciona igual con la visión real del pipeline, como anticipaba
    `check_camara_sim.py` (el error real es menor que el simulado).
- **Video para revisar:** `videos/carrera_v01_3carriles.mp4` (`video_carrera.py --rl-carrera policies/carrera_v01/model.zip
  --rl-vx 0.40`), con μ 1.0 y semilla 1000: **RL 12.7 s, B-Human 16.2 s, NAOqi 49.8 s**.
- **Para el usuario (pasos 56 y 58b).** Qué observar:
  1. en `videos/carrera_v01_3carriles.mp4`, el RL (centro) arranca desde quieto, da pasos reales (no se arrastra ni
     salta), va recto y llega primero;
  2. en `uv run python demo/run_demo.py --live`, el carril central usa la política nueva con su cámara (la ventana
     "Lo que ve cada NAO" muestra su `d`/`psi` estimados) y llega a la meta sin salirse;
  3. que la postura y el balanceo de brazos se vean naturales; si algo se ve raro (por ejemplo, rodillas muy
     dobladas o pies que se cruzan), anotarlo.

### 2026-10-11 ~02:15–02:20 — Paso 60: lanzador de barridos de agentes
- **Autor:** Claude Code (noche autónoma). Sin commits.
- **Qué se hizo:** `scripts/barrido.py`.
  - **Sorteo por agente**, reproducible con `--semilla` y el número de agente:
    - pesos uniformes dentro de los `rangos` del YAML, con choque_robot = 2 × salida;
    - fricción mínima U(0.3, 0.5) y máxima U(1.0, 1.3);
    - `vx_max` U(0.40, 0.60);
    - σ máximos de la cámara U(3, 6) cm y U(3, 5)°;
    - semilla de PPO.
  - **Por agente:** `config.yaml` completa, entrenamiento con `--continuar` desde la base, log, evaluación con la
    batería (visión + perturbaciones, μ 0.4–1.2) y `resultado.json`.
  - **Puntaje de la sección 11.4:** filtro duro y luego media + 1 σ del tiempo; desempate por desvío.
  - Escribe `tabla.md` ordenada.
  - **Reanudable:** salta a los agentes evaluados y repite los entrenamientos que quedaron a medias.
- **Prueba:** 4 agentes de 20k pasos con 4 entornos (`results/barridos/prueba_paso60/`).
  - 4/4 completos, ~50 s cada uno; los 4 pasan el filtro con 11.7–12.2 s (`eval_vx` 0.45).
  - Al relanzar, los 4 se saltan.
  - Con 20k pasos los agentes casi no se apartan de la base: la prueba valida el mecanismo, no compara pesos.
- **Costo estimado de la ronda 1 (paso 61):** 100 agentes × 1M pasos a ~2,700 pasos/s ≈ 6 min de entrenamiento +
  ~1 min de evaluación por agente, es decir **~11–12 h** en este PC. No cabe esta noche junto con `carrera_v02`; se
  propone correrlo en otra noche (decisión del usuario).
- **Errores en consola:** ninguno.

### 2026-10-11 ~02:20–02:35 — Paso 55: orden de comportamientos de la recompensa (FALLA parcial, E47)
- **Autor:** Claude Code (noche autónoma). Sin commits.
- **Qué se hizo:** `scripts/check_recompensa_carrera.py` (resultado en `results/carrera/orden_recompensa.json`).
- **Resultado:**
  - Rápido y limpio (2307) > lento y limpio (547): **OK**.
  - Salirse es peor que ir lento para toda salida hasta los 4.3 m.
  - **No** a 4.8–4.9 m: 579–597 > 547.
  - Con descuento 0.99, cualquier salida después de 4 s "vale más" que ir lento.
- **Decisión:** paso 55 marcado `[!]`; nuevo **paso 55b**, con `salida_carril` ≤ −300, en su propia generación. Mientras
  tanto, el filtro duro de la selección garantiza que no pase ninguna política con salidas.
- **Errores:** E47. El script falló dos veces antes de medir bien (empujón que tumba; sesgo aplicado después de
  `predict`); detalle en E47.

### 2026-10-11 ~02:37–02:50 — `carrera_v02` a 5M pasos: ya no se cae sin visión
- **Autor:** Claude Code (noche autónoma). Sin commits.
- **Evaluación** (`results/carrera/carrera_v02/`, μ 0.4–1.2):

  | Batería | Con visión | Sin visión |
  |---|---|---|
  | Nominal, `vx_cmd` 0.5, 2 semillas | **10/10**, 10.1–10.2 s, desvío máximo de 5–7 cm | **7/10 metas, 0 caídas**, 3 salidas (desvío de 12–27 cm) |
  | Perturbaciones, `vx_cmd` 0.5, 4 semillas | **20/20**, 10.2–10.4 s, desvío de 13–14 cm | 9/20, **0 caídas**, 11 salidas |
  | Perturbaciones, `vx_cmd` 0.40, 4 semillas | **20/20**, 12.2 s, desvío de 15–16 cm | 6/20, **0 caídas**, 14 salidas |

- **Lectura:**
  - **La hipótesis de `v02` se confirma:** sin visión pasó de 10/10 caídas (`v01`) a 0 caídas, y camina a
    ~0.48 m/s solo con la IMU.
  - Sin cámara deriva ~20 cm en 5 m. Con perturbaciones se sale en ~50 % de las corridas, contra ~45 % de B-Human sin
    visión en el benchmark.
  - **Costo:** con visión y perturbaciones el desvío máximo subió de ~8 cm (`v01`, `vx_cmd` 0.40) a 13–16 cm. Sigue
    sin salidas.
- Se sigue entrenando; se evalúa cada 5M.

### 2026-10-11 ~03:05–04:35 — `carrera_v02` de 10M a 25M pasos
- **Autor:** Claude Code (noche autónoma). Sin commits.
- **Evaluación de cada checkpoint:** misma batería que a 5M (`results/carrera/carrera_v02/`). La tabla completa de
  la noche está en `results/carrera/resumen.md` (`scripts/resumen_carrera.py`).

  | Checkpoint | Visión, nominal | Visión + pert. 0.5 | Visión + pert. 0.40 | Sin visión, nominal | Sin visión + pert. 0.40 |
  |---|---|---|---|---|---|
  | 10M | 10/10, 10.1 s | 20/20, 10.4 s | 20/20, 12.5 s | 5/10 | 5/20 |
  | **15M** | 10/10, 10.6 s | **20/20**, 10.85 s | **20/20**, 13.1 s | **10/10**, 11.0 s | 14/20 |
  | 20M | 10/10, 9.8 s | 15/20 (5 salidas) | **20/20**, 12.6 s | **10/10**, 10.2 s | 16/20 |
  | 25M | 10/10, 10.0 s | 14/20 (1 caída, 5 salidas) | 15/20 (5 salidas) | 6/10 | 15/20 |

  Ningún checkpoint se cae sin visión; solo 25M tiene una caída, con visión y perturbaciones.
- **Lectura:**
  - **15M y 20M** son los mejores. Sin visión, sin perturbaciones, ya pasan el filtro: 10/10.
  - Los checkpoints oscilan; 25M empeora. Por eso se elige por batería y no por el último checkpoint.
- **03:40:** se guardó el de 15M como `policies/carrera_v02/`, provisional.
- **Selección:** batería grande (100 episodios por condición, `vx_cmd` 0.40, con perturbaciones) para 15M y 20M, en
  `results/carrera/carrera_v02/seleccion_100/`.

### 2026-10-11 ~04:35–04:55 — Selección de `carrera_v02`: el checkpoint de 15M
- **Autor:** Claude Code (noche autónoma). Sin commits.
- **Batería grande** (`results/carrera/carrera_v02/seleccion_100/`): `vx_cmd` 0.40, con perturbaciones, 5 fricciones
  × 20 semillas por condición.

  | Checkpoint | Con visión | Tiempo con visión | Sin visión |
  |---|---|---|---|
  | **15M** | **100/100**, 0 faltas | 13.0 ± 0.5 s | **89/100**, 0 caídas, 11 salidas |
  | 20M | **100/100**, 0 faltas | 12.5 ± 0.55 s | 86/100, 0 caídas, 14 salidas |
  | `v01` (15M), referencia | 100/100 | 13.2 ± 0.7 s | 0/100: 45 caídas, 47 salidas |

- **Elección: 15M** (`policies/carrera_v02/`, guardado a las 03:40).
  - Por la sección 11.4 (tiempo + 1σ con visión a 0.40), 20M sería algo mejor: 13.05 contra 13.5 s.
  - Pero 15M es el único que también pasa el filtro con visión y perturbaciones a `vx_cmd` 0.5 (20/20 contra 15/20).
    Esto da margen para subir la perilla en el robot real.
  - Sin visión es igual o algo mejor.
  - La diferencia de tiempo, ~0.5 s, es menor que la ventaja sobre B-Human, de ~3.5 s.
- **`carrera_v02` contra `carrera_v01`:** mismo desempeño con visión (13.0 contra 13.2 s), y sin visión pasa de 0/100 a
  **89/100 sin caídas**. Se confirma la hipótesis de `v02` (E45).
- **Lazo cerrado con la cámara renderizada** (`CorredorRLCarrera`, 36 corridas;
  `results/carrera/carrera_v02/camara_renderizada_58b.json`):

  | Condición | Metas | Tiempo |
  |---|---|---|
  | Con cámara, `vx_cmd` 0.40 | 9/9 | 12.7 s |
  | Con cámara, `vx_cmd` 0.5 | 9/9 | 10.5–10.7 s |
  | Sin cámara, `vx_cmd` 0.40 | 9/9 | 13.5–13.7 s |
  | Sin cámara, `vx_cmd` 0.5 | 9/9 | 11.0 s |

  - Desvío máximo de hasta 17.7 cm con cámara (`v01`: 8.8 cm) y de hasta 23.9 cm sin cámara.
- **Costo de `v02`:** se aleja más del centro, porque confía menos en la cámara. Sigue sin salidas con visión, pero
  el margen lateral es menor. Es candidato para la siguiente generación (por ejemplo, con el castigo de salida del
  paso 55b).

### 2026-10-11 ~05:30–06:05 — `carrera_v02` terminado (40M); se queda el de 15M; cierre de la noche
- **Autor:** Claude Code (noche autónoma). Sin commits.
- **Checkpoints finales** (con visión y perturbaciones, `vx_cmd` 0.5):

  | Checkpoint | Metas | Faltas |
  |---|---|---|
  | 30M | 19/20 | 1 salida |
  | 35M | 15/20 | 5 salidas |
  | 40M (final) | 15/20 | 4 caídas, 1 salida |

  El final es el más rápido sin perturbaciones (9.6 s), pero el menos robusto (**E48**).
- **Políticas de la noche:**

  | Política | Origen | Uso | Con visión (`vx_cmd` 0.40, perturbaciones) | Sin visión |
  |---|---|---|---|---|
  | `policies/carrera_v01/` | 15M de `v01` | La más recta (desvío ~8 cm) | 100/100, 13.2 s | Inútil |
  | **`policies/carrera_v02/`** | 15M de `v02` | **Recomendada** | **100/100, 13.0 s** | **89/100, 0 caídas** |

  Las dos llegan con la cámara renderizada. B-Human: 16.2–18.3 s con visión.
- **Estado de los pasos:**
  - 42–48b, 51–54, 57, 59, 59b y 60: hechos.
  - 49, 56, 58 y 58b: esperan la revisión del usuario.
  - 50: bloqueado.
  - 55: `[!]` → 55b.
  - **Siguiente en orden: 61** (100 agentes, ~11–12 h): decidir cuándo correrlo.
- **Para la revisión del usuario:**
  - `videos/carrera_v01_3carriles.mp4`;
  - `uv run python demo/run_demo.py --live` (usa `policies/carrera_v02` con su cámara);
  - `videos/joint_sweep.mp4` (paso 49).

  Las listas de qué observar están en las entradas de los pasos 49 y 58b.

### 2026-10-11 (mañana) — Capítulo del entrenamiento por RL; regla "mejor que sobre documentación a que falte"; E49
- **Autor:** Claude Code, a pedido de Camilo.
- **Indicación del usuario:** el entrenamiento es el paso más importante. Cada mínimo dato del RL tiene que estar
  documentado: cómo funcionó, datos, pesos, variables, qué se cambió y cómo fueron las pruebas. Regla nueva del
  proyecto: **"mejor que sobre documentación a que falte"**.
- **Qué se hizo:**
  - **[`docs/paper/entrenamiento_rl.md`](paper/entrenamiento_rl.md)**, capítulo nuevo del paper:
    - observación (54 variables, con sensor, escala y normalización);
    - acción (13 articulaciones y límites);
    - episodio, perturbaciones y cámara simulada (valores de `v01` y `v02`);
    - los 17 términos de la recompensa, con fórmula, peso y aporte medido;
    - PPO y todos sus parámetros, máquina y versiones, y la versión del código;
    - etapas del aprendizaje de las dos generaciones;
    - todas las baterías y resultados, y la selección;
    - qué aprendió la política;
    - fallos, lo que no se hizo, cómo reproducirlo y las huellas SHA-256 de las políticas.
  - **`scripts/exportar_curvas.py`:** exporta todas las curvas de TensorBoard a `results/` (`runs/` no se versiona).
    - `carrera_v01`: 37 curvas, 61,184 puntos;
    - `carrera_v02`: 37 curvas, 161,097 puntos;
    - en `results/carrera/carrera_v0N/curvas_entrenamiento.{csv,png}`.
  - **`results/carrera/analisis_politicas.json`:** estadísticas de normalización de las 54 observaciones, uso de cada
    acción y métricas de la marcha de las dos políticas.
- **Hallazgos nuevos:**
  - **E49:** la política usa acciones saturadas (brazos fijos y asimétricos, caderas hacia adentro en el límite).
    **Corrige** el "brazos que se balancean" de la entrada de la madrugada.
  - **Retroceso de `v01` entre 9 y 11M pasos** (salidas del 29 %, retorno de ~2,000 a ~1,300), visto en las curvas.
    Explica el checkpoint de 10M. Se agregó a E48.
  - Los dos runs registran `git_commit: ea5e992-modificado`: se entrenó con código sin confirmar. Lo que cambió entre
    `v01` y `v02` quedó en la sección 7 del capítulo.
- **Memoria del asistente:** se guardó la regla para futuras sesiones.

### 2026-10-11 (mañana) — ¿Los brazos fijos se deben al RL? Sí, y la política los necesita
- **Autor:** Claude Code, a pregunta de Camilo.
- **Prueba:** las dos políticas con los hombros forzados a la pose de pie (acción 0). μ 0.4/0.8/1.2 × semillas
  1000–1003, `vx_cmd` 0.40, con visión, con y sin perturbaciones (`results/carrera/prueba_brazos_home.json`):

| Política | Brazos | Sin perturbaciones | Con perturbaciones | Rumbo medio |
|---|---|---|---|---|
| `v01` | Los aprendidos | 12/12, 12.8 s | 12/12, 13.6 s | +0.5° |
| `v01` | Forzados a la pose de pie | 12/12, **17.5 s** | 12/12, **20.6 s** | **+3.5°** |
| `v02` | Los aprendidos | 12/12, 12.7 s | 12/12, 13.1 s | −1.5° |
| `v02` | Forzados a la pose de pie | **0/12, se cae** | **0/12, se cae** | +4.3° |

- **Conclusión:**
  - la postura de los brazos es aprendida por el RL y forma parte del equilibrio y del control del rumbo;
  - no hay ningún premio por balancearlos, moverlos cuesta, y fijos sirven de contrapeso;
  - para tener brazos naturales hay que pedírselo al RL en una generación propia (premio a balancear los brazos en
    fase con las piernas, o límites menores). Quitarlos a la fuerza tumba a `v02`.
- Agregado a E49 y a la sección 12 de `docs/paper/entrenamiento_rl.md`.

### 2026-10-11 (mañana) — README: sección "Dónde está toda la información"
- **Autor:** Claude Code, a pedido de Camilo.
- **Pedido:** que quien llegue al repo encuentre toda la información en un solo lugar, sin sobrecargar el README:
  enlaces a los documentos con una explicación corta.
- **Qué se hizo:**
  - nueva sección del README, justo después del estado del proyecto, enlazada desde el índice ("0.") y desde el
    estado;
  - tablas por tipo: para empezar, diseño, material del paper, resultados y datos, políticas y configuraciones, y
    fuera de git;
  - 32 enlaces revisados con un script, ninguno roto.
- **Regla nueva:** punto 6 del protocolo en `CLAUDE.md`. Todo documento, resultado, política o config nueva se agrega
  a esa sección en el mismo paso.

### 2026-10-11 (mañana) — Salidas malas (E50) y estado del silbato
- **Autor:** Claude Code, a pregunta de Camilo: "¿se varió el ángulo de salida?" y "¿cómo vas con el silbato de
  PenaltyStack?".
- **Colocación en el entrenamiento de anoche:** sí se varió.
  - Corrimiento ~N(0, 2 cm), recortado a ±10 cm.
  - Rumbo ~N(0, 2°), recortado a ±8°.
  - Pero casi siempre son salidas buenas: 8° es 4σ.
- **Prueba de salidas malas** (`results/carrera/carrera_v02/salida_mala.json`):

| Colocación | Con visión | Sin visión |
|---|---|---|
| Recto (0°), corrido 0, ±10 o ±15 cm | 10/10, 12.7–13.0 s | 10/10, 13.7 s |
| +8° | 6/10 (solo con y = 0, −10 y −15 cm) | 0/10 |
| −8° | 0/10, salidas | 0/10 |
| ±15° y ±25° | 0/20, salidas a los 2–5 s | 0/20 |

- **Causa y prueba (E50):** el rumbo objetivo de la IMU es el rumbo con que arrancó, así que le pide mantener el
  ángulo equivocado.
  - Fijándolo a la dirección del carril (rumbo al arrancar − `psi` de la cámara), sin reentrenar, llega en **12/12
    salidas torcidas hasta ±25°**.
  - Nuevo **paso 58c** en el `PLAN.md`.
- **Silbato:** revisión de PenaltyStack (`gh api`, 2026-10-11).
  - Último commit `9c08a41` (2026-10-07), el mismo que se revisó el 2026-10-08.
  - Ramas: `codex/mejora-portero`, `feat/bhuman-simulation` y `feat/rl-contracts`.
  - Lo único relacionado es la **estructura de datos `Whistle` de B-Human**
    (`baseline/bhuman/Src/Representations/Modeling/Whistle.h`: confianza, canales y momento de la última detección),
    copiada con el baseline.
  - **No está el módulo que detecta el silbato** (en B-Human, el que procesa el audio) ni un proveedor de audio; nada
    en el código de penales lo usa.
  - El arranque de PenaltyStack sigue siendo el táctil frontal de la cabeza 0.25 s.
  - En este repo el silbato no está implementado: el plan actual es la activación manual (táctil), que cumple el
    reglamento.
  - Queda a decisión del equipo si se implementa un detector automático.

### 2026-10-11 ~12:00–12:45 — Paso 58c: rumbo de la IMU alineado al carril; lanzamiento de `carrera_v03`
- **Autor:** Claude Code, con Camilo.
- **Pedido del usuario:**
  - seguir con los RL, primero con salidas torcidas, para confirmar que la cámara corrige al robot sin importar cómo
    arranque;
  - **el silbato se pospone** hasta hablar con Luis Mario. Queda como paso 68b.
- **Revisión previa (protocolo):**
  - `git pull`: al día; último commit `d9733e5`, del usuario, con los pasos 44–60;
  - 0 enlaces rotos en los `.md`;
  - se anotó el commit en `historial_pasos.md`;
  - el `PLAN.md` no tenía paso del silbato: se agregó el 68b.
- **Qué se hizo (58c):**
  - **`src/race/contract.py`:** `rumbo_objetivo_inicial(rumbo_imu, psi_mediciones)`, compatible con Python 2.7, para
    el robot.
  - **`NaoRace-v0`:**
    - parámetro `rumbo_objetivo` (`carril`, nuevo default; `arranque` = como antes);
    - guarda las `psi` medidas de pie y las usa al arrancar;
    - `configs/carrera_v01.yaml` y `carrera_v02.yaml` quedan con `rumbo_objetivo: arranque`, para reproducirlas tal
      como se entrenaron.
    - Las políticas guardadas en `policies/` no tienen esa clave, así que **ahora se evalúan con `carril`**. Las
      evaluaciones anteriores se hicieron con `arranque`.
  - **`demo/caminatas/carrera_vivo.py`:** el corredor RL alinea la IMU con la primera foto de su cámara renderizada.
  - **`scripts/eval_carrera.py`:** opciones `--rumbo-objetivo` y colocación fija (`correr(..., colocacion=...)`).
  - **`scripts/eval_salida_mala.py` (nuevo):** batería de 70 salidas malas (y 0/±10/±15 cm × rumbo
    0/±8/±15/±25°), con y sin visión.
  - **Pruebas:**
    - `check_contract.py` en OK, con 3 pruebas nuevas; la primera vez falló por redondeo en la prueba (**E51**);
    - `check_race_env.py` en OK, con la sección 7 nueva: arrancando girado +15°, el error de rumbo de la IMU es
      −14.6°, o sea que apunta al carril.
- **Resultado con `v02` sin reentrenar** (`results/carrera/carrera_v02/salida_mala_model_*.md`):

| Rumbo objetivo de la IMU | Con visión (70 salidas) | Sin visión (70) |
|---|---|---|
| `arranque` (como se entrenó `v02`) | 16/70 metas, 54 salidas | 10/70 (solo las salidas rectas) |
| **`carril` (paso 58c)** | **69/70 metas**, 1 caída (y −15 cm, rumbo −25°), 0 salidas; 12.7–13.5 s | 10/70 (solo las salidas rectas) |

- **`carrera_v03` lanzado a las 12:40** (`configs/carrera_v03.yaml`, desde `policies/carrera_v02`, 20M pasos, ~2 h,
  semilla 3).
  - **Un solo cambio respecto a "v02 + 58c":** colocación de entrenamiento con σ 6 cm / 10°, máximo ±15 cm / ±25°
    (antes, σ 2 cm / 2°, máximo ±10 cm / ±8°).
  - **Hipótesis:** viendo salidas malas, las corrige también con perturbaciones y fricción baja, sin caerse en los
    casos extremos y sin perder velocidad en las salidas buenas.
- **En curso:** batería de salidas malas con perturbaciones (μ 0.4 y 1.2) para `v02` + 58c, como referencia de `v03`.
- **Siguiente:** evaluar `v03` cada 5M con la batería de salidas malas y la batería grande; cerrar 58c y 59c.

### 2026-10-11 ~13:05–14:45 — `carrera_v03` terminado; se elige el de 5M; paso 58c cerrado
- **Autor:** Claude Code, con Camilo.
- **Referencia "`v02` + 58c" con perturbaciones** (`results/carrera/carrera_v02/salida_mala_model_carril_pert.md`):
  - con visión: 128/140, 12 caídas (en +15° y +25°), 0 salidas;
  - sin visión: 19/140.
- **`carrera_v03`:** 20M pasos en 1.65 h (3,375 pasos/s), 12:40–14:18. Curvas en
  `results/carrera/carrera_v03/curvas_entrenamiento.{csv,png}`: planas, porque parte de una política que ya camina.
- **Checkpoints:**

| Checkpoint | Salidas malas, sin perturb. (70) | Salidas malas, con perturb. (140) | Batería grande, con visión (100) | Batería grande, sin visión (100) |
|---|---|---|---|---|
| `v02` + 58c (referencia) | 69/70 (1 caída) | 128/140 (12 caídas) | 100/100, 13.0 s | 89/100 |
| **`v03` 5M (elegido)** | **70/70** | 135/140 (5 caídas) | **100/100, 12.8 ± 0.4 s, desvío 7.4 cm** | 82/100, 0 caídas |
| `v03` 10M | 70/70 | 137/140 (3 caídas) | 98/100 (2 salidas) | 87/100 |
| `v03` 15M | 70/70 | 122/140 (18 salidas) | — | — |
| `v03` 20M (final) | 69/70 (1 salida) | 133/140 (3 caídas, 4 salidas) | — | — |

- **Elegido: 5M** → `policies/carrera_v03/`.
  - Único que pasa el filtro de la batería grande.
  - Más rápido (12.8 contra 13.0 s) y más recto (7.4 contra ~10 cm) que `v02`.
- **Cámara renderizada real** (`results/carrera/carrera_v03/camara_renderizada_salida_mala.json`): 30/30 salidas
  malas (y 0/±15 cm × rumbo 0/±15/±25° × μ 0.4/1.2), en 12.3–12.9 s, con desvío máximo de 23.3 cm. **Confirma que la
  cámara corrige al robot sin importar cómo arranque.**
- **Pasos:**
  - **58c `[x]`:** 70/70 salidas malas con visión.
  - **59c `[!]`:** con perturbaciones quedan 5 caídas, todas el mismo caso (−25°, μ 0.4, semilla 1001); E52. Se acepta
    el de 5M. El paso 59d queda como opción.
- **Qué aprendió `v03`:** igual que `v02` (brazos fijos y RHipRoll en el límite; E49 sigue). Marcha con 28.5 % de
  doble apoyo y 2.03 pasos/s por pie.
- **Documentación:**
  - capítulo `docs/paper/entrenamiento_rl.md` (secciones 12c y 12d, huellas y comandos);
  - `PLAN.md` (58c, 59c y paso actual);
  - README (estado, tabla de carriles y mapa);
  - registro de errores (E52);
  - historial.
- **Siguiente:**
  - paso 61, ronda de 100 agentes (~11–12 h), cuando el usuario decida; la base sería `policies/carrera_v03`;
  - pendientes de revisión: 49, 56, 58 y 58b;
  - silbato pospuesto (68b).

### 2026-10-11 ~14:30–14:50 — Paso 55b (castigo de salida −300) y lanzamiento de la ronda 1 de 100 agentes (paso 61)
- **Autor:** Claude Code. Camilo se ausenta 10 h; pidió terminar lo pendiente y dejar un entrenamiento pesado.
- **Revisión previa (protocolo):**
  - `git pull` al día; último commit `5a5c01d` (pasos 58c y 59c), del usuario;
  - árbol limpio; 0 enlaces rotos en la última revisión.
- **Paso 55b:**
  - `salida_carril` −200 → −300 y rango [−400, −300]; `choque_robot` −600.
  - `check_recompensa_carrera.py` ahora recibe `--modelo`:
    - con `carrera_v03`, **OK** (lento 1264; la salida de mayor retorno queda por debajo);
    - con `carrera_v01`, FALLA: haría falta < −452. El umbral depende de la política (**E53**).
  - Se marca hecho con la política que se usa. La garantía de 0 salidas es el filtro duro.
- **Paso 61, ronda 1 de 100 agentes:**
  - **Lanzador:** `scripts/barrido.py`, cambiado para esta ronda:
    - base `configs/carrera_v03.yaml` + `policies/carrera_v03` (antes, `v01`);
    - el ruido de la cámara se **mezcla** con la de la base (antes la reemplazaba y se perdían los apagones de `v02`);
    - batería corta con 4 salidas torcidas;
    - pide a Windows no suspender el PC mientras corre (`SetThreadExecutionState`, sin cambiar la configuración).
  - **Prueba de humo:** 1 agente de 20k pasos (`results/barridos/prueba_paso61/`). Config correcta: apagones de la
    base, colocación amplia, rumbo `carril`, salida −327 sorteada. 9/9 metas.
  - **Lanzado a las 14:36:** `--nombre ronda1 --agentes 100 --pasos 1000000 --eval-semillas 2`.
    - ~6 min por agente (5.5 min de entrenamiento a ~3,000 pasos/s + evaluación); fin estimado hacia las 00:35.
    - Log general en `runs/barrido_ronda1.log` (no se versiona); por agente, en
      `results/barridos/ronda1/agente_NNN/`.
  - **Referencia, la base con la misma batería** (`results/barridos/ronda1/base_carrera_v03.json`): pasa, 0 faltas,
    **puntaje 12.41 s** (media 11.88 s + 1σ), desvío máximo de 14.3 cm.
  - **Agente 000:** descartado, con 2 caídas en las salidas torcidas de −15° y −25°.
- **Diseño:** la sección 11.1 de `plan_rl_carrera.md` ahora dice qué sortea de verdad la ronda 1. La tabla 6.4 y la
  sección 1.2 quedan con −300.
- **Siguiente:** revisar la ronda a medio camino; al terminar, tabla de los 100, los 20 mejores y el análisis de
  qué pesos ganan (pasos 61–62).

### 2026-10-11 16:48 — Ronda 1 (paso 61): revisión a los 25 agentes
- **Autor:** Claude Code (Camilo ausente).
- **Estado:** 25/100 agentes en 2 h 12 min (~5.3 min por agente); sin errores.
- **Resultado parcial** (`scripts/analizar_barrido.py --nombre ronda1` → `results/barridos/ronda1/analisis.md`):
  - 18/25 pasan el filtro duro;
  - 12 superan a la base `carrera_v03` (12.41 s);
  - el mejor, `agente_023`, saca 11.62 s (t medio 11.33 s).
- **Descartes:** 9 de las 11 corridas con falta son caídas en las salidas torcidas; 1 caída en la batería normal y 1
  salida.
- **Correlaciones tempranas** (Spearman con el puntaje entre los que pasan; con 18 agentes, solo indicativas):
  - `rumbo` +0.43: más peso al rumbo, más lento;
  - `friccion_max` +0.53: entrenar con fricción máxima más baja, mejor;
  - `barrera_margen` −0.29 y `vel_lateral` −0.25.
- **Siguiente:** revisión a los 60 agentes.

### 2026-10-11 19:59–20:20 — Ronda 1 a los 60 agentes; ronda 2 (paso 62) preparada y encadenada
- **Autor:** Claude Code (Camilo ausente).
- **Ronda 1 a los 60 agentes** (19:59, sin errores, ~5.4 min por agente; fin estimado ~23:35):
  - **42/60 pasan** el filtro duro;
  - **28 superan a la base** `carrera_v03` (12.41 s);
  - mejores: `agente_045` 11.43 s, `agente_026` 11.45 s, `agente_037` 11.62 s y `agente_023` 11.62 s.
- **Descartes** (30 corridas con falta en 18 agentes): 17 caídas en salidas torcidas, 8 caídas y 5 salidas en la
  batería normal, y 4 salidas en salidas torcidas.
- **Correlaciones** (Spearman, 42 agentes): se debilitaron frente a los 25 agentes. Las mayores en valor absoluto:
  - `inclinacion` −0.35 (castigar más la inclinación, mejor);
  - `rumbo` +0.28;
  - `vx_max` −0.21.

  Todavía no hay un peso dominante.
- **Paso 62 preparado:** `scripts/ronda_siguiente.py`.
  - Los mejores (`mejores.json`, que escribe `scripts/analizar_barrido.py`) siguen entrenando **con su propia config**
    desde su modelo final de la ronda anterior.
  - Se evalúan con la **batería completa** (44 corridas: 5 μ × 4 semillas + 12 salidas torcidas × μ 0.4 y 1.0, con
    perturbaciones y `vx_cmd` 0.45).
  - Mismo formato de resultados y reanudable.
  - **Prueba:** 1 agente (`agente_045`) de 20k pasos → 44 corridas, pasa, 11.96 s
    (`results/barridos/prueba_paso62/`).
- **Cadena en segundo plano** (log en `runs/cadena_ronda2.log`): al terminar la ronda 1,
  1. `analizar_barrido.py --nombre ronda1`;
  2. evaluación de la base con la batería completa (`results/barridos/ronda2/base_carrera_v03.json`);
  3. `ronda_siguiente.py --anterior ronda1 --nombre ronda2 --pasos 5000000` (20 agentes, ~30 min cada uno, ~10 h).
- **Siguiente:** revisar al terminar la ronda 1 (~23:35) y documentar el paso 61.

### 2026-10-11 23:40–23:55 — Paso 61 cerrado (ronda 1 de 100 agentes); ronda 2 lanzada
- **Autor:** Claude Code (Camilo ausente).
- **Resultado** (`results/barridos/ronda1/tabla.md`, `analisis.md`):

| Resultado | Valor |
|---|---|
| Agentes | 100 (1M pasos cada uno desde `carrera_v03`), 14:36 → 23:40 (9 h 04 min, ~5.4 min por agente), 0 errores |
| Pasan el filtro duro (0 faltas en 14 corridas) | **70/100** |
| Superan a la base (12.41 s) | **49** |
| Puntaje de los que pasan | mejor **11.43 s** (`agente_045`), mediana 12.26 s, peor 13.54 s |
| Faltas de los descartados (48 corridas) | 26 caídas y 5 salidas en las salidas torcidas; 13 caídas y 5 salidas en la batería normal |

- **Correlaciones finales** (Spearman, 70 que pasan):

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

- **Lectura:** no hay un peso dominante, y pasar o no el filtro no depende de los pesos; con 1M pasos domina la
  variación entre entrenamientos. Detalle en el capítulo del entrenamiento, sección 12e.
- **Los 20 mejores** (`mejores.json`): `agente_045` (11.43 s), `026` (11.45), `071` (11.46), `080` (11.53),
  `062` (11.53), `037` (11.62), `023` (11.62), `074` (11.76), `050` (11.79), `090` (11.79), `043` (11.80) y 9 más.
- **Cadena:** a las 23:41 la base se midió con la batería completa (**pasa, 12.54 s**) y arrancó la **ronda 2** (paso
  62): 20 agentes × 5M pasos, ~30 min cada uno, fin estimado ~10:00 del 2026-10-12. Log en `runs/barrido_ronda2.log`.
- **Paso 61 `[x]`:** la tabla de los 100 con su configuración y puntaje está en `results/barridos/ronda1/tabla.md`.

### 2026-10-12 00:05–00:20 — Ronda 2: se elige el mejor checkpoint de cada agente (E54)
- **Autor:** Claude Code (Camilo ausente; vuelve hacia las 00:35).
- **Qué pasó:**
  - el primer agente de la ronda 2 (`agente_045`, el mejor de la ronda 1) **empeoró con 5M pasos más**: 6 caídas en
    salidas de +25° y 13.3 s de media;
  - es E48 otra vez: entrenar más hace oscilar la política.
- **Cambio en `scripts/ronda_siguiente.py`:**
  - evalúa con la batería completa **cada checkpoint** (1M a 5M) de cada agente y se queda con el mejor (sección
    11.4);
  - el resultado guarda el puntaje de todos los checkpoints (`checkpoints`) y el elegido (`checkpoint_elegido`).
- **Con el cambio:** `agente_045`, checkpoint de 4M, **pasa sin faltas con 12.35 s** (la base `carrera_v03`, con la
  misma batería: 12.54 s). Los de 1M, 2M, 3M y 5M tenían 9, 5, 4 y 7 faltas.
- **Problema al relanzar:** un modelo vacío del entrenamiento cortado; ver E54. Corregido; relanzado a las 00:12.
- **Estimación:** ~33 min por agente (28 de entrenamiento + ~3.5 de evaluar 5 checkpoints); fin hacia las 11:30.
- **Lección (a llevar a futuras generaciones):** guardar checkpoints frecuentes y elegir siempre con la batería
  externa. Además, considerar una tasa de aprendizaje decreciente para que la política no oscile.

### 2026-10-12 00:37 — Ronda 2: el segundo agente confirma la selección por checkpoint
- **`agente_026`** (2.º de la ronda 1, 11.45 s), con la batería completa por checkpoint:

  | Checkpoint | 1M | 2M | 3M | 4M | 5M |
  |---|---|---|---|---|---|
  | Faltas | 6 | 3 | 0 | **0** | **25** |
  | Puntaje | — | — | 11.69 s | **11.51 s** | — |

  - Elegido: 4M, que **pasa con 11.51 s**, contra 12.54 s de la base `carrera_v03` en la misma batería.
  - El modelo final (5M) tenía 25 faltas: quedándose con el último modelo, se habría descartado al mejor candidato
    hasta ahora (E54).
- La ronda sigue con `agente_071`; fin estimado ~11:30.

### 2026-10-12 07:05 — Ronda 2 pausada a pedido del usuario (16 de 20 terminados)
- **Autor:** Claude Code, a pedido de Camilo (va a apagar el PC).
- **Estado al pausar:**
  - 16/20 agentes terminados y evaluados (`results/barridos/ronda2/agente_*/resultado.json`);
  - `agente_031` interrumpido en ~4.2M de 5M pasos (se detuvo con `taskkill /T /F`);
  - faltan `agente_031` y 3 más.
- **Al retomar:**
  - `agente_031` se reentrena desde cero: su `final_model.zip` no es válido y el script lo detecta (arreglo de E54);
  - faltan 4 agentes × ~26 min ≈ 1 h 45 min.
- **Para retomar:** `uv run python scripts/ronda_siguiente.py --anterior ronda1 --nombre ronda2 --pasos 5000000`.
