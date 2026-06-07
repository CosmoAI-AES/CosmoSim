all: sampled.csv unsampled.csv resampled.log reunsampled.log

sampled.csv:
 	python -m CosmoSim --csvfile debug.csv --dir sampled --outfile sampled.csv | tee sampled.log
unsampled.csv:
 	python -m CosmoSim --csvfile debug.csv --dir unsampled --outfile unsampled.csv --no-sampled | tee unsampled.log

resampled.log: sampled.csv
 	python -m CosmoSim --roulette $< --dir resampled --outfile resampled.csv | tee resampled.log
reunsampled.log: unsampled.csv
 	python -m CosmoSim --roulette $< --dir reunsampled --outfile reunsampled.csv | tee reunsampled.log
