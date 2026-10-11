# Verificacion de la vision de carril en la pista simulada

Generado por `scripts/check_vision.py`. Pista: piso `madera_clara`, linea `negro`, salida `negro`, meta `rojo`, veta si. Vision por **brillo**, linea oscura que el piso. Error de pose de la camara: 1.5 grados.

Posiciones: x = (0.5, 2.5) m, d = (-0.15, -0.08, 0.0, 0.08, 0.15) m, psi = (-10.0, -5.0, 0.0, 5.0, 10.0) grados (50 en total), robot de pie en la pose `home`.

| Metrica | Valor | Tolerancia |
|---|---|---|
| Contraste linea-piso (0-255) | 141 | >= 30 |
| Mediciones validas | 100 % | 100 % |
| Error medio de d | 1.27 cm | <= 3.0 cm |
| Error maximo de d | 4.01 cm | - |
| Error medio de psi | 0.86 grados | <= 3.0 grados |
| Error maximo de psi | 3.21 grados | - |
| Con las 2 lineas detectadas | 84 % | - |

RESULTADO: OK
