# force color
export PYTEST_ADDOPTS="--color=yes"

cd /lassen

pytest tests/ -k test_fp_mul
