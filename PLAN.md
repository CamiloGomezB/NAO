# Plan de trabajo — Caminata RL para NAO V6

Stack: **MuJoCo + Stable-Baselines3 (PPO)**, Windows nativo, entrenamiento en CPU.
Regla: cada paso termina con una **confirmación** y un **commit**.

## Fase A — Preparación
- [x] **1. Estructura del repo y `.gitignore`** — ✅ Carpetas visibles en VSCode
- [x] **2. Entorno virtual con `uv` + `pyproject.toml` con versiones fijadas** — ✅ `uv sync` sin errores
- [ ] **3. Instalar MuJoCo y abrir el visor con un modelo de prueba** — ✅ Se abre la ventana 3D
- [ ] **4. Push a GitHub** — ✅ Visible en github.com/CamiloGomezB/NAO

## Fase B — Modelo del NAO
- [ ] **5. Buscar el modelo NAO V6 y revisar licencia** — ✅ Fuente y licencia acordadas
- [ ] **6. Convertir a MJCF y cargar** — ✅ Lista de articulaciones y masa total ≈ 5.5 kg
- [ ] **7. Verlo en el visor, suspendido** — ✅ Parece un NAO (partes bien ubicadas)
- [ ] **8. Colisiones de pies con el suelo** — ✅ Se apoya sin hundirse ni rebotar
- [ ] **9. Pose de pie con controlador PD** — ✅ Se mantiene de pie ~10 s
- [ ] **10. Mover cada articulación por separado** — ✅ Direcciones y rangos correctos

## Fase C — Entorno RL
- [ ] **11. Esqueleto `NaoWalkEnv` (Gymnasium)** — ✅ `check_env()` pasa
- [ ] **12. Observaciones** — ✅ Valores con sentido, sin NaN
- [ ] **13. Acciones (posiciones objetivo sobre pose nominal)** — ✅ Acción 0 = de pie; aleatorias no explotan
- [ ] **14. Detección de caída / terminación** — ✅ El episodio termina al caer
- [ ] **15. Recompensa inicial desglosada por términos** — ✅ Tabla de términos coherente
- [ ] **16. Render de video offscreen** — ✅ `.mp4` visto por el usuario
- [ ] **17. Benchmark de entornos en paralelo** — ✅ Pasos/s con 1, 8, 12 entornos

## Fase D — Primer entrenamiento
- [ ] **18. `train.py` + `configs/ppo.yaml`** — ✅ Entrenamiento de 1 min guarda checkpoint
- [ ] **19. `evaluate.py` separado** — ✅ Carga checkpoint e imprime métricas
- [ ] **20. TensorBoard** — ✅ Curvas visibles en el navegador
- [ ] **21. Entrenamiento corto (~20–30 min)** — ✅ La recompensa sube; aguanta más de pie

## Fase E — Caminata
- [ ] **22. Entrenamiento largo (1–3 h o nocturno)** — ✅ Curvas subiendo, checkpoints guardados
- [ ] **23. Revisar video del mejor checkpoint** — ✅ Juicio del usuario: ¿avanza?
- [ ] **24. Ajuste de reward (1ª iteración)** — ✅ Mejora medible
- [ ] **25. Comparar 2–3 variantes** — ✅ Tabla comparativa
- [ ] **26. Seleccionar `checkpoints/best_model.zip`** — ✅ Justificado con métricas

## Fase F — Evaluación y evidencia
- [ ] **27. Evaluación en 20+ episodios con seeds fijas** — ✅ `results/metrics.json`
- [ ] **28. Gráficas de entrenamiento** — ✅ `results/training_curves.png`
- [ ] **29. GIF/video de la demo** — ✅ `media/demo.gif` aprobado

## Fase G — Reproducibilidad y entrega
- [ ] **30. README completo** — ✅ Se entiende al leerlo
- [ ] **31. Prueba de instalación limpia** — ✅ Demo corre siguiendo el README al pie de la letra
- [ ] **32. Push final y revisión en GitHub** — ✅ Repo completo visible
