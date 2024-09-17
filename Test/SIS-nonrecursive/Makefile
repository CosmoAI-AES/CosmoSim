all: chris5.txt bd5.txt

PD=../../CosmoSimPy/

sis5.txt chris5.txt bd5.txt:

%.txt: %.raw
	sort $< > $@

sis%.raw:  $(PD)amplitudes.py
	time python3 $< --output $@ $* 8

chris%.raw: $(PD)sieamplitudes.py 
	time python3 $< --lens SIS --output $@ $* 8

chris%.tex: $(PD)sieamplitudes.py 
	time python3 $< --lens SIS --tex $@ $* 8

bd%.raw: $(PD)sieorig.py 
	time python3 $< --lens SIS --output $@ $* 8

bd%.tex: $(PD)sieorig.py 
	time python3 $< --lens SIS --tex $@ $* 8


%.pdf: %.tex
	pdflatex $<
