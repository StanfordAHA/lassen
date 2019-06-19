# force color
export PYTEST_ADDOPTS="--color=yes"

cd /lassen

pytest --workers=auto --cov lassen --cov-report term-missing -v tests/
