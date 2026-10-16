/**
 * @file CopaRLWalkEngine.cpp
 *
 * @author Repo NAO (caminata RL)
 */

#include "CopaRLWalkEngine.h"
#include "Platform/SystemCall.h"
#include "RobotParts/FsrSensors.h"
#include "RobotParts/Joints.h"
#include "RobotParts/Legs.h"
#include "Representations/MotionControl/MotionInfo.h"
#include "Representations/MotionControl/MotionRequest.h"
#include "Streaming/InStreams.h"
#include "Streaming/Output.h"
#include <cmath>
#include <iostream>

MAKE_MODULE(CopaRLWalkEngine);

// El contrato v1 usa el orden de las 26 articulaciones de B-Human.
constexpr std::size_t indice(Joints::Joint j) { return static_cast<std::size_t>(j); }
static_assert(indice(Joints::numOfJoints) == CopaRace::nArticulaciones, "el contrato v1 tiene 26 articulaciones");
static_assert(indice(Joints::lShoulderPitch) == CopaRace::LShoulderPitch && indice(Joints::rShoulderPitch) == CopaRace::RShoulderPitch &&
              indice(Joints::lHipYawPitch) == CopaRace::LHipYawPitch && indice(Joints::rHipYawPitch) == CopaRace::RHipYawPitch &&
              indice(Joints::rAnkleRoll) == CopaRace::RAnkleRoll, "orden de articulaciones distinto al de B-Human");

namespace
{
  CopaRace::CapaDensa aCapa(const CopaRaceLayerConfig& c)
  {
    CopaRace::CapaDensa capa;
    capa.filas = c.filas;
    capa.columnas = c.columnas;
    capa.pesos.assign(c.pesos.begin(), c.pesos.end());
    capa.sesgo.assign(c.sesgo.begin(), c.sesgo.end());
    return capa;
  }
}

CopaRLWalkEngine::CopaRLWalkEngine()
{
  // La politica se lee al arrancar bhuman: leerla en medio del hilo Motion lo frenaria varios ciclos.
  InMapFile stream("NeuralNets/CopaRace/" + policy + ".cfg");
  if(stream.exists())
  {
    CopaRacePolicyConfig config;
    stream >> config;
    CopaRace::ParametrosPolitica p;
    p.nombre = config.nombre;
    p.activacion = config.activacion == "tanh" ? CopaRace::Activacion::tanh : CopaRace::Activacion::elu;
    p.media = config.media;
    p.varianza = config.varianza;
    p.clipObs = config.clipObs;
    p.epsilon = config.epsilon;
    for(const CopaRaceLayerConfig& capa : config.ocultas)
      p.ocultas.push_back(aCapa(capa));
    p.accion = aCapa(config.accion);
    p.periodoMarcha = config.periodoMarcha;
    p.vxCmd = config.vxCmd;
    if(p.valida())
    {
      politica = CopaRace::Politica(p);
      politicaValida = true;
      periodoMarcha = p.periodoMarcha;
      vxEfectiva = vxCmd > 0.f ? vxCmd : p.vxCmd;
    }
  }
  if(!politicaValida)
  {
    OUTPUT_ERROR("CopaRLWalkEngine: la politica " << policy << " no existe o es invalida");
    SystemCall::say("walking policy missing");
  }
  std::cout << "[CopaRace] politica " << policy << (politicaValida ? " cargada" : " NO cargada") << " vx_cmd="
            << vxEfectiva << " periodo=" << periodoMarcha << std::endl;
}

void CopaRLWalkEngine::update(CopaRLWalkStatus& status)
{
  // El paro se desenclava solo cuando arranca otra carrera.
  if(safetyLatched && theCopaRaceState.attempt != latchedAttempt && theCopaRaceState.isRunning())
  {
    safetyLatched = false;
    safetyReason.clear();
  }
  status.policyLoaded = politicaValida;
  status.active = phaseActive;
  status.walking = phaseWalking;
  status.safetyStop = safetyLatched;
  status.safetyReason = safetyReason;
  status.decisions = decisions;
  status.maxLegTemperature = lastMaxTemperature;
  status.tilt = lastTilt;
  phaseActive = false;  // la fase lo vuelve a marcar en cada ciclo en que corre
}

void CopaRLWalkEngine::update(WalkAtRelativeSpeedGenerator& generator)
{
  generator.createPhase = [this](const MotionRequest& motionRequest, const MotionPhase& lastPhase) -> std::unique_ptr<MotionPhase>
  {
    // Sin politica o con el paro enclavado, se queda de pie con la postura de B-Human.
    if(!politicaValida || safetyLatched)
      return theStandGenerator.createPhase(motionRequest, lastPhase);
    return std::make_unique<CopaRLWalkPhase>(*this);
  };
}

CopaRLWalkPhase::CopaRLWalkPhase(CopaRLWalkEngine& engine) :
  MotionPhase(MotionPhase::calibration),
  engine(engine)
{
  tInicio = tAnterior = engine.theFrameInfo.time;
  for(std::size_t j = 0; j < CopaRace::nArticulaciones; ++j)
  {
    const float angulo = engine.theJointSensorData.angles[j];
    anguloInicial[j] = anguloAnterior[j] = std::isfinite(angulo) ? angulo : CopaRace::poseHome[j];
  }
  objetivos = anguloInicial;
  engine.decisions = 0;
  engine.phaseWalking = false;
}

bool CopaRLWalkPhase::revisarSeguridad()
{
  const double roll = engine.theInertialData.angle.x(), pitch = engine.theInertialData.angle.y();
  const double inclinacion = std::acos(CopaRace::recortar(std::cos(roll) * std::cos(pitch), -1., 1.));
  engine.lastTilt = static_cast<float>(inclinacion);
  int maxTemp = 0;
  Joints::Joint caliente = Joints::lHipYawPitch;
  for(int j = Joints::firstLegJoint; j < Joints::numOfJoints; ++j)
    if(engine.theJointSensorData.temperatures[j] > maxTemp)
    {
      maxTemp = engine.theJointSensorData.temperatures[j];
      caliente = static_cast<Joints::Joint>(j);
    }
  engine.lastMaxTemperature = static_cast<float>(maxTemp);
  std::string motivo;
  if(estado == Estado::caminando && inclinacion > engine.maxTilt)
    motivo = "inclinacion";
  else if(maxTemp >= engine.maxLegTemperature)
    motivo = std::string("temperatura ") + TypeRegistry::getEnumName(caliente);
  if(motivo.empty())
    return false;
  engine.safetyLatched = true;
  engine.safetyReason = motivo;
  engine.latchedAttempt = engine.theCopaRaceState.attempt;
  std::cout << "[CopaRace] t=" << engine.theFrameInfo.time << " PARO de seguridad: " << motivo << " (inclinacion "
            << inclinacion << " rad, " << maxTemp << " C)" << std::endl;
  SystemCall::say("safety stop");
  return true;
}

CopaRace::Sensores CopaRLWalkPhase::leerSensores(double dt)
{
  CopaRace::Sensores s;
  for(std::size_t j = 0; j < CopaRace::nArticulaciones; ++j)
  {
    const float angulo = engine.theJointSensorData.angles[j];
    s.angulos[j] = std::isfinite(angulo) ? angulo : anguloAnterior[j];
    s.velocidades[j] = dt > 0. ? (s.angulos[j] - anguloAnterior[j]) / dt : 0.;
    anguloAnterior[j] = s.angulos[j];
  }
  const auto& g = engine.theInertialData.gyro;
  s.giro = {g.x(), g.y(), g.z()};
  const auto& q = engine.theInertialData.orientation3D;
  s.orientacion = {q.w(), q.x(), q.y(), q.z()};
  const auto& p = engine.theFsrSensorData.pressures;
  s.fsr = {p[Legs::left][FsrSensors::fl], p[Legs::left][FsrSensors::fr], p[Legs::left][FsrSensors::bl], p[Legs::left][FsrSensors::br],
           p[Legs::right][FsrSensors::fl], p[Legs::right][FsrSensors::fr], p[Legs::right][FsrSensors::bl], p[Legs::right][FsrSensors::br]};
  return s;
}

void CopaRLWalkPhase::update()
{
  const unsigned ahora = engine.theFrameInfo.time;
  dtUltimo = std::max(0., engine.theFrameInfo.getTimeSince(tAnterior) / 1000.);
  tAnterior = ahora;
  engine.phaseActive = true;
  const CopaRace::Sensores sensores = leerSensores(dtUltimo);
  if(engine.safetyLatched || revisarSeguridad())
    return;

  // Camara: ultima medicion cruda mantenida entre fotos (contrato v1, EstadoCamara).
  const LanePercept& foto = engine.theLanePercept;
  if(foto.timestamp && foto.timestamp != ultimaFoto)
  {
    ultimaFoto = foto.timestamp;
    camara.nuevaMedicion(foto.timestamp / 1000., foto.d, foto.psi, foto.valid);
    if(foto.valid && estado != Estado::caminando)
      psiDePie.emplace_back(foto.timestamp, foto.psi);
  }

  const bool correr = engine.theCopaRaceDecision.command == CopaRaceDecision::runRL;
  switch(estado)
  {
    case Estado::interpolando:
    {
      const double a = CopaRace::recortar(engine.theFrameInfo.getTimeSince(tInicio) / static_cast<double>(std::max(1, engine.interpolationMs)), 0., 1.);
      const double suave = .5 - .5 * std::cos(CopaRace::pi * a);
      for(std::size_t j = 0; j < CopaRace::nArticulaciones; ++j)
        objetivos[j] = anguloInicial[j] + suave * (CopaRace::poseHome[j] - anguloInicial[j]);
      if(a >= 1.)
      {
        estado = Estado::enHome;
        tEnHome = ahora;
        psiDePie.clear();
      }
      break;
    }
    case Estado::enHome:
      objetivos = CopaRace::poseHome;
      if(correr && engine.theFrameInfo.getTimeSince(tEnHome) >= engine.settleMs)
      {
        std::vector<double> psis;
        for(const auto& [t, psi] : psiDePie)
          if(ahora - t <= static_cast<unsigned>(engine.psiWindowMs))
            psis.push_back(psi);
        const auto& q = sensores.orientacion;
        rumboObjetivo = CopaRace::rumboObjetivoInicial(CopaRace::rumboDesdeCuaternion(q[0], q[1], q[2], q[3]), psis);
        estado = Estado::caminando;
        tMarcha = ahora;
        ciclo = 0;
        accionAnterior.fill(0.);
        engine.phaseWalking = true;
        std::cout << "[CopaRace] t=" << ahora << " marcha RL: " << psis.size() << " psi de pie, rumbo objetivo "
                  << rumboObjetivo << std::endl;
      }
      break;
    case Estado::caminando:
      // La politica actua cada 2 ciclos de 12 ms, como en el entrenamiento (24 ms).
      if(ciclo++ % CopaRace::ciclosPorAccion == 0)
      {
        const double t = engine.theFrameInfo.getTimeSince(tMarcha) / 1000.;
        const CopaRace::Observacion obs = CopaRace::armarObservacion(sensores, rumboObjetivo, camara.observacion(ahora / 1000.),
                                                                     accionAnterior, t, engine.vxEfectiva, engine.periodoMarcha);
        const CopaRace::Accion accion = engine.politica(obs);
        objetivos = CopaRace::objetivosASalida(CopaRace::accionAObjetivos(accion));
        accionAnterior = accion;
        ++engine.decisions;
      }
      break;
  }
}

bool CopaRLWalkPhase::isDone(const MotionRequest& motionRequest) const
{
  return motionRequest.motion != MotionRequest::walkAtRelativeSpeed || engine.safetyLatched;
}

void CopaRLWalkPhase::calcJoints(const MotionRequest&, JointRequest& jointRequest, Pose2f& odometryOffset, MotionInfo& motionInfo)
{
  for(std::size_t j = 0; j < CopaRace::nArticulaciones; ++j)
  {
    jointRequest.angles[j] = static_cast<float>(objetivos[j]);
    jointRequest.stiffnessData.stiffnesses[j] = engine.stiffness;
  }
  motionInfo.isMotionStable = !engine.safetyLatched;
  if(estado == Estado::caminando)
  {
    // La marcha RL no tiene modelo de odometria: se estima con vx_cmd (la politica la sigue en simulacion).
    odometryOffset.translation.x() = static_cast<float>(engine.vxEfectiva * 1000. * dtUltimo);
    motionInfo.speed = Pose2f(0.f, static_cast<float>(engine.vxEfectiva * 1000.), 0.f);
  }
}
