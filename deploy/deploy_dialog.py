"""Ventana de despliegue de la Carrera Individual (Copa NAO CCM MX 2026), como el DeployDialog de Sabana Herons.

Selecciona los robots alcanzables por Ethernet, elige para cada uno el carril (RL o caminata de B-Human), la politica
RL, vx_cmd y el numero de jugador, y los despliega en paralelo. Es la ventana de PenaltyStack
(deploy/deploy_dialog.py) con las opciones de la carrera.

    DeployCarreraNAO.bat                         (Windows, doble clic)
    uv run python deploy/deploy_dialog.py
"""
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import queue
import sys
import threading
import time
import tkinter as tk
from tkinter import messagebox, ttk
from tkinter.scrolledtext import ScrolledText

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'deploy'))
sys.path.insert(0, str(ROOT / 'scripts'))

import check_grafo_modulos  # noqa: E402
import robot_deploy  # noqa: E402

STATE = ROOT / 'deploy/.deploy_dialog_state.json'
LANE_LABELS = {'rl': 'RL (politica)', 'bhuman': 'B-Human + vision'}
START_LABELS = {'buttonOnly': 'Boton medio de la cabeza (tras la senal del juez)',
                'whistleOnly': 'Silbato del juez',
                'buttonOrWhistle': 'Boton o silbato (lo primero)'}
VISION_LABELS = {'pista': 'Segun pista_robot.json: %s' % robot_deploy.vision_pista()['descripcion'],
                 'oscura': 'Linea oscura sobre piso claro (por brillo)',
                 'clara': 'Linea clara sobre piso oscuro (por brillo)'}
COLORS = {'ok': '#1a7f37', 'error': '#cf222e', 'unknown': '#8c959f', 'busy': '#9a6700'}


class RobotRow:
    def __init__(self, dialog, parent, row, robot, registro, saved):
        self.robot = robot
        self.selected = tk.BooleanVar(value=saved.get('selected', False))
        self.lane = tk.StringVar(value=LANE_LABELS.get(saved.get('lane', 'rl'), LANE_LABELS['rl']))
        policy = saved.get('policy', registro['por_defecto'])
        self.policy = tk.StringVar(value=policy if policy in registro['politicas'] else registro['por_defecto'])
        self.vx = tk.DoubleVar(value=saved.get('vx', 0.0))
        self.player = tk.IntVar(value=saved.get('player', row))
        ttk.Checkbutton(parent, variable=self.selected).grid(row=row, column=0, padx=4)
        ttk.Label(parent, text=robot.name, width=12).grid(row=row, column=1, sticky='w')
        ttk.Label(parent, text=robot.lan, width=14).grid(row=row, column=2, sticky='w')
        self.link = tk.Label(parent, text='● sin probar', fg=COLORS['unknown'], width=13, anchor='w')
        self.link.grid(row=row, column=3, sticky='w')
        ttk.Combobox(parent, textvariable=self.lane, values=list(LANE_LABELS.values()), width=16,
                     state='readonly').grid(row=row, column=4, padx=2)
        policy_box = ttk.Combobox(parent, textvariable=self.policy, values=list(registro['politicas']), width=14,
                                  state='readonly')
        policy_box.grid(row=row, column=5, padx=2)
        policy_box.bind('<<ComboboxSelected>>', lambda _event: dialog.describe(self.policy.get()))
        ttk.Spinbox(parent, from_=0.0, to=0.8, increment=0.05, format='%.2f', textvariable=self.vx,
                    width=6).grid(row=row, column=6, padx=2)
        ttk.Spinbox(parent, from_=1, to=20, textvariable=self.player, width=4).grid(row=row, column=7, padx=2)
        self.result = tk.Label(parent, text='', width=14, anchor='w')
        self.result.grid(row=row, column=8, sticky='w')

    def lane_name(self):
        return 'bhuman' if self.lane.get() == LANE_LABELS['bhuman'] else 'rl'

    def vx_value(self):
        try:
            return round(float(self.vx.get()), 3)
        except (tk.TclError, ValueError):
            return -1.0

    def state(self):
        return {'selected': self.selected.get(), 'lane': self.lane_name(), 'policy': self.policy.get(),
                'vx': max(self.vx_value(), 0.0), 'player': DeployDialog.safe_int(self.player, 1)}


class DeployDialog:
    def __init__(self, root):
        self.root = root
        self.events = queue.Queue()
        self.busy = False
        self.registro = robot_deploy.politicas()
        saved = self.load_state()
        root.title('Repo NAO - Despliegue Copa NAO CCM MX 2026 (Carrera Individual)')
        root.geometry('1120x720')
        root.minsize(980, 600)

        general = ttk.LabelFrame(root, text='Configuracion general')
        general.pack(fill='x', padx=10, pady=(10, 4))
        self.config = tk.StringVar(value=saved.get('config', 'Release'))
        self.compile = tk.BooleanVar(value=saved.get('compile', True))
        self.team = tk.IntVar(value=saved.get('team', 49))
        self.start_mode = tk.StringVar(value=START_LABELS[saved.get('start_mode', 'buttonOnly')])
        self.vision = tk.StringVar(value=VISION_LABELS.get(saved.get('vision', 'pista'), VISION_LABELS['pista']))
        self.wifi_off = tk.BooleanVar(value=saved.get('wifi_off', True))
        self.restart = tk.BooleanVar(value=saved.get('restart', True))
        self.volume = tk.IntVar(value=saved.get('volume', 70))
        self.dry_run = tk.BooleanVar(value=False)
        ttk.Label(general, text='Compilacion').grid(row=0, column=0, sticky='w', padx=6, pady=3)
        ttk.Combobox(general, textvariable=self.config, values=robot_deploy.CONFIGS, width=9,
                     state='readonly').grid(row=0, column=1, sticky='w')
        ttk.Checkbutton(general, text='Compilar antes de desplegar', variable=self.compile).grid(row=0, column=2, sticky='w', padx=8)
        ttk.Label(general, text='Equipo #').grid(row=0, column=3, sticky='e', padx=6)
        ttk.Spinbox(general, from_=0, to=255, textvariable=self.team, width=5).grid(row=0, column=4, sticky='w')
        ttk.Label(general, text='Volumen %').grid(row=0, column=5, sticky='e', padx=6)
        ttk.Spinbox(general, from_=0, to=100, increment=5, textvariable=self.volume, width=5).grid(row=0, column=6, sticky='w')
        ttk.Label(general, text='Arranque').grid(row=1, column=0, sticky='w', padx=6, pady=3)
        ttk.Combobox(general, textvariable=self.start_mode, values=list(START_LABELS.values()), width=44,
                     state='readonly').grid(row=1, column=1, columnspan=2, sticky='w')
        ttk.Checkbutton(general, text='Apagar Wi-Fi (regla 2.7: solo cable)', variable=self.wifi_off).grid(row=1, column=3, columnspan=2, sticky='w', padx=6)
        ttk.Checkbutton(general, text='Iniciar bhuman al terminar', variable=self.restart).grid(row=1, column=5, columnspan=2, sticky='w', padx=6)
        ttk.Label(general, text='Vision de la linea').grid(row=2, column=0, sticky='w', padx=6, pady=3)
        ttk.Combobox(general, textvariable=self.vision, values=list(VISION_LABELS.values()), width=56,
                     state='readonly').grid(row=2, column=1, columnspan=2, sticky='w')
        ttk.Checkbutton(general, text='Simulacro (no toca los robots)', variable=self.dry_run).grid(row=2, column=3, columnspan=2, sticky='w', padx=6)

        table = ttk.LabelFrame(root, text='Robots (red cableada)')
        table.pack(fill='x', padx=10, pady=4)
        for column, title in enumerate(('', 'Robot', 'IP LAN', 'Conexion', 'Carril', 'Politica RL',
                                        'vx_cmd (0 = pol.)', 'Jugador', 'Resultado')):
            ttk.Label(table, text=title, font=('Segoe UI', 9, 'bold')).grid(row=0, column=column, sticky='w', padx=2)
        rows = saved.get('robots', {})
        self.rows = [RobotRow(self, table, index + 1, robot, self.registro, rows.get(robot.name, {}))
                     for index, robot in enumerate(robot_deploy.robots())]

        self.description = ttk.Label(root, text='Selecciona una politica para ver su descripcion.', foreground='#57606a')
        self.description.pack(fill='x', padx=14)
        self.describe(self.registro['por_defecto'])

        buttons = ttk.Frame(root)
        buttons.pack(fill='x', padx=10, pady=6)
        self.buttons = []
        for text, command in (('Comprobar conexion', self.check_links), ('Validar escenario', self.validate),
                              ('Compilar', self.build), ('Desplegar seleccionados', self.deploy),
                              ('Estado', lambda: self.on_selected('status')),
                              ('Detener bhuman', lambda: self.on_selected('stop')),
                              ('Iniciar bhuman', lambda: self.on_selected('start')),
                              ('Descargar logs', lambda: self.on_selected('logs'))):
            button = ttk.Button(buttons, text=text, command=command)
            button.pack(side='left', padx=3)
            self.buttons.append(button)
        ttk.Button(buttons, text='Seleccionar todos', command=lambda: self.select_all(True)).pack(side='right', padx=3)
        ttk.Button(buttons, text='Ninguno', command=lambda: self.select_all(False)).pack(side='right', padx=3)

        self.log = ScrolledText(root, height=16, font=('Consolas', 9), state='disabled')
        self.log.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        self.log.tag_config('error', foreground=COLORS['error'])
        self.log.tag_config('ok', foreground=COLORS['ok'])
        root.protocol('WM_DELETE_WINDOW', self.close)
        root.after(100, self.pump)
        self.write('Robots leidos de bhuman/Config/Robots/*/network.cfg. Conecta el PC por Ethernet a la subred de los robots.')
        self.write('En el robot: pecho = ponerse de pie; boton medio = arrancar; trasero mantenido = detener; '
                   'delantero = rearmar (mantener 2 s esperando = cambiar carril); los tres botones 1 s = sin rigidez.')
        self.check_links()

    # -- estado ----------------------------------------------------------------------------
    def load_state(self):
        try:
            return json.loads(STATE.read_text(encoding='utf-8'))
        except (OSError, ValueError):
            return {}

    def start_mode_name(self):
        return next((k for k, v in START_LABELS.items() if v == self.start_mode.get()), 'buttonOnly')

    def vision_name(self):
        return next((k for k, v in VISION_LABELS.items() if v == self.vision.get()), 'pista')

    def save_state(self):
        data = {'config': self.config.get(), 'compile': self.compile.get(), 'team': self.safe_int(self.team, 0),
                'start_mode': self.start_mode_name(), 'vision': self.vision_name(),
                'wifi_off': self.wifi_off.get(), 'restart': self.restart.get(),
                'volume': self.safe_int(self.volume, 70), 'robots': {row.robot.name: row.state() for row in self.rows}}
        try:
            STATE.write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')
        except OSError:
            pass

    @staticmethod
    def safe_int(variable, default):
        try:
            return int(variable.get())
        except (tk.TclError, ValueError):
            return default

    def close(self):
        if self.busy and not messagebox.askyesno('Despliegue en curso', 'Hay una tarea en curso. Cerrar de todos modos?'):
            return
        self.save_state()
        self.root.destroy()

    # -- utilidades de la interfaz ---------------------------------------------------------
    def write(self, text, tag=None):
        self.events.put(('log', text, tag))

    def pump(self):
        try:
            while True:
                event = self.events.get_nowait()
                if event[0] == 'log':
                    _, text, tag = event
                    if tag is None:
                        tag = 'error' if ('error' in text.lower() or 'fallo' in text.lower()) else \
                              'ok' if ('DEPLOY_OK' in text or 'DESPLEGADO' in text) else None
                    self.log.configure(state='normal')
                    self.log.insert('end', time.strftime('%H:%M:%S ') + text + '\n', tag or ())
                    self.log.see('end')
                    self.log.configure(state='disabled')
                elif event[0] == 'link':
                    _, row, ok = event
                    row.link.configure(text='● responde' if ok else '● sin respuesta',
                                       fg=COLORS['ok' if ok else 'error'])
                elif event[0] == 'result':
                    _, row, text, kind = event
                    row.result.configure(text=text, fg=COLORS[kind])
                elif event[0] == 'busy':
                    self.busy = event[1]
                    for button in self.buttons:
                        button.configure(state='disabled' if self.busy else 'normal')
        except queue.Empty:
            pass
        self.root.after(100, self.pump)

    def describe(self, name):
        entry = self.registro['politicas'].get(name, {})
        self.description.configure(text='Politica %s [%s, vx_cmd %.2f m/s]: %s' % (
            name, entry.get('estado', '?'), entry.get('vx_cmd', 0.0), entry.get('descripcion', '')))

    def select_all(self, value):
        for row in self.rows:
            row.selected.set(value)

    def selected(self):
        rows = [row for row in self.rows if row.selected.get()]
        if not rows:
            messagebox.showinfo('Sin robots', 'Selecciona al menos un robot.')
        return rows

    def background(self, work):
        if self.busy:
            return
        self.save_state()
        self.events.put(('busy', True))

        def run():
            try:
                work()
            except Exception as error:  # noqa: BLE001 - se muestra al operador
                self.write('ERROR: %s' % error, 'error')
            finally:
                self.events.put(('busy', False))
        threading.Thread(target=run, daemon=True).start()

    def printer(self, prefix):
        return lambda line: self.write('[%s] %s' % (prefix, line))

    # -- acciones --------------------------------------------------------------------------
    def check_links(self):
        def work():
            with ThreadPoolExecutor(max_workers=max(1, len(self.rows))) as pool:
                for row, ok in zip(self.rows, pool.map(lambda r: robot_deploy.ping(r.robot), self.rows)):
                    self.events.put(('link', row, ok))
            self.write('Conexion comprobada.')
        self.background(work)

    def validate(self):
        def work():
            errors, used = check_grafo_modulos.check('CopaNAORace', 'Default')
            for error in errors:
                self.write('ERROR ' + error, 'error')
            self.write('Escenario CopaNAORace: %d modulos, %d errores.' % (len(used), len(errors)),
                       'ok' if not errors else 'error')
        self.background(work)

    def build(self):
        config = self.config.get()
        self.background(lambda: self.write('Compilacion %s: %s' % (
            config, 'OK' if robot_deploy.build(config, self.printer('compilacion')) == 0 else 'FALLO')))

    def options_for(self, row):
        return robot_deploy.DeployOptions(
            lane=row.lane_name(), policy=row.policy.get(), vx=row.vx_value(), start_mode=self.start_mode_name(),
            player=self.safe_int(row.player, 1), team=self.safe_int(self.team, 0), vision=self.vision_name(),
            wifi_off=self.wifi_off.get(), volume=self.safe_int(self.volume, 70), restart=self.restart.get(),
            config=self.config.get(), dry_run=self.dry_run.get())

    def deploy(self):
        rows = self.selected()
        if not rows:
            return
        jobs = []
        try:
            for row in rows:
                options = self.options_for(row)
                robot_deploy.validate(options)
                jobs.append((row, options))
        except ValueError as error:
            messagebox.showerror('Configuracion invalida', str(error))
            return
        players = [options.player for _, options in jobs]
        if len(set(players)) != len(players) and not messagebox.askyesno(
                'Numeros repetidos', 'Hay numeros de jugador repetidos. Continuar?'):
            return
        if not self.wifi_off.get() and not messagebox.askyesno(
                'Wi-Fi encendido', 'El reglamento (2.7) prohibe redes inalambricas en competencia. Desplegar sin apagar el Wi-Fi?'):
            return
        summary = '\n'.join('%s: carril %s, politica %s, vx_cmd %s, jugador %d' % (
            row.robot.name, LANE_LABELS[o.lane], o.policy,
            '%.2f' % o.vx if o.vx else 'de la politica (%.2f)' % self.registro['politicas'][o.policy]['vx_cmd'],
            o.player) for row, o in jobs)
        summary += '\nVision: %s' % self.vision.get()
        if not self.dry_run.get() and not messagebox.askyesno('Confirmar despliegue', summary + '\n\nDesplegar ahora?'):
            return
        compile_first, config = self.compile.get(), self.config.get()

        def work():
            if compile_first:
                if robot_deploy.build(config, self.printer('compilacion')) != 0:
                    self.write('La compilacion fallo; no se despliega.', 'error')
                    return
            elif robot_deploy.sync(self.printer('sync')) != 0:
                self.write('No se pudo preparar el arbol de compilacion.', 'error')
                return
            robot_deploy.prepare_ssh(self.printer('ssh'))
            for row, _ in jobs:
                self.events.put(('result', row, 'desplegando...', 'busy'))

            def one(job):
                row, options = job
                code = robot_deploy.deploy(row.robot, options, self.printer(row.robot.name))
                self.events.put(('result', row, 'OK' if code == 0 else 'error %d' % code, 'ok' if code == 0 else 'error'))
                return code
            with ThreadPoolExecutor(max_workers=len(jobs)) as pool:
                codes = list(pool.map(one, jobs))
            done = sum(1 for code in codes if code == 0)
            self.write('Despliegue terminado: %d/%d robots%s.' % (done, len(codes), ' (simulacro)' if jobs[0][1].dry_run else ''),
                       'ok' if done == len(codes) else 'error')
        self.background(work)

    def on_selected(self, action):
        rows = self.selected()
        if not rows:
            return
        logs = ROOT / 'data/real/logs_robot'

        def one(row):
            out = self.printer(row.robot.name)
            if action == 'status':
                return robot_deploy.status(row.robot, out)
            if action == 'logs':
                code = robot_deploy.download_logs(row.robot, logs, out)
                out('logs en %s' % (logs / row.robot.name))
                return code
            return robot_deploy.service(row.robot, action, out)

        def work():
            with ThreadPoolExecutor(max_workers=len(rows)) as pool:
                list(pool.map(one, rows))
        self.background(work)


def main():
    root = tk.Tk()
    DeployDialog(root)
    root.mainloop()


if __name__ == '__main__':
    main()
