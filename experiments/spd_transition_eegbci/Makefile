.PHONY: help run synthetic real clean

PYTHON ?= python3
SUBJECT ?= 1
PROTOTYPES ?= 6

help:
	@echo "spd_transition_eegbci targets:"
	@echo "  run        - Run on PhysioNet EEG-BCI subject \$$(SUBJECT) (default 1)."
	@echo "  synthetic  - Run the synthetic-ground-truth control first (required before real)."
	@echo "  real       - Alias for run; requires synthetic to have passed."
	@echo "  reproduce  - synthetic + real for subjects 1 2 3."
	@echo "  clean      - Remove results/."

synthetic:
	cd ../.. && $(PYTHON) -m pytest instrument/tests/verification/test_dynamics.py -q

real: synthetic
	cd ../.. && $(PYTHON) experiments/spd_transition_eegbci/run.py --subject $(SUBJECT) --prototypes $(PROTOTYPES)

run: real

reproduce:
	$(MAKE) synthetic
	for s in 1 2 3; do $(MAKE) real SUBJECT=$$s; done

clean:
	rm -rf results/
