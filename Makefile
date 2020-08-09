ROOT=$(PWD)
SRC=$(ROOT)/benchmarks
BUILD=$(ROOT)/build
BIN=$(ROOT)/bin
PLAYGROUND=$(ROOT)/playground

CRYPTONETS=cryptonets
LINEAR_REGRESSION=linear_regression
LOGISTIC_REGRESSION=logistic_regression
PERCEPTRON=perceptron
MLP=mlp

COMPILE=$(BIN)/compile.py

all: $(CRYPTONETS) $(LINEAR_REGRESSION) $(LOGISTIC_REGRESSION) $(PERCEPTRON) $(MLP)

local-all: $(CRYPTONETS)-local $(LINEAR_REGRESSION)-local $(LOGISTIC_REGRESSION)-local $(PERCEPTRON)-local $(MLP)-local

cryptonets: $(SRC)/$(CRYPTONETS).py
	python $(COMPILE) $^ $(BUILD)

cryptonets-local: $(SRC)/$(CRYPTONETS)_local.py
	python $(COMPILE) $^ $(BUILD)

#cryptonets-test: $(BUILD)/$(CRYPTONETS)_transformed.py

linear_regression: $(SRC)/$(LINEAR_REGRESSION).py
	python $(COMPILE) $^ $(BUILD)

logistic_regression: $(SRC)/$(LOGISTIC_REGRESSION).py
	python $(COMPILE) $^ $(BUILD)

perceptron: $(SRC)/$(PERCEPTRON).py
	python $(COMPILE) $^ $(BUILD)

mlp: $(SRC)/$(MLP).py
	python $(COMPILE) $^ $(BUILD)

zip_all: cryptonets linear_regression
	cp -r tensorslow_he/ build/
	mkdir -p build/utils
	cp -r utils/mypyheal.py build/utils/
	cp -r utils/s3_helper.py build/utils/
	cd build && zip -r $(CRYPTONETS).zip . && cd -

clean:
	rm -rf build/*.py
