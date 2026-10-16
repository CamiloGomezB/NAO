/**
 * @file CopaRaceDecision.h
 *
 * Decision de la carrera, la provee CopaRaceTactics y la ejecuta la opcion HandleCopaNAORace con las skills de
 * B-Human. En el carril RL, la marcha la produce CopaRLWalkEngine dentro del MotionEngine (walkAtRelativeSpeed).
 *
 * @author Repo NAO (caminata RL)
 */

#pragma once

#include "Math/Pose2f.h"
#include "Streaming/AutoStreamable.h"
#include "Streaming/Enum.h"
#include <string>

STREAMABLE(CopaRaceDecision,
{
  ENUM(Command,
  {,
    idle,       /**< Sin rigidez: no se mueve. */
    stand,      /**< De pie con la postura de B-Human (carril B-Human esperando, o al terminar). */
    holdRL,     /**< Carril RL esperando: pose "home" de la politica, midiendo psi para el rumbo objetivo. */
    runRL,      /**< Carril RL corriendo: la politica manda las 13 articulaciones cada 24 ms. */
    runBHuman,  /**< Carril B-Human corriendo: WalkingEngine a walkSpeed, corregido por la vision. */
  });

  bool isRunning() const { return command == runRL || command == runBHuman; },

  (Command)(idle) command,
  (Pose2f) walkSpeed,                 /**< Carril B-Human: velocidad absoluta (rad/s, mm/s). */
  (float)(0.f) laneD,                 /**< d filtrado [m]. */
  (float)(0.f) lanePsi,               /**< psi filtrado [rad]. */
  (float)(0.f) progress,              /**< Avance a lo largo del carril [m] (odometria; estimado en el carril RL). */
  (bool)(false) finishSeen,           /**< Ya se vio la meta en esta carrera. */
  (bool)(false) done,                 /**< La carrera termino por meta o por tope de distancia. */
  (std::string) reason,               /**< Por que se eligio este comando. */
});
