from skbuild_conan import setup
from setuptools import find_packages
setup(  # https://scikit-build.readthedocs.io/en/latest/usage.html#setup-options
    name="CosmoSim",
    version="2.5.3",
    packages=find_packages("src"),  # Include all packages in `./src`.
    # packages=[ "CosmoSim", "CosmoSim/CosmoSimPy" ],
    description="Simulator of Gravitational Lenses",
    author='Hans Georg Schaathun et al',
    license="MIT",
    python_requires=">=3.10",
    package_dir={"": "src"},  # The root for our python package is in `./src`.
    install_requires=["sympy>=1.13", "numpy", "matplotlib", "opencv-python", "pandas"],  # Python Dependencies
    include_package_data=True,
    conan_requirements=[ "symengine/0.14.0", "opencv/4.12.0" ],  # C++ Dependencies
    cmake_minimum_required_version="3.15",
    cmake_install_dir="src/",
    package_data={ "CosmoSim" : [ "*.txt", "*.png", "*.so", "*.pyd" ] },
)

