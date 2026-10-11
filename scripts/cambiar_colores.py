"""Cambia los colores de la pista y verifica que la vision de carril los sigue detectando.

La organizacion de la Copa NAO avisa los colores definitivos de las lineas y del piso poco antes de la
competencia. Este script es el procedimiento completo (paso 75 del PLAN):
  1. actualiza config/pista.yaml (el unico lugar del repo donde estan los colores);
  2. regenera la pista de MuJoCo y config/pista_robot.json (polaridad para la vision a bordo del NAO);
  3. verifica la vision con la camara renderizada en 50 posiciones conocidas, con 1.5 grados de error de
     pose de la camara;
  4. guarda el resultado en results/camara/verificacion_vision.md.
La politica de RL no ve colores (solo d, psi y valido), asi que si la verificacion da OK no hay que reentrenar.

Uso (desde la raiz del repo):
    uv run python scripts/cambiar_colores.py                                        # verificar los colores actuales
    uv run python scripts/cambiar_colores.py --piso madera_oscura --linea blanco    # cambiar y verificar
    uv run python scripts/cambiar_colores.py --piso "#3a2a1a" --linea "#f5f5f5" --sin-veta
    uv run python scripts/cambiar_colores.py --piso gris --linea amarillo --probar  # probar SIN guardar
    uv run python scripts/cambiar_colores.py --matriz                               # todas las combinaciones con nombre
Despues de cambiar los colores, copiar config/pista_robot.json al robot (ver robot/LUNES.md).
"""

import argparse
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "demo"))

import build_scene  # noqa: E402
from check_vision import informe, verificar  # noqa: E402

POSE_NOISE_DEG = 1.5
REPORT = ROOT / "results" / "camara" / "verificacion_vision.md"
MATRIX_REPORT = ROOT / "results" / "camara" / "matriz_colores.md"
MATRIX_GRID = ((0.5,), (-0.12, 0.0, 0.12), (-8.0, 0.0, 8.0))   # 9 posiciones por combinacion
KEYS = ("piso", "veta", "linea", "salida", "meta")


def guardar(cfg: dict) -> None:
    """Escribe los valores en config/pista.yaml conservando los comentarios del archivo."""
    text = build_scene.CONFIG.read_text(encoding="utf-8")
    for key in KEYS:
        if key not in cfg or cfg[key] is None:
            continue
        value = str(cfg[key]).lower() if isinstance(cfg[key], bool) else str(cfg[key])
        value = f'"{value}"' if value.startswith("#") else value
        # Conserva la columna del comentario: "linea: negro           # ..." -> "linea: blanco          # ..."
        pattern = re.compile(rf"^({key}:[ \t]*)(\S+)([ \t]*)(?=#|$)", re.MULTILINE)

        def reemplazar(m, value=value):
            ancho = len(m.group(2)) + len(m.group(3))
            return m.group(1) + value + " " * max(1 if m.group(3) else 0, ancho - len(value))

        if pattern.search(text):
            text = pattern.sub(reemplazar, text, count=1)
        else:
            text = text.rstrip("\n") + f"\n{key}: {value}\n"
    build_scene.CONFIG.write_text(text, encoding="utf-8", newline="\n")


def avisos(cfg: dict, info: dict) -> list[str]:
    out = []
    if info["contraste"] < 45:
        out.append(f"AVISO: contraste linea-piso de solo {info['contraste']:.0f} de 255; la vision puede fallar.")
    if str(cfg["meta"]).lower() not in ("rojo", "#c81919"):
        out.append("AVISO: la deteccion de la meta en la vision busca rojo. Con otro color no se detecta la meta "
                   "(no afecta a d ni a psi, que son los que usa la politica).")
    return out


def matriz() -> int:
    original = build_scene.load_config()
    names_floor, names_line = list(build_scene.PISOS), list(build_scene.LINEAS)
    rows, t0 = [], time.time()
    for piso in names_floor:
        row = []
        for linea in names_line:
            res = verificar(dict(original, piso=piso, linea=linea, salida=None), POSE_NOISE_DEG, grid=MATRIX_GRID)
            modo = " (color)" if res["info"]["modo_vision"] == "color" else ""
            if res["ok"]:
                cell = f"OK {res['err_d_mean']:.1f} cm{modo}"
            elif not res["contraste_ok"]:
                cell = f"**NO APTO** (contraste {res['info']['contraste_efectivo']:.0f})"
            elif res["pct_valid"] < 100:
                cell = f"**FALLA** ({res['pct_valid']:.0f} % validas{modo})"
            else:
                cell = f"**FALLA** (error {res['err_d_mean']:.1f} cm{modo})"
            row.append(cell)
            print(f"  piso {piso:<13} linea {linea:<9} contraste {res['info']['contraste']:5.0f}: {cell}", flush=True)
        rows.append(row)
    build_scene.build(original, verbose=False)   # deja la pista como estaba en config/pista.yaml
    lines = [
        "# Matriz de colores: piso x linea",
        "",
        f"Generado por `scripts/cambiar_colores.py --matriz` en {time.time() - t0:.0f} s. Cada celda: 9 posiciones "
        f"(x = 0.5 m; d = -12, 0, +12 cm; psi = -8, 0, +8 grados), {POSE_NOISE_DEG} grados de error de pose. "
        "OK = 100 % de mediciones validas, error medio <= 3 cm y <= 3 grados, y contraste linea-piso >= "
        f"{build_scene.MIN_CONTRASTE_REAL} de 255; se muestra el error medio de d. (color) = la vision usa la "
        "diferencia de color porque el brillo casi no distingue la linea del piso. NO APTO = tan poco contraste "
        "que en una pista real no se veria, aunque en la simulacion (sin ruido) se detecte.",
        "",
        "| Piso \\ Linea | " + " | ".join(names_line) + " |",
        "|---|" + "---|" * len(names_line),
    ]
    lines += [f"| {piso} | " + " | ".join(row) + " |" for piso, row in zip(names_floor, rows)]
    MATRIX_REPORT.parent.mkdir(parents=True, exist_ok=True)
    MATRIX_REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\nMatriz guardada en {MATRIX_REPORT.relative_to(ROOT).as_posix()}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    build_scene.add_color_args(ap)
    ap.add_argument("--con-veta", action="store_true", help="piso con tablas y veta de madera")
    ap.add_argument("--probar", action="store_true", help="verificar sin guardar en config/pista.yaml")
    ap.add_argument("--matriz", action="store_true", help="probar todas las combinaciones piso x linea con nombre")
    a = ap.parse_args()
    if a.matriz:
        return matriz()

    veta = False if a.sin_veta else (True if a.con_veta else None)
    cfg = build_scene.load_config(piso=a.piso, linea=a.linea, salida=a.salida, meta=a.meta, veta=veta)
    cambios = {k: v for k, v in dict(piso=a.piso, linea=a.linea, salida=a.salida, meta=a.meta, veta=veta).items()
               if v is not None}
    print("Colores:", ", ".join(f"{k}={cfg.get(k)}" for k in KEYS))
    if cambios and not a.probar:
        guardar(cambios)
        print(f"Guardado en {build_scene.CONFIG.relative_to(ROOT).as_posix()}")

    res = verificar(cfg, POSE_NOISE_DEG)
    text = informe(res, origen="scripts/cambiar_colores.py")
    print(text)
    for aviso in avisos(cfg, res["info"]):
        print(aviso)

    if a.probar:
        build_scene.build(build_scene.load_config(), verbose=False)   # restaurar la pista guardada
        print("(--probar: config/pista.yaml no se modifico y la pista volvio a sus colores guardados)")
    else:
        REPORT.parent.mkdir(parents=True, exist_ok=True)
        REPORT.write_text(text, encoding="utf-8")
        print(f"Informe: {REPORT.relative_to(ROOT).as_posix()}")
        print("Pista regenerada: assets/nao/scene_carril.xml y config/pista_robot.json "
              "(copiar este JSON al robot, ver robot/LUNES.md)")
    return 0 if res["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
