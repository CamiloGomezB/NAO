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
