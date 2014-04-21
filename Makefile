DIR=ai_modules

dist: kcwu.tgz

$(DIR)/kcwu_pack.py: $(DIR)/kcwu.py pack.py
	python pack.py $(DIR)/kcwu.py > $(DIR)/kcwu_pack.py
$(DIR)/kcwu2_pack.py: $(DIR)/kcwu2.py pack.py
	python pack.py $(DIR)/kcwu2.py > $(DIR)/kcwu2_pack.py
$(DIR)/kcwu_short_pack.py: $(DIR)/kcwu_short.py pack.py
	python pack.py $(DIR)/kcwu_short.py > $(DIR)/kcwu_short_pack.py
$(DIR)/kcwu_short2_pack.py: $(DIR)/kcwu_short2.py pack.py
	python pack.py $(DIR)/kcwu_short2.py > $(DIR)/kcwu_short2_pack.py

$(DIR)/kcwu_short_min_pack.py: $(DIR)/kcwu_short_min.py
	python ~/Downloads/code/minipy/minipy.py --rename -p AI,getNextMove $(DIR)/kcwu_short_min.py > $(DIR)/kcwu_short_min_pack.py

kcwu.tgz: $(DIR)/kcwu_pack.py $(DIR)/kcwu2_pack.py $(DIR)/kcwu_short_min_pack.py $(DIR)/kcwu_short_pack.py  $(DIR)/kcwu_short2_pack.py
	tar zcf kcwu.tgz $(DIR)/kcwu2_pack.py $(DIR)/kcwu_short_pack.py $(DIR)/kcwu_short_min_pack.py $(DIR)/kcwu_short2_pack.py

test: dist
	time python telemetry_perf_test.py 3 1 kcwu2_pack 2>&1 | tail -4
	@echo -----------------------------------
	time python telemetry_perf_test.py 100 30 kcwu_short_pack 2>&1 | tail -4
	wc -c $(DIR)/kcwu_short_pack.py
	@echo -----------------------------------
	#time python telemetry_perf_test.py 100 1 kcwu_short2_pack 2>&1 | tail -4
	#wc -c $(DIR)/kcwu_short2_pack.py
	@echo -----------------------------------
	time python telemetry_perf_test.py 10000 30 kcwu_short_min_pack 2>&1 | tail -3
	wc -c $(DIR)/kcwu_short_min_pack.py
	head -1 $(DIR)/kcwu_short_min.py
