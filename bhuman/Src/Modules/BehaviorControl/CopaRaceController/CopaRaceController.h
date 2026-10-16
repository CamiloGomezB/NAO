/**
 * @file CopaRaceController.h
 *
 * Control sin GameController de la Carrera Individual (Copa NAO CCM MX 2026, reglas 2.7 y 3.2). Reemplaza a
 * GameStateProvider en el escenario CopaNAORace; solo usa sensores del propio robot. Los gestos son los mismos
 * que el penal de PenaltyStack, para que el equipo opere todos los robots igual:
 *
 *  - pecho (toque):                     unstiff -> waiting (se pone de pie en la pose de salida)
 *  - boton medio de la cabeza (toque):  waiting -> running (activacion del equipo tras el silbato)
 *  - silbato del juez (opcional):       waiting -> running
 *  - boton trasero de la cabeza (mantener) o pecho (mantener 0.3 s): running -> aborted (desactivacion manual,
 *    regla 3.2.3; el pecho conserva el paro del ejecutor NAOqi, robot/race_nao.py)
 *  - meta o tope de distancia:          running -> finished (lo informa CopaRaceTactics)
 *  - tiempo maximo de la carrera:       running -> finished (regla 3.2.5: 3 min)
 *  - paro de seguridad de la marcha RL: running -> aborted (inclinacion o temperatura)
 *  - boton delantero (toque):           finished/aborted -> waiting (rearmado)
 *  - boton delantero (mantener):        cambia el carril RL <-> B-Human mientras espera
 *  - tres botones de la cabeza (mantener): cualquier fase -> unstiff
 *
 * GameState: waiting = waitForOwnKickOff (el silbato escucha en "set"), running = playing, al terminar afterHalf.
 *
 * @author Repo NAO (caminata RL)
 */

#pragma once

#include "Framework/Module.h"
#include "Representations/BehaviorControl/CopaRaceDecision.h"
#include "Representations/BehaviorControl/CopaRaceState.h"
#include "Representations/Infrastructure/FrameInfo.h"
#include "Representations/Infrastructure/GameState.h"
#include "Representations/Infrastructure/SensorData/KeyStates.h"
#include "Representations/Modeling/Whistle.h"
#include "Representations/MotionControl/CopaRLWalkStatus.h"

MODULE(CopaRaceController,
{,
  REQUIRES(CopaRLWalkStatus),
  REQUIRES(EnhancedKeyStates),
  REQUIRES(FrameInfo),
  REQUIRES(Whistle),
  USES(CopaRaceDecision),
  PROVIDES(CopaRaceState),
  PROVIDES(GameState),
  LOADS_PARAMETERS(
  {,
    (CopaRaceState::Lane) lane,                   /**< Carril al encender (lo escribe la ventana de despliegue). */
    (CopaRaceState::StartMode) startMode,         /**< Senales de arranque (lo escribe la ventana de despliegue). */
    (unsigned) maxRunMs,                          /**< Tiempo maximo de la carrera (regla 3.2.5: 180 000 ms). */
    (unsigned) whistleArmDelayMs,                 /**< Se ignoran los silbatos de justo despues de armar. */
    (float) minWhistleConfidence,                 /**< Whistle::confidenceOfLastWhistleDetection minima. */
    (unsigned) tapMinMs,                          /**< Mas corto es un rebote. */
    (unsigned) tapMaxMs,                          /**< Mas largo es mantener, no un toque. */
    (unsigned) abortHoldMs,                       /**< Boton trasero mantenido: desactivacion manual. */
    (unsigned) chestStopHoldMs,                   /**< Pecho mantenido corriendo: desactivacion manual (como race_nao.py). */
    (unsigned) laneToggleHoldMs,                  /**< Boton delantero mantenido esperando: cambia el carril. */
    (unsigned) unstiffHoldMs,                     /**< Tres botones de la cabeza mantenidos: articulaciones sueltas. */
    (bool) speak,                                 /**< Avisos hablados en cada cambio de fase. */
  }),
});

class CopaRaceController : public CopaRaceControllerBase
{
public:
  CopaRaceController();

private:
  void update(CopaRaceState& copaRaceState) override;
  void update(GameState& gameState) override;

  /** Avanza la maquina de fases una vez por ciclo (la comparten las dos representaciones). */
  void step();
  void detectGestures();
  void setPhase(CopaRaceState::Phase phase);
  void start(CopaRaceState::StartSource source);
  void finish(CopaRaceState::EndReason reason, CopaRaceState::Phase phase);
  void say(const std::string& text) const;
  std::string laneName() const;

  CopaRaceState state;
  unsigned lastStep = 0;
  bool stepped = false;
  unsigned lastAcceptedWhistle = 0;

  ENUM_INDEXED_ARRAY(bool, KeyStates::Key) wasPressed;
  ENUM_INDEXED_ARRAY(unsigned, KeyStates::Key) lastDuration;
  ENUM_INDEXED_ARRAY(bool, KeyStates::Key) mixed;
  ENUM_INDEXED_ARRAY(bool, KeyStates::Key) tapped;
  bool unstiffGesture = false;
  bool abortGesture = false;
  bool laneGesture = false;
};
