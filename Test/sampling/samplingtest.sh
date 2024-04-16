#! /bin/sh

( cd ../.. && cmake --build build ) || exit 1

opt=$*

pdir=../../CosmoSimPy
dir1=SampledSIS
# dir2=RouletteSIS
dir2=SIS
diffdir=diff

rm -rf Actual
mkdir -p $dir1 $dir2 $diffdir Actual

fn=../spheres.csv

python3 $pdir/datagen.py $opt --config "Sampled Raytrace SIS" --directory="$dir1" --csvfile $fn   --actual

mv SampledSIS/actual* Actual/
python3 $pdir/datagen.py $opt --config "Raytrace SIS" --directory="$dir2" --csvfile $fn 
python3 $pdir/compare.py --diff $diffdir $dir1 $dir2

CONVERT=convert
mkdir -p montage

for f in diff/*
do
  ff=`basename $f`
  $CONVERT \( Actual/actual-$ff SIS/$ff +append \) \( SampledSIS/$ff diff/$ff +append \) -append montage/$ff
done
