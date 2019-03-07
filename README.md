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
* `e^x = 2^(log2(e^x)) = 2^(x * log2(e)) = 2^y`
* We already have BFloat multiply, and `log2(e)` is a BFloat constant, so we can multiply them to get a BFloat `y`
* Let us just work out the case when y is positive. If y is negative 2^y = 1/(2^-y) and we have already implemented reciprocal.
* The largest BFloat number is `0 11111110 1111111 = 2^127 * (2 - 2^(-7))`. log2 of this number is `127.99..`. For any y larger than `127.99..`, `2^y` will be infinity. 
* So we are only concerned with values of y between 0 and 128. We can break this range into two parts:
* 0 <= y < 1 => 1 <= 2^y < 2
* 1 <= y < 128: here the exponent is positive, and only the last three bits are significant, and we have 7 mantissa bits, so we have a look up table with a 10 bit address (1024 entries)?


4. sin
* To compute sin(x), first we convert x to a value y between -pi/2 to pi/2 which has the same sin
* We implement sin(y), y is between -1.57 and 1.57

5. pow
* a^x = e^(ln(a^x)) = e^(x * ln(a))
* We already have BFloat multiply, ln, and exponential, so we can implement power.
