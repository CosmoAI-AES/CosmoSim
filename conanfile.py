
from conan import ConanFile
from conan.tools.cmake import cmake_layout


class CosmoSimConan(ConanFile):
    name = "CosmoSim"
    license = "MIT"

    settings = "os", "compiler", "build_type", "arch"
    generators = "CMakeToolchain", "CMakeDeps"

    def requirements(self):
        self.requires( "symengine/0.11.2" )
        self.requires( "opencv/4.11.0" )

    def layout(self):
        cmake_layout(self)

