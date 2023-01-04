# (C) 2022: Hans Georg Schaathun <georg@schaathun.net>


message("CMakeLists.txt - CosmoSim - Starting ...")

cmake_minimum_required(VERSION 3.15)
project(CosmoAi LANGUAGES CXX VERSION 1.1.0)

set(CMAKE_CXX_STANDARD 11)

set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/lib)

cmake_host_system_information(RESULT host QUERY HOSTNAME)
# set(host "foobar")
message("Running on ${host}")

# Symengine and OpenCV
if (${host} MATCHES "idun.*")
    message("IDUN - conan is not available")
    set(LLIBS "symengine;gmp;mpfr;pthread")

    find_package(OpenCV REQUIRED)
    include_directories(${OpenCV_INCLUDE_DIRS})

    message("LLIBS=${LLIBS}")
    message("OpenCV_LIBS=${OpenCV_LIBS}")
else ()
    find_package(OpenCV CONFIG REQUIRED)
    find_package(SymEngine CONFIG REQUIRED)
    find_package(pybind11 CONFIG REQUIRED)
endif ()

add_subdirectory(src)

if (${UNIX})
    set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} -Wl,-z,stack-size=1000000")
elseif (${MSVC})
    set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} /STACK:10000000")
else ()
    message(FATAL_ERROR "Compiler and system are not supported")
endif ()
