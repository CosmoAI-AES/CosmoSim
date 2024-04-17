---
title: The CosmoAI project
---

This project provides a simulator for gravitational lensing based on
Chris Clarkson's Roulettes framework.
The initial prototype was an undergraduate
[final year project](https://ntnuopen.ntnu.no/ntnu-xmlui/handle/11250/3003634)
by Ingebrigtsen, Remøy, Westbø, Nedreberg, and Austnes (2022).
The software includes both a GUI simulator for interactive experimentation, 
and a command line interface for batch generation of datasets.

The intention is to be able to use the synthetic datasets to train
machine learning models which can in turn be used to map the dark
matter of the Universe.  This is work in progress.

Documentation is being written at 
[https://cosmoai-aes.github.io/](https://cosmoai-aes.github.io/),
but it still incomplete and fragmented.

# Installation Guide

## Running from Precompiled Version in Python

The libraries are built using Github Workflows and packed
as complete Python modules with lirbraries or scripts.
Currently, we build for Python 3.9, 3,10, and 3.11 on Linux,
and for Python 3.10 and 11 on Windows.
MacOS binaries have to be built manually, and may therefore
be less up to date.
The GUI has not been tested on Windows.

1.  Make sure you have one of the supported Python versions
2.  Download and unpack `CosmoSimPy.zip` from 
    [the latest release](https://github.com/CosmoAI-AES/CosmoSim/releases/latest).
    If a MacOS version exists, it is named as such; there is one for 
    [v2.2.2](https://github.com/CosmoAI-AES/CosmoSim/releases/tag/v2.2.2).
3.  Run `CosmoSimPy/CosmoGUI.py` in python.  This is the GUI tool.
4.  The `CosmoSimPy/datagen.py` is the CLI tool and should be run
    on the command line; see below.

The binaries are not signed, and on MacOS you will have to confirm
that you trust the binary before it will run.

## Building from Source

The build procedure is primarily developed on Debian Bullseye, but it now 
also works reliable on github runners running Windows-2019, Ubuntu-20.04,
or Ubuntu 22.04.  We also have it working on MacOS, but we also have problems with other macs, depending on their setup.  We do not have capacity to develop generic and robust build procedures, but we shall be happy to incorporate contributions.

The following instructions are Linux specific.

### Using conan

To install using conan, you can use the build script included,
We require version 1.60.  The setup is not compatible with conan 2.x.
On some architectures version 1.59 works.
You may also have to create a default profile.
(See [Conan Tutorial](https://docs.conan.io/en/latest/getting_started.html)
for further information.)
```sh
pip3 install conan==1.59
conan profile new default --detect
sh build.sh
```
During the process, it will tell you about any missing libraries that have to be installed on the system level.  


If you want to save time on trial and error, you may install the following first
(Debian).
```sh
sudo apt-get install libgtk2.0-dev libva-dev libx11-xcb-dev libfontenc-dev libxaw7-dev libxkbfile-dev libxmuu-dev libxpm-dev libxres-dev libxtst-dev libxvmc-dev libxcb-render-util0-dev libxcb-xkb-dev libxcb-icccm4-dev libxcb-image0-dev libxcb-keysyms1-dev libxcb-randr0-dev libxcb-shape0-dev libxcb-sync-dev libxcb-xfixes0-dev libxcb-xinerama0-dev libxcb-dri3-dev libxcb-util-dev libxcb-util0-dev libvdpau-dev
```

The setup with conan currently works linux with superuser priviliges as of
24-04-08.  Superuser privileges are required to install some dependencies
using the standard package managers.

### Using vcpkg

As an alternative to conan, [vcpkg](https://vcpkg.io/en/index.html) may be used.
To use vcpkg, pass
```
-DCMAKE_TOOLCHAIN_FILE="[path to vcpkg]/scripts/buildsystems/vcpkg.cmake"
-DCOSMOSIM_USE_CONAN=OFF
```
to CMake, e.g.
```
cmake . -B build -DCMAKE_BUILD_TYPE=Release -DCMAKE_TOOLCHAIN_FILE=../vcpkg/scripts/buildsystems/vcpkg.cmake  -DCOSMOSIM_USE_CONAN=OFF 
```

As of 24-04-08 this does not work on linux.  It seems to require a non-existent
package.

> Note: On Windows you need to copy all .dll files from `/lib` into `CosmoSimPy/CosmoSim` in order to get the Python code to work.

### Testing

Once built, an illustrative test set can be generated by
the following command issued from the root directory.
Note that you have to install python dependencies from the requirements
file.  You may want to install python libraries in a virtual environment.
Here this is given to do that in global user space.

```sh
pip3 -r requirements.txt install
mkdir images
python3 CosmoSimPy/datagen.py -CR -Z 400 --csvfile Datasets/debug.csv --directory images
```

This generates a range of images in the newly created images directory. This should be on the .gitignore.

The flags may be changed; `-C` centres det distorted image in the centre
of the image (being debugged); `-Z` sets the image size; `-R` prints an
axes cross.

### N.B: Installation without Dependency managers

If neither conan nor vcpkg can be used, OpenCV and SymEngine must be installed
on the system.  We have set up cmake not to use conan when the
hostname starts with idun`, in which case the idunbuild.sh`
script can be used for installation.  This has been designed
for the NTNU Idun cluster, but can be tweaked for other systems.

## Running the Software 
There are two ways to interact with CosmoSim; through a GUI tool and the CLI.

### GUI

```sh
python3 CosmoSimPy/CosmoGUI.py
```

The GUI tool is hopefully quite self-explanatory.  
The images shown are the actual source on the left and the distorted (lensed)
image on the right.

### Sidenote: Running the GUI through docker 

Docker images have been created to build and run the GUI.
It should be possible to build and run them as follows, assuming a Unix like system.

```sh
cd docker-sim && docker build -t dockergui .
docker run -ti --rm -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix -u $(id -u):$(id -g) cosmogui
```

### CLI

To generate images from specified parameters, you can use
```sh
python3 CosmoSimPy/datagen.py -S sourcemodel -L lensmodel -x x -y y -s sigma -X chi -E einsteinR -n n -I imageSize -N name -R -C
```
Here are the options specified:
+ `lensmodel` is `p` for point mass (exact), `r` for Roulette (point mass),
  or `s` for SIS (Roulette).
+ `sourcemodel` is `s` for sphere, `e` for ellipse, or `t` for
   triangle.
+ `-C` centres the image on the centre of mass (centre of light)
+ `-R` draw the axes cross
+ `x` and `y` are the coordinates of the actual source
+ `s` is the standard deviation of the source
+ `chi` is the distance to the lens in percent of the distance to the source
+ `einsteinR` is the Einstein radius of the lens
+ `n` is the number of terms to use in roulette sum.  
  (Not used for the point mass model.)
+ `imageSize` size of output image in pixels.  The image will be
  `imageSize`$\times$`imageSize` pixels.
+ `name` is the name of the simulation, and used to generate filenames.
+ `--help` for a complete list of options.

Alternatively, you can parse in a csv file to bulk generate images. Parameters which are constant for all images may be given on the 
command line instead of the CSV file.

```sh
python3 CosmoSimPy/datagen.py --csvfile Datasets/debug.csv --mask -R -C
```


The following script creates a CSV file of random parameter sets to use with the `--csvfile` option above.

```
python3 CosmoSimPy/datasetgen.py
```

It should be tweaked to get the desired distribution.


## Use cases

### Training sets for roulette amplitudes

The datasets generated from `datasetgen.py` give the parameters for the 
lens and the source, as well as the image file.
This allows us to train a machine learning model to identify the lens
parameters, *assuming* a relatively simple lens model.
It is still a long way to go to map cluster lenses.

An alternative approach is to try to estimate the effect (lens potential)
in a neighbourhood around a point in the image.  For instance, we may want
to estimate the roulette amplitudes in the centre of the image.
The `datagen.py` script can generate a CSV file containing these data along
with the image, as follows:

```sh
mkdir images
python3 CosmoSimPy/datagen.py -C -Z 400 --csvfile Datasets/debug.csv \
        --directory images --outfile images.csv --nterms 5
```

The images should be centred (`-C`); the amplitudes may not be
meaningful otherwise.  The `--directory` flag puts images in
the given directory which must exist.  The image size is given by
`-Z` and is square.  The input and output files go without saying.
The number of terms (`--nterms`) is the maximum $m$ for which the
amplitudes are generated; 5 should give about 24 scalar values.

The amplitudes are labeled `alpha[`$s$,$m$`]` and `beta[`$s$,$m$`]` 
in the outout CSV file.  One should focus on predicting the amplitudes
for low values of $m$ first.  The file also reproduces the source
parameters, and the centre of mass $(x,y)$ in the original co-ordinate
system using image coordinates with the origin in the upper left corner.

The most interesting lens model for this exercise is PsiFunctionSIS (fs),
which gives the most accurate computations.  The roulette amplitudes have
not been implemented for any of the point mass lenses yet, and it also
does not work for «SIS (rotated)» which is a legacy implementation of
the roulette model with SIS and functionally equivalent to «Roulette SIS«
(rs).

**Warning** This has yet to be tested properly.

## Versions

+ The imortant git branches are
    - develop is the current state of the art
    - master should be the last stable version
+ Releases
    - v-test-* are test releases, used to debug workflows.  Please ignore.
    - see the releases on githun and CHANGELOG.md
+ Prior to v2.0.0 some releases have been tagged, but not registered
as releases in github.
    - v0.1.0, v0.2.0, v1.0.0 are versions made by the u/g students
      Spring 2022.
    - v1.0.1 is cleaned up to be able to build v1.0.0

## Caveats

The simulator makes numerical calculations and there will always
be approximation errors.

1.  The images generated from the same parameters have changed slightly
    between version.  Some changes are because some unfortunate uses of
    integers and single-precision numbers have later been avoided, and some 
    simply because the order of calculation has changed.
1.  The SIS model is implemented in two versions, one rotating
    to have the source on the x-axis and one working directly with
    arbitrary position.  Difference are not perceptible by visual
    comparison, but the difference image shows noticeable difference.


## Contributors

+ **Idea and Current Maintainance** Hans Georg Schaathun <hasc@ntnu.no>
+ **Mathematical Models** Ben David Normann
+ **Initial Prototype** Simon Ingebrigtsen, Sondre Westbø Remøy,
  Einar Leite Austnes, and Simon Nedreberg Runde


## Troubleshooting

### ERROR: Compiler not defined for compiler.libcxx. Please define compiler value first too

This occurs when conan does not correctly set up the default profile. Sometimes the compiler and version fields are missing.

Run:

```
conan profile show default
```
and check (update) these if they are wrong. Check gcc version using gcc --version.
```
conan profile update settings.compiler=gcc default
conan profile update settings.compiler.libcxx=libstdc++11 default
conan profile update settings.compiler.version=<gcc version e.g 11.4> default
```
These are what I used on Ubuntu, but may vary from system to system.
