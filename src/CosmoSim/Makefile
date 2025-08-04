all: sis100.txt sis50.txt sie05.txt

sis: sis100.txt sis50.txt sis200.txt
sis100.txt sis50.txt sie05.txt:

P=../../python/

%.txt: %.raw
	sort $< > $@

sis%.raw:  $P/amplitudes.py
	time python3 $< --output $@ $* 8

sie%.raw: $P/sieamplitudes.py 
	time python3 $< --output $@ $* 7
sie%.tex: $P/sieamplitudes.py 
	time python3 $< --tex $@ $* 7

siesis%.raw: $P/sieamplitudes.py 
	time python3 $< --lens SIS --output $@ $* 8
sieorig%.raw: $P/sieorig.py 
	time python3 $< --lens SIS --output $@ $* 8


sierecursive%.raw:  $P/amplitudes.py
	time python3 $< --lens SIE --output $@ $* 8

%.pdf: %.tex
	pdflatex $<

clean:
	rm -f *.log *.raw
cleanall: clean
	rm -f *.txt
