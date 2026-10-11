"""Valida la fisica del modelo NAO V6 (assets/nao/nao.xml) contra su fuente, NaoV6H25.rsi3 de B-Human (paso 44 del PLAN).

Lee el RSI3 por su cuenta (sin usar el MJCF generado) y compara con el modelo compilado en MuJoCo:
  1. cada cuerpo: masa, centro de masa e inercia (autovalores, porque MuJoCo diagonaliza la matriz);
  2. cada articulacion: posicion respecto al cuerpo padre, eje y rango;
  3. cada servo: kp, kv y fuerza maxima;
  4. masa total frente al URDF oficial de Aldebaran (NAOH25V60.urdf: 5.35975 kg), como control independiente.
Termina con RESULTADO: OK o FALLA.

Uso:
    uv run python scripts/check_modelo_v6.py
"""

import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import mujoco
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_nao_v6 import SOURCE, unit, vec  # noqa: E402  (unidades y lectura de vectores del RSI3)

MASA_URDF_ALDEBARAN_KG = 5.35975        # NAOH25V60.urdf (Aldebaran, 2022), suma de masas
TOL_MASA, TOL_POS, TOL_REL_INERCIA, TOL_ANG = 1e-6, 1e-6, 1e-4, 1e-6
FALLAS = []


def revisar(ok, texto):
    print(f"   {'OK   ' if ok else 'FALLA'} {texto}")
    if not ok:
        FALLAS.append(texto)


def leer_rsi3():
    """Cuerpos y articulaciones del NAO en el RSI3: {cuerpo: datos}, {articulacion: datos}."""
    raiz = ET.parse(SOURCE).getroot()
    nao = next(b for b in raiz.findall("Body") if b.get("name") == "Nao")
    cuerpos, articulaciones = {}, {}

    def recorrer(body, nombre_mj):
        im = body.find("InertiaMatrixMass")
        i = {k: unit(im.get(k)) for k in ("ixx", "iyy", "izz", "ixy", "ixz", "iyz")}
        I = np.array([[i["ixx"], i["ixy"], i["ixz"]], [i["ixy"], i["iyy"], i["iyz"]], [i["ixz"], i["iyz"], i["izz"]]])
        cuerpos[nombre_mj] = dict(masa=unit(im.get("value")), com=np.array(vec(im)), inercia=np.sort(np.linalg.eigvalsh(I)))
        for hinge in body.findall("Hinge"):
            hijo = hinge.find("Body")
            eje = hinge.find("Axis")
            lim = eje.find("Deflection")
            servo = eje.find("ServoMotor")
            articulaciones[hinge.get("name")] = dict(
                cuerpo=hijo.get("name"), pos=np.array(vec(hinge.find("Translation"))), eje=np.array(vec(eje)),
                rango=(unit(lim.get("min")), unit(lim.get("max"))),
                kp=unit(servo.get("p")), kv=unit(servo.get("d")), fuerza=unit(servo.get("maxForce")))
            recorrer(hijo, hijo.get("name"))

    recorrer(nao, "torso")       # el cuerpo raiz "Nao" del RSI3 es "torso" en el MJCF
    return cuerpos, articulaciones


def main() -> int:
    cuerpos, articulaciones = leer_rsi3()
    m = mujoco.MjModel.from_xml_path(str(ROOT / "assets" / "nao" / "nao.xml"))
    print(f"RSI3: {len(cuerpos)} cuerpos, {len(articulaciones)} articulaciones | MJCF: {m.nbody - 1} cuerpos, "
          f"{m.njnt - 1} articulaciones (+ raiz libre), {m.nu} actuadores")

    print("1. Cuerpos: masa, centro de masa e inercia")
    peor = dict(masa=0.0, com=0.0, inercia=0.0)
    for nombre, ref in cuerpos.items():
        b = m.body(nombre)
        dm = abs(b.mass[0] - ref["masa"])
        dc = float(np.max(np.abs(b.ipos - ref["com"])))
        di = float(np.max(np.abs(np.sort(b.inertia) - ref["inercia"]) / np.maximum(ref["inercia"], 1e-12)))
        peor = dict(masa=max(peor["masa"], dm), com=max(peor["com"], dc), inercia=max(peor["inercia"], di))
        if dm > TOL_MASA or dc > TOL_POS or di > TOL_REL_INERCIA:
            revisar(False, f"{nombre}: dif. masa {dm:.2e} kg, centro de masa {dc:.2e} m, inercia relativa {di:.2e}")
    revisar(peor["masa"] <= TOL_MASA, f"masas de los {len(cuerpos)} cuerpos (dif. max {peor['masa']:.1e} kg)")
    revisar(peor["com"] <= TOL_POS, f"centros de masa (dif. max {peor['com']:.1e} m)")
    revisar(peor["inercia"] <= TOL_REL_INERCIA, f"inercias principales (dif. relativa max {peor['inercia']:.1e})")

    print("2. Articulaciones: posicion, eje y rango")
    peor = dict(pos=0.0, eje=0.0, rango=0.0)
    for nombre, ref in articulaciones.items():
        j = m.joint(nombre)
        b = m.body(ref["cuerpo"])
        dp = float(np.max(np.abs(b.pos - ref["pos"])))
        de = float(np.max(np.abs(j.axis - ref["eje"] / np.linalg.norm(ref["eje"]))))
        dr = float(np.max(np.abs(j.range - np.array(ref["rango"]))))
        peor = dict(pos=max(peor["pos"], dp), eje=max(peor["eje"], de), rango=max(peor["rango"], dr))
        if dp > TOL_POS or de > TOL_ANG or dr > TOL_ANG:
            revisar(False, f"{nombre}: dif. posicion {dp:.2e} m, eje {de:.2e}, rango {dr:.2e} rad")
    revisar(peor["pos"] <= TOL_POS, f"posiciones de las {len(articulaciones)} articulaciones (dif. max {peor['pos']:.1e} m)")
    revisar(peor["eje"] <= TOL_ANG, f"ejes (dif. max {peor['eje']:.1e})")
    revisar(peor["rango"] <= TOL_ANG, f"rangos (dif. max {peor['rango']:.1e} rad)")

    print("3. Servos: kp, kv y fuerza maxima")
    peor = 0.0
    n = 0
    for nombre, ref in articulaciones.items():
        if nombre == "RHipYawPitch":
            continue           # un solo motor para las dos HipYawPitch (restriccion de igualdad)
        a = m.actuator(nombre)
        d = max(abs(a.gainprm[0] - ref["kp"]), abs(-a.biasprm[2] - ref["kv"]), abs(a.forcerange[1] - ref["fuerza"]))
        peor = max(peor, d)
        n += 1
    revisar(peor <= 1e-9, f"{n} servos con los kp, kv y fuerza del RSI3 (dif. max {peor:.1e})")
    revisar("RHipYawPitch" not in [m.actuator(i).name for i in range(m.nu)] and m.neq >= 1,
            "HipYawPitch derecho acoplado al izquierdo (sin actuador propio)")

    print("4. Masa total")
    total_rsi3 = sum(c["masa"] for c in cuerpos.values())
    total_mj = float(m.body_subtreemass[m.body("torso").id])
    print(f"   RSI3 {total_rsi3:.5f} kg | MJCF {total_mj:.5f} kg | URDF oficial de Aldebaran {MASA_URDF_ALDEBARAN_KG:.5f} kg")
    revisar(abs(total_mj - total_rsi3) < 1e-6, "MJCF = RSI3")
    revisar(abs(total_mj - MASA_URDF_ALDEBARAN_KG) < 0.005, "coincide con el URDF oficial de Aldebaran (+-5 g)")

    print(f"\nRESULTADO: {'OK' if not FALLAS else 'FALLA'}")
    return 0 if not FALLAS else 1


if __name__ == "__main__":
    sys.exit(main())
