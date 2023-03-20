#! /bin/sh

dir=$1
test $dir || dir=Test/sampled`date "+%Y%m%d"`
mkdir -p $dir

fn=/tmp/ts.csv 

cat > $fn <<EOF
index,filename,source,lens,chi,x,y,einsteinR,sigma,sigma2,theta,nterms
"ss15",image-ss15.png,t,ss,50,10,10,7,20,0,115,16
"ss16",image-ss16.png,t,ss,50,50,50,7,20,0,115,16
"ss17",image-ss16.png,t,ss,50,50,50,20,20,0,115,16
EOF

python3 Python/datagen.py --directory="$dir" --csvfile $fn --actual --apparent --reflines
