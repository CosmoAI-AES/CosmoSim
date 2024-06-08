#! /bin/sh

( cd ../.. && cmake --build build ) || exit 1

opt=$*

pdir=../../CosmoSimPy/
fn=debug.csv

configlist="ss pss fs rs"
# configlist='"Sampled Roulette SIS" "Sampled Raytrace SIS" "Roulette SIS" "Raytrace SIS"'


for dir in $configlist
do
   echo "Testing" $dir
   mkdir -p $dir
   python3 $pdir/datagen.py $opt --config "$dir" --directory="$dir" --csvfile $fn  --actual
done
