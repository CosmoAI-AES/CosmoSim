#! /bin/sh

( cd ../.. && cmake --build build ) || exit 1

opt=$*

pdir=../../CosmoSimPy/

# Note, origin.csv specifies scenarioes with the almost source at the origin.

configlist="srousie sraysie rousie raysie"
# configlist='"Sampled Roulette SIS" "Sampled Raytrace SIS" "Roulette SIS" "Raytrace SIS"'

mkdir -p cluster

python3 $pdir/datagen.py $opt --model Raytrace --csvfile ../cluster.csv --directory=cluster --actual -R 
