from skbuild import setup  # This line replaces 'from setuptools import setup'
setup(
    name="CosmoSim",
    version="2.5.3",
    description="Simulator of Gravitational Lenses",
    author='Hans Georg Schaathun et al', email="hasc@ntnu.no" },
    license="MIT",
    packages=['CosmoSim'],
    python_requires=">=3.10",
)
