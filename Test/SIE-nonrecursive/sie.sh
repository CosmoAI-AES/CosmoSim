#! /bin/sh

( cd ../.. && cmake --build build ) || exit 1

opt=$*

pdir=../../CosmoSimPy/
fn=../sie.csv
CONVERT=convert


mkdir -p actual-raysie raysie chris bd montage-chris montage-bd diff-chris diff-bd diff2 montage2

python3 $pdir/datagen.py $opt --config raysie --directory="raysie" --csvfile $fn  --actual -R 

mv raysie/actual-* actual-raysie/

python3 $pdir/datagen.py $opt --config rousie --directory="chris" --csvfile $fn   -R -F chris5.txt --nterms 5
python3 $pdir/datagen.py $opt --config rousie --directory="bd" --csvfile $fn   -R -F bd5.txt --nterms 5

python3 $pdir/compare.py --diff diff-bd    bd raysie
python3 $pdir/compare.py --diff diff-chris chris raysie
python3 $pdir/compare.py --diff diff2 chris bd

for f in diff-bd/*
do
  ff=`basename $f`
  $CONVERT \( actual-raysie/actual-$ff bd/$ff +append \) \( raysie/$ff diff-bd/$ff +append \) -append montage-bd/$ff
done

for f in diff-chris/*
do
  ff=`basename $f`
  $CONVERT \( actual-raysie/actual-$ff chris/$ff +append \) \( raysie/$ff diff-chris/$ff +append \) -append montage-chris/$ff
done

for f in diff2/*
do
  ff=`basename $f`
  $CONVERT \( actual-raysie/actual-$ff chris/$ff +append \) \( bd/$ff diff2/$ff +append \) -append montage2/$ff
done

