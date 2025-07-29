from skbuild_conan import setup
from setuptools import find_packages
setup(  # https://scikit-build.readthedocs.io/en/latest/usage.html#setup-options
    name="CosmoSim",
    version="2.5.3",
    packages=find_packages("CosmoSimPy"),  # Include all packages in `./src`.
    description="Simulator of Gravitational Lenses",
    author='Hans Georg Schaathun et al', email="hasc@ntnu.no" },
    license="MIT",
    python_requires=">=3.10",
    package_dir={"": "CosmoSimPy"},  # The root for our python package is in `./src`.
    install_requires=["sympy>=1.13", "numpy", "matplotlib", "opencv-python", "pandas"],  # Python Dependencies
    conan_requirements=["symengine/0.11.2", "opencv/4.11.0", "xz_utils/5.4.5", "zlib/1.2.13" ],  # C++ Dependencies
    cmake_minimum_required_version="3.23",
)


        
# if self.settings.os == "Linux": self.requires("wayland/1.22.0")
