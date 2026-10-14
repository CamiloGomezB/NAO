"""Pruebas automaticas del entorno de carrera NaoRace-v0 (pasos 53 a 57 del PLAN).

  1. API de Gymnasium (check_env) y reproducibilidad con semilla.
  2. Observacion (paso 53): el vector del entorno es igual al que arma src/race/contract.py (armar_observacion, la
     funcion que usara el NAO real) a partir de un "frame" con el formato de PenaltyStack sacado de la simulacion.
  3. Accion (paso 54): los objetivos de los servos son los de contract.accion_a_objetivos; 24 ms por accion.
  4. Faltas y recompensa (paso 55): salida de carril (con la posicion real de los pies), meta, barrera y caida.
  5. Episodio (paso 56): arranca quieto con error de colocacion dentro de +-10 cm y +-8 grados, 0.5 s de pie con
     la camara midiendo, friccion sorteada, 30 s como maximo.
  6. Camara simulada (paso 57): convencion de signos (seccion 6.7), 10 Hz, validez de 300 ms, y estadistica del
     ruido (media y sigma medidas frente a las sorteadas), reproducible con semilla.
  7. Rumbo objetivo de la IMU alineado al carril con las fotos tomadas de pie (paso 58c).
Termina con RESULTADO: OK o FALLA.

Uso:
    uv run python scripts/check_race_env.py
"""

import math
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import gymnasium as gym  # noqa: E402
import mujoco  # noqa: E402
from gymnasium.utils.env_checker import check_env  # noqa: E402

import src.envs  # noqa: E402, F401
from src.envs.nao_race_env import MEDIO_CARRIL_M, NaoRaceEnv  # noqa: E402
from src.race import contract as C  # noqa: E402

FALLAS = []


def revisar(ok, texto):
    print(f"   {'OK   ' if ok else 'FALLA'} {texto}")
    if not ok:
        FALLAS.append(texto)


def frame_desde_sim(env):
    """Frame con el formato del SensorAdapter de PenaltyStack, armado con el estado de la simulacion."""
    m, d = env.model, env.data
    ang, vel = [], []
    for n in C.NOMBRES_MODELO:
        try:
            j = m.joint(n)
            ang.append(float(d.qpos[j.qposadr[0]]))
            vel.append(float(d.qvel[j.dofadr[0]]))
        except KeyError:            # LHand y RHand no estan en el modelo
            ang.append(0.0)
            vel.append(0.0)
    _, kg = env.contactos_y_fsr()
    fsr = [kg[0] / 4] * 4 + [kg[1] / 4] * 4
    return {"angles": ang, "velocity": vel, "gyro": list(d.sensor("gyro").data),
            "orientation": list(d.sensor("torso_quat").data), "fsr": fsr}


def main() -> int:
    print("1. API y reproducibilidad")
    env = NaoRaceEnv()
    try:
        check_env(env, skip_render_check=True)
        revisar(True, "check_env de Gymnasium")
    except Exception as e:  # noqa: BLE001
        revisar(False, f"check_env: {e}")
    revisar(env.observation_space.shape == (C.DIM_OBSERVACION,) == (54,), "observacion de 54 valores")
    revisar(env.action_space.shape == (C.N_ACCION,) == (13,), "accion de 13 valores")
    revisar(abs(env.dt - 0.024) < 1e-12, f"una accion cada {env.dt * 1000:.0f} ms (12 x 2 ms)")
    seqs = []
    for _ in range(2):
        e = gym.make("NaoRace-v0")
        o, _ = e.reset(seed=7)
        acc = np.random.default_rng(7)
        s = [o]
        for _ in range(100):
            o, *_ = e.step(np.clip(acc.normal(0, 0.2, 13), -1, 1))
            s.append(o)
        seqs.append(np.array(s))
    revisar(np.array_equal(seqs[0], seqs[1]), "misma semilla = mismas 101 observaciones (camara, ruido y empujones incluidos)")

    print("2. Observacion = contract.armar_observacion (paso 53)")
    env = NaoRaceEnv(perturbaciones=False)      # sin ruido de sensores para comparar exacto
    obs, _ = env.reset(seed=3)
    rng = np.random.default_rng(3)
    peor = 0.0
    for k in range(200):
        a = np.clip(rng.normal(0, 0.3, 13), -1, 1)
        obs, _, term, _, _ = env.step(a)
        ref = C.armar_observacion(frame_desde_sim(env), env._rumbo_objetivo, env.camara.observacion(env.t),
                                  list(a), env.t, env.vx_cmd)
        peor = max(peor, float(np.max(np.abs(obs - np.array(ref, dtype=np.float32)))))
        if term:
            obs, _ = env.reset(seed=100 + k)
    revisar(peor < 1e-4, f"200 pasos: diferencia maxima {peor:.1e} con la observacion del contrato")
    sl = C.rebanadas_observacion()
    revisar(sl["d_camara"] == (7, 8) and sl["psi_camara"] == (8, 9) and sl["valido_camara"] == (9, 10),
            "d, psi y valido en los indices 7, 8 y 9")

    print("3. Accion (paso 54)")
    env = NaoRaceEnv(perturbaciones=False)
    env.reset(seed=1)
    peor = 0.0
    for _ in range(50):
        a = rng.uniform(-1, 1, 13)
        env.step(a)
        obj = C.accion_a_objetivos(a)
        peor = max(peor, float(np.max(np.abs(env.data.ctrl[env._act] - [obj[n] for n in C.ARTICULACIONES_ACCION]))))
    revisar(peor < 1e-12, f"ctrl de los 13 servos = contract.accion_a_objetivos (dif. {peor:.1e})")
    revisar(abs(env.data.ctrl[env.model.actuator("HeadYaw").id] - C.POSE_HOME["HeadYaw"]) < 1e-12,
            "las articulaciones no controladas quedan en home")
    rhyp = env.data.qpos[env.model.joint("RHipYawPitch").qposadr[0]]
    lhyp = env.data.qpos[env.model.joint("LHipYawPitch").qposadr[0]]
    # La igualdad es una restriccion blanda de MuJoCo: con acciones al azar se separan ~2e-3 rad (0.1 grados).
    revisar(abs(rhyp - lhyp) < 1e-2, f"RHipYawPitch sigue a LHipYawPitch (dif. {abs(rhyp - lhyp):.1e} rad < 0.01)")

    print("4. Faltas y recompensa (paso 55)")
    env = NaoRaceEnv(perturbaciones=False)
    env.reset(seed=1)
    env.data.qpos[1] = MEDIO_CARRIL_M - 0.05      # pie izquierdo pasa el borde interior de la linea
    mujoco.mj_forward(env.model, env.data)
    _, r, term, _, info = env.step(np.zeros(13))
    # El peso se lee de pesos.yaml: estaba fijo en -200 y quedo viejo cuando el paso 55b lo paso a -300 (E55).
    w_salida = env.pesos["salida_carril"]
    revisar(term and info["falta"] == "salida_carril" and info["terminos"]["salida_carril"] == w_salida,
            f"pie sobre la linea -> salida_carril, termina, {w_salida:.0f} (falta={info['falta']}, r={r:.1f})")
    env.reset(seed=1)
    env.data.qpos[1] = MEDIO_CARRIL_M - 0.15
    mujoco.mj_forward(env.model, env.data)
    _, _, term, _, info = env.step(np.zeros(13))
    revisar(not term and info["terminos"]["barrera_margen"] < 0, f"a {100 * info['margen_min']:.1f} cm de la linea: "
            f"barrera {info['terminos']['barrera_margen']:.2f}, sin terminar")
    env.reset(seed=1)
    env.data.qpos[0] = 4.96
    mujoco.mj_forward(env.model, env.data)
    _, _, _, _, info = env.step(np.zeros(13))
    _, _, _, _, info2 = env.step(np.zeros(13))
    revisar(info["meta"] and info["terminos"]["meta"] == 20.0 and info2["terminos"]["meta"] == 0.0,
            "punta del pie en x >= 5 m -> bono de meta +20 una sola vez")
    env.reset(seed=1)
    env.data.qpos[2] = 0.2
    mujoco.mj_forward(env.model, env.data)
    _, _, term, _, info = env.step(np.zeros(13))
    revisar(term and info["terminos"]["caida"] == -100.0, f"torso bajo -> caida -100 ({info['falta']})")
    env.reset(seed=1)
    _, _, term, _, info = env.step(np.zeros(13))
    revisar(not term and info["terminos"]["salida_carril"] == 0 and info["terminos"]["caida"] == 0,
            "de pie en el centro: sin faltas")

    print("5. Episodio (paso 56)")
    env = gym.make("NaoRace-v0")
    ys, yaws, mus, n_valido = [], [], [], 0
    for s in range(200):
        o, info = env.reset(seed=s)
        ys.append(info["d"])
        yaws.append(math.degrees(info["psi"]))
        mus += list(info["friccion"])
        n_valido += o[9] == 1.0
    ys, yaws = np.array(ys), np.array(yaws)
    revisar(np.all(np.abs(ys) <= 0.105) and np.all(np.abs(yaws) <= 8.5),
            f"colocacion en 200 resets: |d| max {100 * np.max(np.abs(ys)):.1f} cm, |psi| max "
            f"{np.max(np.abs(yaws)):.1f} grados; sigma {100 * ys.std():.1f} cm y {yaws.std():.1f} grados")
    # mu en [0.4, 1.2] y cada pie +-0.05 (asimetria 0.1): rango posible por pie [0.35, 1.25].
    revisar(0.35 <= min(mus) and max(mus) <= 1.25 and max(mus) - min(mus) > 0.6,
            f"friccion sorteada por pie entre {min(mus):.2f} y {max(mus):.2f} (posible: 0.35-1.25)")
    revisar(n_valido >= 150, f"tras 0.5 s de pie la camara ya midio en {n_valido}/200 episodios")
    e = NaoRaceEnv()
    o, info = e.reset(seed=0)
    revisar(abs(info["t"]) < 0.025 and abs(o[-3]) < 0.1 and abs(o[-2] - 1) < 0.01,
            f"el reloj de marcha arranca en 0 al terminar los 0.5 s de pie (t = {info['t']:.3f} s)")
    revisar(env.spec.max_episode_steps * 0.024 == 30.0, "30 s como maximo (1250 pasos de 24 ms)")

    print("6. Camara simulada (paso 57)")
    env = NaoRaceEnv(perturbaciones=False)
    env.reset(seed=1)
    for y, yaw in ((0.10, 0.0), (-0.10, 0.0), (0.0, math.radians(6)), (0.0, -math.radians(6))):
        env.reset(seed=1)
        env.data.qpos[1] = y
        env.data.qpos[3:7] = (math.cos(yaw / 2), 0, 0, math.sin(yaw / 2))
        mujoco.mj_forward(env.model, env.data)
        env._hist.clear()
        env._cam.update(sigma_d=0.0, sigma_psi=0.0, perdidas=0.0, malas=0.0)
        for _ in range(20):
            env.step(np.zeros(13))
        dm, pm, v = env.camara.observacion(env.t)
        ok = (abs(dm - y) < 0.02 and abs(pm - yaw) < 0.03)
        revisar(ok and v == 1.0, f"robot en y={100 * y:+.0f} cm, rumbo {math.degrees(yaw):+.0f} grados -> "
                f"d={100 * dm:+.1f} cm, psi={math.degrees(pm):+.1f} grados (signos de la seccion 6.7)")
    # Frecuencia, validez y estadistica del ruido con el robot quieto en el centro.
    env = NaoRaceEnv(perturbaciones=False)
    env.reset(seed=5)
    sd, sp = 0.03, math.radians(2.5)
    env._cam.update(sigma_d=sd, sigma_psi=sp, perdidas=0.2, malas=0.0)
    dv, pv = env.d_psi_reales()
    meds, t_meds, validos, pasos = [], [], [], 0
    ultimo = env.camara.t_medicion
    while pasos < 1250:
        env.step(np.zeros(13))
        pasos += 1
        if env.camara.t_medicion != ultimo:
            ultimo = env.camara.t_medicion
            meds.append((env.camara.d - env.d_psi_reales()[0], env.camara.psi - env.d_psi_reales()[1]))
            t_meds.append(ultimo)
        validos.append(env.camara.observacion(env.t)[2])
    meds = np.array(meds)
    dt = np.diff(t_meds)
    revisar(np.allclose(np.round(dt / 0.1), dt / 0.1, atol=1e-6) and np.min(dt) >= 0.1 - 1e-9,
            f"fotos en multiplos de 100 ms (10 Hz): {len(t_meds)} mediciones validas en 30 s")
    perd = 1 - len(t_meds) / 300
    revisar(0.12 < perd < 0.28, f"perdidas medidas {100 * perd:.0f} % (sorteadas 20 %)")
    revisar(abs(meds[:, 0].std() - sd) < 0.2 * sd and abs(meds[:, 0].mean()) < 0.25 * sd,
            f"ruido de d: media {100 * meds[:, 0].mean():+.2f} cm, sigma {100 * meds[:, 0].std():.2f} cm (sorteada 3.00)")
    revisar(abs(meds[:, 1].std() - sp) < 0.2 * sp and abs(meds[:, 1].mean()) < 0.25 * sp,
            f"ruido de psi: media {math.degrees(meds[:, 1].mean()):+.2f}, sigma {math.degrees(meds[:, 1].std()):.2f} "
            "grados (sorteada 2.50)")
    revisar(0.0 < np.mean(validos) < 1.0, f"valido = 1 el {100 * np.mean(validos):.0f} % del tiempo")
    env = NaoRaceEnv(vision=False)
    o, _ = env.reset(seed=1)
    for _ in range(50):
        o, *_ = env.step(np.zeros(13))
    revisar(o[7] == 0 and o[8] == 0 and o[9] == 0, "sin vision: d = psi = valido = 0")

    print("7. Rumbo objetivo de la IMU al arrancar (paso 58c, E50)")
    for yaw_g in (15.0, -25.0):
        e = NaoRaceEnv(perturbaciones=False, camara_perfecta=True, rumbo_objetivo="carril")
        o, info = e.reset(seed=1, options={"y0": 0.0, "yaw0": math.radians(yaw_g)})
        revisar(abs(math.degrees(o[6]) + yaw_g) < 1.5 and len(e._psi_de_pie) >= 4,
                f"arranca girado {yaw_g:+.0f} grados: error de rumbo de la IMU = {math.degrees(o[6]):+.1f} grados "
                f"(apunta al carril; {len(e._psi_de_pie)} fotos de pie)")
        e = NaoRaceEnv(perturbaciones=False, camara_perfecta=True, rumbo_objetivo="arranque")
        o, _ = e.reset(seed=1, options={"y0": 0.0, "yaw0": math.radians(yaw_g)})
        revisar(abs(math.degrees(o[6])) < 0.5, f"modo 'arranque' (v01/v02): error de rumbo {math.degrees(o[6]):+.1f} grados")
    e = NaoRaceEnv(perturbaciones=False, vision=False)
    o, _ = e.reset(seed=1, options={"y0": 0.0, "yaw0": math.radians(15)})
    revisar(abs(math.degrees(o[6])) < 0.5 and not e._psi_de_pie, "sin camara de pie: se usa el rumbo de la IMU")

    print(f"\nRESULTADO: {'OK' if not FALLAS else 'FALLA'}")
    return 0 if not FALLAS else 1


if __name__ == "__main__":
    sys.exit(main())
