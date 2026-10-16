/**
 * @file CopaRLWalkEngine.h
 *
 * Marcha RL de la Carrera Individual dentro del MotionEngine de B-Human. En el escenario CopaNAORace este modulo
 * provee el generador de walkAtRelativeSpeed: cuando el comportamiento pide esa marcha, el MotionEngine crea una
 * CopaRLWalkPhase que, igual que el entorno NaoRace-v0 del entrenamiento:
 *
 *  1. lleva las 26 articulaciones a la pose "home" del contrato v1 (interpolacion suave);
 *  2. se queda en home mientras el robot espera, guardando los psi validos de la camara;
 *  3. al arrancar, fija el rumbo objetivo de la IMU = rumbo actual - psi medio medido de pie (paso 58c) y cada
 *     24 ms (2 ciclos de 12 ms) arma la observacion de 54 valores, evalua la politica y manda los 13 angulos.
 *
 * La politica (Config/NeuralNets/CopaRace/<policy>.cfg, exportada con scripts/exportar_politicas_robot.py) y todo
 * el contrato estan en Tools/CopaRace/CopaRace.h, comprobados contra Python con scripts/check_paridad_robot.py.
 *
 * Seguridad (CLAUDE.md, robot real): paro enclavado por inclinacion y por temperatura de los motores de las
 * piernas; tras el paro el generador entrega la postura de pie de B-Human hasta la siguiente carrera. Las caidas
 * las sigue atrapando el FallEngine de B-Human y al terminar la fase B-Human se pone de pie desde la postura medida.
 *
 * @author Repo NAO (caminata RL)
 */

#pragma once

#include "Framework/Module.h"
#include "Representations/BehaviorControl/CopaRaceDecision.h"
#include "Representations/BehaviorControl/CopaRaceState.h"
#include "Representations/Infrastructure/FrameInfo.h"
#include "Representations/Infrastructure/SensorData/FsrSensorData.h"
#include "Representations/Infrastructure/SensorData/JointSensorData.h"
#include "Representations/MotionControl/CopaRLWalkStatus.h"
#include "Representations/MotionControl/StandGenerator.h"
#include "Representations/MotionControl/WalkAtRelativeSpeedGenerator.h"
#include "Representations/Perception/LanePercepts/LanePercept.h"
#include "Representations/Sensing/InertialData.h"
#include "Streaming/AutoStreamable.h"
#include "Tools/CopaRace/CopaRace.h"
#include "Tools/Motion/MotionPhase.h"
#include <optional>
#include <string>
#include <vector>

/** Una capa densa de un actor exportado (Config/NeuralNets/CopaRace/<politica>.cfg). */
STREAMABLE(CopaRaceLayerConfig,
{,
  (unsigned)(0) filas,
  (unsigned)(0) columnas,
  (std::vector<float>) pesos,
  (std::vector<float>) sesgo,
});

/** Un actor determinista de SB3 exportado por scripts/exportar_politicas_robot.py. */
STREAMABLE(CopaRacePolicyConfig,
{,
  (std::string) nombre,
  (std::string)("elu") activacion,
  (std::vector<double>) media,
  (std::vector<double>) varianza,
  (double)(10.) clipObs,
  (double)(1e-8) epsilon,
  (std::vector<CopaRaceLayerConfig>) ocultas,
  (CopaRaceLayerConfig) accion,
  (double)(.5) periodoMarcha,
  (double)(.45) vxCmd,
});

MODULE(CopaRLWalkEngine,
{,
  REQUIRES(CopaRaceDecision),
  REQUIRES(CopaRaceState),
  REQUIRES(FrameInfo),
  REQUIRES(FsrSensorData),
  REQUIRES(InertialData),
  REQUIRES(JointSensorData),
  REQUIRES(LanePercept),
  REQUIRES(StandGenerator),
  PROVIDES(CopaRLWalkStatus),
  PROVIDES(WalkAtRelativeSpeedGenerator),
  LOADS_PARAMETERS(
  {,
    (std::string) policy,          /**< rl_v1.2.1 | rl_v1.2 | rl_v1.1 | rl_v1.0 | carrera_v02 | carrera_v01 (ventana de despliegue). */
    (float) vxCmd,                 /**< Velocidad pedida a la politica [m/s] (0 = la recomendada de la politica). */
    (int) interpolationMs,         /**< Tiempo para llevar la postura actual a home. */
    (int) settleMs,                /**< Tiempo minimo en home antes de poder arrancar (entrenamiento: 0.5 s). */
    (int) psiWindowMs,             /**< Ventana de psi medidos de pie para el rumbo objetivo (entrenamiento: 0.5 s). */
    (float) maxTilt,               /**< Inclinacion del torso que detiene la marcha [rad] (robot/race_nao.py: 0.6). */
    (int) maxLegTemperature,       /**< Temperatura de un motor de pierna que detiene la marcha [grados C]. */
    (int) stiffness,               /**< Rigidez de todas las articulaciones [%] (contrato v1: 100). */
  }),
});

class CopaRLWalkEngine : public CopaRLWalkEngineBase
{
public:
  CopaRLWalkEngine();

  CopaRace::Politica politica;
  bool politicaValida = false;
  double vxEfectiva = .45;
  double periodoMarcha = .5;

  // Estado compartido con la fase (la fase vive dentro del MotionEngine).
  bool safetyLatched = false;
  std::string safetyReason;
  bool phaseActive = false;
  bool phaseWalking = false;
  unsigned decisions = 0;
  float lastTilt = 0.f;
  float lastMaxTemperature = 0.f;
  unsigned latchedAttempt = 0;

private:
  void update(CopaRLWalkStatus& status) override;
  void update(WalkAtRelativeSpeedGenerator& generator) override;
};

/** La fase de la marcha RL (tipo calibration: ningun generador de B-Human la reinterpreta como WalkPhase). */
class CopaRLWalkPhase : public MotionPhase
{
public:
  CopaRLWalkPhase(CopaRLWalkEngine& engine);

private:
  enum class Estado { interpolando, enHome, caminando };

  void update() override;
  bool isDone(const MotionRequest& motionRequest) const override;
  void calcJoints(const MotionRequest& motionRequest, JointRequest& jointRequest, Pose2f& odometryOffset,
                  MotionInfo& motionInfo) override;

  CopaRace::Sensores leerSensores(double dt);
  bool revisarSeguridad();

  CopaRLWalkEngine& engine;
  Estado estado = Estado::interpolando;
  unsigned tInicio = 0;
  unsigned tEnHome = 0;
  unsigned tMarcha = 0;
  unsigned tAnterior = 0;
  std::array<double, CopaRace::nArticulaciones> anguloInicial{};
  std::array<double, CopaRace::nArticulaciones> anguloAnterior{};
  std::array<double, CopaRace::nArticulaciones> objetivos{};
  CopaRace::Accion accionAnterior{};
  CopaRace::EstadoCamara camara;
  std::vector<std::pair<unsigned, double>> psiDePie;
  unsigned ultimaFoto = 0;
  double rumboObjetivo = 0.;
  unsigned ciclo = 0;
  double dtUltimo = .012;
};
