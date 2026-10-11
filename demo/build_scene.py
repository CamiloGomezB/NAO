# -*- coding: utf-8 -*-
"""Genera la escena MuJoCo de la Carrera Individual (reglamento 3.2.4) con el NAO V6.

  - Piso (madera con veta o liso), carril de 70 cm con lineas de 1.9 cm, carriles vecinos, franja de
    salida (18 cm) y franja de meta (30 cm) a 5 m. Los COLORES se eligen en config/pista.yaml (el UNICO lugar
    donde se definen; la organizacion los avisa poco antes de la competencia).
  - Camara inferior del NAO en la cabeza, como en el modelo de B-Human: (x 0.05071, z 0.01774) desde
    HeadPitch, inclinada 39.7 grados, 320x240, campo de vision vertical 42.5 grados.

Uso:
    uv run python demo/build_scene.py                              # colores de config/pista.yaml
    uv run python demo/build_scene.py --piso gris --linea blanco   # o pasarlos aqui
    uv run python demo/build_scene.py --piso "#3a3a3a" --linea "#f2f2f2" --sin-veta
Salida: assets/nao/scene_carril.xml, assets/nao/nao_cam.xml, assets/nao/duela.png y config/pista_robot.json
(polaridad y colores para la vision que corre en el NAO, que no tiene PyYAML).
"""
import argparse
import json
import math
import re
import struct
import zlib
from pathlib import Path

import numpy as np
import yaml

ROOT = Path(__file__).resolve().parents[1]
NAO_DIR = ROOT / "assets" / "nao"
CONFIG = ROOT / "config" / "pista.yaml"
ROBOT_JSON = ROOT / "config" / "pista_robot.json"
LANE, LINE, LENGTH = 0.70, 0.019, 5.0
SPACING = LANE + LINE
CAM_PITCH = math.radians(39.7)
CAM_FOVY = 42.5

# Colores con nombre (RGB 0-255). Se puede usar cualquier otro con un codigo HEX "#rrggbb".
PISOS = {
    "madera_clara": (196, 148, 96),
    "madera_oscura": (122, 80, 50),
    "duela_roja": (150, 72, 48),
    "gris": (150, 150, 150),
    "gris_oscuro": (70, 70, 72),
    "blanco": (232, 232, 232),
    "negro": (30, 30, 32),
    "verde": (62, 125, 62),
    "azul": (47, 93, 138),
}
LINEAS = {
    "negro": (15, 15, 18),
    "blanco": (240, 240, 240),
    "amarillo": (240, 200, 30),
    "rojo": (200, 25, 25),
    "azul": (30, 70, 200),
    "verde": (30, 150, 50),
    "gris": (120, 120, 120),
}
MIN_CONTRASTE_BRILLO = 45   # contraste minimo de brillo (0-255) para usar el modo "brillo"
BRILLO_RATIO = 0.62         # el mismo dark_ratio por defecto de carril/lane_estimator.py
MIN_CONTRASTE_REAL = 30     # por debajo, la linea no se veria en una pista real (ruido de camara, luz)
DEFAULT = dict(piso="madera_clara", veta=True, linea="negro", salida=None, meta="rojo")  # salida None = color de linea


def parse_color(value, names):
    """Nombre de la lista o '#rrggbb' -> (r, g, b) en 0-255."""
    v = str(value).strip().lower()
    if v in names:
        return tuple(names[v])
    if v in LINEAS:
        return tuple(LINEAS[v])
    if v in PISOS:
        return tuple(PISOS[v])
    m = re.fullmatch(r"#?([0-9a-f]{6})", v)
    if not m:
        raise ValueError("Color no reconocido: %r. Usa un nombre (%s) o un codigo como '#c49460'."
                         % (value, ", ".join(sorted(set(PISOS) | set(LINEAS)))))
    h = m.group(1)
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def luminance(rgb):
    r, g, b = rgb
    return 0.299 * r + 0.587 * g + 0.114 * b


def load_config(**overrides):
    """Lee config/pista.yaml y aplica los valores pasados (los None se ignoran)."""
    cfg = dict(DEFAULT)
    if CONFIG.exists():
        cfg.update({k: v for k, v in (yaml.safe_load(CONFIG.read_text(encoding="utf-8")) or {}).items() if v is not None})
    cfg.update({k: v for k, v in overrides.items() if v is not None})
    return cfg


def describe(cfg):
    """Colores RGB, polaridad de la linea y contraste para la vision."""
    piso = parse_color(cfg["piso"], PISOS)
    linea = parse_color(cfg["linea"], LINEAS)
    meta = parse_color(cfg["meta"], LINEAS)
    salida = parse_color(cfg["salida"], LINEAS) if cfg.get("salida") else linea
    lp, ll = luminance(piso), luminance(linea)
    info = dict(piso_rgb=piso, linea_rgb=linea, salida_rgb=salida, meta_rgb=meta, veta=bool(cfg.get("veta", True)),
                polaridad="oscura" if ll < lp else "clara", contraste=abs(ll - lp),
                modo_vision="brillo", color_ref=None)
    # El detector por brillo (carril/lane_estimator.py) exige que la linea sea mas oscura que BRILLO_RATIO
    # veces el fondo (o, si es clara, que supere al fondo en (1 - BRILLO_RATIO) de lo que le queda hasta 255).
    # Si el brillo no pasa esa prueba pero el color si distingue la linea (p. ej. verde sobre madera clara),
    # la vision proyecta cada pixel sobre la direccion de color linea - piso (modo "color").
    if ll < lp:
        brillo_ok = ll < BRILLO_RATIO * lp and lp - ll >= MIN_CONTRASTE_BRILLO
    else:
        brillo_ok = ll > lp + (255.0 - lp) * (1.0 - BRILLO_RATIO) and ll - lp >= MIN_CONTRASTE_BRILLO
    dif = [l_ - p_ for l_, p_ in zip(linea, piso)]
    norma = math.sqrt(sum(x * x for x in dif))
    if not brillo_ok and norma > info["contraste"]:
        u = [x / norma for x in dif]
        m = [(l_ + p_) / 2.0 for l_, p_ in zip(linea, piso)]
        info.update(modo_vision="color", polaridad="clara",
                    color_ref=[[round(x, 5) for x in u], [round(x, 2) for x in m]])
    info["contraste_efectivo"] = norma if info["modo_vision"] == "color" else info["contraste"]
    return info


def write_png(path, rgb):
    h, w, _ = rgb.shape
    raw = b"".join(b"\x00" + rgb[i].tobytes() for i in range(h))

    def chunk(tag, data):
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
    png = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b"")
    path.write_bytes(png)


def floor_texture(path, base_rgb, veta=True, size=1024, metres=1.8, seed=0):
    """Textura del piso. Con veta: tablas de 9 cm con tonos distintos, veta y juntas. Sin veta: liso."""
    base = np.array(base_rgb, dtype=float)
    if not veta:
        img = np.ones((size, size, 3)) * base
        write_png(path, np.clip(img, 0, 255).astype(np.uint8))
        return
    rng = np.random.RandomState(seed)
    px = metres / size
    v, u = np.mgrid[0:size, 0:size] * px          # v -> y del mundo, u -> x del mundo
    plank = np.floor(v / 0.09)
    tone = rng.uniform(0.85, 1.08, int(plank.max()) + 2)[plank.astype(int)]
    offset = rng.uniform(0, 3, int(plank.max()) + 2)[plank.astype(int)]
    grain = 0.5 + 0.5 * np.sin(v * 420 + 2.5 * np.sin(u * 3.1 + offset) + offset)
    img = base * (tone[..., None] * (0.93 - 0.08 * grain[..., None]))
    joint = (v % 0.09) < 0.0012
    img[joint] *= 0.72
    write_png(path, np.clip(img, 0, 255).astype(np.uint8))


def rgba(rgb):
    return "%.3f %.3f %.3f 1" % tuple(c / 255.0 for c in rgb)


def build(cfg=None, verbose=True, **overrides):
    """Genera la escena con los colores de cfg (o de config/pista.yaml + overrides). Devuelve describe(cfg)."""
    cfg = cfg or load_config(**overrides)
    info = describe(cfg)
    floor_texture(NAO_DIR / "duela.png", info["piso_rgb"], info["veta"])
    # 1) NAO con camara inferior (copia de nao.xml con la camara agregada en el cuerpo Head)
    nao = (NAO_DIR / "nao.xml").read_text()
    s, c = math.sin(CAM_PITCH), math.cos(CAM_PITCH)
    cam = ('<camera name="CameraBottom" pos="0.05071 0 0.01774" xyaxes="0 -1 0 %.6f 0 %.6f" fovy="%.2f" />'
           % (s, c, CAM_FOVY))
    nao, n = re.subn(r'(<body name="Head" pos="0 0 0">\s*<joint name="HeadPitch"[^>]*/>)', r"\1\n          " + cam, nao)
    assert n == 1, "no se encontro el cuerpo Head en nao.xml"
    (NAO_DIR / "nao_cam.xml").write_text(nao)

    # 2) Escena de la pista
    lc, sc, mc = rgba(info["linea_rgb"]), rgba(info["salida_rgb"]), rgba(info["meta_rgb"])
    geoms = []
    x0, x1 = -0.4, LENGTH + 0.8
    for k in (-2, -1, 0, 1):
        y = (k + 0.5) * SPACING
        geoms.append('<geom type="box" pos="%.4f %.4f 0.0006" size="%.4f %.4f 0.0006" rgba="%s" contype="0" conaffinity="0"/>'
                     % ((x0 + x1) / 2, y, (x1 - x0) / 2, LINE / 2, lc))
    geoms.append('<geom name="salida" type="box" pos="0 0 0.0005" size="0.09 %.4f 0.0005" rgba="%s" contype="0" conaffinity="0"/>'
                 % (SPACING * 1.5, sc))
    # Franja de meta en cada uno de los 3 carriles (entre las lineas): central "meta", vecinos "meta_izq"/"meta_der".
    for nombre, k in (("meta_der", -1), ("meta", 0), ("meta_izq", 1)):
        geoms.append('<geom name="%s" type="box" pos="%.3f %.4f 0.0007" size="0.15 %.4f 0.0007" rgba="%s" contype="0" conaffinity="0"/>'
                     % (nombre, LENGTH + 0.15, k * SPACING, LANE / 2, mc))
    scene = """<mujoco model="nao carrera">
  <include file="nao_cam.xml"/>
  <statistic center="2.5 0 0.25" extent="3"/>
  <visual>
    <headlight diffuse="0.55 0.55 0.55" ambient="0.35 0.35 0.35" specular="0 0 0"/>
    <global azimuth="160" elevation="-25" offwidth="1280" offheight="720"/>
    <quality shadowsize="4096"/>
  </visual>
  <asset>
    <texture type="skybox" builtin="gradient" rgb1="0.85 0.88 0.92" rgb2="0.55 0.6 0.68" width="512" height="3072"/>
    <texture type="2d" name="duela" file="duela.png"/>
    <material name="duela" texture="duela" texuniform="true" texrepeat="%.4f %.4f" reflectance="0.05"/>
  </asset>
  <worldbody>
    <light pos="2.5 0 4" dir="0 0 -1" directional="true" diffuse="0.6 0.6 0.6"/>
    <geom name="floor" type="plane" size="0 0 0.05" material="duela" contype="1" conaffinity="14"/>
    %s
    <camera name="lateral" pos="2.6 -3.4 1.6" xyaxes="1 0 0 0 0.45 0.89"/>
  </worldbody>
</mujoco>
""" % (1 / 1.8, 1 / 1.8, "\n    ".join(geoms))
    (NAO_DIR / "scene_carril.xml").write_text(scene)
    # 3) Lo que necesita la vision a bordo del NAO (Python 2.7, sin PyYAML): robot/race_nao.py lo lee.
    ROBOT_JSON.parent.mkdir(parents=True, exist_ok=True)
    ROBOT_JSON.write_text(json.dumps(dict(
        nota="Generado por demo/build_scene.py desde config/pista.yaml. No editar a mano.",
        piso=str(cfg["piso"]), linea=str(cfg["linea"]), salida=str(cfg.get("salida") or cfg["linea"]),
        meta=str(cfg["meta"]), veta=info["veta"], polaridad=info["polaridad"],
        modo_vision=info["modo_vision"], color_ref=info["color_ref"],
        contraste=round(info["contraste"], 1), contraste_efectivo=round(info["contraste_efectivo"], 1), piso_rgb=list(info["piso_rgb"]), linea_rgb=list(info["linea_rgb"]),
        meta_rgb=list(info["meta_rgb"])), indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    if verbose:
        print("Pista: piso %s (%s), linea %s, meta %s -> vision por %s, linea %s que el piso, contraste %.0f"
              % (cfg["piso"], "con veta" if info["veta"] else "liso", cfg["linea"], cfg["meta"], info["modo_vision"],
                 "mas oscura" if info["polaridad"] == "oscura" else "mas clara", info["contraste_efectivo"]))
        if info["contraste_efectivo"] < MIN_CONTRASTE_REAL:
            print("  AVISO: la linea casi no se distingue del piso (contraste %.0f de 255). La vision puede fallar,"
                  " igual que fallaria en una pista real asi." % info["contraste_efectivo"])
    return info


def add_color_args(ap):
    ap.add_argument("--piso", default=None, help="color del piso: nombre (%s) o '#rrggbb'" % ", ".join(PISOS))
    ap.add_argument("--linea", default=None, help="color de las lineas: nombre (%s) o '#rrggbb'" % ", ".join(LINEAS))
    ap.add_argument("--salida", default=None, help="color de la franja de salida (por defecto, el de la linea)")
    ap.add_argument("--meta", default=None, help="color de la franja de meta")
    ap.add_argument("--sin-veta", action="store_true", help="piso liso, sin tablas ni veta")


def config_from_args(a):
    return load_config(piso=a.piso, linea=a.linea, salida=a.salida, meta=a.meta,
                       veta=(False if a.sin_veta else None))


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    add_color_args(ap)
    build(config_from_args(ap.parse_args()))
