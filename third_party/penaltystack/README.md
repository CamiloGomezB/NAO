# Referencia: contrato de articulaciones de PenaltyStack

De [PenaltyStack](https://github.com/Limao0521/PenaltyStack), el repo final del equipo, solo usamos lo que
la **caminata** necesita. No se trae nada de penales.

| Archivo | Origen | Para qué nos sirve |
|---|---|---|
| `motion_contract.py` | `penalty/motion_contract.py`, rama `feat/bhuman-simulation`, commit `9c08a41`. Copia exacta, sin modificar, del 2026-10-08 | Nombres y **orden de las 26 articulaciones** (enum `Joints` de B-Human) y **ciclo de 12 ms**. La política lee y escribe en ese orden para poder integrarse en PenaltyStack (paso 40 del [`PLAN.md`](../../PLAN.md)). |

El resto de lo que necesitamos de PenaltyStack son datos, no código: formato de sensores, arranque y paro,
despliegue y parámetros de la caminata de B-Human. Están resumidos en
[`docs/integracion_penaltystack.md`](../../docs/integracion_penaltystack.md).

Este archivo es solo de referencia: no se edita ni se importa desde este repo.
