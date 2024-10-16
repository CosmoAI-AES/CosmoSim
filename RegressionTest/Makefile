
all: alltests

status: cpptests
	cat */*.status

clean alltests:
	cd exactpm ; $(MAKE) $@
	cd raytrace ; $(MAKE) $@
	cd roulette ; $(MAKE) $@
	cd roulettepm ; $(MAKE) $@
	cd new-roulette ; $(MAKE) alltests
	cd new-raytrace ; $(MAKE) alltests
	cd sampled-roulette ; $(MAKE) alltests
	cd sampled-raytrace ; $(MAKE) alltests
	cd roulettegen ; $(MAKE) $@
	cd amplitudes ; $(MAKE) $@

cpptests:
	cd exactpm ; $(MAKE) alltests
	cd raytrace ; $(MAKE) alltests
	cd roulette ; $(MAKE) alltests
	cd roulettepm ; $(MAKE) alltests
	cd new-roulette ; $(MAKE) alltests
	cd new-raytrace ; $(MAKE) alltests
	cd sampled-roulette ; $(MAKE) alltests
	cd sampled-raytrace ; $(MAKE) alltests
	# cd roulettelens ; $(MAKE) alltests

baselines:
	cd exactpm ; $(MAKE) baseline`date "+%Y%m%d"`
	cd raytrace ; $(MAKE) baseline`date "+%Y%m%d"` 
	cd roulette ; $(MAKE) baseline`date "+%Y%m%d"` 
	cd roulettepm ; $(MAKE) baseline`date "+%Y%m%d"`
false:
	/bin/false | tee test.log ; echo $${PIPESTATUS[0]} $${PIPESTATUS[1]} 
true:
	/bin/true
15:
	exit 15
