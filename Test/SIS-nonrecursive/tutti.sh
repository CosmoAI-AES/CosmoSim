#! /bin/sh

. ../../pythonenv/bin/activate


opt=$*

echo Options: "$*"

make all

( sh clean.sh &&
  sh sis.sh $opt 
  ) | tee tutti.log
