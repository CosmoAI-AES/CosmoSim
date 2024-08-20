all: 100.txt 200.txt 50.txt sie05.txt


%.txt: %.raw
	sort $< > $@
sis%.raw:  ../amplitudes.py
	time python3 $< --output $@ $* 8

sie05.raw: ../sieamplitudes.py 
	time python3 $< --output $@ 5 7
