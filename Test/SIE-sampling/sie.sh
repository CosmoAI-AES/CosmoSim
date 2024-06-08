#! /bin/sh

( cd ../.. && cmake --build build ) || exit 1

opt=$*

pdir=../../CosmoSimPy
dir1=SampledSIE
dir2=SIE
diffdir=diff

mkdir -p $dir1 $dir2 $diffdir

fn=sie.csv

python3 $pdir/datagen.py $opt --config "Sampled Raytrace SIE" --directory="$dir1" --csvfile $fn  --actual
python3 $pdir/datagen.py $opt --config "Raytrace SIE" --directory="$dir2" --csvfile $fn 

rm -rf Actual
mkdir -p Actual
mv */actual*png Actual

python3 $pdir/compare.py --diff $diffdir $dir1 $dir2

CONVERT=convert
mkdir -p montage

for f in diff/*
do
  ff=`basename $f`
  $CONVERT \( Actual/actual-$ff SIE/$ff +append \) \( SampledSIE/$ff diff/$ff +append \) -append montage/$ff
done
