/**
 * @file CopaRace.h
 *
 * Version en C++ de la capa de carrera del repo NAO (Carrera Individual, Copa NAO CCM MX 2026), sin
 * dependencias de B-Human: el mismo encabezado corre en el NAO (dentro de los modulos de bhuman/) y en las
 * pruebas de paridad que lo comparan con el codigo Python del que sale:
 *
 *  - Contrato v1 (observacion de 54 valores, accion de 13 angulos)  <- src/race/contract.py
 *  - MlpPolicy (actor PPO determinista, ELU, VecNormalize)         <- stable-baselines3 MlpPolicy + VecNormalize
 *  - PyRandom (MT19937 identico a random.Random de Python 3)         <- para que el RANSAC sea el mismo
 *  - EstimadorCarril (d, psi, valido, distancia a la meta roja)       <- carril/lane_estimator_puro.py
 *  - LaneFilter y LaneController (carril B-Human con vision)           <- carril/lane_filter.py, carril/controller.py
 *
 * Unidades: metros, segundos, radianes. Marco del robot: x adelante, y a la izquierda.
 */

#pragma once

#include <algorithm>
#include <array>
#include <cmath>
#include <cstdint>
#include <deque>
#include <optional>
#include <string>
#include <utility>
#include <vector>

namespace CopaRace
{
  constexpr double pi = 3.14159265358979323846;

  inline double recortar(double x, double lo, double hi) { return x < lo ? lo : x > hi ? hi : x; }

  /** (a + pi) % (2 pi) - pi de Python: resultado en [-pi, pi). */
  inline double envolverAngulo(double a)
  {
    double r = std::fmod(a + pi, 2. * pi);
    if(r < 0.)
      r += 2. * pi;
    return r - pi;
  }

  // ---------------------------------------------------------------------------------------- contrato v1

  constexpr double cicloS = .012;              /**< Ciclo de LoLA y del motor de B-Human. */
  constexpr int ciclosPorAccion = 2;           /**< La politica actua cada 24 ms. */
  constexpr double periodoMarchaS = .5;        /**< Periodo de marcha por defecto (cada politica trae el suyo). */
  constexpr double validezCamaraS = .3;        /**< "valido" = hubo medicion en los ultimos 300 ms. */
  constexpr double escalaGiro = .25;
  constexpr double escalaVelArticular = .05;
  constexpr double limiteErrorRumbo = pi / 2.;
  constexpr double masaRobotKg = 5.36;
  constexpr std::size_t nArticulaciones = 26;
  constexpr std::size_t nAccion = 13;
  constexpr std::size_t dimObservacion = 54;

  /** Orden de las 26 articulaciones de B-Human (Joints::Joint), con los nombres del modelo y de NAOqi. */
  enum Articulacion : std::size_t
  {
    HeadYaw, HeadPitch,
    LShoulderPitch, LShoulderRoll, LElbowYaw, LElbowRoll, LWristYaw, LHand,
    RShoulderPitch, RShoulderRoll, RElbowYaw, RElbowRoll, RWristYaw, RHand,
    LHipYawPitch, LHipRoll, LHipPitch, LKneePitch, LAnklePitch, LAnkleRoll,
    RHipYawPitch, RHipRoll, RHipPitch, RKneePitch, RAnklePitch, RAnkleRoll,
  };

  /** Las 13 articulaciones de la accion, en el orden del vector de accion. */
  constexpr std::array<std::size_t, nAccion> articulacionesAccion = {
    LHipYawPitch, LHipRoll, LHipPitch, LKneePitch, LAnklePitch, LAnkleRoll,
    RHipRoll, RHipPitch, RKneePitch, RAnklePitch, RAnkleRoll, LShoulderPitch, RShoulderPitch,
  };

  /** Pose "home" del modelo V6 (keyframe home de assets/nao/nao.xml). */
  constexpr std::array<double, nArticulaciones> poseHome = {
    0., 0.,
    1.57, .2, -1.57, -.2, 0., 0.,
    1.57, -.2, 1.57, .2, 0., 0.,
    0., 0., -.4, .8, -.4, 0.,
    0., 0., -.4, .8, -.4, 0.,
  };

  /** Desviacion respecto a home para accion = -1 (lo) y +1 (hi), en el orden de la accion. */
  constexpr std::array<std::pair<double, double>, nAccion> limitesAccion = {{
    {-.10, .10}, {-.07, .25}, {-.5, .5}, {-.5, .5}, {-.4, .4}, {-.25, .25},
    {-.25, .07}, {-.5, .5}, {-.5, .5}, {-.4, .4}, {-.25, .25}, {-.5, .5}, {-.5, .5},
  }};

  constexpr double presupuestoAdentroRad = .09;
  constexpr double pesoAdentroTobillo = .174;
  constexpr double pesoHipYawPitchPos = .48;
  constexpr double pesoHipYawPitchNeg = .245;

  /** Indices de la accion. */
  enum IndiceAccion : std::size_t { aLHipYawPitch, aLHipRoll, aLHipPitch, aLKneePitch, aLAnklePitch, aLAnkleRoll,
                                    aRHipRoll, aRHipPitch, aRKneePitch, aRAnklePitch, aRAnkleRoll, aLShoulderPitch, aRShoulderPitch };

  /** Vector (0, 0, -1) del mundo en el marco del torso, desde el cuaternion wxyz del torso. */
  inline std::array<double, 3> gravedadProyectada(double w, double x, double y, double z)
  {
    return {-(2. * (x * z - w * y)), -(2. * (y * z + w * x)), -(1. - 2. * (x * x + y * y))};
  }

  inline double rumboDesdeCuaternion(double w, double x, double y, double z)
  {
    return std::atan2(2. * (w * z + x * y), 1. - 2. * (y * y + z * z));
  }

  /** Rumbo objetivo de la IMU = direccion del carril medida de pie (paso 58c, E50). */
  inline double rumboObjetivoInicial(double rumboImu, const std::vector<double>& psiMediciones)
  {
    if(psiMediciones.empty())
      return envolverAngulo(rumboImu);
    double suma = 0.;
    for(const double psi : psiMediciones)
      suma += psi;
    return envolverAngulo(rumboImu - suma / static_cast<double>(psiMediciones.size()));
  }

  /** (izquierdo, derecho) = suma de los 4 FSR de cada pie [kg] / masa. Orden: izq fl, fr, bl, br; der fl, fr, bl, br. */
  inline std::array<double, 2> cargaPies(const std::array<double, 8>& fsr, double masaKg = masaRobotKg)
  {
    double izq = 0., der = 0.;
    for(int i = 0; i < 4; ++i)
      izq += fsr[i];
    for(int i = 4; i < 8; ++i)
      der += fsr[i];
    return {recortar(izq / masaKg, 0., 2.), recortar(der / masaKg, 0., 2.)};
  }

  /** (seno, coseno) de la fase de marcha; t en segundos desde que arranca la marcha (0 mientras esta de pie). */
  inline std::array<double, 2> relojMarcha(double t, double periodo = periodoMarchaS)
  {
    double fraccion = std::fmod(t / periodo, 1.);
    if(fraccion < 0.)
      fraccion += 1.;
    const double fase = 2. * pi * fraccion;
    return {std::sin(fase), std::cos(fase)};
  }

  /** La ultima medicion CRUDA de la camara, mantenida entre fotos; valido si tiene menos de 300 ms. */
  class EstadoCamara
  {
  public:
    void nuevaMedicion(double t, double d, double psi, bool valida)
    {
      if(valida)
      {
        this->d = d;
        this->psi = psi;
        tMedicion = t;
      }
    }

    std::array<double, 3> observacion(double t) const
    {
      const bool valido = tMedicion.has_value() && (t - *tMedicion) <= validezCamaraS + 1e-9;
      return {d, psi, valido ? 1. : 0.};
    }

  private:
    double d = 0.;
    double psi = 0.;
    std::optional<double> tMedicion;
  };

  /** Sensores en el formato del SensorAdapter de PenaltyStack (orden de B-Human). */
  struct Sensores
  {
    std::array<double, nArticulaciones> angulos{};
    std::array<double, nArticulaciones> velocidades{};
    std::array<double, 3> giro{};                 /**< rad/s */
    std::array<double, 4> orientacion{1., 0., 0., 0.}; /**< Cuaternion wxyz del torso. */
    std::array<double, 8> fsr{};                  /**< kg */
  };

  using Observacion = std::array<double, dimObservacion>;
  using Accion = std::array<double, nAccion>;

  /** armar_observacion(): observacion de 54 valores (contrato v1). */
  inline Observacion armarObservacion(const Sensores& s, double rumboObjetivo, const std::array<double, 3>& camara,
                                      const Accion& accionAnterior, double tMarcha, double vxCmd,
                                      double periodo = periodoMarchaS)
  {
    Observacion obs{};
    std::size_t k = 0;
    const auto& q = s.orientacion;
    for(const double g : gravedadProyectada(q[0], q[1], q[2], q[3]))
      obs[k++] = g;
    for(const double g : s.giro)
      obs[k++] = g * escalaGiro;
    obs[k++] = recortar(envolverAngulo(rumboObjetivo - rumboDesdeCuaternion(q[0], q[1], q[2], q[3])),
                        -limiteErrorRumbo, limiteErrorRumbo);
    for(const double c : camara)
      obs[k++] = c;
    for(const std::size_t j : articulacionesAccion)
      obs[k++] = s.angulos[j] - poseHome[j];
    for(const std::size_t j : articulacionesAccion)
      obs[k++] = s.velocidades[j] * escalaVelArticular;
    for(const double a : accionAnterior)
      obs[k++] = a;
    for(const double c : cargaPies(s.fsr))
      obs[k++] = c;
    for(const double r : relojMarcha(tMarcha, periodo))
      obs[k++] = r;
    obs[k++] = vxCmd;
    return obs;
  }

  /** Cuanto entran las dos piernas (radianes equivalentes de HipRoll) para desviaciones respecto a home. */
  inline double cuantoAdentro(const Accion& off)
  {
    const double y = off[aLHipYawPitch];
    return std::max(0., -off[aLHipRoll]) + std::max(0., off[aRHipRoll]) +
           pesoAdentroTobillo * (std::max(0., -off[aLAnkleRoll]) + std::max(0., off[aRAnkleRoll])) +
           (y > 0. ? pesoHipYawPitchPos * y : pesoHipYawPitchNeg * (-y));
  }

  /** accion_a_objetivos(): 13 acciones en [-1, 1] -> 13 angulos objetivo (home + desviacion, con presupuesto). */
  inline Accion accionAObjetivos(const Accion& accion)
  {
    Accion off{};
    for(std::size_t i = 0; i < nAccion; ++i)
    {
      const double a = recortar(accion[i], -1., 1.);
      const auto [lo, hi] = limitesAccion[i];
      off[i] = a >= 0. ? a * hi : -a * lo;
    }
    const double total = cuantoAdentro(off);
    if(total > presupuestoAdentroRad)
    {
      const double f = presupuestoAdentroRad / total;
      const std::pair<std::size_t, int> adentro[] = {{aLHipRoll, -1}, {aRHipRoll, 1}, {aLAnkleRoll, -1}, {aRAnkleRoll, 1}};
      for(const auto& [i, signo] : adentro)
        if(off[i] * signo > 0.)
          off[i] *= f;
      off[aLHipYawPitch] *= f;
    }
    Accion objetivos{};
    for(std::size_t i = 0; i < nAccion; ++i)
      objetivos[i] = poseHome[articulacionesAccion[i]] + off[i];
    return objetivos;
  }

  /** objetivos_a_salida_bhuman(): angulos de las 26 articulaciones (resto en home, RHipYawPitch = LHipYawPitch). */
  inline std::array<double, nArticulaciones> objetivosASalida(const Accion& objetivos)
  {
    std::array<double, nArticulaciones> angulos = poseHome;
    for(std::size_t i = 0; i < nAccion; ++i)
      angulos[articulacionesAccion[i]] = objetivos[i];
    angulos[RHipYawPitch] = angulos[LHipYawPitch];
    return angulos;
  }

  // ---------------------------------------------------------------------------------------- politica

  enum class Activacion { tanh, elu };

  struct CapaDensa
  {
    std::size_t filas = 0;        /**< Salidas. */
    std::size_t columnas = 0;     /**< Entradas. */
    std::vector<double> pesos;    /**< filas x columnas, por filas. */
    std::vector<double> sesgo;

    bool valida() const { return filas > 0 && columnas > 0 && pesos.size() == filas * columnas && sesgo.size() == filas; }

    std::vector<double> aplicar(const std::vector<double>& x, std::optional<Activacion> activacion) const
    {
      std::vector<double> y(filas);
      for(std::size_t r = 0; r < filas; ++r)
      {
        double suma = sesgo[r];
        const double* fila = pesos.data() + r * columnas;
        for(std::size_t c = 0; c < columnas; ++c)
          suma += fila[c] * x[c];
        if(activacion == Activacion::tanh)
          suma = std::tanh(suma);
        else if(activacion == Activacion::elu)
          suma = suma > 0. ? suma : std::expm1(suma);
        y[r] = suma;
      }
      return y;
    }
  };

  struct ParametrosPolitica
  {
    std::string nombre;
    Activacion activacion = Activacion::elu;
    std::vector<double> media;     /**< VecNormalize obs_rms.mean (54). */
    std::vector<double> varianza;  /**< VecNormalize obs_rms.var (54). */
    double clipObs = 10.;
    double epsilon = 1e-8;
    std::vector<CapaDensa> ocultas;
    CapaDensa accion;
    double periodoMarcha = periodoMarchaS;
    double vxCmd = .45;

    bool valida() const
    {
      if(media.size() != dimObservacion || varianza.size() != dimObservacion || ocultas.empty() || !accion.valida() ||
         accion.filas != nAccion)
        return false;
      std::size_t ancho = dimObservacion;
      for(const CapaDensa& capa : ocultas)
      {
        if(!capa.valida() || capa.columnas != ancho)
          return false;
        ancho = capa.filas;
      }
      return accion.columnas == ancho && periodoMarcha > 0.;
    }
  };

  /** Actor de stable-baselines3 con deterministic=True: clip(media, -1, 1) tras VecNormalize. */
  class Politica
  {
  public:
    Politica() = default;
    explicit Politica(ParametrosPolitica p) : p(std::move(p)) {}

    bool valida() const { return p.valida(); }
    const ParametrosPolitica& parametros() const { return p; }

    Accion operator()(const Observacion& obs) const
    {
      std::vector<double> x(dimObservacion);
      for(std::size_t i = 0; i < dimObservacion; ++i)
      {
        // La observacion del entorno es float32; las estadisticas, float64; la entrada a la red, float32.
        const double v = static_cast<double>(static_cast<float>(obs[i]));
        const double n = (v - p.media[i]) / std::sqrt(p.varianza[i] + p.epsilon);
        x[i] = static_cast<double>(static_cast<float>(recortar(n, -p.clipObs, p.clipObs)));
      }
      for(const CapaDensa& capa : p.ocultas)
        x = capa.aplicar(x, p.activacion);
      const std::vector<double> media = p.accion.aplicar(x, std::nullopt);
      Accion a{};
      for(std::size_t i = 0; i < nAccion; ++i)
        a[i] = recortar(media[i], -1., 1.);
      return a;
    }

  private:
    ParametrosPolitica p;
  };

  // ---------------------------------------------------------------------------------------- azar de Python

  /** MT19937 con la siembra y randrange() de random.Random de Python 3 (init_by_array, _randbelow). */
  class PyRandom
  {
  public:
    explicit PyRandom(std::uint64_t semilla = 0) { sembrar(semilla); }

    void sembrar(std::uint64_t semilla)
    {
      std::vector<std::uint32_t> clave;
      do
      {
        clave.push_back(static_cast<std::uint32_t>(semilla & 0xffffffffu));
        semilla >>= 32;
      }
      while(semilla);
      initByArray(clave);
    }

    std::uint32_t genrand()
    {
      if(indice >= N)
        generar();
      std::uint32_t y = mt[indice++];
      y ^= (y >> 11);
      y ^= (y << 7) & 0x9d2c5680u;
      y ^= (y << 15) & 0xefc60000u;
      y ^= (y >> 18);
      return y;
    }

    /** getrandbits(k) para 1 <= k <= 32. */
    std::uint32_t getrandbits(int k) { return genrand() >> (32 - k); }

    /** randrange(n) = _randbelow(n) para n >= 1. */
    std::size_t randrange(std::size_t n)
    {
      int k = 0;
      for(std::size_t m = n; m; m >>= 1)
        ++k;
      std::uint32_t r = getrandbits(k);
      while(r >= n)
        r = getrandbits(k);
      return r;
    }

  private:
    static constexpr int N = 624;
    static constexpr int M = 397;
    std::array<std::uint32_t, N> mt{};
    int indice = N + 1;

    void initGenrand(std::uint32_t s)
    {
      mt[0] = s;
      for(int i = 1; i < N; ++i)
        mt[i] = 1812433253u * (mt[i - 1] ^ (mt[i - 1] >> 30)) + static_cast<std::uint32_t>(i);
      indice = N;
    }

    void initByArray(const std::vector<std::uint32_t>& clave)
    {
      initGenrand(19650218u);
      int i = 1, j = 0;
      const int largo = static_cast<int>(clave.size());
      for(int k = N > largo ? N : largo; k; --k)
      {
        mt[i] = (mt[i] ^ ((mt[i - 1] ^ (mt[i - 1] >> 30)) * 1664525u)) + clave[j] + static_cast<std::uint32_t>(j);
        ++i;
        ++j;
        if(i >= N)
        {
          mt[0] = mt[N - 1];
          i = 1;
        }
        if(j >= largo)
          j = 0;
      }
      for(int k = N - 1; k; --k)
      {
        mt[i] = (mt[i] ^ ((mt[i - 1] ^ (mt[i - 1] >> 30)) * 1566083941u)) - static_cast<std::uint32_t>(i);
        ++i;
        if(i >= N)
        {
          mt[0] = mt[N - 1];
          i = 1;
        }
      }
      mt[0] = 0x80000000u;
      indice = N;
    }

    void generar()
    {
      static constexpr std::uint32_t mag01[2] = {0u, 0x9908b0dfu};
      int k = 0;
      for(; k < N - M; ++k)
      {
        const std::uint32_t y = (mt[k] & 0x80000000u) | (mt[k + 1] & 0x7fffffffu);
        mt[k] = mt[k + M] ^ (y >> 1) ^ mag01[y & 1u];
      }
      for(; k < N - 1; ++k)
      {
        const std::uint32_t y = (mt[k] & 0x80000000u) | (mt[k + 1] & 0x7fffffffu);
        mt[k] = mt[k + (M - N)] ^ (y >> 1) ^ mag01[y & 1u];
      }
      const std::uint32_t y = (mt[N - 1] & 0x80000000u) | (mt[0] & 0x7fffffffu);
      mt[N - 1] = mt[M - 1] ^ (y >> 1) ^ mag01[y & 1u];
      indice = 0;
    }
  };

  // ---------------------------------------------------------------------------------------- vision de carril

  /** Imagen RGB intercalada (w x h x 3), como la entrega ALVideoDevice (orden rgb). */
  struct ImagenRGB
  {
    int ancho = 0;
    int alto = 0;
    std::vector<unsigned char> datos;
  };

  struct Estimacion
  {
    bool valida = false;
    double d = 0.;
    double psi = 0.;
    int nLineas = 0;
    std::optional<double> cIzquierda;
    std::optional<double> cDerecha;
    double pendiente = 0.;
    int nPuntos = 0;
    std::optional<double> distanciaRoja;  /**< red_dist: distancia [m] a la meta roja, si se ve. */
    double calidad = 0.;
  };

  /** Parametros de EstimadorCarrilPuro (mismos valores por defecto). */
  struct ParametrosCarril
  {
    int ancho = 320;
    int alto = 240;
    double hfovGrados = 56.3;
    double vfovGrados = 43.7;
    std::optional<double> fx;     /**< Si se dan, reemplazan a los derivados del campo de vision (intrinsecos calibrados). */
    std::optional<double> fy;
    std::optional<double> cx;
    std::optional<double> cy;
    double anchoCarril = .70;
    double anchoLinea = .019;
    int pasoFilas = 4;
    double darkRatio = .62;
    double minContraste = 10.;
    double relContraste = .18;
    int ventanaLocal = 41;
    double tolAnchoMin = .35;
    double tolAnchoMax = 2.6;
    double xMin = .12;
    double xMax = 2.2;
    double maxAbsY = 1.6;
    int iteracionesRansac = 60;
    double tolInlier = .02;
    int minInliers = 8;
    int maxLineas = 4;
    double tolPar = .08;
    double rojoRatio = 2.;
    int rojoMin = 80;
    int rojoMinSat = 70;
    int rojoMinPxFila = 25;
    int rojoMinFilas = 3;
    bool polaridadClara = false;  /**< false = "oscura" (cinta negra sobre madera). */
    std::optional<std::array<std::array<double, 3>, 2>> colorRef; /**< Modo "color": ((ur, ug, ub), (mr, mg, mb)). */
    std::uint64_t semilla = 0;
  };

  /** EstimadorCarrilPuro: lineas del carril en la imagen -> d, psi, valido y distancia a la meta roja. */
  class EstimadorCarril
  {
  public:
    explicit EstimadorCarril(ParametrosCarril p = ParametrosCarril()) : p(std::move(p)), azar(this->p.semilla)
    {
      const ParametrosCarril& q = this->p;
      fx = q.fx ? *q.fx : (q.ancho / 2.) / std::tan(q.hfovGrados * (pi / 180.) / 2.);  // math.radians = x * (pi / 180)
      fy = q.fy ? *q.fy : (q.alto / 2.) / std::tan(q.vfovGrados * (pi / 180.) / 2.);
      cx = q.cx ? *q.cx : (q.ancho - 1) / 2.;
      cy = q.cy ? *q.cy : (q.alto - 1) / 2.;
      espaciado = q.anchoCarril + q.anchoLinea;
      k = q.ventanaLocal | 1;
      clara = q.polaridadClara || q.colorRef.has_value();
    }

    const ParametrosCarril& parametros() const { return p; }

    /** T: transformacion camara -> robot (4x4 por filas, metros). */
    Estimacion procesar(const ImagenRGB& img, const std::array<double, 16>& T)
    {
      Estimacion est;
      std::vector<std::pair<double, double>> puntos = escanear(img, T, est.distanciaRoja);
      est.nPuntos = static_cast<int>(puntos.size());
      std::vector<std::array<double, 3>> lineas;
      if(static_cast<int>(puntos.size()) >= p.minInliers)
        lineas = ransacLineas(puntos);
      const auto [cl, cr, m, n] = elegir(lineas);
      if(n == 0)
        return est;
      est.valida = true;
      est.nLineas = n;
      est.cIzquierda = cl;
      est.cDerecha = cr;
      est.pendiente = m;
      est.d = -.5 * (cl + cr) / std::sqrt(1. + m * m);
      est.psi = -std::atan(m);
      est.calidad = n == 2 ? 1. : .5;
      return est;
    }

  private:
    ParametrosCarril p;
    PyRandom azar;
    double fx = 0., fy = 0., cx = 0., cy = 0., espaciado = 0.;
    int k = 41;
    bool clara = false;

    std::optional<std::array<double, 3>> proyectar(double u, double v, const std::array<double, 16>& T) const
    {
      const double rx = 1., ry = -(u - cx) / fx, rz = -(v - cy) / fy;
      const double dx = T[0] * rx + T[1] * ry + T[2] * rz;
      const double dy = T[4] * rx + T[5] * ry + T[6] * rz;
      const double dz = T[8] * rx + T[9] * ry + T[10] * rz;
      if(dz > -1e-6)
        return std::nullopt;
      const double s = -T[11] / dz;
      return std::array<double, 3>{T[3] + s * dx, T[7] + s * dy, s};
    }

    std::vector<std::pair<double, double>> escanear(const ImagenRGB& img, const std::array<double, 16>& T,
                                                    std::optional<double>& distanciaRoja) const
    {
      const int w = p.ancho, half = k / 2;
      std::vector<std::pair<double, double>> pts;
      std::vector<std::pair<int, double>> filasRojas;
      std::vector<double> gris(w);
      for(int v = 0; v < p.alto; v += p.pasoFilas)
      {
        const unsigned char* fila = img.datos.data() + static_cast<std::size_t>(v) * w * 3;
        if(p.colorRef)
        {
          const auto& [u, m] = *p.colorRef;
          for(int i = 0; i < w; ++i)
            gris[i] = std::min(255., std::max(0., 128. + u[0] * (fila[3 * i] - m[0]) + u[1] * (fila[3 * i + 1] - m[1]) +
                                                    u[2] * (fila[3 * i + 2] - m[2])));
        }
        else
          for(int i = 0; i < w; ++i)
            gris[i] = .299 * fila[3 * i] + .587 * fila[3 * i + 1] + .114 * fila[3 * i + 2];
        // Meta roja: pixeles rojos saturados en la fila.
        int nRojo = 0, sumaU = 0;
        for(int i = 0; i < w; i += 2)
        {
          const int r = fila[3 * i], g = fila[3 * i + 1], b = fila[3 * i + 2];
          if(r > p.rojoMin && r > p.rojoRatio * g && r > p.rojoRatio * b && r - std::max(g, b) > p.rojoMinSat)
          {
            ++nRojo;
            sumaU += i;
          }
        }
        if(2 * nRojo >= p.rojoMinPxFila)
          filasRojas.emplace_back(v, sumaU / static_cast<double>(nRojo));
        // Fondo local: media movil con borde replicado.
        // Mismo orden que Python: gray[0] * (half + 1) + sum(gray[1:half + 1]).
        double tramo = 0.;
        for(int i = 1; i < half + 1; ++i)
          tramo += gris[i];
        double acc = gris[0] * (half + 1) + tramo;
        int inicio = -1;
        for(int i = 0; i < w + 1; ++i)
        {
          bool oscuro = false;
          if(i < w)
          {
            const int jIn = i + half < w ? i + half : w - 1;
            const int jOut = i - half - 1 > 0 ? i - half - 1 : 0;
            if(i > 0)
              acc += gris[jIn] - gris[jOut];
            const double bg = acc / k;
            const double gi = gris[i];
            const double umbral = p.minContraste > p.relContraste * bg ? p.minContraste : p.relContraste * bg;
            if(clara)
              oscuro = gi > bg + (255. - bg) * (1. - p.darkRatio) && (gi - bg) > umbral;
            else
              oscuro = gi < bg * p.darkRatio && (bg - gi) > umbral;
          }
          if(oscuro && inicio < 0)
            inicio = i;
          else if(!oscuro && inicio >= 0)
          {
            const int ancho = i - inicio;
            const double uc = (inicio + i - 1) / 2.;
            inicio = -1;
            const auto punto = proyectar(uc, static_cast<double>(v), T);
            if(!punto)
              continue;
            const auto [x, y, profundidad] = *punto;
            const double esperado = fx * p.anchoLinea / std::max(profundidad, .05);
            if(ancho >= std::max(1., p.tolAnchoMin * esperado) && ancho <= p.tolAnchoMax * esperado + 2. &&
               p.xMin < x && x < p.xMax && std::abs(y) < p.maxAbsY)
              pts.emplace_back(x, y);
          }
        }
      }
      distanciaRoja.reset();
      if(static_cast<int>(filasRojas.size()) >= p.rojoMinFilas)
      {
        std::vector<double> xs;
        for(const auto& [v, uc] : filasRojas)
          if(const auto punto = proyectar(uc, static_cast<double>(v), T))
            xs.push_back((*punto)[0]);
        if(static_cast<int>(xs.size()) >= p.rojoMinFilas)
        {
          std::sort(xs.begin(), xs.end());
          distanciaRoja = xs[static_cast<std::size_t>(.1 * static_cast<double>(xs.size() - 1))];
        }
      }
      return pts;
    }

    static std::optional<std::pair<double, double>> ajustar(const std::vector<std::pair<double, double>>& pts)
    {
      const double n = static_cast<double>(pts.size());
      double sx = 0., sy = 0.;
      for(const auto& q : pts)
        sx += q.first;
      for(const auto& q : pts)
        sy += q.second;
      const double xm = sx / n, ym = sy / n;
      double vx = 0.;
      for(const auto& q : pts)
        vx += std::pow(q.first - xm, 2.);
      if(vx < 1e-9)
        return std::nullopt;
      double cov = 0.;
      for(const auto& q : pts)
        cov += (q.first - xm) * (q.second - ym);
      const double m = cov / vx;
      return std::make_pair(ym - m * xm, m);
    }

    std::vector<std::array<double, 3>> ransacLineas(const std::vector<std::pair<double, double>>& pts)
    {
      std::vector<std::array<double, 3>> lineas;
      std::vector<std::pair<double, double>> resto = pts;
      const double tol = p.tolInlier;
      for(int l = 0; l < p.maxLineas; ++l)
      {
        const std::size_t n = resto.size();
        if(static_cast<int>(n) < p.minInliers)
          break;
        std::optional<std::pair<double, double>> mejor;
        int mejorN = 0;
        for(int it = 0; it < p.iteracionesRansac; ++it)
        {
          const auto [x1, y1] = resto[azar.randrange(n)];
          const auto [x2, y2] = resto[azar.randrange(n)];
          if(std::abs(x2 - x1) < .08)
            continue;
          const double m = (y2 - y1) / (x2 - x1);
          if(std::abs(m) > 1.2)
            continue;
          const double c = y1 - m * x1;
          const double lim = tol * std::sqrt(1. + m * m);
          int cuenta = 0;
          for(const auto& [x, y] : resto)
            if(std::abs(y - c - m * x) < lim)
              ++cuenta;
          if(cuenta > mejorN)
          {
            mejor = std::make_pair(c, m);
            mejorN = cuenta;
          }
        }
        if(!mejor || mejorN < p.minInliers)
          break;
        double c = mejor->first, m = mejor->second;
        double lim = tol * std::sqrt(1. + m * m);
        std::vector<std::pair<double, double>> inl;
        for(const auto& q : resto)
          if(std::abs(q.second - c - m * q.first) < lim)
            inl.push_back(q);
        double minX = inl.front().first, maxX = inl.front().first;
        for(const auto& q : inl)
        {
          minX = std::min(minX, q.first);
          maxX = std::max(maxX, q.first);
        }
        if(maxX - minX > .15)
          if(const auto f = ajustar(inl))
          {
            c = f->first;
            m = f->second;
          }
        lim = tol * std::sqrt(1. + m * m);
        std::vector<std::pair<double, double>> quedan;
        int nIn = 0;
        for(const auto& q : resto)
        {
          if(std::abs(q.second - c - m * q.first) < lim)
            ++nIn;
          else
            quedan.push_back(q);
        }
        if(nIn < p.minInliers)
          break;
        lineas.push_back({c, m, static_cast<double>(nIn)});
        resto = std::move(quedan);
      }
      return lineas;
    }

    /** Devuelve (c_izq, c_der, pendiente, n_lineas). */
    std::tuple<double, double, double, int> elegir(const std::vector<std::array<double, 3>>& lineas) const
    {
      std::optional<std::array<double, 4>> mejor;  // (puntaje, cl, cr, m)
      for(std::size_t a = 0; a < lineas.size(); ++a)
        for(std::size_t b = 0; b < lineas.size(); ++b)
        {
          if(a == b)
            continue;
          const double cl = lineas[a][0], ml = lineas[a][1], nl = lineas[a][2];
          const double cr = lineas[b][0], mr = lineas[b][1], nr = lineas[b][2];
          if(!(cl > 0. && 0. > cr) || std::abs(ml - mr) > .15)
            continue;
          const double m = (ml * nl + mr * nr) / (nl + nr);
          const double err = std::abs((cl - cr) / std::sqrt(1. + m * m) - espaciado);
          if(err > p.tolPar)
            continue;
          const double puntaje = nl + nr - 200. * err;
          if(!mejor || puntaje > (*mejor)[0])
            mejor = std::array<double, 4>{puntaje, cl, cr, m};
        }
      if(mejor)
        return {(*mejor)[1], (*mejor)[2], (*mejor)[3], 2};
      // Una sola linea: la de mas puntos (y mas cercana al centro en empate) dentro de 1.1 carriles.
      const std::array<double, 3>* elegida = nullptr;
      for(const auto& l : lineas)
      {
        if(!(std::abs(l[0]) < espaciado * 1.1))
          continue;
        if(!elegida || l[2] > (*elegida)[2] || (l[2] == (*elegida)[2] && -std::abs(l[0]) > -std::abs((*elegida)[0])))
          elegida = &l;
      }
      if(!elegida)
        return {0., 0., 0., 0};
      const double c = (*elegida)[0], m = (*elegida)[1];
      const double off = espaciado * std::sqrt(1. + m * m);
      if(c > 0.)
        return {c, c - off, m, 1};
      return {c + off, c, m, 1};
    }
  };

  // ---------------------------------------------------------------------------------------- carril B-Human

  /** LaneFilter: Kalman de dos estados (d, psi) que fusiona vision con odometria y acumula el avance s. */
  class LaneFilter
  {
  public:
    double qD = 2e-4, qPsi = 4e-4, qDPorM = 4e-3, qPsiPorM = 1e-2;
    std::array<double, 2> rD = {.015 * .015, .03 * .03};
    std::array<double, 2> rPsi = {std::pow(2. * (pi / 180.), 2.), std::pow(4. * (pi / 180.), 2.)};
    double gateSigma = 3.5;
    int maxRechazos = 6;

    double d = 0., psi = 0., pD = 1., pPsi = 1., s = 0.;
    bool inicializado = false;
    int rechazos = 0;

    void reiniciar()
    {
      d = psi = s = 0.;
      pD = pPsi = 1.;
      inicializado = false;
      rechazos = 0;
    }

    /** dx, dy, dth: desplazamiento del robot en SU marco desde la ultima prediccion. */
    void predecir(double dx, double dy, double dth)
    {
      const double psiMedio = psi + .5 * dth;
      d += dx * std::sin(psiMedio) + dy * std::cos(psiMedio);
      s += dx * std::cos(psiMedio) - dy * std::sin(psiMedio);
      psi += dth;
      const double dist = std::hypot(dx, dy);
      pD += qD + qDPorM * dist;
      pPsi += qPsi + qPsiPorM * dist;
    }

    bool actualizar(const Estimacion& est)
    {
      if(!est.valida)
        return false;
      const std::size_t k = est.nLineas == 2 ? 0 : 1;
      const double rd = rD[k], rp = rPsi[k];
      if(!inicializado)
      {
        d = est.d;
        psi = est.psi;
        pD = rd;
        pPsi = rp;
        inicializado = true;
        return true;
      }
      const double nd = (est.d - d) / std::sqrt(pD + rd);
      const double np = (est.psi - psi) / std::sqrt(pPsi + rp);
      if(std::abs(nd) > gateSigma || std::abs(np) > gateSigma)
      {
        if(++rechazos >= maxRechazos)
        {
          d = est.d;
          psi = est.psi;
          pD = rd;
          pPsi = rp;
          rechazos = 0;
          return true;
        }
        return false;
      }
      rechazos = 0;
      const double kd = pD / (pD + rd), kp = pPsi / (pPsi + rp);
      d += kd * (est.d - d);
      psi += kp * (est.psi - psi);
      pD *= (1. - kd);
      pPsi *= (1. - kp);
      return true;
    }
  };

  /** LaneController: (d, psi) -> (vx, vy, vtheta) normalizados en [-1, 1] (como moveToward de NAOqi). */
  class LaneController
  {
  public:
    double vxMax = 1., vxMin = .35, kPsi = 1.6, kDTheta = 1.2, kDY = 2.5, thetaMax = .45, vyMax = .5;
    double psiLento = 20. * (pi / 180.), dLento = .15, mitadCarril = .35, mitadHuella = .095;

    double margen(double d) const { return mitadCarril - std::abs(d) - mitadHuella; }

    std::array<double, 3> comando(double d, double psi, double confianza = 1.) const
    {
      double theta = -kPsi * psi - kDTheta * d;
      double vy = -kDY * d;
      theta = recortar(theta, -thetaMax, thetaMax);
      vy = recortar(vy, -vyMax, vyMax);
      const double lento = std::max(std::abs(psi) / psiLento, std::abs(d) / dLento);
      double vx = vxMax * (1. - .6 * std::min(1., lento));
      vx *= .6 + .4 * recortar(confianza, 0., 1.);
      vx = recortar(vx, vxMin, vxMax);
      return {vx, vy, theta};
    }
  };
}
