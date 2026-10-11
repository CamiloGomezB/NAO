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
