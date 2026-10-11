# Resumen de las evaluaciones de carrera

Generado por `scripts/resumen_carrera.py` a partir de `results/carrera/*/eval_*.json` (`scripts/eval_carrera.py`).
Batería: μ 0.4–1.2, colocación del benchmark (semillas 1000…). **Pasa** = 0 caídas y 0 salidas (sección 11.4).

**Referencia, B-Human (benchmark de 3 carriles, sin perturbaciones):** con visión 25/25 metas en 16.2–18.3 s; sin visión 14/25 metas.

| Visión | Perturb. | vx_cmd | Modelo | Metas | Caídas | Salidas | Pasa | Tiempo a meta [s] | Desvío máx. medio [cm] |
|---|---|---|---|---|---|---|---|---|---|
| sí | no | 0.50 | `runs/carrera_v01/checkpoints/model_10000000_steps.zip` | 9/10 | 0 | 1 | no | 10.07 ± 0.10 | 18.2 |
| sí | no | 0.50 | `runs/carrera_v01/checkpoints/model_15000000_steps.zip` | 10/10 | 0 | 0 | **sí** | 10.57 ± 0.11 | 4.7 |
| sí | no | 0.50 | `runs/carrera_v01/checkpoints/model_5000000_steps.zip` | 10/10 | 0 | 0 | **sí** | 9.58 ± 0.27 | 12.0 |
| sí | no | 0.50 | `runs/carrera_v02/checkpoints/model_10000000_steps.zip` | 10/10 | 0 | 0 | **sí** | 10.10 ± 0.10 | 11.4 |
| sí | no | 0.50 | `runs/carrera_v02/checkpoints/model_15000000_steps.zip` | 10/10 | 0 | 0 | **sí** | 10.58 ± 0.09 | 10.3 |
| sí | no | 0.50 | `runs/carrera_v02/checkpoints/model_20000000_steps.zip` | 10/10 | 0 | 0 | **sí** | 9.80 ± 0.11 | 6.6 |
| sí | no | 0.50 | `runs/carrera_v02/checkpoints/model_25000000_steps.zip` | 10/10 | 0 | 0 | **sí** | 9.99 ± 0.02 | 7.2 |
| sí | no | 0.50 | `runs/carrera_v02/checkpoints/model_30000000_steps.zip` | 10/10 | 0 | 0 | **sí** | 10.54 ± 0.10 | 6.5 |
| sí | no | 0.50 | `runs/carrera_v02/checkpoints/model_35000000_steps.zip` | 10/10 | 0 | 0 | **sí** | 10.15 ± 0.29 | 15.1 |
| sí | no | 0.50 | `runs/carrera_v02/checkpoints/model_5000000_steps.zip` | 10/10 | 0 | 0 | **sí** | 10.12 ± 0.08 | 6.1 |
| sí | no | 0.50 | `runs/carrera_v02/final_model.zip` | 10/10 | 0 | 0 | **sí** | 9.64 ± 0.17 | 8.4 |
| sí | sí | 0.50 | `runs/carrera_v01/checkpoints/model_10000000_steps.zip` | 9/20 | 1 | 10 | no | 10.56 ± 0.10 | 18.0 |
| sí | sí | 0.50 | `runs/carrera_v01/checkpoints/model_15000000_steps.zip` | 20/20 | 0 | 0 | **sí** | 11.15 ± 0.59 | 8.3 |
| sí | sí | 0.50 | `runs/carrera_v01/checkpoints/model_5000000_steps.zip` | 16/20 | 4 | 0 | no | 9.94 ± 0.37 | 14.3 |
| sí | sí | 0.50 | `runs/carrera_v02/checkpoints/model_10000000_steps.zip` | 20/20 | 0 | 0 | **sí** | 10.40 ± 0.33 | 16.6 |
| sí | sí | 0.50 | `runs/carrera_v02/checkpoints/model_15000000_steps.zip` | 20/20 | 0 | 0 | **sí** | 10.85 ± 0.23 | 15.0 |
| sí | sí | 0.50 | `runs/carrera_v02/checkpoints/model_20000000_steps.zip` | 15/20 | 0 | 5 | no | 10.05 ± 0.10 | 14.7 |
| sí | sí | 0.50 | `runs/carrera_v02/checkpoints/model_25000000_steps.zip` | 14/20 | 1 | 5 | no | 10.02 ± 0.07 | 10.5 |
| sí | sí | 0.50 | `runs/carrera_v02/checkpoints/model_30000000_steps.zip` | 19/20 | 0 | 1 | no | 10.71 ± 0.43 | 16.7 |
| sí | sí | 0.50 | `runs/carrera_v02/checkpoints/model_35000000_steps.zip` | 15/20 | 0 | 5 | no | 10.39 ± 0.41 | 15.9 |
| sí | sí | 0.50 | `runs/carrera_v02/checkpoints/model_5000000_steps.zip` | 20/20 | 0 | 0 | **sí** | 10.25 ± 0.25 | 13.5 |
| sí | sí | 0.50 | `runs/carrera_v02/final_model.zip` | 15/20 | 4 | 1 | no | 9.81 ± 0.23 | 9.8 |
| sí | sí | 0.40 | `policies/carrera_v01/model.zip` | 100/100 | 0 | 0 | **sí** | 13.23 ± 0.70 | 8.2 |
| sí | sí | 0.40 | `runs/carrera_v01/checkpoints/model_15000000_steps.zip` | 20/20 | 0 | 0 | **sí** | 13.57 ± 0.71 | 11.3 |
| sí | sí | 0.40 | `runs/carrera_v01/checkpoints/model_5000000_steps.zip` | 20/20 | 0 | 0 | **sí** | 12.35 ± 0.33 | 15.1 |
| sí | sí | 0.40 | `runs/carrera_v02/checkpoints/model_10000000_steps.zip` | 20/20 | 0 | 0 | **sí** | 12.53 ± 0.40 | 14.4 |
| sí | sí | 0.40 | `runs/carrera_v02/checkpoints/model_15000000_steps.zip` | 20/20 | 0 | 0 | **sí** | 13.12 ± 0.37 | 13.1 |
| sí | sí | 0.40 | `runs/carrera_v02/checkpoints/model_15000000_steps.zip` | 100/100 | 0 | 0 | **sí** | 13.05 ± 0.55 | 10.3 |
| sí | sí | 0.40 | `runs/carrera_v02/checkpoints/model_20000000_steps.zip` | 20/20 | 0 | 0 | **sí** | 12.56 ± 0.69 | 16.1 |
| sí | sí | 0.40 | `runs/carrera_v02/checkpoints/model_20000000_steps.zip` | 100/100 | 0 | 0 | **sí** | 12.49 ± 0.54 | 10.1 |
| sí | sí | 0.40 | `runs/carrera_v02/checkpoints/model_25000000_steps.zip` | 15/20 | 0 | 5 | no | 12.25 ± 0.24 | 13.9 |
| sí | sí | 0.40 | `runs/carrera_v02/checkpoints/model_30000000_steps.zip` | 17/20 | 0 | 3 | no | 13.12 ± 0.63 | 13.5 |
| sí | sí | 0.40 | `runs/carrera_v02/checkpoints/model_35000000_steps.zip` | 15/20 | 0 | 5 | no | 12.58 ± 0.55 | 14.3 |
| sí | sí | 0.40 | `runs/carrera_v02/checkpoints/model_5000000_steps.zip` | 20/20 | 0 | 0 | **sí** | 12.23 ± 0.36 | 15.1 |
| sí | sí | 0.40 | `runs/carrera_v02/final_model.zip` | 15/20 | 1 | 4 | no | 12.26 ± 0.23 | 11.6 |
| sí | sí | 0.40 | `runs/carrera_v03/checkpoints/model_10000000_steps.zip` | 98/100 | 0 | 2 | no | 12.83 ± 0.34 | 8.2 |
| sí | sí | 0.40 | `runs/carrera_v03/checkpoints/model_5000000_steps.zip` | 100/100 | 0 | 0 | **sí** | 12.82 ± 0.44 | 7.4 |
| sí | sí | 0.30 | `runs/carrera_v01/checkpoints/model_5000000_steps.zip` | 20/20 | 0 | 0 | **sí** | 16.81 ± 0.30 | 15.5 |
| no | no | 0.50 | `runs/carrera_v01/checkpoints/model_10000000_steps.zip` | 0/10 | 0 | 10 | no | — | 25.5 |
| no | no | 0.50 | `runs/carrera_v01/checkpoints/model_15000000_steps.zip` | 0/10 | 6 | 4 | no | — | 14.3 |
| no | no | 0.50 | `runs/carrera_v01/checkpoints/model_5000000_steps.zip` | 0/10 | 10 | 0 | no | — | 8.6 |
| no | no | 0.50 | `runs/carrera_v02/checkpoints/model_10000000_steps.zip` | 5/10 | 0 | 5 | no | 10.36 ± 0.10 | 17.5 |
| no | no | 0.50 | `runs/carrera_v02/checkpoints/model_15000000_steps.zip` | 10/10 | 0 | 0 | **sí** | 11.01 ± 0.01 | 11.2 |
| no | no | 0.50 | `runs/carrera_v02/checkpoints/model_20000000_steps.zip` | 10/10 | 0 | 0 | **sí** | 10.24 ± 0.12 | 11.3 |
| no | no | 0.50 | `runs/carrera_v02/checkpoints/model_25000000_steps.zip` | 6/10 | 0 | 4 | no | 10.08 ± 0.10 | 18.1 |
| no | no | 0.50 | `runs/carrera_v02/checkpoints/model_30000000_steps.zip` | 9/10 | 0 | 1 | no | 10.29 ± 0.14 | 17.3 |
| no | no | 0.50 | `runs/carrera_v02/checkpoints/model_35000000_steps.zip` | 10/10 | 0 | 0 | **sí** | 10.31 ± 0.13 | 13.8 |
| no | no | 0.50 | `runs/carrera_v02/checkpoints/model_5000000_steps.zip` | 7/10 | 0 | 3 | no | 10.03 ± 0.09 | 17.0 |
| no | no | 0.50 | `runs/carrera_v02/final_model.zip` | 10/10 | 0 | 0 | **sí** | 9.50 ± 0.09 | 13.1 |
| no | sí | 0.50 | `runs/carrera_v02/checkpoints/model_10000000_steps.zip` | 6/20 | 0 | 14 | no | 10.46 ± 0.13 | 21.0 |
| no | sí | 0.50 | `runs/carrera_v02/checkpoints/model_15000000_steps.zip` | 10/20 | 0 | 10 | no | 11.41 ± 0.15 | 20.5 |
| no | sí | 0.50 | `runs/carrera_v02/checkpoints/model_20000000_steps.zip` | 14/20 | 0 | 6 | no | 10.37 ± 0.12 | 17.4 |
| no | sí | 0.50 | `runs/carrera_v02/checkpoints/model_25000000_steps.zip` | 6/20 | 0 | 14 | no | 10.08 ± 0.09 | 24.5 |
| no | sí | 0.50 | `runs/carrera_v02/checkpoints/model_30000000_steps.zip` | 6/20 | 0 | 14 | no | 10.42 ± 0.23 | 24.5 |
| no | sí | 0.50 | `runs/carrera_v02/checkpoints/model_35000000_steps.zip` | 15/20 | 0 | 5 | no | 10.52 ± 0.23 | 14.8 |
| no | sí | 0.50 | `runs/carrera_v02/checkpoints/model_5000000_steps.zip` | 9/20 | 0 | 11 | no | 10.20 ± 0.24 | 21.1 |
| no | sí | 0.50 | `runs/carrera_v02/final_model.zip` | 14/20 | 0 | 6 | no | 9.62 ± 0.17 | 19.1 |
| no | sí | 0.40 | `policies/carrera_v01/model.zip` | 0/100 | 45 | 47 | no | — | 16.3 |
| no | sí | 0.40 | `runs/carrera_v02/checkpoints/model_10000000_steps.zip` | 5/20 | 0 | 15 | no | 12.23 ± 0.01 | 24.4 |
| no | sí | 0.40 | `runs/carrera_v02/checkpoints/model_15000000_steps.zip` | 14/20 | 0 | 6 | no | 13.89 ± 0.42 | 22.3 |
| no | sí | 0.40 | `runs/carrera_v02/checkpoints/model_15000000_steps.zip` | 89/100 | 0 | 11 | no | 13.79 ± 0.52 | 16.0 |
| no | sí | 0.40 | `runs/carrera_v02/checkpoints/model_20000000_steps.zip` | 16/20 | 0 | 4 | no | 12.76 ± 0.25 | 17.7 |
| no | sí | 0.40 | `runs/carrera_v02/checkpoints/model_20000000_steps.zip` | 86/100 | 0 | 14 | no | 12.75 ± 0.34 | 13.1 |
| no | sí | 0.40 | `runs/carrera_v02/checkpoints/model_25000000_steps.zip` | 15/20 | 0 | 5 | no | 12.22 ± 0.09 | 15.1 |
| no | sí | 0.40 | `runs/carrera_v02/checkpoints/model_30000000_steps.zip` | 9/20 | 0 | 11 | no | 13.10 ± 0.24 | 20.1 |
| no | sí | 0.40 | `runs/carrera_v02/checkpoints/model_35000000_steps.zip` | 15/20 | 0 | 5 | no | 12.78 ± 0.40 | 16.2 |
| no | sí | 0.40 | `runs/carrera_v02/checkpoints/model_5000000_steps.zip` | 6/20 | 0 | 14 | no | 11.87 ± 0.36 | 20.8 |
| no | sí | 0.40 | `runs/carrera_v02/final_model.zip` | 15/20 | 0 | 5 | no | 11.90 ± 0.32 | 16.8 |
| no | sí | 0.40 | `runs/carrera_v03/checkpoints/model_10000000_steps.zip` | 87/100 | 0 | 13 | no | 13.10 ± 0.47 | 13.8 |
| no | sí | 0.40 | `runs/carrera_v03/checkpoints/model_5000000_steps.zip` | 82/100 | 0 | 18 | no | 12.55 ± 0.38 | 14.4 |
