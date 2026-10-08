"""Genera el modelo MuJoCo del NAO V6 a partir de la descripcion oficial de B-Human (RSI3).

Entrada:  assets/nao/bhuman/NaoV6H25.rsi3  (archivo original de B-Human, sin modificar)
Salidas:  assets/nao/meshes/*.obj           (mallas visuales del NAO V6)
          assets/nao/nao.xml                (MJCF que usa el entorno RL)

Del RSI3 se conservan: cuerpos, marcos y ejes articulares, rangos, masas e inercias, cajas/esferas de
colision, mallas y servos (p, d, fuerza maxima). Lo que se anade para el entorno RL se describe en
assets/nao/SOURCE.md.

Uso:
    uv run python scripts/build_nao_v6.py
"""

import hashlib
import math
import re
import xml.etree.ElementTree as ET
from pathlib import Path

import mujoco
import numpy as np

NAO_DIR = Path(__file__).resolve().parents[1] / "assets" / "nao"
SOURCE = NAO_DIR / "bhuman" / "NaoV6H25.rsi3"
SOURCE_SHA256 = "73f8c9a78b35fbdd18e6e407193924b2d1996812ff78cd405377cc57b0981369"
MESH_DIR = NAO_DIR / "meshes"
OUTPUT = NAO_DIR / "nao.xml"

UNITS = {"mm": 1e-3, "g": 1e-3, "degree": math.pi / 180, "g*mm^2": 1e-9, "": 1.0}
NUMBER = re.compile(r"^([-+0-9.eE]+)(mm|g|degree|g\*mm\^2)?$")
RGB = re.compile(r"rgb\((\d+)%\s*,\s*(\d+)%\s*,\s*(\d+)%\)")

# Etiquetas del RSI3 que el conversor entiende dentro del robot; cualquier otra detiene el proceso.
KNOWN_TAGS = {"Translation", "Rotation", "Set", "InertiaMatrixMass", "BoxGeometry", "SphereGeometry",
              "Geometry", "Appearance", "ComplexAppearance", "Gyroscope", "Accelerometer", "Camera", "Hinge"}

# Grupos de colision (bit en contype, grupos con los que choca en conaffinity), como en el modelo anterior:
# suelo=1, torso/cabeza/caderas=2, brazos=4, piernas/pies=8. Torso: suelo, brazos y piernas.
# Brazos y piernas: todo, incluido el otro brazo o la otra pierna.
COLLISION_GROUPS = (
    (("Nao", "Head", "LHip2", "RHip2"), "2", "13"),
    (("UpperArm", "LowerArm", "Wrist"), "4", "15"),
    (("Thigh", "Tibia", "Foot"), "8", "15"),
)
COLLISION_NAMES = {"Nao": "torso", "Head": "head", "LFoot": "left_foot", "RFoot": "right_foot"}
# Cajas que en el NAO real no se tocan dentro del rango articular, pero que con las primitivas de B-Human
# chocan en la articulacion intermedia: brazo-antebrazo al flexionar el codo, tibia-pie al mover el tobillo.
JOINT_EXCLUDES = [("LUpperArm", "LLowerArm"), ("RUpperArm", "RLowerArm"), ("LTibia", "LFoot"), ("RTibia", "RFoot")]

# Piel blanca del NAO (el RSI3 la define gris y la aclara con iluminacion propia de SimRobot).
# La camiseta de equipo de B-Human se muestra del mismo color.
WHITE = (0.92, 0.94, 0.97)
WHITE_SURFACES = {"NaoMat_MainSkin", "nao-$TeamColor"}

# Pose "home": rodillas flexionadas y brazos abajo (la misma del modelo anterior; las munecas en 0).
HOME = {
    "HipPitch": -0.4, "KneePitch": 0.8, "AnklePitch": -0.4,
    "LShoulderPitch": 1.57, "LShoulderRoll": 0.2, "LElbowYaw": -1.57, "LElbowRoll": -0.2,
    "RShoulderPitch": 1.57, "RShoulderRoll": -0.2, "RElbowYaw": 1.57, "RElbowRoll": 0.2,
}
SOLE_CLEARANCE_M = 0.0005  # holgura entre la suela y el suelo en "home"


def unit(text: str) -> float:
    match = NUMBER.match(text)
    if not match:
        raise ValueError(f"Unidad RSI3 no soportada: {text}")
    value, suffix = match.groups()
    return float(value) * UNITS[suffix or ""]


def vec(element, attrs="xyz") -> list[float]:
    return [unit(element.get(a, "0")) if element is not None else 0.0 for a in attrs]


def fmt(values) -> str:
    return " ".join(format(float(v), ".10g") for v in values)


def tokens(text: str | None) -> list[str]:
    """Numeros de un bloque de texto del RSI3 (admite comentarios con #)."""
    return [t for line in (text or "").splitlines() for t in line.split("#", 1)[0].split()]


def simrobot_quat(rotation) -> np.ndarray:
    """Cuaternion de un <Rotation> de SimRobot: R = Rz * Ry * Rx (ParserCore3::rotationElement)."""
    x, y, z = vec(rotation)
    quat = np.array([1.0, 0, 0, 0])
    for axis, angle in ((2, z), (1, y), (0, x)):
        q = np.zeros(4)
        mujoco.mju_axisAngle2Quat(q, np.eye(3)[axis], angle)
        mujoco.mju_mulQuat(quat, quat.copy(), q)
    return quat


class Rsi3:
    def __init__(self, path: Path):
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest != SOURCE_SHA256:
            raise ValueError(f"{path.name} no coincide con la version fijada (sha256 {digest})")
        root = ET.parse(path).getroot()
        self.defs = {tag: {e.get("name"): e for e in root.iter(tag) if e.get("name")}
                     for tag in ("Appearance", "ComplexAppearance", "Vertices", "Normals", "Surface")}
        self.robot = next(b for b in root.findall("Body") if b.get("name") == "Nao")

    def resolve(self, element, tag):
        return self.defs[tag][element.get("ref")] if element.get("ref") else element

    def meshes(self, appearance) -> list[str]:
        """Nombres de las ComplexAppearance (mallas) a las que remite una apariencia del cuerpo."""
        if appearance.tag == "ComplexAppearance":
            return [appearance.get("ref")]
        definition = self.defs["Appearance"][appearance.get("ref")]
        if definition.find("Translation") is not None or definition.find("Rotation") is not None:
            raise ValueError(f"Apariencia con transformacion propia no soportada: {definition.get('name')}")
        return [name for child in definition if child.tag in ("Appearance", "ComplexAppearance")
                for name in self.meshes(child)]

    def write_obj(self, name: str, path: Path) -> None:
        part = self.defs["ComplexAppearance"][name]
        vertices = tokens(self.resolve(part.find("Vertices"), "Vertices").text)
        normals_el = part.find("Normals")
        normals = tokens(self.resolve(normals_el, "Normals").text) if normals_el is not None else []
        index = [int(t) for t in tokens(part.find("Triangles").text)]
        # Con normales, SimRobot intercala indices (vertice, normal) por cada esquina del triangulo.
        stride = 2 if normals else 1
        if len(vertices) % 3 or len(normals) % 3 or len(index) % (3 * stride):
            raise ValueError(f"Malla RSI3 mal formada: {name}")
        if max(index[::stride]) >= len(vertices) // 3 or (normals and max(index[1::2]) >= len(normals) // 3):
            raise ValueError(f"Indice fuera de rango en la malla {name}")
        lines = [f"v {' '.join(vertices[i:i + 3])}" for i in range(0, len(vertices), 3)]
        lines += [f"vn {' '.join(normals[i:i + 3])}" for i in range(0, len(normals), 3)]
        corner = (lambda k: f"{index[k] + 1}//{index[k + 1] + 1}") if normals else (lambda k: str(index[k] + 1))
        step = 3 * stride
        lines += ["f " + " ".join(corner(k + j * stride) for j in range(3)) for k in range(0, len(index), step)]
        path.write_text("\n".join(lines) + "\n", encoding="ascii")

    def surface_rgba(self, name: str) -> tuple:
        part = self.defs["ComplexAppearance"][name]
        surface = part.find("Surface").get("ref")
        if surface in WHITE_SURFACES:
            return (*WHITE, 1.0)
        match = RGB.search(self.defs["Surface"][surface].get("diffuseColor", ""))
        return (*(int(c) / 100 for c in match.groups()), 1.0)


def collision_attrs(body: str) -> dict:
    for keys, contype, conaffinity in COLLISION_GROUPS:
        if body in keys or any(body.endswith(k) for k in keys):
            return {"contype": contype, "conaffinity": conaffinity}
    raise ValueError(f"Cuerpo con colision sin grupo asignado: {body}")


def build_xml(rsi3: Rsi3, torso_z: float, excludes: list[tuple[str, str]]) -> tuple[ET.Element, list, set]:
    """Construye el MJCF. Devuelve (raiz, articulaciones [(nombre, servo)], mallas usadas)."""
    mj = ET.Element("mujoco", model="nao_v6")
    ET.SubElement(mj, "compiler", angle="radian", autolimits="true", inertiafromgeom="false", meshdir="meshes")
    ET.SubElement(mj, "option", timestep="0.002", integrator="implicitfast")
    default = ET.SubElement(mj, "default")
    # Valores que SimRobotCore3 fija en cada articulacion con servo (ServoMotor::act).
    ET.SubElement(default, "joint", damping="0.01", armature="0.01", frictionloss="0")
    ET.SubElement(default, "geom", condim="3")
    ET.SubElement(ET.SubElement(default, "default", {"class": "visual"}), "geom",
                  type="mesh", contype="0", conaffinity="0", group="1")
    ET.SubElement(ET.SubElement(default, "default", {"class": "collision"}), "geom",
                  group="3", rgba="0.9 0.4 0.1 0.4")
    asset = ET.SubElement(mj, "asset")
    world = ET.SubElement(mj, "worldbody")
    joints, meshes, materials = [], set(), {}

    def add_body(src, dst):
        unknown = {child.tag for child in src} - KNOWN_TAGS - {"Body"}
        if unknown:
            raise ValueError(f"Etiquetas RSI3 no soportadas en {src.get('name')}: {sorted(unknown)}")
        name = src.get("name")
        inertia = src.find("InertiaMatrixMass")
        ET.SubElement(dst, "inertial", pos=fmt(vec(inertia)), mass=fmt([unit(inertia.get("value"))]),
                      fullinertia=fmt(unit(inertia.get(k)) for k in ("ixx", "iyy", "izz", "ixy", "ixz", "iyz")))
        for geom in src:
            if geom.tag not in ("BoxGeometry", "SphereGeometry"):
                continue
            attrs = {"name": COLLISION_NAMES.get(name, name), "class": "collision",
                     "pos": fmt(vec(geom.find("Translation"))), **collision_attrs(name)}
            if geom.tag == "BoxGeometry":
                attrs.update(type="box", size=fmt(unit(geom.get(k)) / 2 for k in ("depth", "width", "height")))
            else:
                attrs.update(type="sphere", size=fmt([unit(geom.get("radius"))]))
            if geom.find("Rotation") is not None:
                attrs["quat"] = fmt(simrobot_quat(geom.find("Rotation")))
            ET.SubElement(dst, "geom", attrs)
        for appearance in src:
            if appearance.tag not in ("Appearance", "ComplexAppearance"):
                continue
            for mesh in rsi3.meshes(appearance):
                meshes.add(mesh)
                rgba = fmt(rsi3.surface_rgba(mesh))
                material = materials.setdefault(rgba, f"nao_{len(materials)}")
                ET.SubElement(dst, "geom", {"class": "visual", "mesh": mesh, "material": material})
        for hinge in src.findall("Hinge"):
            if hinge.find("Rotation") is not None:
                raise ValueError(f"Articulacion rotada no soportada: {hinge.get('name')}")
            child = hinge.find("Body")
            body = ET.SubElement(dst, "body", name=child.get("name"), pos=fmt(vec(hinge.find("Translation"))))
            axis = hinge.find("Axis")
            limits = axis.find("Deflection")
            ET.SubElement(body, "joint", name=hinge.get("name"), axis=fmt(vec(axis)),
                          range=fmt([unit(limits.get("min")), unit(limits.get("max"))]))
            joints.append((hinge.get("name"), axis.find("ServoMotor")))
            add_body(child, body)

    torso = ET.SubElement(world, "body", name="torso", pos=fmt([0, 0, torso_z]))
    ET.SubElement(torso, "freejoint", name="root")
    accelerometer = rsi3.robot.find("Accelerometer/Translation")
    ET.SubElement(torso, "site", name="imu", pos=fmt(vec(accelerometer)))
    ET.SubElement(torso, "camera", name="track", mode="trackcom", pos="0 -1.18 0.21", xyaxes="1 0 0 0 0.174 0.985")
    add_body(rsi3.robot, torso)

    for rgba, material in materials.items():
        ET.SubElement(asset, "material", name=material, rgba=rgba, specular="0.3", shininess="0.3")
    for mesh in sorted(meshes):
        ET.SubElement(asset, "mesh", name=mesh, file=mesh + ".obj")

    if excludes:
        contact = ET.SubElement(mj, "contact")
        for body1, body2 in excludes:
            ET.SubElement(contact, "exclude", body1=body1, body2=body2)

    equality = ET.SubElement(mj, "equality")
    ET.SubElement(equality, "joint", name="hip_yaw_pitch_coupling", joint1="RHipYawPitch",
                  joint2="LHipYawPitch", polycoef="0 1 0 0 0")

    actuator = ET.SubElement(mj, "actuator")
    for name, servo in joints:
        if name == "RHipYawPitch":
            continue
        force = unit(servo.get("maxForce"))
        ET.SubElement(actuator, "position", name=name, joint=name, inheritrange="1",
                      kp=fmt([unit(servo.get("p"))]), kv=fmt([unit(servo.get("d"))]),
                      forcerange=fmt([-force, force]))

    sensor = ET.SubElement(mj, "sensor")
    ET.SubElement(sensor, "framequat", name="torso_quat", objtype="site", objname="imu")
    ET.SubElement(sensor, "gyro", name="gyro", site="imu")
    ET.SubElement(sensor, "accelerometer", name="accelerometer", site="imu")
    ET.SubElement(sensor, "velocimeter", name="local_linvel", site="imu")
    return mj, joints, meshes


def home_angle(joint: str) -> float:
    return HOME.get(joint, HOME.get(joint[1:], 0.0))


def add_foot_sites_and_keyframe(mj: ET.Element, joints: list, torso_z: float) -> None:
    """Sitios en el centro de cada suela y keyframe "home" (orden de qpos/ctrl = orden del modelo)."""
    for body in mj.iter("body"):
        name = COLLISION_NAMES.get(body.get("name"))
        if name in ("left_foot", "right_foot"):
            box = next(g for g in body.findall("geom") if g.get("name") == name)
            x, y, z = (float(v) for v in box.get("pos").split())
            half_height = float(box.get("size").split()[2])
            body.append(ET.Element("site", name=name, pos=fmt([x, y, z - half_height])))
    qpos = [0, 0, torso_z, 1, 0, 0, 0] + [home_angle(name) for name, _ in joints]
    ctrl = [home_angle(name) for name, _ in joints if name != "RHipYawPitch"]
    keyframe = ET.SubElement(mj, "keyframe")
    ET.SubElement(keyframe, "key", name="home", qpos=fmt(qpos), ctrl=fmt(ctrl))


def write(mj: ET.Element, path: Path) -> None:
    header = ET.Comment(
        "\n  NAO V6 (H25) para MuJoCo, generado por scripts/build_nao_v6.py. NO EDITAR A MANO."
        "\n  Fuente: assets/nao/bhuman/NaoV6H25.rsi3 (B-Human, ver SOURCE.md y bhuman/License.md)."
        "\n  Convenciones: ejes y rangos en la convencion de Aldebaran (mismos signos que NAOqi y B-Human);"
        "\n  grupos de colision suelo=1, torso/cabeza/caderas=2, brazos=4, piernas/pies=8.\n")
    tree = ET.ElementTree(mj)
    ET.indent(tree, space="  ")
    path.write_text(ET.tostring(header, encoding="unicode") + "\n" + ET.tostring(mj, encoding="unicode") + "\n",
                    encoding="utf-8")


def lowest_sole_z(model: mujoco.MjModel, data: mujoco.MjData) -> float:
    """Altura del punto mas bajo de las dos suelas."""
    lowest = np.inf
    for name in ("left_foot", "right_foot"):
        geom = model.geom(name)
        corners = np.array([[sx, sy, sz] for sx in (-1, 1) for sy in (-1, 1) for sz in (-1, 1)]) * geom.size
        world = data.geom_xpos[geom.id] + corners @ data.geom_xmat[geom.id].reshape(3, 3).T
        lowest = min(lowest, world[:, 2].min())
    return float(lowest)


def self_contacts(model: mujoco.MjModel, data: mujoco.MjData) -> set[tuple[str, str]]:
    """Pares de cuerpos que se tocan en la pose actual (el modelo suelto no tiene suelo)."""
    mujoco.mj_forward(model, data)
    pairs = set()
    for c in data.contact[: data.ncon]:
        bodies = sorted(model.body(model.geom_bodyid[g]).name for g in (c.geom1, c.geom2))
        pairs.add(tuple(bodies))
    return pairs


def main() -> None:
    rsi3 = Rsi3(SOURCE)
    MESH_DIR.mkdir(exist_ok=True)

    # 1) Primera version (sin exclusiones) para medir la pose "home" y los solapes de construccion.
    probe_z = 0.4
    mj, joints, meshes = build_xml(rsi3, probe_z, excludes=[])
    for mesh in sorted(meshes):
        rsi3.write_obj(mesh, MESH_DIR / f"{mesh}.obj")
    for stale in set(MESH_DIR.glob("*.obj")) - {MESH_DIR / f"{m}.obj" for m in meshes}:
        stale.unlink()
    add_foot_sites_and_keyframe(mj, joints, probe_z)
    write(mj, OUTPUT)
    model = mujoco.MjModel.from_xml_path(str(OUTPUT))
    data = mujoco.MjData(model)

    # Las cajas de B-Human se solapan entre cuerpos vecinos (p. ej. esfera de cadera y torso). Se excluyen
    # solo los pares que ya se tocan en la pose cero o en "home": son solapes de construccion, no choques.
    excludes = self_contacts(model, data) | {tuple(sorted(pair)) for pair in JOINT_EXCLUDES}
    mujoco.mj_resetDataKeyframe(model, data, model.key("home").id)
    excludes |= self_contacts(model, data)
    mujoco.mj_kinematics(model, data)
    torso_z = probe_z - lowest_sole_z(model, data) + SOLE_CLEARANCE_M

    # 2) Version final.
    mj, joints, _ = build_xml(rsi3, torso_z, excludes=sorted(excludes))
    add_foot_sites_and_keyframe(mj, joints, torso_z)
    write(mj, OUTPUT)
    model = mujoco.MjModel.from_xml_path(str(OUTPUT))
    data = mujoco.MjData(model)
    mujoco.mj_resetDataKeyframe(model, data, model.key("home").id)
    leftover = self_contacts(model, data)
    if leftover:
        raise RuntimeError(f"Quedan autocolisiones en 'home': {sorted(leftover)}")

    print(f"Fuente: {SOURCE.name} (sha256 verificado)")
    print(f"Escrito: {OUTPUT.relative_to(NAO_DIR.parents[1])} | {len(meshes)} mallas en "
          f"{MESH_DIR.relative_to(NAO_DIR.parents[1])}")
    print(f"Cuerpos={model.nbody - 1}  articulaciones={model.njnt - 1}  actuadores={model.nu}  "
          f"masa={model.body_subtreemass[1]:.3f} kg  torso en 'home' z={torso_z:.4f} m")
    print("Pares de cuerpos sin colision entre si:")
    for body1, body2 in sorted(excludes):
        print(f"  {body1} - {body2}")


if __name__ == "__main__":
    main()
