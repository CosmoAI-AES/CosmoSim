all: sampled.csv unsampled.csv resampled.log reunsampled.log

sampled.csv:
	python -m CosmoSim -vvv --csvfile debug.csv --dir sampled --outfile sampled.csv | tee sampled.log
unsampled.csv:
	python -m CosmoSim -vvv --csvfile debug.csv --dir unsampled --outfile unsampled.csv --no-sampled | tee unsampled.log

resampled.log: sampled.csv
	python -m CosmoSim -vvv --roulette $< --dir resampled --outfile resampled.csv | tee resampled.log
reunsampled.log: unsampled.csv
	python -m CosmoSim -vvv --roulette $< --dir reunsampled --outfile reunsampled.csv | tee reunsampled.log

clean: 
	rm -f *.log
	rm -f sampled.csv unsampled.csv 
