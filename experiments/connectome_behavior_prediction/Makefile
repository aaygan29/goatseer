.PHONY: reproduce synthetic real clean

reproduce: real

synthetic:
	python3 -m pytest instrument/tests/verification/test_behavior.py -q

real: synthetic
	python3 experiments/connectome_behavior_prediction/run.py --subjects 1 2 3 4 5

clean:
	rm -rf results/
