[![Build Status](https://travis-ci.com/StanfordAHA/whitney.svg?branch=master)](https://travis-ci.com/StanfordAHA/whitney)

# Whitney
The PE for the second generation CGRA (garnet).

## Instructions to run
* Make sure you have python 3.7. Peak needs this.

* First install peak
```
git clone https://github.com/phanrahan/peak.git
cd peak
python setup.py install --user
```
* Install whitney
```
git clone git@github.com:StanfordAHA/whitney.git
cd whitney
python setup.py install --user
```
* Run tests using
```
pytest
```

## Whitney related tasks
| Date | Person | Status | Task |
| ---- | ------ | ------ | ---- |
| Feb 13 | Alex | | Add BFloat16 add and multiply functional model to whitney |
| | | | Add Float (configurable width?) type to CoreIR, create float add and multiply operator implementations in CoreIR by wrapping designware module |
| | | | Add Float type to Magma |
| | | | Generate verilog from Peak |
| | | | Figure out what to do about different latencies (if they are different for the floating point ops) |
| | | | Add multi-PE support to Peak |
| | | | Change CoreIR mapper, PnR to support multi-PE |

## Whitney architectural description
Compared to the first generation PE (Diablo), Whitney shall have two new features:
* BFloat16 addition and multiplication in every PE
* Transcendental functions (div, log, e^x, sin, pow) implemented using a cluster of PEs and memory
```diff
- What types and precisions for the transcendental operations?
```
