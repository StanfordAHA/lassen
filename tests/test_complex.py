from lassen.stdlib.fma import gen_FMA
from lassen.isa import DATAWIDTH
from hwtypes import BitVector, Bit
from hwtypes import BitVector, Bit, SIntVector
from lassen.sim import gen_pe
import pytest
import lassen.asm as asm
import math
import random


Bit = Bit
Data = BitVector[DATAWIDTH]
SData = SIntVector[DATAWIDTH]

NTESTS=16

FMA = gen_FMA(BitVector.get_family())

@pytest.mark.parametrize("args", [
    (random.randint(-10,10),
     random.randint(-10,10),
     random.randint(-10,10))
    for _ in range(NTESTS) ] )
def test_fma(args):
    fma = FMA()
    assert SData(args[0]*args[1]+args[2]) == fma(SData(args[0]), SData(args[1]), SData(args[2]))
