all: sis50.txt sie05.txt pm50.txt

sis: sis100.txt sis50.txt sis200.txt
sis100.txt sis50.txt sie05.txt:

P=../../python/

%.txt: %.raw
	sort $< > $@

sis%.raw:  $P/amplitudes.py
	time python3 $< --output $@ $* 8
pm%.raw:  $P/amplitudes.py
	time python3 $< --lens PM --output $@ $* 8

sie%.raw: $P/sieamplitudes.py 
	time python3 $< --output $@ $* 7
sie%.tex: $P/sieamplitudes.py 
	time python3 $< --tex $@ $* 7

%.pdf: %.tex
	pdflatex $<

clean:
	rm -f *.log *.raw
cleanall: clean
	rm -f *.txt
