from collections import namedtuple
import operator
import random

import pytest

from hwtypes import SIntVector, UIntVector, BitVector, Bit
from peak.family import PyFamily

import lassen.asm as asm
from lassen import PE_fc, DATAWIDTH

PE = PE_fc(PyFamily())
Data = BitVector[DATAWIDTH]

op = namedtuple("op", ["name", "func"])
NTESTS = 32


@pytest.mark.parametrize(
    "op",
    [
        op("and", lambda x, y: x & y),
        op("or", lambda x, y: x | y),
        op("xor", lambda x, y: x ^ y),
    ],
)
def test_lut_binary(op):
    pe = PE()
    inst = getattr(asm, f"lut_{op.name}")()
    for _ in range(NTESTS):
        b0 = Bit(random.choice([0, 1]))
        b1 = Bit(random.choice([0, 1]))
        b2 = Bit(random.choice([0, 1]))
        data0 = UIntVector.random(DATAWIDTH)
        _, res_p, _, _, _ = pe(inst, data0=data0, bit0=b0, bit1=b1, bit2=b2)
        assert res_p == op.func(b1, b2)  # Testing from bit1 and bit2 port


@pytest.mark.parametrize(
    "op",
    [
        op("not", lambda x: ~x),
    ],
)
def test_lut_unary(op):
    pe = PE()
    inst = getattr(asm, f"lut_{op.name}")()
    for _ in range(NTESTS):
        b0 = Bit(random.choice([0, 1]))
        b1 = Bit(random.choice([0, 1]))
        b2 = Bit(random.choice([0, 1]))
        data0 = UIntVector.random(DATAWIDTH)
        _, res_p, _, _, _ = pe(inst, data0=data0, bit0=b0, bit1=b1, bit2=b2)
        assert res_p == op.func(b1)


@pytest.mark.parametrize(
    "op",
    [
        op("mux", lambda sel, d0, d1: d1 if sel else d0),
    ],
)
def test_lut_ternary(op):
    pe = PE()
    inst = getattr(asm, f"lut_{op.name}")()
    for _ in range(NTESTS):
        sel = Bit(random.choice([0, 1]))
        d0 = Bit(random.choice([0, 1]))
        d1 = Bit(random.choice([0, 1]))
        data0 = UIntVector.random(DATAWIDTH)
        _, res_p, _, _, _ = pe(inst, data0=data0, bit0=d0, bit1=d1, bit2=sel)
        assert res_p == op.func(sel, d0, d1)


def test_lut():
    pe = PE()
    for _ in range(NTESTS):
        lut_val = BitVector.random(8)
        inst = asm.lut(lut_val)
        b0 = Bit(random.choice([0, 1]))
        b1 = Bit(random.choice([0, 1]))
        b2 = Bit(random.choice([0, 1]))
        data0 = UIntVector.random(DATAWIDTH)
        _, res_p, _, _, _ = pe(inst, data0=data0, bit0=b0, bit1=b1, bit2=b2)
        assert res_p == lut_val[int(BitVector[3]([b0, b1, b2]))]
