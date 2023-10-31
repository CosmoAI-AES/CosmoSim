for FILE in Datasets/Batch/*; 

do 

echo $FILE;

python3 CosmoSimPy/datagen.py -CR -Z 400 --csvfile $FILE --directory images

done