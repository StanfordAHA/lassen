<img src="https://avatars0.githubusercontent.com/in/67?s=20&v=4"> [![Build Status](https://travis-ci.com/StanfordAHA/lassen.svg?branch=master)](https://travis-ci.com/StanfordAHA/lassen)

<img src="https://avatars1.githubusercontent.com/oa/46194?s=20&v=4"> [![Build Status](https://badge.buildkite.com/ff881d32201c87b9105d613c55df78ac85de68a0e819cf7205.svg)](https://buildkite.com/stanford-aha/lassen)

[![Coverage Status](https://coveralls.io/repos/github/StanfordAHA/lassen/badge.svg?branch=master)](https://coveralls.io/github/StanfordAHA/lassen?branch=master)

# Lassen
The PE for the second generation CGRA (garnet).


## Instructions to run
* Make sure you have python 3.7. Peak needs this.

* First install peak
```
git clone https://github.com/phanrahan/peak.git
cd peak
python setup.py install --user
```
* Install Lassen
```
git clone git@github.com:StanfordAHA/lassen.git
cd lassen
python setup.py install --user
```
* Run tests using
```
pytest
```

## Tasks
| Date | Person | Status | Task |
| ---- | ------ | ------ | ---- |
| Feb 13 | Alex | Complete | Add BFloat16 add and multiply functional model |
| | | | Add Float (configurable width?) type to CoreIR, create float add and multiply operator implementations in CoreIR by wrapping designware module |
| | | | Add Float type to Magma |
| | | | Generate verilog from Peak |
| | | | Figure out what to do about different latencies (if they are different for the floating point ops) |
| | | | Add multi-PE support to Peak |
| | | | Change CoreIR mapper, PnR to support multi-PE |

## Architectural description
Compared to the first generation PE (Diablo), Lassen shall have two new features:
* BFloat addition and multiplication in every PE
* Transcendental functions (div, log, e^x, sin, pow) on BFloats implemented using a cluster of PEs and memory. The PEs and memory will get some small special instructions to support these operations.
* It will not support denormalized numbers

### BFloat
+/- 1.mantissa * 2 ^ exponent, where mantissa is a 7 bit unsigned integer, and exponent is 8 bit signed integer (. dot means decimal point)

### Transcendental functions
1. div
* Implements `out = a/b`, where a, b and out are all BFloats
* It is performed using `out = a * (1/b)`, the BFloat multiply already exists as an instruction. So we basically have to implement reciprocal, `1/b`
* Let us say `b = +/- 1.f * 2 ^ x`
* `1/b = +/- (1/1.f) * 2 ^ (-x)`
* `(1/1.f)` is stored as a Bfloat in a look up table in a memory tile. It is a table with 128 entries as f is 7 bits. So you read this entry out, let us say it is some `+/- 1.g * 2 ^ y`
* Then `1/b = +/- 1.g * 2 ^ y * 2 ^ (-x) = +/- 1.g * 2 ^ (y - x)`
* We implement subtraction of the exponent portions of two BFloats as a new instruction in the PE
* So div boils down to a 16 bit lookup from a 128 entry table, one 8 bit signed integer subtraction and 1 BFloat multiply
* We must take into account corner cases when a, b, out are not normal numbers

2. ln
* Implements `out = ln(a)` where a and out are BFloats
* Let us say `a = +/- 1.f * 2 ^ x`
* `ln(a)` should error out when `a < 0`
* Otherwise, `ln(a) = ln(1.f * 2 ^ x) = ln(1.f) + x * ln(2)`
* `ln(1.f)` is a look up table, similar to what we did for div
* We add a special instruction to PE to convert 8 bit signed integer x to a BFloat, `ln(2)` is also a BFloat
* So ln boils down to a lookup, 8 bit signed integer to BFloat conversion, a BFloat multiply and a BFloat add

3. e^x
* `e^x = (2^(1/ln(2)))^x = 2^(x/ln(2)) = 2^y`
* We can get `y` with existing instructions. Bfloat multiply it with a constant 1/ln(2).
* Let us just work out the case when y is positive. If y is negative 2^y = 1/(2^-y) and we have already implemented reciprocal.
* Convert Bfloat y to a+b where a is integer part and b is fractional part. When b is smaller than 2^-6 it is zero in Bfloat16.
* We look up 2^b from a table, this has 64 entries.
* Then we increment exponent of the looked up number by a. 

4. sin
* To compute sin(x), first we calculate y = x mod (pi/2)
* If y is less than some number, return y, else lookup in table. This gets rid of most negative exponents, and table it basically dependent on mantissa.

5. pow
* a^x = e^(ln(a^x)) = e^(x * ln(a))
* We already have BFloat multiply, ln, and exponential, so we can implement power.

