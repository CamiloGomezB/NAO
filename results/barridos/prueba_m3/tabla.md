# Barrido de esfuerzo `prueba_m3` (fase M2)

Ajuste fino de `rl_v1.1` con el castigo `esfuerzo_motor`. Bateria completa (44 corridas). Filtro duro: caida, salida o una articulacion con par RMS > 80 % del par continuo = falta; desde la fase M3, ademas, desvio maximo medio de las salidas normales <= 10 cm y, en la bateria del benchmark (sin perturbaciones), cada corrida con meta, <= 80 % y desvio <= 10 cm. Puntaje = tiempo medio + 1 sigma.

**Base `continua`:** faltas 1/44 (con el filtro del 80 %), esfuerzo maximo 87 % (LKneePitch), tiempo medio 11.78 s.

| # | Agente | Peso (modo) | Checkpoint | Pasa | Faltas | Sobre 80 % | Puntaje [s] | t medio [s] | Peor esfuerzo |
|---|---|---|---|---|---|---|---|---|---|
| 1 | agente_000 | -0.5 (instante) | 0M | si | 0 | 0 | 12.02 | 11.74 | 76 % (LAnklePitch) |

Checkpoints de cada agente (faltas, corridas sobre 80 %, peor esfuerzo, desvio medio de las salidas normales, tiempo medio; y si se corrio, la bateria del benchmark):

- `agente_000` (esfuerzo -0.5, centrado -5.0): 0.02M: 0 faltas, 0 sobre 80 %, 76 %, desvio 7.4 cm, 11.74 s [benchmark: pasa, 0 malas, desvio max 8.2 cm, 74 %, 11.19 s]
