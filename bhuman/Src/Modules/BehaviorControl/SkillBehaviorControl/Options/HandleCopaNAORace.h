/**
 * @file HandleCopaNAORace.h
 *
 * Comportamiento raiz de la Carrera Individual (escenario CopaNAORace). La fase viene de CopaRaceController y la
 * decision de CopaRaceTactics; esta opcion solo la ejecuta con las skills de B-Human. En el carril RL, pedir
 * walkAtRelativeSpeed hace que el MotionEngine use la marcha RL de CopaRLWalkEngine (pose home esperando y la
 * politica corriendo); la cabeza la fija esa fase en la pose del entrenamiento.
 *
 * @author Repo NAO (caminata RL)
 */

// Repo NAO: Carrera Individual de la Copa NAO CCM MX 2026.

option(HandleCopaNAORace)
{
  common_transition
  {
    switch(theCopaRaceDecision.command)
    {
      case CopaRaceDecision::idle:
        goto unstiff;
      case CopaRaceDecision::holdRL:
      case CopaRaceDecision::runRL:
        goto rlWalk;
      case CopaRaceDecision::runBHuman:
        goto bhumanWalk;
      default:
        goto stand;
    }
  }

  initial_state(selectCommand)
  {}

  state(unstiff)
  {
    action
    {
      theLookAtAnglesSkill({.pan = JointAngles::off,
                            .tilt = JointAngles::off});
      thePlayDeadSkill();
    }
  }

  // De pie con la cabeza recta, como la camara del entrenamiento (HeadPitch 0).
  state(stand)
  {
    action
    {
      theLookAtAnglesSkill({.pan = 0_deg,
                            .tilt = 0_deg});
      theStandSkill();
    }
  }

  // La fase RL controla las 26 articulaciones: home esperando, la politica corriendo.
  state(rlWalk)
  {
    action
    {
      theWalkAtRelativeSpeedSkill({.speed = Pose2f(0.f, 1.f, 0.f)});
    }
  }

  state(bhumanWalk)
  {
    action
    {
      theLookAtAnglesSkill({.pan = 0_deg,
                            .tilt = 0_deg});
      theWalkAtAbsoluteSpeedSkill({.speed = theCopaRaceDecision.walkSpeed});
    }
  }
}
