
message("CMakeLists.txt - CosmoSim - Starting ...")

cmake_minimum_required(VERSION 3.15)
project(CosmoAi CXX)

add_definitions("-std=c++11")

cmake_host_system_information(RESULT host QUERY HOSTNAME)
# set(host "foobar")
message("Running on ${host}")

if( ${host} MATCHES "idun.*")
	set(LLIBS "symengine;opencv_ml;opencv_photo;opencv_highgui;opencv_videoio;opencv_imgcodecs;opencv_stitching;opencv_dnn;opencv_objdetect;opencv_gapi;opencv_video;opencv_calib3d;opencv_features2d;opencv_flann;opencv_imgproc;opencv_core;gmpxx;gmp;jasper;tiffxx;tiff;avdevice;avfilter;avformat;avcodec;swscale;swresample;postproc;avutil;protoc;protobuf;jpeg;lzma;jbig;zstd;webpdemux;webpmux;webp;freetype;x264;x265;mp3lame;png;bz2;brotlidec-static;brotlienc-static;brotlicommon-static;ssl;crypto;wayland-server;wayland-cursor;wayland-egl;wayland-client;FLAC++;FLAC;ffi;xml2;expat;z;ogg;gtk-x11-2.0;gdk-x11-2.0;pangocairo-1.0;atk-1.0;cairo;gdk_pixbuf-2.0;gio-2.0;pangoft2-1.0;pango-1.0;gobject-2.0;glib-2.0;harfbuzz;fontconfig;freetype;stdc++;X11;X11-xcb;xcb;fontenc;ICE;SM;Xau;Xaw7;Xt;Xcomposite;Xcursor;Xdamage;Xfixes;Xdmcp;Xext;Xi;Xinerama;xkbfile;Xmu;Xmuu;Xpm;Xrandr;Xrender;XRes;Xss;Xtst;Xv;XvMC;Xxf86vm;xcb-xkb;xcb-icccm;xcb-image;xcb-shm;xcb-keysyms;xcb-randr;xcb-render;xcb-render-util;xcb-shape;xcb-sync;xcb-xfixes;xcb-xinerama;xcb-util;xcb-dri3;uuid;rt;dl;m;pthread")
else()
      include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
      conan_basic_setup()
endif()

add_executable(makeimage src/makeimage.cpp)
add_executable(Simulator src/Simulator.cpp)
add_library(SimLib 
   src/simaux.cpp 
   src/Source.cpp src/SphericalSource.cpp src/EllipsoidSource.cpp
   src/TriangleSource.cpp
   src/LensModel.cpp src/PointMassLens.cpp src/SphereLens.cpp 
   src/RoulettePMLens.cpp
   src/Window.cpp)

message("CONAN_LIBS=${CONAN_LIBS}")
message("LLIBS=${LLIBS}")

target_link_libraries(makeimage ${LLIBS} ${CONAN_LIBS} SimLib)
target_link_libraries(Simulator ${LLIBS} ${CONAN_LIBS} SimLib)
target_link_libraries(SimLib ${LLIBS} ${CONAN_LIBS})

if(${UNIX})
    set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} -Wl,-z,stack-size=1000000")
elseif(${MSVC})
    set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} /STACK:10000000")
else()
    message(FATAL_ERROR "Compiler and system are not supported")
endif()
