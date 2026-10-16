"""Importa el subconjunto del framework B-Human 2023 / SabanaHerons2026 que necesita el NAO V6.

Copia de la revision fijada de SabanaHerons2026 (base: B-Human Code Release 2023) todo lo necesario para
compilar el ejecutable `bhuman` del NAO V6 y desplegarlo por Ethernet: CMake, scripts de despliegue e
instalacion, codigo, configuracion (sin escenas de SimRobot), el sysroot V6 y las librerias Linux/V6. Deja
fuera binarios de Windows/macOS, SimRobot y librerias de escritorio. Los submodulos CompiledNN y SimRobot
(solo Eigen) se toman de checkouts locales en sus commits fijados.

Es la misma importacion que usa PenaltyStack (tools/import_robot_framework.py); aqui el destino es bhuman/.
Cada archivo importado queda con su SHA-256 en bhuman/PROVENANCE.json, y
`uv run python scripts/compilar_bhuman.py --check-originals` lista que originales se modificaron.

Uso (desde la raiz del repo):
    uv run python scripts/importar_framework_bhuman.py --source <SabanaHerons2026> --compilednn <CompiledNN> --simrobot <SimRobot>
"""
import argparse
import hashlib
import io
import json
from pathlib import Path
import subprocess
import tarfile

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / 'bhuman'
COMMIT = '2360ab1100ad28f70e190c893f6b095651ff0bbc'
UPSTREAM = 'https://github.com/juanulloa2050/SabanaHerons2026'
SUBMODULES = {
    'Util/CompiledNN': ('https://github.com/bhuman/CompiledNN',
                        '091512e44520debafe3f502974ee4c0c39158794', None),
    'Util/SimRobot': ('https://github.com/bhuman/SimRobot',
                      '732794cf0f7d617f92bba6a37c284b6b4ceb7912',
                      ('Make/CMake/Eigen.cmake', 'Util/Eigen/')),
}
INCLUDE = (
    'CMakeLists.txt', 'CMakePresets.json', 'License.md', 'CITATION.cff', '.editorconfig',
    'Make/CMake/', 'Make/Common/', 'Make/Linux/',
    'Src/', 'Config/', 'Install/',
    'Util/Buildchain/V6/', 'Util/CompiledNN2ONNX/include/', 'Util/GameController/', 'Util/MD5/',
    'Util/fftw-3.3/COPYRIGHT', 'Util/fftw-3.3/VERSION.txt', 'Util/fftw-3.3/fftw3.h', 'Util/fftw-3.3/V6/',
    'Util/flite/COPYING', 'Util/flite/VERSION', 'Util/flite/include/', 'Util/flite/lib/V6/',
    'Util/hdf5/COPYING', 'Util/hdf5/VERSION', 'Util/hdf5/include/', 'Util/hdf5/lib/V6/',
    'Util/libjpeg/README', 'Util/libjpeg/VERSION', 'Util/libjpeg/include/', 'Util/libjpeg/lib/V6/',
    'Util/onnxruntime/LICENSE', 'Util/onnxruntime/ThirdPartyNotices.txt',
    'Util/onnxruntime/VERSION_NUMBER', 'Util/onnxruntime/GIT_COMMIT_ID',
    'Util/onnxruntime/include/', 'Util/onnxruntime/lib/Linux/',
    'Util/sse2neon/', 'Util/voronoi/',
)
EXCLUDE = ('Config/Scenes/',)


def _selected(name, include=INCLUDE, exclude=EXCLUDE):
    if any(name.startswith(prefix) for prefix in exclude):
        return False
    if include is None:
        return True
    return any(name == entry or (entry.endswith('/') and name.startswith(entry)) for entry in include)


def _record(manifest, name, data, mode, origin):
    path = DEST / name
    if path.exists() and path.read_bytes() != data:
        raise ValueError('no se reemplaza un archivo modificado: bhuman/' + name)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    manifest['files'][name] = {'sha256': hashlib.sha256(data).hexdigest(),
                               'executable': bool(mode & 0o111), 'origin': origin}


def _normalize(path):
    parts = []
    for part in path.split('/'):
        if part == '..':
            parts.pop()
        elif part not in ('', '.'):
            parts.append(part)
    return '/'.join(parts)


def _read(tar, member):
    stream = tar.extractfile(member)
    if stream is None:
        raise ValueError('no es un archivo regular en el archivo tar: ' + member.name)
    return stream.read()


def _import_archive(manifest, repository, commit, origin, prefix='', include=INCLUDE, exclude=EXCLUDE,
                    pathspecs=()):
    # git archive lee el almacen de objetos en un commit exacto: un checkout sparse o parcial
    # igual exporta la revision fijada completa.
    archive = subprocess.check_output(['git', '-C', str(Path(repository).resolve()), 'archive',
                                       '--format=tar', commit, '--', *pathspecs])
    symlinks = {}
    with tarfile.open(fileobj=io.BytesIO(archive)) as tar:
        members = {m.name: m for m in tar.getmembers()}
        for name, member in members.items():
            if not _selected(name, include, exclude):
                continue
            if member.issym():
                symlinks[name] = member.linkname
            elif member.isfile():
                _record(manifest, prefix + name, _read(tar, member), member.mode, origin)
        # En Windows no se puede depender de enlaces simbolicos: se guardan los bytes del destino.
        for name, target in symlinks.items():
            resolved = _normalize(str(Path(name).parent / target).replace('\\', '/'))
            member = members[resolved]
            _record(manifest, prefix + name, _read(tar, member), member.mode, origin)
            manifest['materialized_symlinks'][prefix + name] = prefix + resolved


def import_framework(source, compilednn, simrobot):
    manifest = {'version': 'penaltystack_robot_framework_v1', 'source': UPSTREAM, 'commit': COMMIT,
                'base': 'B-Human Code Release 2023', 'submodules': {}, 'materialized_symlinks': {},
                'files': {}}
    _import_archive(manifest, source, COMMIT, 'SabanaHerons2026')
    for prefix, checkout in (('Util/CompiledNN', compilednn), ('Util/SimRobot', simrobot)):
        url, commit, subset = SUBMODULES[prefix]
        manifest['submodules'][prefix] = {'url': url, 'commit': commit}
        _import_archive(manifest, checkout, commit, prefix, prefix + '/', subset, (), subset or ())
    (DEST / 'PROVENANCE.json').write_text(json.dumps(manifest, indent=1, sort_keys=True) + '\n',
                                          encoding='utf-8')
    return manifest


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Importa el framework B-Human del NAO en bhuman/.')
    parser.add_argument('--source', required=True, help='checkout de SabanaHerons2026 (aunque sea sparse)')
    parser.add_argument('--compilednn', required=True, help='checkout de bhuman/CompiledNN en el commit fijado')
    parser.add_argument('--simrobot', required=True, help='checkout de bhuman/SimRobot con Eigen en el commit fijado')
    args = parser.parse_args()
    result = import_framework(args.source, args.compilednn, args.simrobot)
    total = sum(1 for _ in result['files'])
    print('Importados %d archivos del framework en bhuman/ (%d enlaces simbolicos materializados).'
          % (total, len(result['materialized_symlinks'])))
