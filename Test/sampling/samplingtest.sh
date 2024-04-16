#! /bin/sh

( cd ../.. && cmake --build build ) || exit 1

opt=$*

pdir=../../CosmoSimPy
dir1=SampledSIS
# dir2=RouletteSIS
dir2=SIS
diffdir=diff

mkdir -p $dir1 $dir2 $diffdir

fn=../spheres.csv

python3 $pdir/datagen.py $opt --config "Sampled Raytrace SIS" --directory="$dir1" --csvfile $fn 
python3 $pdir/datagen.py $opt --config "Raytrace SIS" --directory="$dir2" --csvfile $fn 
python3 $pdir/compare.py --diff $diffdir $dir1 $dir2

