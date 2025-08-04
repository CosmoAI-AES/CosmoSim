# (C) 2023: Hans Georg Schaathun <georg@schaathun.net> 

all: sie05.status sis50.status

sie05.new sis50.new:
sie05.baseline:
sis50.baseline:

P=../../python

%.baseline: ../../src/CosmoSim/%.txt
	sort $< > $@
%.new: %.txt
	sort $< > $@
sis%.txt:
	echo $*
	python3 $P/amplitudes.py --output $@ --lens SIS $* 
sie%.txt:
	python3 $P/sieamplitudes.py --output $@ --lens SIE $* 
%.status: %.new %.baseline
	diff $^ && echo Regression test passes > $@

clean:
	rm -f 50.* *.txt *.new

alltests: all
