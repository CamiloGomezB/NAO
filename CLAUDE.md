# Instrucciones del proyecto (equipo y asistentes de IA)

Caminata por RL para un **NAO V6 real**, con la meta de ganar la **Carrera Individual de la Copa NAO CCM
MX 2026** (3 de noviembre de 2026): 5 m × 70 cm, lo más rápido y **lo más recto** posible, sin caer.
Stack: MuJoCo + Stable-Baselines3 (PPO), Python 3.12 con `uv`, Windows, entrenamiento en CPU.

**Este repo solo hace el RL de la caminata.** El repo final es
[PenaltyStack](https://github.com/Limao0521/PenaltyStack). Todo lo que se haga aquí tiene que poder
pasarse allá y funcionar.

**Tres carriles de comparación:** RL (este repo), B-Human y NAOqi. El RL tiene que ser el más rápido sin
faltas. **Baseline 1:** NAOqi. **Baseline 2:** B-Human, la de PenaltyStack. La **cámara** y el
simulador de la pista vienen de [danielpaya/nao_linea](https://github.com/danielpaya/nao_linea) (Daniel)
y viven en `carril/` y `demo/`. Entrega `d`, `psi` y válido, que la
política recibe como observación. En el entrenamiento se simula con ruido gaussiano, sin renderizar
imágenes.

Este repo será la base de un **paper**: todo el proceso tiene que quedar documentado, incluidos los
errores. Por ahora lo trabaja **una sola persona** (Camilo), **solo en la rama `main`**. No se crean
ramas. Todos los entrenamientos corren en **un solo PC**, la laptop Ryzen 7 5800H.

## Antes de empezar a trabajar

1. Hacer `git pull` en `main`.
2. Leer en [`PLAN.md`](PLAN.md) cuál es el **paso actual** y cuáles están `[~]` en curso, para no duplicar trabajo.
3. Leer las **últimas entradas** de [`docs/bitacora.md`](docs/bitacora.md).
4. Para entender el diseño del sistema: [`docs/plan_rl_carrera.md`](docs/plan_rl_carrera.md).
5. Para lo que exige el repo final: [`docs/integracion_penaltystack.md`](docs/integracion_penaltystack.md).
   De PenaltyStack solo se usa lo que sirve para la **caminata**. No se trae nada de penales.

## Revisión de la documentación al empezar CADA paso (obligatoria)

Antes de tocar código de un paso nuevo, se revisa **toda** la documentación y se corrige lo que esté
desactualizado. Esa revisión se registra en la bitácora como parte del paso. Lista de revisión:

1. **`docs/paper/`:**
   - ¿el `historial_pasos.md` tiene el paso anterior completo (qué, cómo, verificación, commit)?
   - ¿el `registro_errores.md` tiene todos los errores vistos, **con su salida de consola textual**?
   - ¿`fuentes_y_repositorios.md` registra todo lo tomado de otra fuente?
   - ¿`vision_carril.md` está al día?
2. **`PLAN.md`:** las casillas, la línea "Paso actual" y la ruta crítica coinciden con la realidad.
3. **README:** la línea de estado y la tabla de los 3 carriles.
4. **`docs/plan_rl_carrera.md`, `docs/integracion_penaltystack.md` y `docs/camara_y_carriles.md`:** sin
   datos contradictorios con lo último decidido.
5. **Enlaces:** no hay enlaces rotos entre documentos.
6. **Bitácora:** la última entrada dice cuál es el siguiente paso.

## Protocolo de trabajo (obligatorio)

- Se trabaja **un paso del `PLAN.md` a la vez**. Al empezarlo, se marca `[~]`.
- Un paso se marca `[x]` **solo** cuando se cumple su criterio de aceptación (lo que va después del ✅).
  Si el criterio requiere ver algo, por ejemplo un video, el visor o el robot real, se le pide a la persona
  que lo verifique con una lista concreta de qué observar.
- Al terminar, fallar o bloquearse un paso:
  1. **Entrada nueva al final de [`docs/bitacora.md`](docs/bitacora.md)**, con la plantilla que hay ahí:
     objetivo, qué se hizo, resultado con números y rutas, problemas y solución, decisiones, siguiente.
  2. Actualizar la casilla en `PLAN.md` y la línea **"Paso actual"**.
  3. Si cambió el estado del proyecto o hay resultados nuevos, actualizar la **sección "Proyecto actual"
     del README**: línea de estado y tabla de generaciones.
  4. Si cambió una decisión de diseño, actualizar [`docs/plan_rl_carrera.md`](docs/plan_rl_carrera.md) y
     explicar el motivo en la bitácora.
  5. **Material del paper** ([`docs/paper/`](docs/paper/README.md)):
     - **todo** error, fallo o callejón sin salida va también a `docs/paper/registro_errores.md`, con el
       siguiente ID `E##`, síntoma, causa, solución y evidencia. Incluye errores de herramientas y del
       sistema operativo. **Si salió en consola, se copia el texto exacto** (traceback, mensaje de git o
       del sistema) en un bloque de código, seguido de cómo se solucionó;
     - al cerrar un paso, se agrega su resumen a `docs/paper/historial_pasos.md` (qué se hizo, cómo se
       verificó, resultado y commit);
     - si cambia algo de la cámara o la visión, se actualiza `docs/paper/vision_carril.md`;
     - si se toma algo de otro repositorio o fuente (código, modelo, datos, parámetros), se registra en
       `docs/paper/fuentes_y_repositorios.md`: qué es la fuente, cómo funciona, qué se tomó (commit o
       SHA-256), por qué y qué se le cambió.
- **Los fallos no se borran.** Un paso fallido se marca `[!]` y se documenta. Si hace falta corregirlo, se
  agrega un paso nuevo (p. ej. `56b`). Las entradas viejas de la bitácora no se editan; se corrigen con
  una entrada nueva.
- **Commits:** en `main`, los hace **el usuario manualmente**, cuando él decida, a veces agrupando varios pasos.
  El asistente **no hace commit ni push**: al terminar, deja los cambios sin confirmar, resume qué cambió y
  propone el mensaje del commit. Hubo una autorización temporal del 2026-10-10 que el usuario retiró ese
  mismo día.

## Convenciones

- **Idioma:** español en documentación, comentarios, mensajes de los scripts y nombres de métricas.
- **Comandos:** siempre con `uv run …` desde la raíz del repo, por ejemplo
  `uv run python -m src.train --config configs/ppo.yaml --run-name nombre`.
- **Generaciones de RL:**
  - Se nombran `carrera_vNN`.
  - Cada una cambia **una sola cosa** respecto a la anterior, con una hipótesis escrita.
  - Cada una tiene su config en `configs/`, una fila en la tabla de generaciones del README y una entrada
    en la bitácora.
- **Qué se versiona:**
  - código;
  - configs;
  - políticas seleccionadas (`policies/carrera_vNN/`, desde el paso 42);
  - métricas (`results/`);
  - datos del robot real (`data/real/sesion_NN/`);
  - documentación.

  `runs/` y `videos/` **no** se suben. Para compartir una política se exporta a `policies/`.
- **Reproducibilidad:** semilla fija en cada config. Evaluación con semillas 1000, 1001…. Cada run guarda
  config, versiones, commit y máquina. Una métrica sin su archivo de origen no se reporta.
- **Modelo del robot:** `assets/nao/nao.xml` se **genera** con `scripts/build_nao_v6.py` y no se edita a
  mano. Sale del mismo `NaoV6H25.rsi3` que el modelo de PenaltyStack. Los ángulos usan la convención de
  NAOqi y B-Human. No usar valores del modelo aproximado del sprint inicial: el V6 tiene piernas más
  anchas y solo ~3 cm entre ellas (ver `docs/plan_rl_carrera.md`, sección 12).
- **Compatibilidad con PenaltyStack** (no romperla sin documentarlo):
  - La observación usa **solo** sensores que da su `SensorAdapter` o ALMemory: ángulos, velocidades,
    giroscopio, acelerómetro, orientación y 8 FSR en kg. Nada de velocidad lineal ni posición global.
  - Las articulaciones usan los nombres y el orden de B-Human (`third_party/penaltystack/motion_contract.py`).
  - La política actúa en múltiplos del ciclo de 12 ms (24 ms).
  - La inferencia exportada debe correr en Python 2.7 a bordo, sin torch.
  - El arranque es por el táctil frontal de la cabeza (0.25 s) y el paro por el botón del pecho (0.3 s).
- **Colores de la pista:** solo en `config/pista.yaml` (desde el paso 48). Nunca escribir un color de piso,
  línea o meta en el código: la organización los avisa poco antes del evento.
- **Fricción:** siempre explícita, en el piso y en los pies. Nunca depender del 1.0 por defecto de MuJoCo.
- **Faltas del reglamento:** salida de carril, caída y choque entre robots son terminales en la recompensa y
  **descartan** al agente en la selección. Ver `docs/plan_rl_carrera.md`, sección 1.2.
- **`third_party/penaltystack/`:** solo el contrato de articulaciones, como copia exacta de referencia. No
  se edita ni se importa. No se agregan archivos de penales.
- **Robot real:**
  - Nada se ejecuta en el NAO sin paro por táctil de la cabeza y paro de seguridad por inclinación.
  - Las primeras pruebas de cada política nueva se hacen con el robot suspendido o con arnés.
  - Cada sesión guarda sus logs en `data/real/sesion_NN/` y se resume en la bitácora.
- **Reglamento:** ante cualquier duda de reglas, ver la sección 1 de
  [`docs/plan_rl_carrera.md`](docs/plan_rl_carrera.md) (resumen del reglamento V1.0, sección 3.2).
