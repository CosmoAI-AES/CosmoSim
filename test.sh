#! /bin/sh

dir=$1
test $dir || dir=Test/`date "+%Y%m%d"`
mkdir -p $dir

python3 Python/datagen.py --directory="$dir" --csvfile Datasets/debug.csv 
python3 Python/compare.py Tests/v2.0.2 $dir
