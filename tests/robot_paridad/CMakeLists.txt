cmake_minimum_required(VERSION 3.17)
project(CarreraParidad LANGUAGES CXX)

# Paridad en el PC del encabezado que corre en el NAO (sin dependencias de B-Human).
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

add_executable(carrera_paridad main.cpp)
target_include_directories(carrera_paridad PRIVATE
  "${CMAKE_CURRENT_SOURCE_DIR}/../../bhuman/Src"
  "${CMAKE_CURRENT_SOURCE_DIR}")
if(MSVC)
  target_compile_options(carrera_paridad PRIVATE /W4 /permissive- /EHsc /bigobj)
else()
  target_compile_options(carrera_paridad PRIVATE -Wall -Wextra -Wconversion -Wno-sign-conversion)
endif()
