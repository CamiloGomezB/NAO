# Matriz de colores: piso x linea

Generado por `scripts/cambiar_colores.py --matriz` en 34 s. Cada celda: 9 posiciones (x = 0.5 m; d = -12, 0, +12 cm; psi = -8, 0, +8 grados), 1.5 grados de error de pose. OK = 100 % de mediciones validas, error medio <= 3 cm y <= 3 grados, y contraste linea-piso >= 30 de 255; se muestra el error medio de d. (color) = la vision usa la diferencia de color porque el brillo casi no distingue la linea del piso. NO APTO = tan poco contraste que en una pista real no se veria, aunque en la simulacion (sin ruido) se detecte.

| Piso \ Linea | negro | blanco | amarillo | rojo | azul | verde | gris |
|---|---|---|---|---|---|---|---|
| madera_clara | OK 1.4 cm | OK 1.4 cm | OK 1.4 cm (color) | OK 1.4 cm | OK 1.4 cm | OK 1.4 cm (color) | **FALLA** (89 % validas (color)) |
| madera_oscura | OK 1.4 cm | OK 1.4 cm | OK 1.4 cm | OK 1.4 cm (color) | OK 1.4 cm (color) | OK 1.4 cm (color) | OK 1.4 cm (color) |
| duela_roja | OK 1.4 cm | OK 1.4 cm | OK 1.4 cm | OK 1.4 cm (color) | OK 1.4 cm (color) | OK 1.4 cm (color) | OK 1.4 cm (color) |
| gris | OK 1.4 cm | OK 1.4 cm | OK 1.4 cm (color) | **FALLA** (89 % validas) | OK 1.4 cm | OK 1.4 cm (color) | **FALLA** (0 % validas (color)) |
| gris_oscuro | OK 1.4 cm | OK 1.4 cm | OK 1.4 cm | OK 1.4 cm (color) | OK 1.4 cm (color) | OK 1.4 cm (color) | OK 1.4 cm (color) |
| blanco | OK 1.4 cm | **NO APTO** (contraste 14) | OK 1.4 cm (color) | OK 1.4 cm | OK 1.4 cm | OK 1.4 cm | **FALLA** (0 % validas) |
| negro | **NO APTO** (contraste 25) | OK 1.4 cm | OK 1.4 cm | OK 1.4 cm (color) | OK 1.4 cm (color) | OK 1.4 cm (color) | OK 1.4 cm |
| verde | OK 1.4 cm | OK 1.4 cm | OK 1.4 cm | OK 1.4 cm (color) | OK 1.4 cm (color) | **FALLA** (0 % validas (color)) | OK 1.4 cm (color) |
| azul | OK 1.4 cm | OK 1.4 cm | OK 1.4 cm | OK 1.4 cm (color) | OK 1.4 cm (color) | OK 1.4 cm (color) | OK 1.4 cm (color) |
