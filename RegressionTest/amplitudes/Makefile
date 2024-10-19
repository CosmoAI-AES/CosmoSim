# (C) 2023: Hans Georg Schaathun <georg@schaathun.net> 

all: sie05.status sis50.status

sie05.new sis50.new:
sie05.baseline:
sis50.baseline:

%.baseline: ../../CosmoSimPy/CosmoSim/%.txt
	sort $< > $@
%.new: %.txt
	sort $< > $@
sis%.txt:
	python3 ../../CosmoSimPy/amplitudes.py --output $@ --lens SIS $* 16
sie%.txt:
	python3 ../../CosmoSimPy/sieamplitudes.py --output $@ --lens SIE $* 16
%.status: %.new %.baseline
	diff $^ && echo Regression test passes > $@

clean:
	rm -f 50.* *.txt *.new

alltests: all
