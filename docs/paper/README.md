# Material para el paper

Documentos que reúnen todo lo necesario para escribir el paper del proyecto. Se mantienen **al día en cada
paso**: no se escriben al final.

| Documento | Contenido | Se actualiza cuando… |
|---|---|---|
| [`historial_pasos.md`](historial_pasos.md) | Qué se hizo en cada paso, cómo se verificó, resultados y commit | Se cierra un paso |
| [`registro_errores.md`](registro_errores.md) | **Todos** los errores, fallos y callejones sin salida, con síntoma, causa, solución y evidencia | Aparece cualquier error (con ID `E##`) |
| [`fuentes_y_repositorios.md`](fuentes_y_repositorios.md) | De dónde sale cada pieza: B-Human (modelo V6), PenaltyStack (repo final), nao_linea (cámara, que salió de este repo), modelo V5 original. Qué es cada uno, cómo funciona, qué se tomó (commit/SHA) y por qué | Se toma algo de otro repositorio o fuente |
| [`entrenamiento_rl.md`](entrenamiento_rl.md) | **Capítulo del entrenamiento por RL**: observación, acción, episodio, cámara simulada, los 17 términos de la recompensa con fórmula, peso y aporte medido, PPO y sus parámetros, etapas del aprendizaje, todas las baterías, la selección, qué aprendió la política (uso de cada acción, marcha), fallos y lo que no se hizo. Regla: **mejor que sobre documentación a que falte** | Se entrena o evalúa una generación (`carrera_vNN`) |
| [`vision_carril.md`](vision_carril.md) | Capítulo de la visión de carril (cámara): método, precisión, colores, 3 carriles y cómo entra al RL | Cambia algo de la visión |

**Otras fuentes:**
- [`../bitacora.md`](../bitacora.md): el diario detallado de cada sesión;
- [`../plan_rl_carrera.md`](../plan_rl_carrera.md): el diseño del RL;
- [`../../PLAN.md`](../../PLAN.md): el plan con los criterios de aceptación;
- [`../../results/`](../../results/): los números con su origen.
