#! /bin/sh

pdir=../../CosmoSimPy
dir1=RaytraceSIE
dir2=RouletteSIE
diffdir=diff

mkdir -p $dir1 $dir2 $diffdir

fn=sie.csv

python3 $pdir/datagen.py --model Raytrace --lens SIE --directory="$dir1" --csvfile $fn 
python3 $pdir/datagen.py --model Roulette --lens SIE --directory="$dir2" --csvfile $fn 
python3 $pdir/compare.py --diff $diffdir $dir1 $dir2

./montageimages.sh $dir1 $dir2 $diffdir  | tee montage.log
