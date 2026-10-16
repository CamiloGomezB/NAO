/**
 * @file CopaLanePerceptor.cpp
 *
 * @author Repo NAO (caminata RL)
 */

#include "CopaLanePerceptor.h"
#include "ImageProcessing/ColorModelConversions.h"
#include <algorithm>

MAKE_MODULE(CopaLanePerceptor);

void CopaLanePerceptor::update(LanePercept& lanePercept)
{
  if(theCameraInfo.camera != CameraInfo::lower)
    return;
  if(lastProcessed && theFrameInfo.getTimeSince(lastProcessed) < periodMs)
    return;  // se conserva la ultima medicion (con su timestamp) entre imagenes
  if(requireStableMatrix && !theCameraMatrix.isValid)
    return;
  lastProcessed = theFrameInfo.time;

  // Imagen de trabajo de 320 x 240 (QVGA, la del entrenamiento); si la camara entrega mas, se submuestrea.
  const int paso = std::max(1, theCameraInfo.width / 320);
  const int ancho = theCameraInfo.width / paso, alto = theCameraInfo.height / paso;
  if(!estimador || ancho != anchoEstimador || alto != altoEstimador)
  {
    CopaRace::ParametrosCarril p;
    p.ancho = ancho;
    p.alto = alto;
    if(useCalibratedIntrinsics)
    {
      p.fx = theCameraInfo.focalLength / paso;
      p.fy = theCameraInfo.focalLengthHeight / paso;
      p.cx = theCameraInfo.opticalCenter.x() / paso;
      p.cy = theCameraInfo.opticalCenter.y() / paso;
    }
    p.polaridadClara = lightLine;
    if(colorMode)
      p.colorRef = std::array<std::array<double, 3>, 2>{{{colorAxis.x(), colorAxis.y(), colorAxis.z()},
                                                        {colorMean.x(), colorMean.y(), colorMean.z()}}};
    p.anchoCarril = laneWidth;
    p.anchoLinea = lineWidth;
    p.pasoFilas = rowStep;
    p.darkRatio = darkRatio;
    p.minContraste = minContrast;
    p.relContraste = relContrast;
    p.ventanaLocal = localWindow;
    p.xMin = xMin;
    p.xMax = xMax;
    p.maxAbsY = maxAbsY;
    p.iteracionesRansac = ransacIterations;
    p.tolInlier = inlierTol;
    p.minInliers = minInliers;
    p.maxLineas = maxLines;
    p.tolPar = pairTol;
    p.rojoRatio = redRatio;
    p.rojoMin = redMin;
    p.rojoMinSat = redMinSat;
    p.rojoMinPxFila = redMinRowPx;
    p.rojoMinFilas = redMinRows;
    estimador = std::make_unique<CopaRace::EstimadorCarril>(p);
    anchoEstimador = ancho;
    altoEstimador = alto;
    imagen.ancho = ancho;
    imagen.alto = alto;
  }

  imagen.datos.resize(static_cast<std::size_t>(ancho) * alto * 3);
  unsigned char* destino = imagen.datos.data();
  for(int v = 0; v < alto; ++v)
    for(int u = 0; u < ancho; ++u)
    {
      const PixelTypes::YUVPixel yuv = theCameraImage.getYUV(u * paso, v * paso);
      ColorModelConversions::fromYUVToRGB(yuv.y, yuv.u, yuv.v, destino[0], destino[1], destino[2]);
      destino += 3;
    }

  // Pose camara -> robot (origen en el suelo entre los pies), en metros, por filas.
  const auto& R = theCameraMatrix.rotation;
  const Vector3f& t = theCameraMatrix.translation;
  const std::array<double, 16> T = {R(0, 0), R(0, 1), R(0, 2), t.x() / 1000., R(1, 0), R(1, 1), R(1, 2), t.y() / 1000.,
                                    R(2, 0), R(2, 1), R(2, 2), t.z() / 1000., 0., 0., 0., 1.};
  const CopaRace::Estimacion e = estimador->procesar(imagen, T);
  lanePercept.valid = e.valida;
  lanePercept.d = static_cast<float>(e.d);
  lanePercept.psi = static_cast<float>(e.psi);
  lanePercept.nLines = e.nLineas;
  lanePercept.nPoints = e.nPuntos;
  lanePercept.quality = static_cast<float>(e.calidad);
  lanePercept.finishSeen = e.distanciaRoja.has_value();
  lanePercept.finishDistance = static_cast<float>(e.distanciaRoja.value_or(0.));
  lanePercept.timestamp = theFrameInfo.time;
}
