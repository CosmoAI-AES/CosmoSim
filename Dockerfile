FROM  cosmosim

RUN apt-get update
RUN apt-get install -y \
     python3 python3-tk  \
     python3-pil python3-numpy python3-opencv \
     pybind11-dev libboost-python-dev \
     python3-pil.imagetk

WORKDIR /CosmoSim/Python/

RUN /usr/bin/python3 --version
RUN ls -l CosmoSim

USER user
CMD /usr/bin/python3 CosmoGUI.py
