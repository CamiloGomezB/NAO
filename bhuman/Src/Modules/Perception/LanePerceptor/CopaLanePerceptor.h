/**
 * @file CopaLanePerceptor.h
 *
 * Vision de carril de la Carrera Individual con la camara inferior del NAO: el estimador de Daniel
 * (carril/lane_estimator_puro.py, portado a C++ en Tools/CopaRace/CopaRace.h y comprobado imagen por imagen)
 * sobre la imagen YUYV convertida a RGB, con la pose camara -> robot de CameraMatrix. Como en el NAO con NAOqi,
 * procesa una imagen cada `periodMs` (10 FPS en el entrenamiento) y entrega d, psi, valido y la meta roja.
 *
 * @author Repo NAO (caminata RL)
 */

#pragma once

#include "Framework/Module.h"
#include "Representations/Infrastructure/CameraImage.h"
#include "Representations/Infrastructure/CameraInfo.h"
#include "Representations/Infrastructure/FrameInfo.h"
#include "Representations/Perception/ImagePreprocessing/CameraMatrix.h"
#include "Representations/Perception/LanePercepts/LanePercept.h"
#include "Tools/CopaRace/CopaRace.h"
#include <memory>

MODULE(CopaLanePerceptor,
{,
  REQUIRES(CameraImage),
  REQUIRES(CameraInfo),
  REQUIRES(CameraMatrix),
  REQUIRES(FrameInfo),
  PROVIDES(LanePercept),
  LOADS_PARAMETERS(
  {,
    (int) periodMs,                 /**< Una imagen cada este tiempo (100 ms = 10 FPS, como el entrenamiento). */
    (bool) useCalibratedIntrinsics, /**< true: focal y centro de CameraInfo; false: campo de vision nominal. */
    (bool) requireStableMatrix,     /**< Ignorar imagenes con CameraMatrix no valida (caidas). */
    (bool) lightLine,               /**< Polaridad "clara" (cinta blanca sobre piso oscuro). */
    (bool) colorMode,               /**< Modo "color" de config/pista_robot.json (el brillo no separa linea y piso). */
    (Vector3f) colorAxis,           /**< color_ref[0]: direccion RGB linea - piso, normalizada. */
    (Vector3f) colorMean,           /**< color_ref[1]: punto medio RGB entre linea y piso. */
    (float) laneWidth,              /**< Ancho interior del carril [m] (regla 3.2.4: 0.70). */
    (float) lineWidth,              /**< Ancho de la linea [m] (regla 3.2.4: 0.019). */
    (int) rowStep,
    (float) darkRatio,
    (float) minContrast,
    (float) relContrast,
    (int) localWindow,
    (float) xMin,
    (float) xMax,
    (float) maxAbsY,
    (int) ransacIterations,
    (float) inlierTol,
    (int) minInliers,
    (int) maxLines,
    (float) pairTol,
    (float) redRatio,
    (int) redMin,
    (int) redMinSat,
    (int) redMinRowPx,
    (int) redMinRows,
  }),
});

class CopaLanePerceptor : public CopaLanePerceptorBase
{
  void update(LanePercept& lanePercept) override;

  std::unique_ptr<CopaRace::EstimadorCarril> estimador;
  int anchoEstimador = 0;
  int altoEstimador = 0;
  unsigned lastProcessed = 0;
  CopaRace::ImagenRGB imagen;
};
