"""Exporta las politicas de carrera para el NAO (framework B-Human) y escribe los datos de paridad.

Salidas:
  bhuman/Config/NeuralNets/CopaRace/<politica>.cfg   pesos del actor, VecNormalize congelado, periodo de marcha y
      vx_cmd recomendado, en el formato de configuracion de B-Human (lo lee el modulo CopaRLWalkEngine).
  bhuman/Config/NeuralNets/CopaRace/politicas.json   registro para la ventana de despliegue (estado, vx, SHA-256).
  tests/robot_paridad/carrera_golden.json           entradas y salidas del codigo Python (contrato v1, politicas,
  tests/robot_paridad/imagenes_carril.bin               azar, vision de carril, filtro y controlador) que
  tests/robot_paridad/imagenes_carril_modos.bin         scripts/check_paridad_robot.py compara con CopaRace.h.
                                                        Las "modos" son la vision con linea clara y en modo color.

La accion determinista es clip(media) del actor de SB3, la misma que model.predict(deterministic=True). Las
politicas publicadas en policies/ solo se leen.

Uso (desde la raiz del repo):
    uv run python scripts/exportar_politicas_robot.py
"""
import argparse
import hashlib
import json
import math
import pickle
import random
import sys
from pathlib import Path

import numpy as np
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from carril.controller import LaneController  # noqa: E402
from carril.lane_estimator_puro import EstimadorCarrilPuro  # noqa: E402
from carril.lane_filter import LaneFilter  # noqa: E402
from src.race import contract as C  # noqa: E402

SALIDA = ROOT / "bhuman/Config/NeuralNets/CopaRace"
PARIDAD = ROOT / "tests/robot_paridad"

# nombre -> (estado, vx_cmd recomendado, descripcion). Estados y vx de los README de policies/ y del README del repo.
POLITICAS = {
    "rl_v1.2.1": ("recomendada", 0.45, "Version actual: motores <= 80 % y recta (desvio max. 6.5 cm), 11.7 s en el benchmark."),
    "rl_v1.2": ("alternativa", 0.45, "Motores <= 80 %, 10.9 s, pero se desvia hasta 23 cm (E59)."),
    "rl_v1.1": ("rapida", 0.45, "La mas rapida (10.7 s), con motores sobre el 80 % del par continuo (97-105 %)."),
    "rl_v1.0": ("anterior", 0.40, "carrera_v03: corrige salidas torcidas hasta +-25 grados; 12.8 s."),
    "carrera_v02": ("anterior", 0.40, "Mas perdida de vision en el entrenamiento; 13.0 s a 0.40 m/s."),
    "carrera_v01": ("anterior", 0.40, "Primera politica de carrera; 10.5 s con vision a 0.5 m/s."),
}
RECOMENDADA = "rl_v1.2.1"


def fmt(valor, digitos=9):
    valor = float(valor)
    if not math.isfinite(valor):
        raise ValueError("parametro no finito")
    texto = "%.*g" % (digitos, valor)
    return "0" if texto in ("0", "-0") else texto


def arreglo_cfg(valores, digitos=9, por_linea=8):
    valores = [fmt(v, digitos) for v in np.asarray(valores).ravel()]
    lineas = [", ".join(valores[i:i + por_linea]) for i in range(0, len(valores), por_linea)]
    return "[\n    " + ",\n    ".join(lineas) + "\n  ]"


def capa_cfg(peso, sesgo):
    peso, sesgo = np.asarray(peso), np.asarray(sesgo)
    return ("{\n  filas = %d;\n  columnas = %d;\n  pesos = %s;\n  sesgo = %s;\n}"
            % (peso.shape[0], peso.shape[1], arreglo_cfg(peso), arreglo_cfg(sesgo)))


def cargar(nombre):
    from stable_baselines3 import PPO
    carpeta = ROOT / "policies" / nombre
    modelo = PPO.load(carpeta / "model.zip", device="cpu")
    with open(carpeta / "model_vecnormalize.pkl", "rb") as f:
        vecnorm = pickle.load(f)
    config = yaml.safe_load((carpeta / "config.yaml").read_text(encoding="utf-8"))
    return modelo, vecnorm, config


def exportar(nombre):
    import torch
    modelo, vecnorm, config = cargar(nombre)
    politica = modelo.policy
    activacion = config["policy"].get("activation", "tanh")
    if activacion not in ("elu", "tanh"):
        raise ValueError("activacion no soportada: %s" % activacion)
    capas = [m for m in politica.mlp_extractor.policy_net if isinstance(m, torch.nn.Linear)]
    ocultas = [(c.weight.detach().numpy().astype(np.float32), c.bias.detach().numpy().astype(np.float32)) for c in capas]
    accion_w = politica.action_net.weight.detach().numpy().astype(np.float32)
    accion_b = politica.action_net.bias.detach().numpy().astype(np.float32)
    media = np.asarray(vecnorm.obs_rms.mean, np.float64)
    varianza = np.asarray(vecnorm.obs_rms.var, np.float64)
    if media.shape != (C.DIM_OBSERVACION,) or accion_w.shape[0] != C.N_ACCION:
        raise ValueError("%s no usa el contrato v1 (54 -> 13)" % nombre)
    estado, vx, descripcion = POLITICAS[nombre]
    periodo = float(config["env"].get("gait_period", C.PERIODO_MARCHA_S))
    texto = ["// Generado por scripts/exportar_politicas_robot.py desde policies/%s. No editar." % nombre,
             "// Actor determinista de SB3: clip(media), MLP %s, VecNormalize congelado (contrato %s)."
             % (activacion, C.VERSION_CONTRATO),
             'nombre = "%s";' % nombre,
             'activacion = "%s";' % activacion,
             "media = %s;" % arreglo_cfg(media, 17),
             "varianza = %s;" % arreglo_cfg(varianza, 17),
             "clipObs = %s;" % fmt(vecnorm.clip_obs, 17),
             "epsilon = %s;" % fmt(vecnorm.epsilon, 17),
             "ocultas = [\n%s\n];" % ",\n".join(capa_cfg(w, b) for w, b in ocultas),
             "accion = %s;" % capa_cfg(accion_w, accion_b),
             "periodoMarcha = %s;" % fmt(periodo),
             "vxCmd = %s;" % fmt(vx)]
    datos = ("\n".join(texto) + "\n").encode("utf-8")
    SALIDA.mkdir(parents=True, exist_ok=True)
    (SALIDA / (nombre + ".cfg")).write_bytes(datos)
    dorado = {"nombre": nombre, "activacion": activacion, "media": media.tolist(), "varianza": varianza.tolist(),
              "clipObs": float(vecnorm.clip_obs), "epsilon": float(vecnorm.epsilon), "periodoMarcha": periodo,
              "vxCmd": vx,
              "ocultas": [{"pesos": w.astype(np.float64).tolist(), "sesgo": b.astype(np.float64).tolist()} for w, b in ocultas],
              "accion": {"pesos": accion_w.astype(np.float64).tolist(), "sesgo": accion_b.astype(np.float64).tolist()}}
    return modelo, vecnorm, dorado, hashlib.sha256(datos).hexdigest()


def observaciones_reales(pasos=160, semilla=1000):
    """Observaciones de NaoRace-v0 recorridas por la politica recomendada (en distribucion)."""
    import gymnasium as gym
    import src.envs  # noqa: F401  (registra NaoRace-v0)
    modelo, vecnorm, config = cargar(RECOMENDADA)
    env = gym.make("NaoRace-v0", **config["env"])
    obs, _ = env.reset(seed=semilla, options={"vx_cmd": 0.45})
    lista = []
    for _ in range(pasos):
        lista.append(np.asarray(obs, np.float32))
        accion, _ = modelo.predict(vecnorm.normalize_obs(obs), deterministic=True)
        obs, _, terminado, truncado, _ = env.step(accion)
        if terminado or truncado:
            obs, _ = env.reset(seed=semilla + len(lista), options={"vx_cmd": 0.40})
    env.close()
    return lista


def casos_politica(modelo, vecnorm, observaciones, rng):
    casos = []
    extras = [obs.copy() for obs in observaciones[:8]]
    for obs in extras:   # fuera de rango, para ejercitar el recorte de VecNormalize
        obs[rng.integers(0, C.DIM_OBSERVACION)] = float(rng.choice([-40.0, 40.0]))
    for obs in list(observaciones) + extras:
        accion, _ = modelo.predict(vecnorm.normalize_obs(obs), deterministic=True)
        casos.append({"observacion": np.asarray(obs, np.float64).tolist(),
                      "accion": np.asarray(accion, np.float64).tolist()})
    return casos


def casos_contrato(rng, n=60):
    casos = []
    for k in range(n):
        q = rng.normal(0, 1, 4)
        q /= np.linalg.norm(q)
        if k % 3 == 0:  # casi de pie, como en la carrera
            ang = rng.normal(0, 0.05, 3)
            q = np.array([1.0, *ang])
            q /= np.linalg.norm(q)
        frame = {"angles": (np.array([C.POSE_HOME[nm] for nm in C.NOMBRES_MODELO]) + rng.normal(0, 0.2, 26)).tolist(),
                 "velocity": rng.normal(0, 3, 26).tolist(), "gyro": rng.normal(0, 1, 3).tolist(),
                 "acc": [0.0, 0.0, 9.81], "orientation": q.tolist(), "fsr": rng.uniform(0, 3, 8).tolist()}
        accion_anterior = rng.uniform(-1, 1, C.N_ACCION).tolist()
        camara = (float(rng.normal(0, 0.1)), float(rng.normal(0, 0.1)), float(rng.integers(0, 2)))
        rumbo_obj = float(rng.uniform(-math.pi, math.pi))
        t = float(rng.uniform(0, 30))
        vx = float(rng.uniform(0.15, 0.56))
        obs = C.armar_observacion(frame, rumbo_obj, camara, accion_anterior, t, vx)
        accion = rng.uniform(-1.3, 1.3, C.N_ACCION)
        if k % 4 == 0:  # hacia adentro a la vez: ejercita el presupuesto lateral
            accion[1], accion[6], accion[5], accion[10], accion[0] = -1.0, 1.0, -1.0, 1.0, rng.choice([-1.0, 1.0])
        objetivos = C.accion_a_objetivos(accion.tolist())
        angulos, _ = C.objetivos_a_salida_bhuman(objetivos)
        psis = rng.normal(0, 0.1, int(rng.integers(0, 6))).tolist()
        rumbo_imu = float(rng.uniform(-math.pi, math.pi))
        casos.append({"frame": frame, "rumbo_objetivo": rumbo_obj, "camara": list(camara),
                      "accion_anterior": accion_anterior, "t": t, "vx": vx, "observacion": obs,
                      "accion": accion.tolist(), "objetivos": [objetivos[nm] for nm in C.ARTICULACIONES_ACCION],
                      "angulos": angulos, "rumbo_imu": rumbo_imu, "psis": psis,
                      "rumbo_inicial": C.rumbo_objetivo_inicial(rumbo_imu, psis)})
    camara = C.EstadoCamara()
    secuencia = []
    for paso in range(40):
        t = paso * 0.05
        medicion = None
        if paso % 2 == 0:
            medicion = (t, float(rng.normal(0, 0.1)), float(rng.normal(0, 0.1)), bool(rng.random() > 0.3))
            camara.nueva_medicion(*medicion)
        secuencia.append({"t": t, "medicion": medicion, "observacion": list(camara.observacion(t))})
    return casos, secuencia


def casos_azar():
    generador = random.Random(0)
    return [{"n": n, "valor": generador.randrange(n)} for n in (1, 2, 3, 7, 10, 64, 100, 257, 1000, 4095, 70000) * 12]


def camara_sintetica(altura, inclinacion, x=0.05):
    """T camara -> robot (4x4 por filas): camara a `altura` m, inclinada hacia abajo `inclinacion` rad."""
    c, s = math.cos(inclinacion), math.sin(inclinacion)
    # Columnas = ejes de la camara (x optico, y izquierda, z arriba) en el marco del robot.
    return [c, 0.0, s, x, 0.0, 1.0, 0.0, 0.0, -s, 0.0, c, altura, 0.0, 0.0, 0.0, 1.0]


def imagen_sintetica(rng, d, psi, T, una_linea=False, meta=None, ancho=320, alto=240,
                     piso=(196.0, 148.0, 96.0), linea=(15.0, 15.0, 18.0)):
    """Pista vista por la camara inferior: piso con veta, dos cintas y meta roja opcional (madera y cinta negra)."""
    est = EstimadorCarrilPuro()
    m = -math.tan(psi)
    raiz = math.sqrt(1 + m * m)
    espaciado = 0.70 + 0.019
    c_izq = (-d + espaciado / 2) * raiz
    c_der = (-d - espaciado / 2) * raiz
    img = np.zeros((alto, ancho, 3), np.float64)
    for v in range(alto):
        for u in range(ancho):
            p = est._project(float(u), float(v), T)
            if p is None:
                img[v, u] = (120, 120, 125)
                continue
            x, y, _ = p
            color = np.array(piso, np.float64) + 12 * math.sin(40 * x + 3 * y)
            for c, activa in ((c_izq, True), (c_der, not una_linea)):
                if activa and abs(y - c - m * x) / raiz < 0.0095:
                    color = np.array(linea, np.float64)
            if meta is not None and meta <= x <= meta + 0.30:
                color = np.array([200.0, 25.0, 25.0])
            img[v, u] = color
    img += rng.normal(0, 4, img.shape)
    return np.clip(np.round(img), 0, 255).astype(np.uint8)


def casos_vision(rng):
    escenas = [(0.0, 0.0, False, None), (0.08, 0.0, False, None), (-0.12, 0.05, False, None),
               (0.03, -0.15, False, None), (0.15, 0.2, True, None), (0.0, 0.0, False, 1.0),
               (-0.05, 0.1, False, 0.6), (0.2, -0.05, True, None), (-0.2, -0.2, False, None), (0.05, 0.3, False, 1.4)]
    estimador = EstimadorCarrilPuro()   # semilla 0: el RANSAC avanza a lo largo de toda la secuencia
    imagenes, casos = [], []
    for k, (d, psi, una, meta) in enumerate(escenas):
        T = camara_sintetica(altura=0.45 + 0.02 * math.sin(k), inclinacion=math.radians(42 + 4 * math.cos(k)))
        img = imagen_sintetica(rng, d, psi, T, una, meta)
        imagenes.append(img.tobytes())
        e = estimador.procesar(img.tobytes(), T)
        casos.append({"T": T, "verdad": {"d": d, "psi": psi}, "valida": bool(e.valid), "d": e.d, "psi": e.psi,
                      "n_lineas": e.n_lines, "n_puntos": e.n_points, "pendiente": e.slope,
                      "distancia_roja": e.red_dist, "calidad": e.quality})
    return casos, b"".join(imagenes)


def referencia_color(piso, linea):
    """color_ref del modo "color", con la formula y el redondeo de demo/build_scene.py (describe)."""
    dif = [l_ - p_ for l_, p_ in zip(linea, piso)]
    norma = math.sqrt(sum(x * x for x in dif))
    return [[round(x / norma, 5) for x in dif], [round((l_ + p_) / 2.0, 2) for l_, p_ in zip(linea, piso)]]


# (modo, piso, linea): cinta blanca sobre piso oscuro (polaridad "clara") y cinta verde sobre madera (modo "color",
# el brillo casi no distingue la linea). Son los dos casos que config/pista_robot.json puede pedir ademas del normal.
MODOS_VISION = [("clara", (70.0, 52.0, 40.0), (235.0, 235.0, 230.0)),
                ("color", (196.0, 148.0, 96.0), (70.0, 160.0, 80.0))]


def casos_vision_modos(rng):
    escenas = [(0.0, 0.0, False, None), (0.1, -0.1, False, 0.8), (-0.15, 0.15, True, None)]
    imagenes, casos = [], []
    for modo, piso, linea in MODOS_VISION:
        color_ref = referencia_color(piso, linea) if modo == "color" else None
        estimador = EstimadorCarrilPuro(polaridad="clara", color_ref=color_ref)
        for k, (d, psi, una, meta) in enumerate(escenas):
            T = camara_sintetica(altura=0.46 + 0.01 * k, inclinacion=math.radians(41 + 2 * k))
            img = imagen_sintetica(rng, d, psi, T, una, meta, piso=piso, linea=linea)
            imagenes.append(img.tobytes())
            e = estimador.procesar(img.tobytes(), T)
            casos.append({"modo": modo, "color_ref": color_ref, "T": T, "verdad": {"d": d, "psi": psi},
                          "valida": bool(e.valid), "d": e.d, "psi": e.psi, "n_lineas": e.n_lines,
                          "n_puntos": e.n_points, "pendiente": e.slope, "distancia_roja": e.red_dist,
                          "calidad": e.quality})
    return casos, b"".join(imagenes)


def casos_filtro(rng, n=80):
    filtro, ctrl = LaneFilter(), LaneController(vx_max=0.8)
    casos = []

    class Est(object):
        valid, n_lines, d, psi = False, 0, 0.0, 0.0
    for k in range(n):
        dx, dy, dth = float(rng.uniform(0, 0.02)), float(rng.normal(0, 0.003)), float(rng.normal(0, 0.02))
        filtro.predict(dx, dy, dth)
        est = Est()
        est.valid = bool(rng.random() > 0.2)
        est.n_lines = int(rng.choice([1, 2]))
        est.d = float(rng.normal(0, 0.05) + (0.5 if k == 40 else 0.0))
        est.psi = float(rng.normal(0, 0.05))
        aceptada = filtro.update(est)
        confianza = float(rng.uniform(0, 1))
        comando = ctrl.command(filtro.d, filtro.psi, confianza)
        casos.append({"pred": [dx, dy, dth], "est": {"valida": est.valid, "n_lineas": est.n_lines, "d": est.d, "psi": est.psi},
                      "aceptada": aceptada, "d": filtro.d, "psi": filtro.psi, "s": filtro.s, "P_d": filtro.P_d,
                      "P_psi": filtro.P_psi, "confianza": confianza, "comando": list(comando),
                      "margen": ctrl.margin(filtro.d)})
    return casos


def registro(hashes):
    politicas = {"version": "copa_race_politicas_v1", "carriles": {
        "rl": "Politica RL a nivel de articulaciones (CopaRLWalkEngine, cada 24 ms).",
        "bhuman": "WalkingEngine de B-Human + vision de carril (LaneFilter y LaneController de Daniel)."},
        "politicas": {}, "por_defecto": RECOMENDADA}
    for nombre, (estado, vx, descripcion) in POLITICAS.items():
        politicas["politicas"][nombre] = {"estado": estado, "vx_cmd": vx, "descripcion": descripcion,
                                          "archivo": nombre + ".cfg", "sha256": hashes[nombre],
                                          "fuente": "policies/%s" % nombre}
    return politicas


def main():
    parser = argparse.ArgumentParser(description="Exporta las politicas de carrera para el NAO y los datos de paridad.")
    parser.add_argument("--semilla", type=int, default=20261103)
    args = parser.parse_args()
    rng = np.random.default_rng(args.semilla)
    observaciones = observaciones_reales()
    dorado = {"version": "carrera_golden_v1", "semilla": args.semilla, "politicas": {}}
    hashes = {}
    for nombre in POLITICAS:
        modelo, vecnorm, parametros, digest = exportar(nombre)
        hashes[nombre] = digest
        # Los pesos no se repiten aqui: el arnes C++ lee el mismo .cfg que lee el robot.
        dorado["politicas"][nombre] = {"archivo": "bhuman/Config/NeuralNets/CopaRace/%s.cfg" % nombre,
                                       "periodoMarcha": parametros["periodoMarcha"], "vxCmd": parametros["vxCmd"],
                                       "casos": casos_politica(modelo, vecnorm, observaciones, rng)}
        print("exportada %-12s sha256=%s" % (nombre, digest))
    dorado["contrato"], dorado["camara"] = casos_contrato(rng)
    dorado["azar"] = casos_azar()
    dorado["vision"], imagenes = casos_vision(rng)
    dorado["filtro"] = casos_filtro(rng)
    dorado["vision_modos"], imagenes_modos = casos_vision_modos(rng)
    (SALIDA / "politicas.json").write_text(json.dumps(registro(hashes), indent=2, ensure_ascii=False) + "\n",
                                           encoding="utf-8", newline="\n")
    PARIDAD.mkdir(parents=True, exist_ok=True)
    (PARIDAD / "carrera_golden.json").write_text(json.dumps(dorado) + "\n", encoding="utf-8", newline="\n")
    (PARIDAD / "imagenes_carril.bin").write_bytes(imagenes)
    (PARIDAD / "imagenes_carril_modos.bin").write_bytes(imagenes_modos)
    validas = sum(1 for c in dorado["vision"] if c["valida"])
    print("vision: %d/%d imagenes con carril; datos en %s" % (validas, len(dorado["vision"]), PARIDAD))
    for caso in dorado["vision_modos"]:
        print("vision %-5s valida=%s d=%+.3f (verdad %+.3f) psi=%+.3f (verdad %+.3f) meta=%s" % (
            caso["modo"], caso["valida"], caso["d"], caso["verdad"]["d"], caso["psi"], caso["verdad"]["psi"],
            caso["distancia_roja"]))


if __name__ == "__main__":
    main()
