# force color
export PYTEST_ADDOPTS="--color=yes"

cd /lassen

pytest tests/ -vs
