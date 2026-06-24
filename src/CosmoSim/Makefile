all: sis100.txt sis50.txt sie05.txt

sis: sis100.txt sis50.txt sis200.txt
sis100.txt sis50.txt sie05.txt:

P=./Roulettes

%.txt: %.raw
	sort $< > $@

sis%.raw:  $P/__main__.py
	time python3 $< --output $@ $* 8
pm%.raw:  $P/__main__.py
	time python3 $< --lens PM --output $@ $* 8

sie%.raw: $P/sie.py 
	time python3 $< --output $@ $* 7
sie%.tex: $P/sie.py 
	time python3 $< --tex $@ $* 7

%.pdf: %.tex
	pdflatex $<

clean:
	rm -f *.log *.raw
cleanall: clean
	rm -f *.txt
