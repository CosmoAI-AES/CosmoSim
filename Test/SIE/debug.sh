#! /bin/sh

( cd ../.. && cmake --build build ) || exit 1

opt=$*

pdir=../../CosmoSimPy
dir1=SampledSIE
dir2=SIE
diffdir=diff

mkdir -p $dir1 $dir2 $diffdir

fn=test.csv

python3 $pdir/datagen.py $opt --config "Sampled Raytrace SIE" --directory="$dir1" --csvfile $fn 
