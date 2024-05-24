#! /bin/sh

pdir=../../CosmoSimPy
dir1=RaytraceSIS
dir2=RouletteSIS
diffdir=diff

mkdir -p $dir1 $dir2 $diffdir

fn=../spheres.csv

python3 $pdir/datagen.py --model Raytrace --lens SIS --directory="$dir1" --csvfile $fn 
python3 $pdir/datagen.py --model Roulette --lens SIS --directory="$dir2" --csvfile $fn 
python3 $pdir/compare.py --diff $diffdir $dir1 $dir2

./montageimages.sh $dir1 $dir2 $diffdir  | tee montage.log
