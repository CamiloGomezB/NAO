# -*- coding: utf-8 -*-
"""Choques entre robots de carriles vecinos (paso 48b del PLAN; falta del reglamento 3.2.6: descalifica al equipo).

Cada robot se simula en su propia fisica, como en la carrera real, donde corren por separado. Para saber si dos
robots se TOCARIAN, sus poses se copian a la escena de 3 carriles (`carrera_vivo.escena_tres`, que tiene los 3 NAOs
con sus geometrias de colision) y MuJoCo calcula los contactos de esa configuracion (`mj_forward` corre la deteccion
de colisiones). Cualquier contacto entre geometrias de robots distintos es un choque.

Simplificacion (documentada en la bitacora, paso 48b): la deteccion es exacta, pero despues del choque los robots no
se empujan entre si. Para la seleccion de agentes basta: un solo contacto ya descarta al agente.
"""
import numpy as np

PREFIJOS = (("B_", "bhuman"), ("N_", "naoqi"))      # el RL no lleva prefijo


class DetectorChoques(object):
    def __init__(self, m):
        self.m = m
        robot = []
        for g in range(m.ngeom):
            b = m.geom_bodyid[g]
            if b == 0:                                   # el mundo (piso y marcas de la pista)
                robot.append(None)
                continue
            nombre = m.body(b).name
            robot.append(next((r for p, r in PREFIJOS if nombre.startswith(p)), "rl"))
        self.robot = robot

    def choques(self, d):
        """Pares de robots que se tocan en la configuracion actual de d (llamar despues de mj_forward)."""
        pares = set()
        for i in range(d.ncon):
            c = d.contact[i]
            a, b = self.robot[c.geom1], self.robot[c.geom2]
            if a is not None and b is not None and a != b:
                pares.add(tuple(sorted((a, b))))
        return sorted(pares)


def distancia_minima(m, d, detector, a="rl", b="bhuman", distmax=1.0):
    """Distancia minima [m] entre las geometrias de colision de dos robots (para informar el margen)."""
    import mujoco
    ga = [g for g in range(m.ngeom) if detector.robot[g] == a and (m.geom_contype[g] or m.geom_conaffinity[g])]
    gb = [g for g in range(m.ngeom) if detector.robot[g] == b and (m.geom_contype[g] or m.geom_conaffinity[g])]
    ft = np.zeros(6)
    return min(mujoco.mj_geomDistance(m, d, i, j, distmax, ft) for i in ga for j in gb)
