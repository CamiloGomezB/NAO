/**
 * @file CopaRaceTactics.h
 *
 * Tactica de la Carrera Individual: decide que hace el cuerpo en cada fase.
 *
 *  - Carril RL: esperando, pose "home" de la politica (holdRL); corriendo, la politica (runRL). La politica y
 *    vx_cmd viven en CopaRLWalkEngine; aqui solo se decide cuando terminar.
 *  - Carril B-Human: WalkingEngine de B-Human (walkAtAbsoluteSpeed) corregido con la vision, con el mismo
 *    LaneFilter y LaneController del ejecutor NAOqi (carril/lane_filter.py, carril/controller.py, portados a C++).
 *  - Meta (los dos carriles): al ver la franja roja a menos de finishTrigger, recorre postFinish mas y termina,
 *    como robot/race_nao.py. En el carril RL el tramo final se mide por tiempo a vx_cmd.
 *
 * @author Repo NAO (caminata RL)
 */

#pragma once

#include "Framework/Module.h"
#include "Representations/BehaviorControl/CopaRaceDecision.h"
#include "Representations/BehaviorControl/CopaRaceState.h"
#include "Representations/Infrastructure/FrameInfo.h"
#include "Representations/MotionControl/OdometryData.h"
#include "Representations/Perception/LanePercepts/LanePercept.h"
#include "Tools/CopaRace/CopaRace.h"

MODULE(CopaRaceTactics,
{,
  REQUIRES(CopaRaceState),
  REQUIRES(FrameInfo),
  REQUIRES(LanePercept),
  REQUIRES(OdometryData),
  PROVIDES(CopaRaceDecision),
  LOADS_PARAMETERS(
  {,
    (float) rlVxCmd,            /**< vx_cmd de la politica [m/s] (la ventana lo escribe igual que en CopaRLWalkEngine). */
    (float) finishTrigger,      /**< Distancia a la meta roja que dispara el final [m]. */
    (float) postFinish,         /**< Tramo que se sigue caminando despues [m]. */
    (float) maxDistance,        /**< Tope de seguridad por odometria en el carril B-Human [m]. */
    (float) rlMaxDistance,      /**< Tope de seguridad del carril RL [m], estimado con vx_cmd (sin odometria real). */
    (int) lostTimeoutMs,        /**< Sin vision por mas de esto, el carril B-Human baja la velocidad. */
    (float) bhumanVxMax,        /**< LaneController: fraccion de la velocidad maxima hacia adelante. */
    (Pose2f) bhumanMaxSpeed,    /**< Velocidad maxima del WalkingEngine (rad/s, mm/s, mm/s) para el comando normalizado. */
  }),
});

class CopaRaceTactics : public CopaRaceTacticsBase
{
  void update(CopaRaceDecision& decision) override;

  void startRace();

  unsigned raceAttempt = 0;
  CopaRace::LaneFilter filter;
  CopaRace::LaneController controller;
  Pose2f lastOdometry;
  unsigned lastPerceptTime = 0;
  unsigned lastAccepted = 0;
  bool finishSeen = false;
  unsigned timeWhenFinishSeen = 0;
  double finishProgress = 0.;
  double rlProgress = 0.;
  unsigned lastUpdate = 0;
};
