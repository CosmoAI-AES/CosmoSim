#! /bin/sh

( cd ../.. && cmake --build build ) || exit 1

opt=$*

pdir=../../CosmoSimPy
dir1=SampledSIS
dir2=SIS
diffdir=diff

mkdir -p $dir1 $dir2 $diffdir

fn=sie.csv

python3 $pdir/datagen.py $opt --config "Sampled Raytrace SIS" --directory="$dir1" --csvfile $fn  --actual
python3 $pdir/datagen.py $opt --config "Raytrace SIS" --directory="$dir2" --csvfile $fn 

rm -rf Actual
mkdir -p Actual
mv */actual*png Actual

python3 $pdir/compare.py --diff $diffdir $dir1 $dir2

CONVERT=convert
mkdir -p montageSIS

for f in diff/*
do
  ff=`basename $f`
  $CONVERT \( Actual/actual-$ff SIS/$ff +append \) \( SampledSIS/$ff $diffdir/$ff +append \) -append montageSIS/$ff
done
