#! /bin/sh

echo Running: $0
bindir=`dirname $0`
echo Running from $bindir

CONVERT=convert
mkdir -p montage

if test -z "$CONVERT"
then
     echo ImageMagick is not installed 
     exit 6 
elif test ! -d SampledSIE 
then 
   echo $baseline does not exist 
   exit 5 
elif test ! -d SIE
then 
   echo Images have not been 
   exit 5 
elif test ! -d diff
then 
   echo Difference images have not been 
   exit 5 
else
    for f in diff/*
    do
          ff=`basename $f`
	  $CONVERT \( Actual/actual-$ff SIE/$ff +append \) \( SampledSIE/$ff diff/$ff +append \) -append montage/$ff
    done
fi
