# Whitney
The PE for the second generation CGRA (garnet).

# Instructions to run
* Make sure you have python 3.7. Peak needs this.

* First install peak
```
git clone https://github.com/phanrahan/peak.git
cd peak
python setup.py install --user
```

* Run tests using
```
pytest test_pe.py
```

# Tasks
| Date | Person | Status | Task |
| ---- | ------ | ------ | ---- |
| | | | Add BFloat16 add and multiply functional model to whitney |
| | | | Add Float (configurable width?) type to CoreIR, create float add and multiply operator implementations in CoreIR by wrapping designware module |
| | | | Add Float type to Magma |
| | | | Generate verilog from Peak |
| | | | Figure out what to do about different latencies (if they are different for the floating point ops) |
| | | | Add multi-PE support to Peak |
| | | | Change CoreIR mapper, PnR to support multi-PE |

# Whitney Architectural Description
