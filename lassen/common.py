from hwtypes import make_modifier, BitVector
from hwtypes import SMTFPVector, FPVector, RoundingMode
from hwtypes import SMTBit

# Current PE has 16-bit data path
DATAWIDTH = 16
Data = BitVector[DATAWIDTH]
def BFloat16_fc(family):
    if family is SMTBit.get_family():
        FPV = SMTFPVector
    else:
        FPV = FPVector
    BFloat16 = FPV[8,7,RoundingMode.RNE,False]
    return BFloat16

# Global signal modifier.
Global = make_modifier("Global")

DATA01_ADDR = 3
BIT012_ADDR = 4
DATA0_START = 0
DATA0_WIDTH = DATAWIDTH
DATA1_START = 16
DATA1_WIDTH = DATAWIDTH
BIT0_START = 0
BIT1_START = 1
BIT2_START = 2


