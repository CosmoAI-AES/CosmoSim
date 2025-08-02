FROM quay.io/pypa/manylinux_2_28_x86_64

RUN yum update && yum install -y python3-pip 
RUN python3.13 -m pip install build

RUN yum -y install libva-devel libvdpau-devel xkeyboard-config-devel libfontenc-devel libXaw-devel libXcomposite-devel libXcursor-devel libXdmcp-devel libXtst-devel libXinerama-devel libxkbfile-devel libXrandr-devel libXres-devel libXScrnSaver-devel xcb-util-wm-devel xcb-util-image-devel xcb-util-keysyms-devel xcb-util-renderutil-devel libXdamage-devel libXxf86vm-devel libXv-devel xcb-util-devel libuuid-devel xcb-util-cursor-devel 

WORKDIR /
RUN git clone -b develop https://github.com/CosmoAI-AES/CosmoSim.git

