all: sis10.txt chris10.txt bd10.txt

sis10.txt chris10.txt bd10.txt:

%.txt: %.raw
	sort $< > $@

sis%.raw:  ../amplitudes.py
	time python3 $< --output $@ $* 8

chris%.raw: ../sieamplitudes.py 
	time python3 $< --lens SIS --output $@ $* 8

chris%.tex: ../sieamplitudes.py 
	time python3 $< --lens SIS --tex $@ $* 8

bd%.raw: ../sieorig.py 
	time python3 $< --lens SIS --output $@ $* 8

bd%.tex: ../sieorig.py 
	time python3 $< --lens SIS --tex $@ $* 8


%.pdf: %.tex
	pdflatex $<
