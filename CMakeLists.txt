# (C) 2022: Hans Georg Schaathun <georg@schaathun.net>


message("CMakeLists.txt - CosmoSim - Starting ...")

cmake_minimum_required(VERSION 3.23)
project(CosmoAi LANGUAGES CXX VERSION 1.1.0)

include(FetchContent)
FetchContent_Declare( pybind11
      GIT_REPOSITORY https://github.com/pybind/pybind11.git
      GIT_TAG        v3.0.0
      )
FetchContent_MakeAvailable(pybind11)
add_subdirectory("${pybind11_SOURCE_DIR}")

FetchContent_Declare( symengine
      GIT_REPOSITORY https://github.com/symengine/symengine.git
      GIT_TAG        v0.14.0
      )
FetchContent_MakeAvailable(symengine)
add_subdirectory("${symengine_SOURCE_DIR}")

find_library(gmp gmp)
find_package(OpenCV CONFIG REQUIRED)
find_package(SymEngine CONFIG REQUIRED)
find_package(Python COMPONENTS Development Interpreter)

message("OpenCV_LIBS=${OpenCV_LIBS}")

option(COSMOSIM_BUILD_SIMULATOR "Build native cosmosim simulator executable" OFF)
option(COSMOSIM_BUILD_MAKEIMAGE "Build native cosmosim makeimage executable" OFF)

set(CMAKE_CXX_STANDARD 17)

# Place target artifacts into bin and lib folders
set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/lib)
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/lib)
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)


cmake_host_system_information(RESULT host QUERY HOSTNAME)
message("Running on ${host}")

add_subdirectory(src)

if(${UNIX})
    set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} -Wl,-z,stack-size=1000000")
elseif(${MSVC})
    set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} /STACK:10000000")
else()
    message(FATAL_ERROR "Compiler and system are not supported")
endif()

message("Cross-Compile Options: ${CROSS_COMPILE}")
add_compile_options(${CROSS_COMPILE})

