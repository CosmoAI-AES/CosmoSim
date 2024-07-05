#! /bin/sh

pyd=../../CosmoSimPy
mkdir Raytrace
python3 $pyd/datagen.py -Z 600 --csvfile dataset.csv \
   --model Raytrace --lens SIS --xireference -D Raytrace  -R 
