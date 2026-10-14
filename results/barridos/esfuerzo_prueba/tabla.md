# Barrido de esfuerzo `esfuerzo_prueba` (fase M2)

Ajuste fino de `rl_v1.1` con el castigo `esfuerzo_motor`. Bateria completa (44 corridas). Filtro duro: caida, salida o una articulacion con par RMS > 80 % del par continuo = falta. Puntaje = tiempo medio + 1 sigma.

**Base `rl_v1.1`:** faltas 44/44 (con el filtro del 80 %), esfuerzo maximo 109 % (RAnklePitch), tiempo medio 11.26 s.

| # | Agente | Peso | Checkpoint | Pasa | Faltas | Sobre 80 % | Puntaje [s] | t medio [s] | Peor esfuerzo |
|---|---|---|---|---|---|---|---|---|---|
| 1 | agente_000 | -1.0 | 1M | no | 44 | 44 | — | 11.22 | 108 % (LAnklePitch) |

Checkpoints de cada agente (faltas, corridas sobre 80 %, peor esfuerzo, tiempo medio):

- `agente_000` (peso -1.0): 1M: 44 faltas, 44 sobre 80 %, 108 %, 11.22 s
