#! /bin/bash


opt=$*

pdir=../../CosmoSimPy

configlist="ss pss fs rs"
CONVERT=convert


mkdir -p {diff,montage}-{roulette,raytrace,compare}
python3 $pdir/compare.py --diff diff-roulette fs ss
python3 $pdir/compare.py --diff diff-raytrace rs pss
python3 $pdir/compare.py --diff diff-compare fs rs



for f in diff-roulette/*
do
  ff=`basename $f`
  $CONVERT \( actual-ss/actual-$ff fs/$ff +append \) \( ss/$ff diff-roulette/$ff +append \) -append montage-roulette/$ff
done

for f in diff-raytrace/*
do
  ff=`basename $f`
  $CONVERT \( actual-pss/actual-$ff rs/$ff +append \) \( pss/$ff diff-roulette/$ff +append \) -append montage-roulette/$ff
done
for f in diff-compare/*
do
  ff=`basename $f`
  $CONVERT \( actual-fs/actual-$ff rs/$ff +append \) \( fs/$ff diff-roulette/$ff +append \) -append montage-roulette/$ff
done
