/**
 * @file CopaRaceTactics.cpp
 *
 * @author Repo NAO (caminata RL)
 */

#include "CopaRaceTactics.h"
#include <iostream>

MAKE_MODULE(CopaRaceTactics);

void CopaRaceTactics::update(CopaRaceDecision& decision)
{
  decision = CopaRaceDecision();
  const bool rl = theCopaRaceState.lane == CopaRaceState::rl;
  if(!theCopaRaceState.isRunning())
  {
    switch(theCopaRaceState.phase)
    {
      case CopaRaceState::unstiff:
        decision.command = CopaRaceDecision::idle;
        break;
      case CopaRaceState::waiting:
        decision.command = rl ? CopaRaceDecision::holdRL : CopaRaceDecision::stand;
        break;
      default:
        decision.command = CopaRaceDecision::stand;
        break;
    }
    decision.reason = TypeRegistry::getEnumName(theCopaRaceState.phase);
    lastUpdate = theFrameInfo.time;
    return;
  }
  if(theCopaRaceState.attempt != raceAttempt)
    startRace();

  // Odometria desde la ultima actualizacion, en el marco del robot (m, rad).
  const Pose2f delta = lastOdometry.inverse() * theOdometryData;
  lastOdometry = theOdometryData;
  filter.predecir(delta.translation.x() / 1000., delta.translation.y() / 1000., delta.rotation);
  // En el carril RL la marcha no da odometria: el avance se estima con vx_cmd.
  rlProgress += rlVxCmd * theFrameInfo.getTimeSince(lastUpdate) / 1000.;
  lastUpdate = theFrameInfo.time;

  if(theLanePercept.timestamp && theLanePercept.timestamp != lastPerceptTime)
  {
    lastPerceptTime = theLanePercept.timestamp;
    CopaRace::Estimacion e;
    e.valida = theLanePercept.valid;
    e.nLineas = theLanePercept.nLines;
    e.d = theLanePercept.d;
    e.psi = theLanePercept.psi;
    if(filter.actualizar(e))
      lastAccepted = theFrameInfo.time;
    if(theLanePercept.finishSeen && theLanePercept.finishDistance < finishTrigger && !finishSeen)
    {
      finishSeen = true;
      timeWhenFinishSeen = theFrameInfo.time;
      finishProgress = filter.s + postFinish;
      std::cout << "[CopaRace] t=" << theFrameInfo.time << " meta a la vista a " << theLanePercept.finishDistance << " m"
                << std::endl;
    }
  }

  decision.laneD = static_cast<float>(filter.d);
  decision.lanePsi = static_cast<float>(filter.psi);
  decision.progress = static_cast<float>(rl ? rlProgress : filter.s);
  decision.finishSeen = finishSeen;

  if(rl)
  {
    decision.command = CopaRaceDecision::runRL;
    decision.reason = "politica";
    if(finishSeen && theFrameInfo.getTimeSince(timeWhenFinishSeen) >= 1000.f * postFinish / std::max(rlVxCmd, .05f))
    {
      decision.done = true;
      decision.reason = "finish_line";
    }
    else if(rlProgress > rlMaxDistance)
    {
      decision.done = true;
      decision.reason = "distance_limit";
    }
    return;
  }

  decision.command = CopaRaceDecision::runBHuman;
  const double confianza = theFrameInfo.getTimeSince(lastAccepted) < lostTimeoutMs ? 1. : 0.;
  const auto cmd = controller.comando(filter.d, filter.psi, confianza);
  decision.walkSpeed = Pose2f(static_cast<float>(cmd[2]) * bhumanMaxSpeed.rotation,
                              static_cast<float>(cmd[0]) * bhumanMaxSpeed.translation.x(),
                              static_cast<float>(cmd[1]) * bhumanMaxSpeed.translation.y());
  decision.reason = confianza > 0. ? "vision" : "sin_vision";
  if(finishSeen && filter.s >= finishProgress)
  {
    decision.done = true;
    decision.reason = "finish_line";
  }
  else if(filter.s > maxDistance)
  {
    decision.done = true;
    decision.reason = "distance_limit";
  }
}

void CopaRaceTactics::startRace()
{
  raceAttempt = theCopaRaceState.attempt;
  filter.reiniciar();
  controller = CopaRace::LaneController();
  controller.vxMax = bhumanVxMax;
  lastOdometry = theOdometryData;
  lastAccepted = 0;
  finishSeen = false;
  timeWhenFinishSeen = 0;
  finishProgress = 0.;
  rlProgress = 0.;
  lastUpdate = theFrameInfo.time;
  // La ultima medicion antes de arrancar (de pie) inicializa el filtro, como en robot/race_nao.py.
  lastPerceptTime = 0;
}
