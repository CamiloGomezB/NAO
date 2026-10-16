// Prueba de paridad: reproduce tests/robot_paridad/carrera_golden.json (escrito por
// scripts/exportar_politicas_robot.py con el codigo Python) con bhuman/Src/Tools/CopaRace/CopaRace.h, el
// encabezado que corre en el NAO. Las politicas se leen de los mismos .cfg que se despliegan.
// Sale con codigo 0 solo si todo coincide.
#include "Tools/CopaRace/CopaRace.h"

#include "json.hpp"

#include <chrono>
#include <cmath>
#include <fstream>
#include <iostream>
#include <memory>
#include <sstream>
#include <string>

using nlohmann::json;
using namespace CopaRace;

namespace
{
  int fallos = 0;
  int revisiones = 0;
  double maxDiferenciaPolitica = 0.; // max |accion C++ - SB3| sobre todos los casos de las politicas
  std::string raiz;

  void esperar(bool condicion, const std::string& que)
  {
    ++revisiones;
    if(!condicion && ++fallos <= 30)
      std::cerr << "DIFERENCIA " << que << "\n";
  }

  void cerca(double real, double esperado, double tol, const std::string& que)
  {
    const double escala = std::max(1., std::abs(esperado));
    esperar(std::abs(real - esperado) <= tol * escala,
            que + " real=" + std::to_string(real) + " esperado=" + std::to_string(esperado));
  }

  // ---------------------------------------------------------------- lector minimo del .cfg exportado
  std::string leer(const std::string& ruta)
  {
    std::ifstream f(ruta, std::ios::binary);
    std::stringstream s;
    s << f.rdbuf();
    return s.str();
  }

  std::string sinComentarios(const std::string& texto)
  {
    std::string salida;
    std::istringstream lineas(texto);
    for(std::string linea; std::getline(lineas, linea);)
    {
      const auto p = linea.find("//");
      salida += (p == std::string::npos ? linea : linea.substr(0, p)) + "\n";
    }
    return salida;
  }

  /** Bloque que sigue a "clave =" desde `desde`: devuelve [inicio, fin) del valor sin el ';'. */
  std::pair<std::size_t, std::size_t> valor(const std::string& t, const std::string& clave, std::size_t desde = 0)
  {
    const std::size_t k = t.find(clave + " =", desde);
    if(k == std::string::npos)
      throw std::runtime_error("falta " + clave);
    std::size_t i = t.find('=', k) + 1;
    while(t[i] == ' ' || t[i] == '\n' || t[i] == '\r')
      ++i;
    if(t[i] == '[' || t[i] == '{')
    {
      const char abre = t[i], cierra = abre == '[' ? ']' : '}';
      int nivel = 0;
      for(std::size_t j = i; j < t.size(); ++j)
      {
        if(t[j] == abre)
          ++nivel;
        else if(t[j] == cierra && --nivel == 0)
          return {i, j + 1};
      }
      throw std::runtime_error("bloque sin cerrar en " + clave);
    }
    return {i, t.find(';', i)};
  }

  std::vector<double> numeros(const std::string& t, std::pair<std::size_t, std::size_t> r)
  {
    std::vector<double> v;
    std::string s = t.substr(r.first, r.second - r.first);
    for(char& c : s)
      if(c == '[' || c == ']' || c == ',' || c == '\n' || c == '\r')
        c = ' ';
    std::istringstream in(s);
    for(std::string tok; in >> tok;)
      v.push_back(std::strtod(tok.c_str(), nullptr));
    return v;
  }

  CapaDensa capa(const std::string& t)
  {
    CapaDensa c;
    c.filas = static_cast<std::size_t>(numeros(t, valor(t, "filas"))[0]);
    c.columnas = static_cast<std::size_t>(numeros(t, valor(t, "columnas"))[0]);
    // Como el robot: float32 leido del texto y llevado a double.
    for(const double w : numeros(t, valor(t, "pesos")))
      c.pesos.push_back(static_cast<double>(static_cast<float>(w)));
    for(const double b : numeros(t, valor(t, "sesgo")))
      c.sesgo.push_back(static_cast<double>(static_cast<float>(b)));
    return c;
  }

  ParametrosPolitica leerPolitica(const std::string& ruta)
  {
    const std::string t = sinComentarios(leer(ruta));
    ParametrosPolitica p;
    const auto act = valor(t, "activacion");
    p.activacion = t.substr(act.first, act.second - act.first).find("elu") != std::string::npos ? Activacion::elu
                                                                                                    : Activacion::tanh;
    p.media = numeros(t, valor(t, "media"));
    p.varianza = numeros(t, valor(t, "varianza"));
    p.clipObs = numeros(t, valor(t, "clipObs"))[0];
    p.epsilon = numeros(t, valor(t, "epsilon"))[0];
    p.periodoMarcha = numeros(t, valor(t, "periodoMarcha"))[0];
    p.vxCmd = numeros(t, valor(t, "vxCmd"))[0];
    const auto ocultas = valor(t, "ocultas");
    std::size_t i = ocultas.first + 1;
    while(true)
    {
      const std::size_t a = t.find('{', i);
      if(a == std::string::npos || a >= ocultas.second)
        break;
      int nivel = 0;
      std::size_t b = a;
      for(; b < ocultas.second; ++b)
        if(t[b] == '{')
          ++nivel;
        else if(t[b] == '}' && --nivel == 0)
          break;
      p.ocultas.push_back(capa(t.substr(a, b - a + 1)));
      i = b + 1;
    }
    const auto accion = valor(t, "accion");
    p.accion = capa(t.substr(accion.first, accion.second - accion.first));
    return p;
  }

  // ---------------------------------------------------------------- pruebas
  void politicas(const json& g)
  {
    for(const auto& [nombre, entrada] : g.at("politicas").items())
    {
      const ParametrosPolitica p = leerPolitica(raiz + "/" + entrada.at("archivo").get<std::string>());
      esperar(p.valida(), nombre + " parametros validos");
      cerca(p.periodoMarcha, entrada.at("periodoMarcha").get<double>(), 0., nombre + " periodo");
      cerca(p.vxCmd, entrada.at("vxCmd").get<double>(), 0., nombre + " vx");
      const Politica politica(p);
      int k = 0;
      for(const json& caso : entrada.at("casos"))
      {
        Observacion obs{};
        const auto v = caso.at("observacion").get<std::vector<double>>();
        std::copy(v.begin(), v.end(), obs.begin());
        const Accion a = politica(obs);
        const auto esperado = caso.at("accion").get<std::vector<double>>();
        for(std::size_t i = 0; i < nAccion; ++i)
        {
          maxDiferenciaPolitica = std::max(maxDiferenciaPolitica, std::abs(a[i] - esperado[i]));
          cerca(a[i], esperado[i], 2e-4, nombre + " caso " + std::to_string(k) + " a" + std::to_string(i));
        }
        ++k;
      }
      // Tiempo de inferencia en el PC (referencia; en el NAO se mide en la sesion real).
      Observacion obs{};
      const auto v = entrada.at("casos").at(0).at("observacion").get<std::vector<double>>();
      std::copy(v.begin(), v.end(), obs.begin());
      constexpr int repeticiones = 5000;
      double suma = 0.;
      const auto inicio = std::chrono::steady_clock::now();
      for(int r = 0; r < repeticiones; ++r)
      {
        obs[0] += 1e-9;
        suma += politica(obs)[0];
      }
      const double us = std::chrono::duration<double, std::micro>(std::chrono::steady_clock::now() - inicio).count() / repeticiones;
      std::cout << "inferencia " << nombre << ": " << us << " us por decision (PC)" << (suma == 12345. ? " " : "") << "\n";
    }
  }

  void contrato(const json& g)
  {
    int k = 0;
    for(const json& c : g.at("contrato"))
    {
      const std::string donde = "contrato " + std::to_string(k++);
      Sensores s;
      const json& f = c.at("frame");
      for(std::size_t i = 0; i < nArticulaciones; ++i)
      {
        s.angulos[i] = f.at("angles")[i].get<double>();
        s.velocidades[i] = f.at("velocity")[i].get<double>();
      }
      for(int i = 0; i < 3; ++i)
        s.giro[i] = f.at("gyro")[i].get<double>();
      for(int i = 0; i < 4; ++i)
        s.orientacion[i] = f.at("orientation")[i].get<double>();
      for(int i = 0; i < 8; ++i)
        s.fsr[i] = f.at("fsr")[i].get<double>();
      Accion anterior{};
      for(std::size_t i = 0; i < nAccion; ++i)
        anterior[i] = c.at("accion_anterior")[i].get<double>();
      const std::array<double, 3> camara = {c.at("camara")[0].get<double>(), c.at("camara")[1].get<double>(),
                                            c.at("camara")[2].get<double>()};
      const Observacion obs = armarObservacion(s, c.at("rumbo_objetivo").get<double>(), camara, anterior,
                                               c.at("t").get<double>(), c.at("vx").get<double>());
      for(std::size_t i = 0; i < dimObservacion; ++i)
        cerca(obs[i], c.at("observacion")[i].get<double>(), 1e-12, donde + " obs" + std::to_string(i));
      Accion accion{};
      for(std::size_t i = 0; i < nAccion; ++i)
        accion[i] = c.at("accion")[i].get<double>();
      const Accion objetivos = accionAObjetivos(accion);
      for(std::size_t i = 0; i < nAccion; ++i)
        cerca(objetivos[i], c.at("objetivos")[i].get<double>(), 1e-12, donde + " objetivo" + std::to_string(i));
      const auto angulos = objetivosASalida(objetivos);
      for(std::size_t i = 0; i < nArticulaciones; ++i)
        cerca(angulos[i], c.at("angulos")[i].get<double>(), 1e-12, donde + " angulo" + std::to_string(i));
      cerca(rumboObjetivoInicial(c.at("rumbo_imu").get<double>(), c.at("psis").get<std::vector<double>>()),
            c.at("rumbo_inicial").get<double>(), 1e-12, donde + " rumbo inicial");
    }
    EstadoCamara camara;
    for(const json& paso : g.at("camara"))
    {
      if(!paso.at("medicion").is_null())
      {
        const json& m = paso.at("medicion");
        camara.nuevaMedicion(m[0].get<double>(), m[1].get<double>(), m[2].get<double>(), m[3].get<bool>());
      }
      const auto obs = camara.observacion(paso.at("t").get<double>());
      for(int i = 0; i < 3; ++i)
        cerca(obs[i], paso.at("observacion")[i].get<double>(), 0., "camara t=" + std::to_string(paso.at("t").get<double>()));
    }
  }

  void azar(const json& g)
  {
    PyRandom r(0);
    for(const json& c : g.at("azar"))
      esperar(r.randrange(c.at("n").get<std::size_t>()) == c.at("valor").get<std::size_t>(),
              "randrange(" + std::to_string(c.at("n").get<std::size_t>()) + ")");
  }

  void casoVision(EstimadorCarril& estimador, const json& c, const std::string& datos, int indice,
                  const std::string& donde)
  {
    const std::size_t tam = 320 * 240 * 3;
    ImagenRGB img;
    img.ancho = 320;
    img.alto = 240;
    img.datos.assign(datos.begin() + static_cast<std::ptrdiff_t>(indice * tam),
                     datos.begin() + static_cast<std::ptrdiff_t>((indice + 1) * tam));
    std::array<double, 16> T{};
    for(int i = 0; i < 16; ++i)
      T[i] = c.at("T")[i].get<double>();
    const Estimacion e = estimador.procesar(img, T);
    esperar(e.valida == c.at("valida").get<bool>(), donde + " valida");
    esperar(e.nLineas == c.at("n_lineas").get<int>(), donde + " n_lineas " + std::to_string(e.nLineas));
    esperar(e.nPuntos == c.at("n_puntos").get<int>(), donde + " n_puntos " + std::to_string(e.nPuntos));
    cerca(e.d, c.at("d").get<double>(), 1e-12, donde + " d");
    cerca(e.psi, c.at("psi").get<double>(), 1e-12, donde + " psi");
    cerca(e.pendiente, c.at("pendiente").get<double>(), 1e-12, donde + " pendiente");
    cerca(e.calidad, c.at("calidad").get<double>(), 0., donde + " calidad");
    esperar(e.distanciaRoja.has_value() == !c.at("distancia_roja").is_null(), donde + " meta vista");
    if(e.distanciaRoja && !c.at("distancia_roja").is_null())
      cerca(*e.distanciaRoja, c.at("distancia_roja").get<double>(), 1e-12, donde + " distancia meta");
    std::cout << donde << ": d=" << e.d << " (verdad " << c.at("verdad").at("d").get<double>() << ") psi=" << e.psi
              << " (verdad " << c.at("verdad").at("psi").get<double>() << ") lineas=" << e.nLineas
              << (e.distanciaRoja ? " meta=" + std::to_string(*e.distanciaRoja) : std::string()) << "\n";
  }

  void vision(const json& g)
  {
    const std::string datos = leer(raiz + "/tests/robot_paridad/imagenes_carril.bin");
    EstimadorCarril estimador;
    int k = 0;
    for(const json& c : g.at("vision"))
    {
      casoVision(estimador, c, datos, k, "imagen " + std::to_string(k));
      ++k;
    }
  }

  // Linea clara sobre piso oscuro y modo "color" (config/pista_robot.json): un estimador nuevo por modo, como Python.
  void visionModos(const json& g)
  {
    const std::string datos = leer(raiz + "/tests/robot_paridad/imagenes_carril_modos.bin");
    std::unique_ptr<EstimadorCarril> estimador;
    std::string modo;
    int k = 0;
    for(const json& c : g.at("vision_modos"))
    {
      if(!estimador || c.at("modo").get<std::string>() != modo)
      {
        modo = c.at("modo").get<std::string>();
        ParametrosCarril p;
        p.polaridadClara = true;
        if(!c.at("color_ref").is_null())
        {
          std::array<std::array<double, 3>, 2> ref{};
          for(int i = 0; i < 2; ++i)
            for(int j = 0; j < 3; ++j)
              ref[i][j] = c.at("color_ref")[i][j].get<double>();
          p.colorRef = ref;
        }
        estimador = std::make_unique<EstimadorCarril>(p);
      }
      casoVision(*estimador, c, datos, k, "imagen " + modo + " " + std::to_string(k));
      ++k;
    }
  }

  void filtro(const json& g)
  {
    LaneFilter f;
    LaneController ctrl;
    ctrl.vxMax = .8;
    int k = 0;
    for(const json& c : g.at("filtro"))
    {
      const std::string donde = "filtro " + std::to_string(k++);
      f.predecir(c.at("pred")[0].get<double>(), c.at("pred")[1].get<double>(), c.at("pred")[2].get<double>());
      Estimacion e;
      e.valida = c.at("est").at("valida").get<bool>();
      e.nLineas = c.at("est").at("n_lineas").get<int>();
      e.d = c.at("est").at("d").get<double>();
      e.psi = c.at("est").at("psi").get<double>();
      esperar(f.actualizar(e) == c.at("aceptada").get<bool>(), donde + " aceptada");
      cerca(f.d, c.at("d").get<double>(), 1e-12, donde + " d");
      cerca(f.psi, c.at("psi").get<double>(), 1e-12, donde + " psi");
      cerca(f.s, c.at("s").get<double>(), 1e-12, donde + " s");
      cerca(f.pD, c.at("P_d").get<double>(), 1e-12, donde + " P_d");
      cerca(f.pPsi, c.at("P_psi").get<double>(), 1e-12, donde + " P_psi");
      const auto cmd = ctrl.comando(f.d, f.psi, c.at("confianza").get<double>());
      for(int i = 0; i < 3; ++i)
        cerca(cmd[i], c.at("comando")[i].get<double>(), 1e-12, donde + " comando" + std::to_string(i));
      cerca(ctrl.margen(f.d), c.at("margen").get<double>(), 1e-12, donde + " margen");
    }
  }
}

int main(int argc, char** argv)
{
  if(argc != 2)
  {
    std::cerr << "uso: carrera_paridad <raiz del repo NAO>\n";
    return 2;
  }
  raiz = argv[1];
  std::ifstream f(raiz + "/tests/robot_paridad/carrera_golden.json");
  if(!f)
  {
    std::cerr << "no se encontro carrera_golden.json\n";
    return 2;
  }
  const json g = json::parse(f);
  politicas(g);
  contrato(g);
  azar(g);
  vision(g);
  filtro(g);
  visionModos(g);
  std::cout << "max |accion C++ - SB3| = " << maxDiferenciaPolitica << "\n";
  std::cout << "revisiones=" << revisiones << " fallos=" << fallos << "\n";
  return fallos == 0 ? 0 : 1;
}
