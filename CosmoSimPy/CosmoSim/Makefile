all: sis100.txt sis50.txt sie05.txt

sis: sis100.txt sis50.txt sis200.txt
sis100.txt sis50.txt sie05.txt:

%.txt: %.raw
	sort $< > $@

sis%.raw:  ../amplitudes.py
	time python3 $< --output $@ $* 8

sie%.raw: ../sieamplitudes.py 
	time python3 $< --output $@ $* 7
sie%.tex: ../sieamplitudes.py 
	time python3 $< --tex $@ $* 7

siesis%.raw: ../sieamplitudes.py 
	time python3 $< --lens SIS --output $@ $* 8
sieorig%.raw: ../sieorig.py 
	time python3 $< --lens SIS --output $@ $* 8


sierecursive%.raw:  ../amplitudes.py
	time python3 $< --lens SIE --output $@ $* 8

%.pdf: %.tex
	pdflatex $<

clean:
	rm -f *.log *.raw
cleanall: clean
	rm -f *.txt
