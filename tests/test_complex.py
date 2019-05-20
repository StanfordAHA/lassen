from lassen.stdlib.fma import gen_FMA
from lassen.isa import DATAWIDTH
from hwtypes import BitVector, Bit
from lassen.sim import gen_pe
import pytest
import lassen.asm as asm
import math
import random


#Hack
#random.seed(10)

Bit = Bit
Data = BitVector[DATAWIDTH]

FMA = gen_FMA(BitVector.get_family())

def test_fma():
    fma = FMA()
    assert Data(58) == fma(Data(5), Data(10), Data(8))
