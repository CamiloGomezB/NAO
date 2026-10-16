"""Compila (compilacion cruzada) el ejecutable `bhuman` del NAO V6 desde bhuman/ (framework B-Human 2023).

En Windows todo corre dentro de WSL: bhuman/ se copia al sistema de archivos ext4 de WSL (mucho mas rapido que
/mnt/c), se configura con el NaoToolchain.cmake original (clang + mold + sysroot V6) y se compila con Ninja. En
Linux corre nativo. El binario queda en el arbol de WSL, desde donde deploy/robot_deploy.py lo copia a los robots.
Es la misma herramienta de PenaltyStack (tools/robot_build.py) con el arbol de este repo.

    uv run python scripts/compilar_bhuman.py                     # compilacion Release
    uv run python scripts/compilar_bhuman.py --config Develop
    uv run python scripts/compilar_bhuman.py --install-toolchain # clang/mold/cmake/ccache/ninja sin sudo
    uv run python scripts/compilar_bhuman.py --check             # solo revisa las herramientas
    uv run python scripts/compilar_bhuman.py --check-originals   # originales de B-Human modificados y archivos nuevos
"""
import argparse
import json
import os
from pathlib import Path
import shlex
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
ROBOT = ROOT / 'bhuman'
CONFIGS = ('Release', 'Develop', 'Debug')
DEFAULT_DISTRO = os.environ.get('PENALTYSTACK_WSL_DISTRO', 'Ubuntu-24.04')
WORK = '$HOME/.cache/nao-race/bhuman'
TOOLCHAIN = '$HOME/.local/penaltystack-toolchain'
# Paquetes de Ubuntu 24.04 para el toolchain en el perfil del usuario (sin sudo): clang 18, mold, cmake, ccache, ninja.
# Es el mismo directorio que usa PenaltyStack: si ya esta instalado, sirve para los dos repos.
TOOLCHAIN_PACKAGES = ('ccache libhiredis1.1.0 ninja-build clang-18 cmake cmake-data libarchive13t64 libclang-common-18-dev libclang-cpp18 '
                      'libclang1-18 libgc1 libjsoncpp25 libllvm18 libobjc-13-dev libobjc4 librhash0 '
                      'llvm-18-linker-tools mold')
# Scripts agregados por este repo (los bits de ejecucion de los originales salen de PROVENANCE.json).
EXTRA_EXECUTABLES = ('Make/Common/deployCopaRace',)

ENVIRONMENT = r'''
TC="%(toolchain)s"
if [ -x "$TC/bin/clang++" ]; then
  export PATH="$TC/bin:$PATH"
  export LD_LIBRARY_PATH="$TC/root/usr/lib/x86_64-linux-gnu:$TC/root/usr/lib/llvm-18/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
fi
''' % {'toolchain': TOOLCHAIN}


def to_wsl_path(path):
    path = Path(path).resolve()
    if os.name != 'nt':
        return str(path)
    drive, rest = path.drive, path.as_posix()[len(path.drive):]
    return '/mnt/' + drive[0].lower() + rest


def run_bash(script, distro=DEFAULT_DISTRO, check=True, capture=False):
    """Corre un script de bash nativo o en WSL; muestra la salida salvo que se capture."""
    if os.name == 'nt':
        # --exec evita el shell externo de WSL, que expandiria las $variables antes de tiempo.
        command = ['wsl.exe', '-d', distro, '--exec', 'bash', '-lc', script]
    else:
        command = ['bash', '-lc', script]
    env = dict(os.environ, MSYS_NO_PATHCONV='1')
    if capture:
        return subprocess.run(command, env=env, check=check, text=True,
                              stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return subprocess.run(command, env=env, check=check, text=True)


def executables():
    provenance = json.loads((ROBOT / 'PROVENANCE.json').read_text(encoding='utf-8'))
    names = [name for name, info in provenance['files'].items() if info.get('executable')]
    return sorted(set(names) | set(EXTRA_EXECUTABLES))


def modified_originals():
    """Originales importados cuyos bytes cambiaron y archivos agregados por este repo (solo bhuman/)."""
    import hashlib
    provenance = json.loads((ROBOT / 'PROVENANCE.json').read_text(encoding='utf-8'))
    changed, missing = [], []
    for name, info in sorted(provenance['files'].items()):
        path = ROBOT / name
        if not path.is_file():
            missing.append(name)
        elif hashlib.sha256(path.read_bytes()).hexdigest() != info['sha256']:
            changed.append(name)
    added = sorted(p.relative_to(ROBOT).as_posix() for p in ROBOT.rglob('*')
                   if p.is_file() and not p.relative_to(ROBOT).as_posix().startswith('Build/')
                   and p.relative_to(ROBOT).as_posix() not in provenance['files']
                   and p.name != 'PROVENANCE.json')
    return changed, missing, added


def sync_script():
    """Copia bhuman/ al arbol de trabajo de WSL y restaura los bits de ejecucion."""
    chmod = ' '.join(shlex.quote(name) for name in executables())
    return ENVIRONMENT + r'''
set -euo pipefail
SRC=%(src)s
WORK="%(work)s"
mkdir -p "$WORK"
rsync -a --delete --exclude=/Build/ --exclude=/PROVENANCE.json "$SRC/" "$WORK/"
cd "$WORK"
for f in %(chmod)s; do [ -f "$f" ] && chmod +x "$f"; done
''' % {'src': shlex.quote(to_wsl_path(ROBOT)), 'work': WORK, 'chmod': chmod}


def check_script():
    return ENVIRONMENT + r'''
missing=0
for tool in clang++ ld.mold cmake ccache ninja rsync ssh; do
  if command -v $tool >/dev/null 2>&1; then echo "ok      $tool -> $(command -v $tool)"; else echo "missing $tool"; missing=1; fi
done
exit $missing
'''


def build_script(config, jobs):
    return sync_script() + r'''
BUILD="$WORK/Build/Linux/CMake/%(config)s"
if [ ! -f "$BUILD/build.ninja" ]; then
  cmake -S "$WORK/Make/Linux" -B "$BUILD" -G Ninja -DBUILD_NAO=ON -DCMAKE_BUILD_TYPE=%(config)s
fi
cmake --build "$BUILD" --target Nao -- -j%(jobs)s
BIN="$WORK/Build/Linux/Nao/%(config)s/bhuman"
test -x "$BIN"
echo "BHUMAN_BINARY=$BIN"
sha256sum "$BIN"
''' % {'config': config, 'jobs': jobs}


def install_toolchain_script():
    return r'''
set -euo pipefail
T="%(toolchain)s"
mkdir -p "$T/debs" "$T/root" "$T/bin"
cd "$T/debs"
apt-get download %(packages)s
for d in *.deb; do dpkg -x "$d" "$T/root"; done
ln -sf ../root/usr/lib/llvm-18/bin/clang "$T/bin/clang"
ln -sf ../root/usr/lib/llvm-18/bin/clang++ "$T/bin/clang++"
ln -sf ../root/usr/bin/cmake "$T/bin/cmake"
ln -sf ../root/usr/bin/mold "$T/bin/mold"
ln -sf ../root/usr/bin/mold "$T/bin/ld.mold"
ln -sf ../root/usr/bin/ccache "$T/bin/ccache"
ln -sf ../root/usr/bin/ninja "$T/bin/ninja"
echo "Toolchain instalado en $T (rsync y ssh vienen de la distribucion)."
''' % {'toolchain': TOOLCHAIN, 'packages': TOOLCHAIN_PACKAGES}


def main(argv=None):
    parser = argparse.ArgumentParser(description='Compila bhuman para el NAO V6 (en WSL desde Windows).')
    parser.add_argument('--config', choices=CONFIGS, default='Release')
    parser.add_argument('--jobs', type=int, default=os.cpu_count() or 4)
    parser.add_argument('--distro', default=DEFAULT_DISTRO, help='distribucion de WSL (solo Windows)')
    parser.add_argument('--check', action='store_true', help='solo revisar las herramientas')
    parser.add_argument('--sync-only', action='store_true', help='solo copiar bhuman/ al arbol de trabajo')
    parser.add_argument('--check-originals', action='store_true',
                        help='listar los originales de B-Human/Sabana Herons modificados y los archivos nuevos')
    parser.add_argument('--install-toolchain', action='store_true',
                        help='descargar clang/mold/cmake/ccache/ninja del archivo de Ubuntu al perfil del usuario')
    args = parser.parse_args(argv)
    if args.check_originals:
        changed, missing, added = modified_originals()
        for title, names in (('originales modificados', changed), ('originales faltantes', missing), ('archivos nuevos', added)):
            print('%s (%d):' % (title, len(names)))
            for name in names:
                print('  ' + name)
        return 1 if missing else 0
    if args.install_toolchain:
        return run_bash(install_toolchain_script(), args.distro, check=False).returncode
    if args.check:
        return run_bash(check_script(), args.distro, check=False).returncode
    if args.sync_only:
        return run_bash(sync_script(), args.distro, check=False).returncode
    if run_bash(check_script(), args.distro, check=False, capture=True).returncode != 0:
        print('Toolchain incompleto. Ejecuta: python tools/robot_build.py --install-toolchain '
              '(o en WSL: sudo apt install clang mold cmake ccache ninja-build rsync)', file=sys.stderr)
        return 2
    return run_bash(build_script(args.config, max(1, args.jobs)), args.distro, check=False).returncode


if __name__ == '__main__':
    sys.exit(main())
