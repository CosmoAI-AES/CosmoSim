#!/bin/sh

pyd=../../CosmoSimPy

mkdir -p Original Roulette diff montage

# python3 ./datasetgen.py

python3 $pyd/datagen.py -Z 600 --csvfile dataset.csv --outfile roulette.csv \
   --model Roulette --xireference -D Original --actual  -R --nterms 9

python3 $pyd/roulettegen.py -n 10 -Z 600 --csvfile roulette.csv --xireference -D Roulette -R --nterms 9

mkdir -p Actual
mv Original/actual-* Actual

python3 $pyd/roulettestatistics -o roulette.tex roulette.csv
