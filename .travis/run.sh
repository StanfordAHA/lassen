# force color
export PYTEST_ADDOPTS="--color=yes"

pytest --cov lassen --cov-report term-missing -v tests/
