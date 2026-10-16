/**
 * @file CopaRaceState.h
 *
 * Fase de la Carrera Individual (Copa NAO CCM MX 2026, reglas 2.7 y 3.2), la provee CopaRaceController. No hay
 * GameController: el robot se arma con el pecho, arranca con el silbato del juez y/o el boton medio de la cabeza,
 * y se detiene solo al llegar a la meta, al pasar el tiempo maximo o con la desactivacion manual.
 *
 * @author Repo NAO (caminata RL)
 */

#pragma once

#include "Streaming/AutoStreamable.h"
#include "Streaming/Enum.h"

STREAMABLE(CopaRaceState,
{
  ENUM(Phase,
  {,
    unstiff,  /**< Articulaciones sueltas (al encender o con los tres botones de la cabeza). El pecho lo arma. */
    waiting,  /**< De pie (en la pose de salida del carril elegido) esperando la senal de arranque. */
    running,  /**< Corriendo hacia la meta. */
    finished, /**< Llego a la meta o se acabo el tiempo: de pie hasta que el juez autorice retirarlo. */
    aborted,  /**< Desactivacion manual (boton trasero de la cabeza): de pie, quieto. */
  });

  ENUM(Lane,
  {,
    rl,       /**< Politica RL a nivel de articulaciones (CopaRLWalkEngine). */
    bhuman,   /**< WalkingEngine de B-Human + vision de carril (LaneFilter y LaneController). */
  });

  ENUM(StartSource,
  {,
    noStart,
    headButton,
    refereeWhistle,
  });

  ENUM(StartMode,
  {,
    buttonOnly,      /**< Solo el boton medio de la cabeza (el equipo activa tras el silbato, regla 2.7). */
    whistleOnly,     /**< Solo el silbato del juez. */
    buttonOrWhistle, /**< Lo primero que llegue. */
  });

  ENUM(EndReason,
  {,
    notEnded,
    finishLine,      /**< Meta roja vista y recorrido el tramo final. */
    distanceLimit,   /**< Tope de distancia por odometria (carril B-Human). */
    timeLimit,       /**< Tiempo maximo de la carrera. */
    manualStop,      /**< Boton trasero de la cabeza. */
    safetyStop,      /**< Paro de seguridad de la marcha RL (inclinacion o temperatura de los motores). */
  });

  bool isRunning() const { return phase == running; },

  (Phase)(unstiff) phase,                /**< Fase actual. */
  (Lane)(rl) lane,                       /**< Carril (forma de caminar) elegido en el despliegue; se puede cambiar esperando. */
  (StartMode)(buttonOnly) startMode,     /**< Senales de arranque aceptadas. */
  (StartSource)(noStart) startSource,    /**< Que arranco la carrera actual o la ultima. */
  (EndReason)(notEnded) endReason,       /**< Por que termino la ultima carrera. */
  (unsigned)(0) timeWhenPhaseStarted,    /**< Momento del ultimo cambio de fase. */
  (unsigned)(0) timeWhenStarted,         /**< Momento en que arranco la carrera actual o la ultima. */
  (unsigned)(0) deadline,                /**< Momento en que la carrera debe terminar como maximo. */
  (unsigned)(0) attempt,                 /**< Carreras arrancadas desde que se encendio. */
});
