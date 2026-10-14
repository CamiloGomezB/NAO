"""Dashboard local del avance del RL: benchmark de 3 carriles, versiones, 100 agentes, motores y simulacion.

Arma los datos desde results/ (nada se calcula de nuevo), los mete en una sola pagina HTML y la abre en el navegador.
Cualquiera que clone el repo lo ve igual con un comando. Los graficos usan d3 desde cdnjs: hace falta internet al abrir.

Uso:
    uv run python scripts/dashboard.py              # genera results/dashboard/index.html y lo abre
    uv run python scripts/dashboard.py --no-abrir   # solo lo genera

Fuentes de cada pestana:
    Benchmark   results/benchmark/benchmark.json, results/barridos/ronda2/comparacion_3_carriles/,
                results/carrera/carrera_v0{1,2}/benchmark_vx0.45/
    Versiones   lo anterior + la descripcion de cada version (abajo, VERSIONES)
    100 agentes results/barridos/ronda{1,2}/agente_*/resultado.json y base_carrera_v03.json
    Motores     results/riesgo_motores/riesgo.json (scripts/riesgo_motores.py)
    Simulacion  docs/plan_rl_carrera.md, seccion 6.8 (valores de src/envs/nao_race_env.py)
La pagina esta en scripts/dashboard/pagina.html.
"""

import argparse
import collections
import glob
import json
import sys
import webbrowser
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
PAGINA = ROOT / "scripts" / "dashboard" / "pagina.html"
SALIDA = ROOT / "results" / "dashboard" / "index.html"
D3 = "https://cdnjs.cloudflare.com/ajax/libs/d3/7.8.5/d3.min.js"

VERSIONES = [
    ("Sprint", "RL sprint (sep.)", "2026-09", 5, "Primera caminata por RL (modelo V5 aproximado, sin cámara)",
     "Punto de partida: aprender a caminar", "Camina a 0.2 m/s; no usa cámara (truco del giroscopio)"),
    ("v01", "carrera_v01", "2026-10-11", 15.3, "Entorno de carrera nuevo: modelo V6 oficial, cámara simulada, faltas del reglamento, fricción aleatoria y perturbaciones",
     "Entrenar la tarea real de la carrera desde cero", "Gana a B-Human con visión; se cae si pierde la cámara"),
    ("v02", "carrera_v02", "2026-10-11", 40, "Más pérdida de visión en el entrenamiento: 15 % de episodios sin cámara y apagones de 1–8 s",
     "La v01 se caía sin cámara (válido = 0 quedaba fuera de lo que conocía)", "Sin cámara llega 89/100 y no se cae"),
    ("1.0", "RL v1.0", "2026-10-11", 20, "Rumbo de la IMU alineado al carril con la cámara + salidas torcidas de hasta ±25° en el entrenamiento",
     "Si arrancaba torcida ≥ 8°, la IMU la empujaba a seguir torcida", "Llega desde salidas de ±15 cm y ±25°"),
    ("1.1", "RL v1.1", "2026-10-12", 6, "Ronda de 100 agentes con pesos sorteados y luego los 20 mejores con 5M pasos más; se elige el mejor checkpoint",
     "Buscar qué pesos de la recompensa hacen la caminata más rápida sin faltas", "La más rápida: premiar la velocidad y castigar cambios bruscos ayuda"),
]
EXPLICACION_PESOS = {
    "seguimiento_vx": "Premio por ir a la velocidad pedida", "barrera_margen": "Castigo por acercarse a la línea (< 10 cm)",
    "cambio_accion": "Castigo por cambios bruscos de los motores", "salida_carril": "Castigo por salirse del carril",
    "caida": "Castigo por caerse", "choque_piernas": "Castigo por chocar una pierna con la otra",
    "patron_marcha": "Premio por pisar al ritmo del reloj", "inclinacion": "Castigo por inclinar el torso",
    "vx_max": "Velocidad máxima pedida en el entrenamiento", "rumbo": "Premio por ir derecho",
    "centrado": "Castigo por alejarse del centro", "vel_lateral": "Castigo por moverse de lado", "vel_giro": "Castigo por girar",
    "meta": "Bono por llegar a la meta"}
SIMULACION = [
    ("Física", "Gravedad", "9.81 m/s², inclinada hasta ±1° por episodio", "Piso no perfectamente nivelado"),
    ("Física", "Paso de simulación", "2 ms (500 Hz)", "Estable con servos rígidos"),
    ("Física", "Masa del robot", "5.36 kg en 25 piezas", "Modelo oficial NAO V6 (B-Human = URDF de Aldebaran)"),
    ("Física", "Aire / viento", "No se simula", "Interior y < 0.5 m/s; los empujones cubren fuerzas externas"),
    ("Piso", "Fricción pie–suelo", "Aleatoria 0.4–1.2 por episodio, ±0.05 por pie", "La duela real no está medida (se espera 0.5–0.8)"),
    ("Piso", "Contacto", "Blando, constante de tiempo 20 ms", "Estándar de MuJoCo; el pie penetra 0.4 mm"),
    ("Motores", "Servo", "PD: kp 40, kv 0.5, par máx. 5 N·m", "Parámetros de B-Human"),
    ("Motores", "Fuerza de los servos", "±15 % por pierna", "Motores gastados o distintos"),
    ("Motores", "Calibración", "±1.5° por articulación", "Sensores de ángulo imperfectos"),
    ("Control", "Ciclo de la política", "24 ms", "Ciclo de 12 ms de PenaltyStack × 2"),
    ("Cámara", "Fotos", "10 por segundo", "Cámara del NAO a la resolución usada"),
    ("Cámara", "Error", "1–5 cm y 1–4°", "La cámara real se equivoca ~1 cm: margen"),
    ("Cámara", "Retardo y pérdidas", "50–250 ms; hasta 30 % de fotos perdidas", "Procesamiento y reflejos"),
    ("Cámara", "Apagones", "1–8 s; 15 % de episodios sin cámara", "Que no se caiga si la visión falla (desde v02)"),
    ("Perturbaciones", "Empujones", "Hasta 6 N y 0.4 N·m, cada 2–6 s", "Golpes y desequilibrios"),
    ("Perturbaciones", "Salida", "Hasta ±15 cm y ±25°", "Colocación a mano imprecisa (desde v1.0)"),
    ("Perturbaciones", "Sensores", "Ruido en giroscopio y ángulos; deriva de la brújula", "IMU real"),
]
MOTORES_REALES = [
    dict(articulaciones="HipPitch, KneePitch, AnklePitch", motor="Tipo 5 (22NT Z20)", reductora=130.85, par_parada_Nm=8.51,
         par_continuo_Nm=2.33, vel_max_rad_s=6.96),
    dict(articulaciones="HipYawPitch, HipRoll, AnkleRoll", motor="Tipo 1", reductora=201.3, par_parada_Nm=11.97,
         par_continuo_Nm=2.47, vel_max_rad_s=4.16)]


def leer(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def filas_resumen(resumen, etiqueta):
    return [dict(caminata=etiqueta, vision="sí" if r["vision"] else "no", mu=r["mu"], metas=r["metas"], n=r["n"],
                 caidas=r["caidas"], salidas=r["salidas"], t_meta_s=None if r["metas"] == 0 else round(r["t_meta_medio"], 2),
                 desvio_cm=round(r["desvio_max_medio_cm"], 1)) for r in resumen]


def spearman(x, y):
    rx, ry = np.argsort(np.argsort(x)), np.argsort(np.argsort(y))
    return float(np.corrcoef(rx, ry)[0, 1])


def datos():
    D = {}
    # Benchmark de 3 carriles (misma bateria para todos)
    b = leer(ROOT / "results/benchmark/benchmark.json")
    nombres = {"bhuman": "B-Human", "naoqi": "NAOqi", "rl": "RL sprint (sep.)"}
    bench = []
    for r in b["resumen"]:
        bench += filas_resumen([r], nombres[r["caminata"]])
    comp = ROOT / "results/barridos/ronda2/comparacion_3_carriles"
    bench += filas_resumen(leer(comp / "eval_model_vx0.45.json")["resumen"], "RL v1.0")
    bench += filas_resumen(leer(comp / "eval_model_3000000_steps_vx0.45.json")["resumen"], "RL v1.1")
    for v in ("carrera_v01", "carrera_v02"):
        bench += filas_resumen(leer(ROOT / f"results/carrera/{v}/benchmark_vx0.45/eval_model_vx0.45_arranque.json")["resumen"], v)
    for f in bench:
        f["clave"] = f"{f['caminata']}|{f['vision']}|{f['mu']}"
    D["benchmark"] = bench

    def t_bench(c):
        con = [f for f in bench if f["caminata"] == c and f["vision"] == "sí"]
        return (round(float(np.mean([f["t_meta_s"] for f in con if f["t_meta_s"]])), 2),
                f"{sum(f['metas'] for f in con)}/{sum(f['n'] for f in con)}")

    vers = []
    for orden, (ver, nombre, fecha, pasos, cambio, porque, resultado) in enumerate(VERSIONES):
        t, metas = t_bench(nombre)
        vers.append(dict(orden=orden, version=ver, politica=nombre, fecha=fecha, pasos_M=pasos, t_benchmark_s=t, metas=metas,
                         que_cambio=cambio, por_que=porque, resultado=resultado))
    for ref in ("B-Human", "NAOqi"):
        t, metas = t_bench(ref)
        vers.append(dict(orden=None, version=ref, politica=ref, fecha=None, pasos_M=None, t_benchmark_s=t, metas=metas,
                         que_cambio="Línea base", por_que="Comparación (réplica en simulación)", resultado=None))
    D["versiones"] = vers

    # Rondas de agentes
    r1 = []
    for p in sorted(glob.glob(str(ROOT / "results/barridos/ronda1/agente_*/resultado.json"))):
        r = leer(p)
        s, pu = r["sorteo"], r["puntaje"]
        r1.append(dict(agente=r["agente"], pasa="sí" if pu["pasa_filtro"] else "no", faltas=pu["faltas"],
                       puntaje_s=None if pu["puntaje"] is None else round(pu["puntaje"], 2), vx_max=s["vx_max"],
                       friccion_min=s["friction_range"][0], friccion_max=s["friction_range"][1],
                       **{k: round(v, 3) for k, v in s["pesos"].items() if k != "choque_robot"}))
    D["ronda1"] = r1
    r2 = []
    for p in sorted(glob.glob(str(ROOT / "results/barridos/ronda2/agente_*/resultado.json"))):
        r = leer(p)
        pu, pa = r["puntaje"], r["puntaje_ronda_anterior"]
        r2.append(dict(agente=r["agente"], pasa="sí" if pu["pasa_filtro"] else "no", faltas=pu["faltas"],
                       puntaje_s=None if pu["puntaje"] is None else round(pu["puntaje"], 2),
                       checkpoint_M=round(r.get("pasos_elegidos", 5e6) / 1e6),
                       puntaje_ronda1_s=None if pa["puntaje"] is None else round(pa["puntaje"], 2), desvio_cm=round(pu["desvio_max_cm"], 1)))
    D["ronda2"] = r2
    D["base_rondas"] = [dict(ronda=n, puntaje_base_s=round(leer(ROOT / f"results/barridos/{n}/base_carrera_v03.json")["puntaje"]["puntaje"], 2))
                        for n in ("ronda1", "ronda2")]

    def correl(ronda):
        res = [leer(p) for p in glob.glob(str(ROOT / f"results/barridos/{ronda}/agente_*/resultado.json"))]
        pas = [r for r in res if r["puntaje"]["pasa_filtro"]]
        y = [r["puntaje"]["puntaje"] for r in pas]
        out = {k: spearman([r["sorteo"]["pesos"][k] for r in pas], y) for k in pas[0]["sorteo"]["pesos"] if k != "choque_robot"}
        out["vx_max"] = spearman([r["sorteo"]["vx_max"] for r in pas], y)
        return out

    c1, c2 = correl("ronda1"), correl("ronda2")
    D["pesos"] = [dict(parametro=k, que_es=EXPLICACION_PESOS.get(k, k), rho_ronda1=round(c1[k], 2), rho_ronda2=round(c2[k], 2)) for k in c1]

    # Motores
    rg = leer(ROOT / "results/riesgo_motores/riesgo.json")
    por = collections.defaultdict(list)
    for r in rg["corridas"]:
        por[r["caminata"]].append(r)
    nom = {"rl_v1.0 (vx 0.45)": "RL v1.0", "rl_v1.1 (vx 0.45)": "RL v1.1", "rl_v1.2 (vx 0.45)": "RL v1.2",
           "B-Human (0.30)": "B-Human", "NAOqi (0.12)": "NAOqi"}
    riesgo, resumen = [], []
    for c, n in nom.items():
        rs = por[c]
        if not rs:      # rl_v1.2 solo aparece cuando existe (fase M2)
            continue
        for j in rs[0]["articulaciones"]:
            def media(k):
                v = [r["articulaciones"][j].get(k) for r in rs]
                v = [x for x in v if x is not None]
                return float(np.mean(v)) if v else None
            rc = media("rms_vs_continuo")
            riesgo.append(dict(caminata=n, articulacion=j, par_rms_Nm=round(media("tau_rms"), 2),
                               rms_sobre_continuo_pct=None if rc is None else round(100 * rc),
                               pct_tiempo_sobre_continuo=None if media("pct_sobre_continuo") is None else round(media("pct_sobre_continuo"), 1),
                               vel_p99_rad_s=round(media("w_p99"), 2),
                               pct_fuera_curva=None if media("pct_fuera_envolvente") is None else round(media("pct_fuera_envolvente"), 1),
                               pct_cerca_tope=round(media("pct_cerca_tope"), 1), clave=f"{n}|{j}"))
        resumen.append(dict(caminata=n, t_s=round(float(np.mean([r["t"] for r in rs])), 1),
                            impacto_pico_x_peso=round(float(np.mean([r["grf_pico_sobre_peso"] for r in rs])), 2),
                            energia_J_m=round(float(np.mean([r["energia_por_m"] for r in rs])), 1),
                            choque_piernas_pct=round(float(np.mean([r["pct_choque_piernas"] for r in rs])), 2)))
    D["riesgo"], D["riesgo_resumen"], D["motores_reales"] = riesgo, resumen, MOTORES_REALES
    D["simulacion"] = [dict(grupo=g, parametro=p, valor=v, por_que=w) for g, p, v, w in SIMULACION]
    return D


ESTILO = """
:root { color-scheme: light;
  --font-anthropic-sans: "Segoe UI", system-ui, -apple-system, Roboto, "Helvetica Neue", Arial, sans-serif;
  --font-anthropic-serif: Georgia, "Times New Roman", serif;
  --cds-font-size-caption: 12px; --cds-font-size-body: 14px; --cds-font-size-heading: 16px; --cds-font-size-title: 30px;
  --cds-font-weight-medium: 600; --cds-gap-xs: 4px; --cds-gap-sm: 8px; --cds-gap-md: 16px; --cds-gap-lg: 24px; --cds-gap-xl: 32px;
  --cds-pad-xs: 4px; --cds-pad-sm: 8px; --cds-pad-md: 12px; --cds-pad-lg: 16px; --cds-radius: 8px; --cds-dur-slow: 300ms;
  --color-bg: #f7f7f5; --color-panel: #ffffff; --color-fg: #1b1b19; --color-fg-muted: #5f5e59; --color-border-line: #e3e2dc;
  --color-ok: #087a08; --color-warn: #a26800; --color-bad: #c22f2f;
  --cds-surface-popover: #ffffff; --cds-border: #d9d8d1; --cds-shadow-popover: 0 4px 16px rgba(0,0,0,.12); --cds-text-secondary: #5f5e59;
  --cds-chart-axis: #b9b8b0; --cds-chart-grid: #ecebe6; --cds-chart-muted: #c4c3bb; --cds-chart-reference: #8a8983; --cds-chart-status-critical: #d03b3b; }
@media (prefers-color-scheme: dark) { :root { color-scheme: dark;
  --color-bg: #151514; --color-panel: #1e1e1d; --color-fg: #f2f1ec; --color-fg-muted: #b3b2aa; --color-border-line: #33332f;
  --color-ok: #4cc34c; --color-warn: #f0b440; --color-bad: #ee6a6a;
  --cds-surface-popover: #262624; --cds-border: #3d3d39; --cds-shadow-popover: 0 4px 16px rgba(0,0,0,.5); --cds-text-secondary: #b3b2aa;
  --cds-chart-axis: #55554f; --cds-chart-grid: #2b2b28; --cds-chart-muted: #5c5b55; --cds-chart-reference: #8f8e87; --cds-chart-status-critical: #e66767; } }
[hidden] { display: none !important; }
body { margin: 0; background: var(--color-bg); color: var(--color-fg); font-family: var(--font-anthropic-sans); }
#dash-root { max-width: 1280px; margin-inline: auto; padding: 24px clamp(16px, 4vw, 40px); }
.nx-pie { margin-top: 24px; font-size: 12px; color: var(--color-fg-muted); }
"""

# Reemplaza el servicio de dashboards de claude.ai: mismos llamados (dash.data, dash.onData, dash.calc, ...) sobre datos fijos.
ADAPTADOR = """
window.dash = (() => {
  const DATOS = __DATOS__;
  const oscuro = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
  const calcs = {}, subs = [];
  const api = {
    colors: oscuro ? ['#3987e5', '#d95926', '#199e70', '#c98500', '#d55181', '#008300', '#9085e9', '#e66767']
                   : ['#2a78d6', '#eb6834', '#1baf7a', '#eda100', '#e87ba4', '#008300', '#4a3aa7', '#e34948'],
    data(id) {
      if (id in DATOS) return { status: 'ok', data: DATOS[id], columns: Object.keys(DATOS[id][0] || {}), meta: [], refreshing: false };
      if (id in calcs) return { status: 'ok', data: calcs[id](), meta: [], refreshing: false };
      return { status: 'missing', data: [], meta: [], refreshing: false };
    },
    calc(id, cfg) { calcs[id] = () => cfg.fn(...cfg.inputs.map((i) => api.data(i).data)); },
    onData(fn) { subs.push(fn); fn(); },
    setLink(nombre) { try { history.replaceState(null, '', '#' + nombre); } catch (e) {} },
    params() { return {}; }, setParams() {}, resetParams() {}, refresh() {}, loader() {},
  };
  let t = null;
  window.addEventListener('resize', () => { clearTimeout(t); t = setTimeout(() => subs.forEach((f) => f()), 150); });
  return api;
})();
"""


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--no-abrir", action="store_true", help="solo generar el archivo, sin abrir el navegador")
    a = ap.parse_args()
    D = datos()
    pagina = PAGINA.read_text(encoding="utf-8")
    datos_js = json.dumps(D, ensure_ascii=False).replace("</", "<\\/")
    html = "\n".join([
        "<!doctype html>", '<html lang="es">', "<head>", '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">', "<title>Carrera NAO: avance del RL</title>",
        f"<style>{ESTILO}</style>", f'<script src="{D3}"></script>', "</head>", "<body>", '<div id="dash-root">',
        "<script>" + ADAPTADOR.replace("__DATOS__", datos_js) + "</script>", pagina,
        '<p class="nx-pie">Generado con <code>uv run python scripts/dashboard.py</code> a partir de <code>results/</code> '
        "del repo NAO. Los datos vienen de los archivos listados en el encabezado de ese script.</p>",
        "</div>", "</body>", "</html>"])
    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    SALIDA.write_text(html, encoding="utf-8")
    print(f"Dashboard: {SALIDA.relative_to(ROOT).as_posix()} ({len(html) / 1024:.0f} KB; "
          + ", ".join(f"{k} {len(v)}" for k, v in D.items()) + ")")
    if not a.no_abrir:
        webbrowser.open(SALIDA.as_uri())
        print("Abierto en el navegador. Si no se abrió, abre ese archivo con doble clic.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
