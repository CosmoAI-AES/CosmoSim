#! /bin/sh

. ../../pythonenv/bin/activate

( sh clean.sh &&
  sh sie.sh &&
  sh compare.sh ) | tee tutti.log
