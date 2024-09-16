#! /bin/sh

( cd ../.. && cmake --build build ) || exit 1

opt=$*

pdir=../../CosmoSimPy/
fn=sis.csv

configlist="ss pss fs rs"
# configlist='"Sampled Roulette SIS" "Sampled Raytrace SIS" "Roulette SIS" "Raytrace SIS"'


for dir in $configlist
do
   echo "Testing" $dir
   mkdir -p $dir actual-$dir
   python3 $pdir/datagen.py $opt --config "$dir" --directory="$dir" --csvfile $fn  --actual -R
   mv $dir/actual*png actual-$dir
done


