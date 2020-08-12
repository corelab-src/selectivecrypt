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
	python $(COMPILE) $^ $(PLAYGROUND)

#cryptonets-test: $(BUILD)/$(CRYPTONETS)_transformed.py

linear_regression: $(SRC)/$(LINEAR_REGRESSION).py
	python $(COMPILE) $^ $(BUILD)

logistic_regression: $(SRC)/$(LOGISTIC_REGRESSION).py
	python $(COMPILE) $^ $(BUILD)

perceptron: $(SRC)/$(PERCEPTRON).py
	python $(COMPILE) $^ $(BUILD)

mlp: $(SRC)/$(MLP).py
	python $(COMPILE) $^ $(BUILD)

prepare_zipping: 
	cp -r tensorslow_he/ build/
	mkdir -p build/utils
	cp -r utils/mypyheal.py build/utils/
	cp -r utils/s3_helper.py build/utils/

zip_cryptonets: cryptonets prepare_zipping
	cd build && zip -r cryptonets.zip . && cd -

zip_linear_regression: linear_regression prepare_zipping
	cd build && zip -r linear_regression.zip . && cd -

zip_logistic_regression: logistic_regression prepare_zipping
	cd build && zip -r logistic_regression.zip . && cd -

zip_perceptron: preceptron prepare_zipping
	cd build && zip -r perceptron.zip . && cd -

zip_mlp: mlp prepare_zipping
	cd build && zip -r mlp.zip . && cd -

zip-all: prepare_zipping cryptonets linear_regression logistic_regression perceptron mlp
	cd build && zip -r all_transformed.zip . && cd -

clean:
	rm -rf build/*.py
