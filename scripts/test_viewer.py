"""Prueba de instalacion de MuJoCo: abre el visor 3D con objetos cayendo al suelo.

Uso:
    uv run python scripts/test_viewer.py
"""

import mujoco
import mujoco.viewer

SCENE_XML = """
<mujoco model="test_scene">
  <option timestep="0.002" gravity="0 0 -9.81"/>
  <visual>
    <headlight ambient="0.4 0.4 0.4" diffuse="0.6 0.6 0.6"/>
  </visual>
  <asset>
    <texture name="grid" type="2d" builtin="checker" rgb1="0.2 0.3 0.4" rgb2="0.1 0.2 0.3"
             width="512" height="512"/>
    <material name="grid" texture="grid" texrepeat="8 8" reflectance="0.1"/>
  </asset>
  <worldbody>
    <light pos="0 0 3" dir="0 0 -1"/>
    <geom name="floor" type="plane" size="3 3 0.1" material="grid"/>
    <body name="box" pos="0 0 1" euler="20 30 0">
      <freejoint/>
      <geom type="box" size="0.1 0.1 0.1" rgba="0.9 0.4 0.2 1" mass="1"/>
    </body>
    <body name="ball" pos="0.3 0.1 1.5">
      <freejoint/>
      <geom type="sphere" size="0.08" rgba="0.2 0.7 0.9 1" mass="0.5"/>
    </body>
  </worldbody>
</mujoco>
"""


def main() -> None:
    model = mujoco.MjModel.from_xml_string(SCENE_XML)
    data = mujoco.MjData(model)
    print(f"MuJoCo {mujoco.__version__} - cuerpos: {model.nbody}, geoms: {model.ngeom}")
    print("Cierra la ventana para terminar. (Doble clic en la caja + Ctrl+clic derecho para empujarla)")
    mujoco.viewer.launch(model, data)


if __name__ == "__main__":
    main()
