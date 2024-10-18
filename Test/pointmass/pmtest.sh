#! /bin/sh

( cd ../.. && cmake --build build )

. ../../pythonenv/bin/activate

pdir=../../CosmoSimPy
dir1=Exact
dir2=Raytrace
diffdir=diff

mkdir -p $dir1 $dir2 $diffdir montage

fn=../spheres.csv

python3 $pdir/datagen.py --config p --directory="$dir1" --csvfile $fn  
python3 $pdir/datagen.py --lens PM --model Raytrace --directory="$dir2" --csvfile $fn  --actual 
python3 $pdir/compare.py --diff $diffdir $dir1 $dir2

mkdir -p actual
mv "$dir2"/actual-* actual/

for f in diff/*
do
  ff=`basename $f`
  convert \( actual/actual-$ff "$dir1"/$ff +append \) \( "$dir2"/$ff diff/$ff +append \) -append montage/$ff
done
