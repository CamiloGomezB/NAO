"""Paridad entre el codigo del NAO (C++) y el codigo Python de la carrera.

Compila tests/robot_paridad (compilador del PC: Visual Studio en Windows) y reproduce
tests/robot_paridad/carrera_golden.json, escrito por scripts/exportar_politicas_robot.py:

  - las 6 politicas leidas de los mismos .cfg que se despliegan (bhuman/Config/NeuralNets/CopaRace/);
  - el contrato v1 (observacion de 54 valores, accion -> angulos con el presupuesto lateral, camara);
  - el azar de Python (para que el RANSAC de la vision sea el mismo);
  - la vision de carril en 10 imagenes sinteticas (d, psi, numero de lineas, meta roja);
  - el filtro y el controlador de carril.

Tambien revisa que politicas.json coincida con los .cfg (SHA-256). Sale con 0 si todo coincide.

Uso (desde la raiz del repo):
    uv run python scripts/check_paridad_robot.py
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARNES = ROOT / "tests/robot_paridad"
BUILD = ARNES / "build"
POLITICAS = ROOT / "bhuman/Config/NeuralNets/CopaRace"


def encontrar_cmake():
    cmake = shutil.which("cmake")
    if cmake or os.name != "nt":
        return cmake, []
    vswhere = Path("C:/Program Files (x86)/Microsoft Visual Studio/Installer/vswhere.exe")
    if not vswhere.is_file():
        return None, []
    instalaciones = json.loads(subprocess.check_output(
        [str(vswhere), "-latest", "-products", "*", "-requires",
         "Microsoft.VisualStudio.Component.VC.Tools.x86.x64", "-format", "json"], text=True))
    if not instalaciones:
        return None, []
    inst = instalaciones[0]
    generador = {17: "Visual Studio 17 2022", 18: "Visual Studio 18 2026"}.get(int(inst["installationVersion"].split(".")[0]))
    cmake = Path(inst["installationPath"]) / "Common7/IDE/CommonExtensions/Microsoft/CMake/CMake/bin/cmake.exe"
    return (str(cmake), ["-G", generador, "-A", "x64"]) if cmake.is_file() and generador else (None, [])


def main():
    registro = json.loads((POLITICAS / "politicas.json").read_text(encoding="utf-8"))
    for nombre, entrada in registro["politicas"].items():
        digest = hashlib.sha256((POLITICAS / entrada["archivo"]).read_bytes()).hexdigest()
        if digest != entrada["sha256"]:
            print("[FALLA] %s no coincide con politicas.json" % entrada["archivo"])
            return 1
    print("[OK] politicas.json coincide con los %d .cfg" % len(registro["politicas"]))
    cmake, generador = encontrar_cmake()
    if cmake is None:
        print("[FALLA] no hay CMake ni compilador de C++ (instalar Visual Studio Build Tools con C++)")
        return 2
    subprocess.run([cmake, "-S", str(ARNES), "-B", str(BUILD), *generador, "-DCMAKE_BUILD_TYPE=Release"],
                   check=True, capture_output=True, text=True)
    compilado = subprocess.run([cmake, "--build", str(BUILD), "--config", "Release"], capture_output=True, text=True)
    if compilado.returncode != 0:
        print(compilado.stdout[-4000:], compilado.stderr[-2000:])
        print("[FALLA] no compilo el arnes")
        return 1
    ejecutable = next(p for p in (BUILD / "Release/carrera_paridad.exe", BUILD / "carrera_paridad") if p.is_file())
    resultado = subprocess.run([str(ejecutable), str(ROOT)], capture_output=True, text=True)
    print(resultado.stdout.strip())
    if resultado.returncode != 0:
        print(resultado.stderr.strip())
        print("[FALLA] el C++ del NAO no coincide con Python")
        return 1
    print("[OK] el C++ del NAO coincide con Python")
    return 0


if __name__ == "__main__":
    sys.exit(main())
