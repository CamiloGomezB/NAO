"""Despliega la Carrera Individual (Copa NAO CCM MX 2026) en NAO V6 reales por Ethernet.

Lo usa la ventana de despliegue (deploy/deploy_dialog.py) y tambien la linea de comandos:

    uv run python deploy/robot_deploy.py --list
    uv run python deploy/robot_deploy.py --ping falcanao loki
    uv run python deploy/robot_deploy.py --deploy falcanao:rl loki:bhuman --team 49 --policy rl_v1.2.1
    uv run python deploy/robot_deploy.py --status falcanao

Los robots salen de bhuman/Config/Robots/<nombre>/network.cfg (direccion LAN). Cada paso remoto corre en WSL
(Windows) o bash (Linux) desde el arbol de scripts/compilar_bhuman.py con bhuman/Make/Common/deployCopaRace. El
Wi-Fi se apaga por defecto (regla 2.7). La vision (polaridad de la linea y modo color) sale por defecto de
config/pista_robot.json, que se genera desde config/pista.yaml: los colores no se escriben a mano.
Es la misma herramienta de PenaltyStack (deploy/robot_deploy.py), con el escenario de la carrera.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
import json
import os
from pathlib import Path
import re
import shlex
import subprocess
import sys
import threading

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))

import compilar_bhuman as robot_build  # noqa: E402

ROBOTS = ROOT / 'bhuman/Config/Robots'
POLITICAS = ROOT / 'bhuman/Config/NeuralNets/CopaRace/politicas.json'
PISTA = ROOT / 'config/pista_robot.json'
CARRILES = ('rl', 'bhuman')
START_MODES = ('buttonOnly', 'whistleOnly', 'buttonOrWhistle')
VISIONES = ('pista', 'oscura', 'clara')   # pista = lo que diga config/pista_robot.json
CONFIGS = robot_build.CONFIGS
WORK_COMMON = robot_build.WORK + '/Make/Common'
# coreutils 9.4 avisa por el `cp -n` del setupSSH original de B-Human; es inofensivo y confunde al operador.
CP_N_WARNING = 'cp: warning: behavior of -n is non-portable'


@dataclass(frozen=True)
class Robot:
    name: str
    lan: str
    wlan: str


@dataclass
class DeployOptions:
    lane: str = 'rl'
    policy: str = 'rl_v1.2.1'
    vx: float = 0.0             # 0 = el vx_cmd recomendado de la politica
    start_mode: str = 'buttonOnly'
    player: int = 1
    team: int = 0
    vision: str = 'pista'
    wifi_off: bool = True
    volume: int = 70
    restart: bool = True
    config: str = 'Release'
    dry_run: bool = False


def robots():
    """Robots de bhuman/Config/Robots/*/network.cfg, ordenados por nombre."""
    encontrados = []
    for network in sorted(ROBOTS.glob('*/network.cfg')):
        texto = network.read_text(encoding='utf-8', errors='replace')
        valores = dict(re.findall(r'^\s*(\w+)\s*=\s*"([^"]*)"\s*;', texto, re.M))
        if valores.get('lan'):
            encontrados.append(Robot(valores.get('name', network.parent.name), valores['lan'], valores.get('wlan', '')))
    return encontrados


def politicas():
    return json.loads(POLITICAS.read_text(encoding='utf-8'))


def vision_pista():
    """Polaridad y color_ref de config/pista_robot.json (generado desde config/pista.yaml por demo/build_scene.py)."""
    try:
        pista = json.loads(PISTA.read_text(encoding='utf-8'))
    except (OSError, ValueError):
        pista = {}
    color_ref = pista.get('color_ref') if pista.get('modo_vision') == 'color' else None
    return {'clara': pista.get('polaridad') == 'clara' or color_ref is not None, 'color_ref': color_ref,
            'descripcion': 'linea %s sobre %s, modo %s' % (pista.get('linea', '?'), pista.get('piso', '?'),
                                                         pista.get('modo_vision', 'brillo'))}


def resolver_vision(vision):
    """(linea clara, color_ref o None) que recibe deployCopaRace."""
    if vision == 'pista':
        pista = vision_pista()
        return pista['clara'], pista['color_ref']
    return vision == 'clara', None


def validate(options):
    registro = politicas()
    if options.lane not in CARRILES:
        raise ValueError('carril desconocido: %s' % options.lane)
    if options.policy not in registro['politicas']:
        raise ValueError('politica RL desconocida: %s' % options.policy)
    if not (options.vx == 0 or 0.0 < options.vx <= 0.8):
        raise ValueError('vx_cmd fuera de (0, 0.8] m/s')
    if options.start_mode not in START_MODES:
        raise ValueError('modo de arranque desconocido: %s' % options.start_mode)
    if not 1 <= options.player <= 20:
        raise ValueError('numero de jugador fuera de 1..20')
    if options.config not in CONFIGS:
        raise ValueError('configuracion desconocida: %s' % options.config)
    if options.vision not in VISIONES:
        raise ValueError('vision desconocida: %s' % options.vision)
    _, color_ref = resolver_vision(options.vision)
    if color_ref is not None and [len(v) for v in color_ref] != [3, 3]:
        raise ValueError('color_ref de config/pista_robot.json mal formado: %s' % color_ref)


def deploy_command(robot, options):
    validate(options)
    clara, color_ref = resolver_vision(options.vision)
    color = ','.join('%.6f' % x for x in color_ref[0] + color_ref[1]) if color_ref else 'none'
    args = ['./deployCopaRace', options.config, robot.lan, '-n', robot.name, '-p', str(options.player),
            '--lane', options.lane, '--policy', options.policy, '--vx', '%g' % options.vx,
            '--start-mode', options.start_mode, '--light-line', 'on' if clara else 'off', '--color-ref', color,
            '-v', str(options.volume)]
    if options.team:
        args += ['-t', str(options.team)]
    if options.wifi_off:
        args += ['-w', 'NONE']
    if options.restart:
        args.append('-b')
    if options.dry_run:
        args.append('--dry-run')
    return 'cd "%s" && %s' % (WORK_COMMON, ' '.join(shlex.quote(a) for a in args))


def ssh_command(robot, remote):
    return ('cd "%s" && source ./setupSSH && ssh $SSHOPTIONS -o ConnectTimeout=4 nao@%s %s'
            % (WORK_COMMON, shlex.quote(robot.lan), shlex.quote(remote)))


def stream(script, on_line, distro=robot_build.DEFAULT_DISTRO):
    """Corre un script de bash (WSL en Windows) y pasa cada linea de salida a on_line. Devuelve el codigo."""
    if sys.platform == 'win32':
        command = ['wsl.exe', '-d', distro, '--exec', 'bash', '-lc', script]
    else:
        command = ['bash', '-lc', script]
    flags = getattr(subprocess, 'CREATE_NO_WINDOW', 0)
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                               encoding='utf-8', errors='replace', creationflags=flags)
    assert process.stdout is not None
    with process.stdout:
        for line in process.stdout:
            if not line.startswith(CP_N_WARNING):
                on_line(line.rstrip('\n'))
    return process.wait()


def ping(robot):
    """True si el robot responde en su direccion LAN (ping de Windows, sin WSL)."""
    if sys.platform == 'win32':
        command = ['ping', '-n', '1', '-w', '800', robot.lan]
    else:
        command = ['ping', '-c', '1', '-W', '1', robot.lan]
    flags = getattr(subprocess, 'CREATE_NO_WINDOW', 0)
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                            errors='replace', creationflags=flags)
    return result.returncode == 0 and 'TTL=' in result.stdout.upper()


def sync(on_line):
    return stream(robot_build.sync_script(), on_line)


def prepare_ssh(on_line):
    """Copia la llave del robot a /tmp una sola vez antes de los despliegues en paralelo (setupSSH usa cp -n)."""
    return stream('cd "%s" && source ./setupSSH && echo "llave SSH lista"' % WORK_COMMON, on_line)


def build(config, on_line):
    return stream(robot_build.build_script(config, os.cpu_count() or 4), on_line)


def deploy(robot, options, on_line):
    return stream(deploy_command(robot, options), on_line)


def status(robot, on_line):
    remote = ('echo "bhuman: $(systemctl --user is-active bhuman.service)"; '
              'cat /home/nao/Config/carrera_deploy.json 2>/dev/null || echo "sin manifiesto de la carrera"')
    return stream(ssh_command(robot, remote), on_line)


def service(robot, action, on_line):
    if action not in ('start', 'stop', 'restart'):
        raise ValueError(action)
    return stream(ssh_command(robot, 'systemctl --user %s bhuman.service && echo "bhuman %s ok"' % (action, action)),
                  on_line)


def download_logs(robot, destination, on_line):
    destination = Path(destination).resolve() / robot.name
    destination.mkdir(parents=True, exist_ok=True)
    script = ('cd "%s" && source ./setupSSH && rsync -rzce "ssh $SSHOPTIONS" nao@%s:/home/nao/logging/ "%s/"'
              % (WORK_COMMON, shlex.quote(robot.lan), robot_build.to_wsl_path(destination)))
    return stream(script, on_line)


def _parse_targets(values, known):
    by_name = {r.name.lower(): r for r in known}
    targets = []
    for value in values:
        name, _, lane = value.partition(':')
        robot = by_name.get(name.lower())
        if robot is None:
            if re.match(r'^\d+\.\d+\.\d+\.\d+$', name):
                robot = Robot(name, name, '')
            else:
                raise SystemExit('robot desconocido: %s' % name)
        targets.append((robot, lane or None))
    return targets


def main(argv=None):
    parser = argparse.ArgumentParser(description='Despliegue de la Carrera Individual (Copa NAO CCM MX 2026) por Ethernet.')
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument('--list', action='store_true', help='robots conocidos y politicas disponibles')
    action.add_argument('--ping', nargs='+', metavar='ROBOT')
    action.add_argument('--status', nargs='+', metavar='ROBOT')
    action.add_argument('--stop', nargs='+', metavar='ROBOT')
    action.add_argument('--start', nargs='+', metavar='ROBOT')
    action.add_argument('--deploy', nargs='+', metavar='ROBOT[:CARRIL]')
    action.add_argument('--logs', nargs='+', metavar='ROBOT')
    parser.add_argument('--config', choices=CONFIGS, default='Release')
    parser.add_argument('--no-build', action='store_true', help='usar el binario ya compilado')
    parser.add_argument('--team', type=int, default=0)
    parser.add_argument('--first-player', type=int, default=1)
    parser.add_argument('--policy', default=None, help='politica RL (por defecto la recomendada)')
    parser.add_argument('--vx', type=float, default=0.0, help='vx_cmd [m/s]; 0 = el recomendado de la politica')
    parser.add_argument('--start-mode', choices=START_MODES, default='buttonOnly')
    parser.add_argument('--vision', choices=VISIONES, default='pista',
                        help='pista = polaridad y modo color de config/pista_robot.json (por defecto)')
    parser.add_argument('--keep-wifi', action='store_true', help='no apagar el Wi-Fi (prohibido en competencia)')
    parser.add_argument('--volume', type=int, default=70)
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--logs-dir', default=str(ROOT / 'data/real/logs_robot'))
    args = parser.parse_args(argv)

    known = robots()
    registro = politicas()
    lock = threading.Lock()

    def printer(prefix):
        def emit(line):
            with lock:
                print('[%s] %s' % (prefix, line), flush=True)
        return emit

    if args.list:
        for robot in known:
            print('%-12s LAN %-15s WLAN %s' % (robot.name, robot.lan, robot.wlan))
        for name, entry in registro['politicas'].items():
            print('politica %-12s %-12s vx %.2f  %s' % (name, entry['estado'], entry['vx_cmd'], entry['descripcion']))
        pista = vision_pista()
        print('vision (config/pista_robot.json): %s; linea %s%s' % (pista['descripcion'], 'clara' if pista['clara'] else 'oscura',
              ', color_ref %s' % pista['color_ref'] if pista['color_ref'] else ''))
        return 0
    if args.ping:
        codes = []
        for robot, _ in _parse_targets(args.ping, known):
            ok = ping(robot)
            codes.append(ok)
            print('%-12s %-15s %s' % (robot.name, robot.lan, 'responde' if ok else 'SIN RESPUESTA'))
        return 0 if all(codes) else 1
    targets = _parse_targets(args.status or args.stop or args.start or args.deploy or args.logs, known)
    if args.status or args.stop or args.start or args.logs:
        def one(item):
            robot = item[0]
            if args.status:
                return status(robot, printer(robot.name))
            if args.logs:
                return download_logs(robot, args.logs_dir, printer(robot.name))
            return service(robot, 'stop' if args.stop else 'start', printer(robot.name))
        with ThreadPoolExecutor(max_workers=max(1, len(targets))) as pool:
            return max(pool.map(one, targets))

    if not args.no_build:
        if build(args.config, printer('compilacion')) != 0:
            print('La compilacion fallo; no se despliega.', file=sys.stderr)
            return 1
    elif sync(printer('sync')) != 0:
        return 1
    prepare_ssh(printer('ssh'))
    jobs = []
    for index, (robot, lane) in enumerate(targets):
        options = DeployOptions(lane=lane or 'rl', policy=args.policy or registro['por_defecto'], vx=args.vx,
                                start_mode=args.start_mode, player=args.first_player + index, team=args.team,
                                vision=args.vision, wifi_off=not args.keep_wifi, volume=args.volume,
                                config=args.config, dry_run=args.dry_run)
        validate(options)
        jobs.append((robot, options))
    with ThreadPoolExecutor(max_workers=max(1, len(jobs))) as pool:
        codes = list(pool.map(lambda job: deploy(job[0], job[1], printer(job[0].name)), jobs))
    for (robot, _), code in zip(jobs, codes):
        print('%-12s %s' % (robot.name, 'DESPLEGADO' if code == 0 else 'ERROR (codigo %d)' % code))
    return 0 if all(code == 0 for code in codes) else 1


if __name__ == '__main__':
    sys.exit(main())
