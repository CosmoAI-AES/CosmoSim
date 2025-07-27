
set(SimLibFiles
        simlib/SampledLens.cpp
        simlib/SampledPsiFunctionLens.cpp
        simlib/Lens.cpp
	simlib/ClusterLens.cpp
        simlib/PsiFunctionLens.cpp
        simlib/SIS.cpp
        simlib/SIE.cpp
        simlib/RaytraceModel.cpp
        simlib/RouletteModel.cpp
        simlib/RotatedModel.cpp
        simlib/EllipsoidSource.cpp
        simlib/ImageSource.cpp
        simlib/SimulatorModel.cpp
        simlib/PointMass.cpp
        simlib/PointMassExact.cpp
        simlib/PointMassRoulette.cpp
        simlib/RouletteRegenerator.cpp
        simlib/simaux.cpp
        simlib/Source.cpp
        simlib/SphericalSource.cpp
        simlib/TriangleSource.cpp
        simlib/SourceConstellation.cpp
        )
     # Currently unused:
     #    simlib/LensMap.cpp
     #    simlib/PMCLens.cpp

add_library(SimLib ${SimLibFiles})
set_target_properties(SimLib PROPERTIES POSITION_INDEPENDENT_CODE ON)
target_include_directories(SimLib PUBLIC BEFORE "${CMAKE_SOURCE_DIR}/include" ${pybind11_INCLUDE_DIRS})
target_link_libraries(SimLib ZLIB::ZLIB ${OpenCV_LIBS} symengine)

# Python Bindings
pybind11_add_module(CosmoSimPy MODULE cosmosimpy/bindings.cpp cosmosimpy/CosmoSim.cpp )
target_link_libraries(CosmoSimPy PRIVATE SimLib)


# copy CosmoSimPy.*.pyd into Python directory
add_custom_command(TARGET CosmoSimPy POST_BUILD
   COMMAND ${CMAKE_COMMAND} -E copy $<TARGET_FILE:CosmoSimPy> "${CMAKE_SOURCE_DIR}/CosmoSimPy/CosmoSim"
        )
