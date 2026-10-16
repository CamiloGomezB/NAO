/**
 * @file CopaRaceController.cpp
 *
 * @author Repo NAO (caminata RL)
 */

#include "CopaRaceController.h"
#include "Debugging/Annotation.h"
#include "Platform/SystemCall.h"
#include <algorithm>
#include <iostream>

MAKE_MODULE(CopaRaceController);

CopaRaceController::CopaRaceController()
{
  wasPressed.fill(false);
  lastDuration.fill(0);
  mixed.fill(false);
  tapped.fill(false);
  state.lane = lane;
  state.startMode = startMode;
  state.phase = CopaRaceState::unstiff;
}

void CopaRaceController::update(CopaRaceState& copaRaceState)
{
  step();
  copaRaceState = state;
}

void CopaRaceController::update(GameState& gameState)
{
  step();
  gameState = GameState(); // equipo, colores y numero de jugador de la configuracion desplegada
  gameState.ownTeam.playerStates.fill(GameState::active);
  gameState.opponentTeam.playerStates.fill(GameState::active);
  gameState.gameControllerActive = false;
  gameState.timeWhenStateStarted = state.timeWhenPhaseStarted;
  gameState.timeWhenPlayerStateStarted = state.timeWhenPhaseStarted;
  gameState.whistled = state.phase == CopaRaceState::running && state.startSource == CopaRaceState::refereeWhistle &&
                       state.timeWhenPhaseStarted == theFrameInfo.time;
  gameState.playerState = state.phase == CopaRaceState::unstiff ? GameState::unstiff : GameState::active;
  switch(state.phase)
  {
    case CopaRaceState::unstiff:
      gameState.state = GameState::beforeHalf;
      break;
    case CopaRaceState::waiting:
      gameState.state = GameState::waitForOwnKickOff;
      break;
    case CopaRaceState::running:
      gameState.state = GameState::playing;
      gameState.timeWhenStateEnds = state.deadline;
      break;
    default:
      gameState.state = GameState::afterHalf;
      break;
  }
}

void CopaRaceController::step()
{
  if(stepped && lastStep == theFrameInfo.time)
    return;
  stepped = true;
  lastStep = theFrameInfo.time;
  detectGestures();

  if(unstiffGesture && state.phase != CopaRaceState::unstiff)
  {
    say("joints off");
    setPhase(CopaRaceState::unstiff);
    return;
  }

  switch(state.phase)
  {
    case CopaRaceState::unstiff:
      if(tapped[KeyStates::chest])
      {
        setPhase(CopaRaceState::waiting);
        say(laneName() + " ready");
      }
      break;

    case CopaRaceState::waiting:
    {
      if(laneGesture)
      {
        state.lane = state.lane == CopaRaceState::rl ? CopaRaceState::bhuman : CopaRaceState::rl;
        setPhase(CopaRaceState::waiting);
        say(laneName());
        break;
      }
      const bool buttonAllowed = state.startMode != CopaRaceState::whistleOnly;
      const bool whistleAllowed = state.startMode != CopaRaceState::buttonOnly;
      if(buttonAllowed && tapped[KeyStates::headMiddle])
        start(CopaRaceState::headButton);
      else if(whistleAllowed && theWhistle.lastTimeWhistleDetected > lastAcceptedWhistle &&
              theWhistle.lastTimeWhistleDetected > state.timeWhenPhaseStarted + whistleArmDelayMs &&
              theWhistle.confidenceOfLastWhistleDetection >= minWhistleConfidence)
      {
        lastAcceptedWhistle = theWhistle.lastTimeWhistleDetected;
        start(CopaRaceState::refereeWhistle);
      }
      break;
    }

    case CopaRaceState::running:
      if(abortGesture)
      {
        finish(CopaRaceState::manualStop, CopaRaceState::aborted);
        say("stop");
      }
      else if(state.lane == CopaRaceState::rl && theCopaRLWalkStatus.safetyStop)
        finish(CopaRaceState::safetyStop, CopaRaceState::aborted);
      else if(theFrameInfo.time >= state.deadline)
      {
        finish(CopaRaceState::timeLimit, CopaRaceState::finished);
        say("time");
      }
      else if(theCopaRaceDecision.done)
        finish(theCopaRaceDecision.reason == "distance_limit" ? CopaRaceState::distanceLimit : CopaRaceState::finishLine,
               CopaRaceState::finished);
      break;

    default: // finished, aborted: de pie hasta el rearmado
      if(tapped[KeyStates::headFront])
      {
        setPhase(CopaRaceState::waiting);
        say(laneName() + " ready");
      }
      break;
  }
}

void CopaRaceController::detectGestures()
{
  const KeyStates::Key head[] = {KeyStates::headFront, KeyStates::headMiddle, KeyStates::headRear};
  FOREACH_ENUM(KeyStates::Key, key)
  {
    const bool pressed = theEnhancedKeyStates.pressed[key];
    tapped[key] = false;
    if(pressed)
    {
      if(!wasPressed[key])
        mixed[key] = false;
      lastDuration[key] = theEnhancedKeyStates.pressedDuration[key];
      for(const KeyStates::Key other : head)
        if(other != key && theEnhancedKeyStates.pressed[other])
          mixed[key] = true;
    }
    else if(wasPressed[key])
      tapped[key] = !mixed[key] && lastDuration[key] >= tapMinMs && lastDuration[key] <= tapMaxMs;
    wasPressed[key] = pressed;
  }

  const bool allHead = theEnhancedKeyStates.pressed[KeyStates::headFront] && theEnhancedKeyStates.pressed[KeyStates::headMiddle] &&
                       theEnhancedKeyStates.pressed[KeyStates::headRear];
  const unsigned allHeadDuration = std::min({theEnhancedKeyStates.pressedDuration[KeyStates::headFront],
                                             theEnhancedKeyStates.pressedDuration[KeyStates::headMiddle],
                                             theEnhancedKeyStates.pressedDuration[KeyStates::headRear]});
  unstiffGesture = allHead && allHeadDuration >= unstiffHoldMs;
  abortGesture = theEnhancedKeyStates.isPressedFor(KeyStates::headRear, abortHoldMs) ||
                 theEnhancedKeyStates.isPressedFor(KeyStates::chest, chestStopHoldMs);
  laneGesture = theEnhancedKeyStates.isPressedFor(KeyStates::headFront, laneToggleHoldMs) &&
                !theEnhancedKeyStates.pressed[KeyStates::headMiddle] && !theEnhancedKeyStates.pressed[KeyStates::headRear];
}

void CopaRaceController::setPhase(CopaRaceState::Phase phase)
{
  if(state.phase != phase)
  {
    ANNOTATION("CopaRaceController", TypeRegistry::getEnumName(state.phase) << " -> " << TypeRegistry::getEnumName(phase));
    // bhuman -b escribe stdout en /home/nao/logging: una linea por cambio de fase para revisar cada carrera.
    std::cout << "[CopaRace] t=" << theFrameInfo.time << " fase " << TypeRegistry::getEnumName(state.phase) << " -> "
              << TypeRegistry::getEnumName(phase) << " carril=" << laneName() << std::endl;
  }
  state.phase = phase;
  state.timeWhenPhaseStarted = theFrameInfo.time;
}

void CopaRaceController::start(CopaRaceState::StartSource source)
{
  setPhase(CopaRaceState::running);
  state.startSource = source;
  state.endReason = CopaRaceState::notEnded;
  state.timeWhenStarted = theFrameInfo.time;
  state.deadline = theFrameInfo.time + maxRunMs;
  ++state.attempt;
  std::cout << "[CopaRace] t=" << theFrameInfo.time << " arranque " << TypeRegistry::getEnumName(source) << " intento "
            << state.attempt << " carril=" << laneName() << std::endl;
}

void CopaRaceController::finish(CopaRaceState::EndReason reason, CopaRaceState::Phase phase)
{
  state.endReason = reason;
  std::cout << "[CopaRace] t=" << theFrameInfo.time << " fin " << TypeRegistry::getEnumName(reason) << " tiempo="
            << theFrameInfo.getTimeSince(state.timeWhenStarted) << " ms" << std::endl;
  setPhase(phase);
}

void CopaRaceController::say(const std::string& text) const
{
  if(speak)
    SystemCall::say(text.c_str());
}

std::string CopaRaceController::laneName() const
{
  return state.lane == CopaRaceState::rl ? "learned walk" : "b human walk";
}
