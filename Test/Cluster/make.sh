#! /bin/sh

( cd ../.. && cmake --build build ) || exit 1

opt=$*

pdir=../../CosmoSimPy/
fn=../sie.csv
# Note, origin.csv specifies scenarioes with the almost source at the origin.

configlist="srousie sraysie rousie raysie"
# configlist='"Sampled Roulette SIS" "Sampled Raytrace SIS" "Roulette SIS" "Raytrace SIS"'

mkdir -p singleton reference diff actual montage

python3 $pdir/datagen.py $opt --model Raytrace --csvfile singleton.csv --directory=singleton --actual -R 
python3 $pdir/datagen.py $opt --model Raytrace --csvfile reference.csv --directory=reference -R 

python3 $pdir/compare.py --diff diff singleton reference

mv singleton/actual* actual

for f in diff/*
do
  ff=`basename $f`
  convert \( actual/actual-$ff singleton/$ff +append \) \( reference/$ff diff/$ff +append \) -append montage/$ff
done

