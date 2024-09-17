#! /bin/sh

. ../../pythonenv/bin/activate


opt=$*

echo Options: "$*"

make all

( sh clean.sh &&
  sh sie.sh $opt 
  ) | tee tutti.log
