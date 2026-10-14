# Barrido de esfuerzo `esfuerzo_v12` (fase M2)

Ajuste fino de `rl_v1.1` con el castigo `esfuerzo_motor`. Bateria completa (44 corridas). Filtro duro: caida, salida o una articulacion con par RMS > 80 % del par continuo = falta. Puntaje = tiempo medio + 1 sigma.

**Base `rl_v1.1`:** faltas 44/44 (con el filtro del 80 %), esfuerzo maximo 109 % (RAnklePitch), tiempo medio 11.26 s.

| # | Agente | Peso (modo) | Checkpoint | Pasa | Faltas | Sobre 80 % | Puntaje [s] | t medio [s] | Peor esfuerzo |
|---|---|---|---|---|---|---|---|---|---|
| 1 | agente_000 | -0.5 (instante) | 4M | no | 2 | 2 | — | 11.63 | 105 % (RAnklePitch) |
| 2 | agente_003 | -0.8 (instante) | 3M | no | 15 | 15 | — | 12.54 | 94 % (LAnklePitch) |
| 3 | agente_001 | -1.0 (media) | 3M | no | 44 | 44 | — | 11.70 | 101 % (LKneePitch) |
| 4 | agente_002 | -0.3 (instante) | 3M | no | 44 | 44 | — | 11.93 | 102 % (LAnklePitch) |

Checkpoints de cada agente (faltas, corridas sobre 80 %, peor esfuerzo, tiempo medio):

- `agente_000` (peso -0.5): 1M: 44 faltas, 44 sobre 80 %, 106 %, 12.50 s; 2M: 44 faltas, 44 sobre 80 %, 96 %, 11.68 s; 3M: 41 faltas, 41 sobre 80 %, 96 %, 11.82 s; 4M: 2 faltas, 2 sobre 80 %, 105 %, 11.63 s
- `agente_003` (peso -0.8): 1M: 44 faltas, 44 sobre 80 %, 113 %, 12.54 s; 2M: 44 faltas, 44 sobre 80 %, 88 %, 12.59 s; 3M: 15 faltas, 15 sobre 80 %, 94 %, 12.54 s; 4M: 21 faltas, 21 sobre 80 %, 110 %, 12.57 s
- `agente_001` (peso -1.0): 1M: 44 faltas, 44 sobre 80 %, 108 %, 11.22 s; 2M: 44 faltas, 44 sobre 80 %, 102 %, 11.99 s; 3M: 44 faltas, 44 sobre 80 %, 101 %, 11.70 s; 4M: 44 faltas, 44 sobre 80 %, 103 %, 11.30 s
- `agente_002` (peso -0.3): 1M: 44 faltas, 44 sobre 80 %, 106 %, 11.65 s; 2M: 44 faltas, 44 sobre 80 %, 110 %, 11.57 s; 3M: 44 faltas, 44 sobre 80 %, 102 %, 11.93 s; 4M: 44 faltas, 44 sobre 80 %, 105 %, 11.63 s
