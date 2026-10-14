# Barrido de esfuerzo `esfuerzo_v12_cont` (fase M2)

Ajuste fino de `rl_v1.1` con el castigo `esfuerzo_motor`. Bateria completa (44 corridas). Filtro duro: caida, salida o una articulacion con par RMS > 80 % del par continuo = falta. Puntaje = tiempo medio + 1 sigma.

**Base `continua`:** faltas 2/44 (con el filtro del 80 %), esfuerzo maximo 105 % (RAnklePitch), tiempo medio 11.63 s.

| # | Agente | Peso (modo) | Checkpoint | Pasa | Faltas | Sobre 80 % | Puntaje [s] | t medio [s] | Peor esfuerzo |
|---|---|---|---|---|---|---|---|---|---|
| 1 | agente_000 | -0.5 (instante) | 3M | si | 0 | 0 | 11.78 | 11.52 | 79 % (RKneePitch) |

Checkpoints de cada agente (faltas, corridas sobre 80 %, peor esfuerzo, tiempo medio):

- `agente_000` (peso -0.5): 0M: 5 faltas, 5 sobre 80 %, 105 %, 11.74 s; 1M: 1 faltas, 1 sobre 80 %, 87 %, 11.78 s; 2M: 7 faltas, 1 sobre 80 %, 84 %, 11.66 s; 2M: 0 faltas, 0 sobre 80 %, 76 %, 11.79 s; 2M: 4 faltas, 2 sobre 80 %, 83 %, 11.69 s; 3M: 0 faltas, 0 sobre 80 %, 79 %, 11.52 s
