
from conan import ConanFile

class CosmoSimConan(ConanFile):
    name = "CosmoSim"
    license = "MIT"

    settings = "os", "compiler", "build_type", "arch"
    generators = "CMakeToolchain", "CMakeDeps"

    def requirements(self):
        self.requires( "symengine/0.11.2" )
        self.requires( "opencv/4.11.0" )
        self.requires( "xz_utils/5.4.5" )
        self.requires( "zlib/1.2.13" )
        if self.settings.os == "Linux":
            self.requires("wayland/1.22.0")
