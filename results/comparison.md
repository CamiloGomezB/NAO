# Comparación de variantes (20 episodios, semillas 1000–1019, acciones deterministas)

Valores: media ± desviación estándar sobre los episodios. Cada episodio dura como máximo 20 s.

| Variante | Caídas | Distancia [m] | Velocidad [m/s] | Duración [s] | Desv. lateral [m] | Inclinación máx. [°] | Doble apoyo [%] | Pie izq. [cm] | Pie der. [cm] | Esfuerzo Σ τ² |
|---|---|---|---|---|---|---|---|---|---|---|
| **Base** (`ppo_base_5M`) | 0 % | 3.02 ± 0.00 | 0.151 ± 0.000 | 20.0 ± 0.0 | -0.13 ± 0.02 | 3.0 ± 0.3 | 0.2 ± 0.0 | 4.1 ± 0.1 | 2.5 ± 0.1 | 12.84 ± 0.02 |
| **V1 natural** (`ppo_natural_5M`) | 0 % | 3.98 ± 0.00 | 0.199 ± 0.000 | 20.0 ± 0.0 | -0.04 ± 0.03 | 3.5 ± 0.0 | 20.1 ± 0.0 | 3.7 ± 0.0 | 3.3 ± 0.1 | 12.28 ± 0.01 |
| **V2 brazos** (`ppo_brazos_5M`) | 0 % | 4.00 ± 0.00 | 0.200 ± 0.000 | 20.0 ± 0.0 | +0.05 ± 0.03 | 3.5 ± 0.1 | 20.0 ± 0.0 | 3.7 ± 0.0 | 4.1 ± 0.0 | 14.27 ± 0.01 |

Configuraciones: `configs/ppo.yaml` (Base), `configs/ppo_natural.yaml` (V1), `configs/ppo_brazos.yaml` (V2).
Regenerar: `uv run python scripts/compare_runs.py`.
