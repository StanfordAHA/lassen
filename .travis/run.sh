# force color
export PYTEST_ADDOPTS="--color=yes"

cd /lassen

pytest -x -v tests/test_pe.py -k fp_binary
