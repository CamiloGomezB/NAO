# Barrido de esfuerzo `recto_v13` (fase M2)

Ajuste fino de `rl_v1.1` con el castigo `esfuerzo_motor`. Bateria completa (44 corridas). Filtro duro: caida, salida o una articulacion con par RMS > 80 % del par continuo = falta; desde la fase M3, ademas, desvio maximo medio de las salidas normales <= 10 cm y, en la bateria del benchmark (sin perturbaciones), cada corrida con meta, <= 80 % y desvio <= 10 cm. Puntaje = tiempo medio + 1 sigma.

**Base `continua`:** faltas 1/44 (con el filtro del 80 %), esfuerzo maximo 87 % (LKneePitch), tiempo medio 11.78 s.

| # | Agente | Peso (modo) | Checkpoint | Pasa | Faltas | Sobre 80 % | Puntaje [s] | t medio [s] | Peor esfuerzo |
|---|---|---|---|---|---|---|---|---|---|
| 1 | agente_000 | -0.5 (instante) | 2M | si | 0 | 0 | 12.80 | 12.44 | 77 % (LKneePitch) |
| 2 | agente_001 | -0.5 (instante) | 0.5M | no | 3 | 3 | — | 11.98 | 83 % (LKneePitch) |

Checkpoints de cada agente (faltas, corridas sobre 80 %, peor esfuerzo, desvio medio de las salidas normales, tiempo medio; y si se corrio, la bateria del benchmark):

- `agente_000` (esfuerzo -0.5, centrado -5.0): 0.5M: 3 faltas, 3 sobre 80 %, 98 %, desvio 7.0 cm, 12.12 s; 1M: 1 faltas, 1 sobre 80 %, 96 %, desvio 7.8 cm, 11.92 s; 1.5M: 5 faltas, 5 sobre 80 %, 89 %, desvio 6.7 cm, 12.15 s; 2M: 0 faltas, 0 sobre 80 %, 77 %, desvio 5.6 cm, 12.44 s [benchmark: pasa, 0 malas, desvio max 6.5 cm, 79 %, 11.74 s]; 2.5M: 18 faltas, 18 sobre 80 %, 82 %, desvio 8.8 cm, 12.18 s; 3M: 28 faltas, 28 sobre 80 %, 86 %, desvio 14.0 cm, 11.84 s
- `agente_001` (esfuerzo -0.5, centrado -10.0): 0.5M: 3 faltas, 3 sobre 80 %, 83 %, desvio 9.6 cm, 11.98 s; 1M: 5 faltas, 5 sobre 80 %, 84 %, desvio 7.2 cm, 11.91 s; 1.5M: 6 faltas, 6 sobre 80 %, 83 %, desvio 7.6 cm, 12.50 s; 2M: 7 faltas, 7 sobre 80 %, 82 %, desvio 10.2 cm, 11.94 s; 2.5M: 22 faltas, 22 sobre 80 %, 84 %, desvio 11.7 cm, 12.08 s; 3M: 9 faltas, 6 sobre 80 %, 92 %, desvio 18.4 cm, 12.87 s
