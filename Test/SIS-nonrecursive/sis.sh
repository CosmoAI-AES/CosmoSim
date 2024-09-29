#! /bin/sh

( cd ../.. && cmake --build build ) || exit 1

opt=$*

pdir=../../CosmoSimPy/
fn=../sis.csv
CONVERT=convert


mkdir -p actual-rs rs chris bd montage-chris montage-bd diff-chris diff-bd

python3 $pdir/datagen.py $opt --config rs --directory="rs" --csvfile $fn  --actual -R 

mv rs/actual-* actual-rs/

python3 $pdir/datagen.py $opt --config fs --directory="chris" --csvfile $fn   -R -F chris7.txt --nterms 5
python3 $pdir/datagen.py $opt --config fs --directory="bd" --csvfile $fn   -R -F bd7.txt --nterms 5

python3 $pdir/compare.py --diff diff-bd    bd rs
python3 $pdir/compare.py --diff diff-chris chris rs

for f in diff-bd/*
do
  ff=`basename $f`
  $CONVERT \( actual-rs/actual-$ff bd/$ff +append \) \( rs/$ff diff-bd/$ff +append \) -append montage-bd/$ff
done

for f in diff-chris/*
do
  ff=`basename $f`
  $CONVERT \( actual-rs/actual-$ff chris/$ff +append \) \( rs/$ff diff-chris/$ff +append \) -append montage-chris/$ff
done

