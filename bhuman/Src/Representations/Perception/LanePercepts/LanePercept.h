/**
 * @file LanePercept.h
 *
 * Medicion del carril de la Carrera Individual (Copa NAO CCM MX 2026, regla 3.2.4) con la camara inferior:
 * desplazamiento lateral d y rumbo psi respecto a las lineas negras, y distancia a la franja roja de meta.
 * La calcula CopaLanePerceptor con el estimador de carril de carril/lane_estimator_puro.py (portado a C++).
 *
 * @author Repo NAO (caminata RL)
 */

#pragma once

#include "Streaming/AutoStreamable.h"

STREAMABLE(LanePercept,
{,
  (bool)(false) valid,          /**< Se encontraron las lineas del carril en esta imagen. */
  (float)(0.f) d,               /**< Desplazamiento lateral [m]; + = robot a la izquierda del centro. */
  (float)(0.f) psi,             /**< Angulo respecto a las lineas [rad]; + = girado a la izquierda. */
  (int)(0) nLines,              /**< 2 = ambas lineas, 1 = una sola. */
  (int)(0) nPoints,             /**< Puntos de linea proyectados al suelo. */
  (float)(0.f) quality,         /**< 1 con dos lineas, 0.5 con una. */
  (bool)(false) finishSeen,     /**< Se ve la franja roja de meta. */
  (float)(0.f) finishDistance,  /**< Distancia a la meta [m] (solo si finishSeen). */
  (unsigned)(0) timestamp,      /**< Momento de la imagen procesada (0 = nunca). */
});
