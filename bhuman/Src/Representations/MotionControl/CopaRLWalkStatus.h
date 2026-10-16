/**
 * @file CopaRLWalkStatus.h
 *
 * Estado de la marcha RL (CopaRLWalkEngine, hilo Motion) para el controlador de la carrera.
 *
 * @author Repo NAO (caminata RL)
 */

#pragma once

#include "Streaming/AutoStreamable.h"
#include <string>

STREAMABLE(CopaRLWalkStatus,
{,
  (bool)(false) policyLoaded,      /**< La politica de NeuralNets/CopaRace se cargo y es valida. */
  (bool)(false) active,            /**< La fase de la marcha RL esta ejecutandose. */
  (bool)(false) walking,           /**< La politica esta mandando las articulaciones (no solo la pose de salida). */
  (bool)(false) safetyStop,        /**< Paro de seguridad enclavado hasta la siguiente carrera. */
  (std::string) safetyReason,      /**< "inclinacion" o "temperatura <articulacion>". */
  (unsigned)(0) decisions,         /**< Decisiones de la politica en la carrera actual. */
  (float)(0.f) maxLegTemperature,  /**< Temperatura maxima de las piernas [grados C]. */
  (float)(0.f) tilt,               /**< Inclinacion del torso [rad]. */
});
