from collections import namedtuple
from itertools import product
import random

import pytest

from hwtypes import SIntVector, UIntVector, BitVector, Bit
from magma.bitutils import int2seq
from peak.family import PyFamily


import lassen.asm as asm
from lassen import PE_fc, Inst_fc
from lassen.common import DATAWIDTH, BFloat16_fc

from rtl_utils import rtl_tester, CAD_ENV

Inst = Inst_fc(PyFamily())
Mode_t = Inst.rega

PE = PE_fc(PyFamily())
pe = PE()

BFloat16 = BFloat16_fc(PyFamily())
Data = BitVector[DATAWIDTH]

op = namedtuple("op", ["inst", "func"])
NTESTS = 4


@pytest.mark.parametrize(
    "op",
    [
        op(asm.and_(), lambda x, y: x & y),
        op(asm.or_(), lambda x, y: x | y),
        op(asm.xor(), lambda x, y: x ^ y),
        op(asm.add(), lambda x, y: x + y),
        op(asm.sub(), lambda x, y: x - y),
        op(asm.lsl(), lambda x, y: x << y),
        op(asm.umin(), lambda x, y: (x < y).ite(x, y)),
        op(asm.umax(), lambda x, y: (x > y).ite(x, y)),
    ],
)
@pytest.mark.parametrize(
    "args",
    [
        (UIntVector.random(DATAWIDTH), UIntVector.random(DATAWIDTH))
        for _ in range(NTESTS)
    ],
)
def test_unsigned_binary(op, args):
    x, y = args
    res, _, _, _, _ = pe(op.inst, Data(x), Data(y))
    assert res == op.func(x, y)
    rtl_tester(op, x, y, res=res)


@pytest.mark.parametrize("op", [op(asm.lsr(), lambda x, y: x >> y)])
@pytest.mark.parametrize(
    "args",
    [
        (UIntVector.random(DATAWIDTH), UIntVector.random(DATAWIDTH))
        for _ in range(NTESTS)
    ],
)
def test_unsigned_binary(op, args):
    x, y = args
    res, _, _, _, _ = pe(op.inst, data0=Data(x), data2=Data(y))
    assert res == op.func(x, y)
    rtl_tester(op, x, data2=y, res=res)


@pytest.mark.parametrize(
    "op",
    [
        op(asm.lsl(), lambda x, y: x << y),
        op(asm.smin(), lambda x, y: (x < y).ite(x, y)),
        op(asm.smax(), lambda x, y: (x > y).ite(x, y)),
    ],
)
@pytest.mark.parametrize(
    "args",
    [
        (SIntVector.random(DATAWIDTH), SIntVector.random(DATAWIDTH))
        for _ in range(NTESTS)
    ],
)
def test_signed_binary(op, args):
    x, y = args
    res, _, _, _, _ = pe(op.inst, Data(x), Data(y))
    assert res == op.func(x, y)
    rtl_tester(op, x, y, res=res)


@pytest.mark.parametrize("op", [op(asm.asr(), lambda x, y: x >> y)])
@pytest.mark.parametrize(
    "args",
    [
        (SIntVector.random(DATAWIDTH), SIntVector.random(DATAWIDTH))
        for _ in range(NTESTS)
    ],
)
def test_signed_binary(op, args):
    x, y = args
    res, _, _, _, _ = pe(op.inst, Data(x), data2=Data(y))
    assert res == op.func(x, y)
    rtl_tester(op, x, data2=y, res=res)


@pytest.mark.parametrize(
    "op",
    [
        op(asm.abs(), lambda x: x if x > 0 else -x),
    ],
)
@pytest.mark.parametrize("args", [SIntVector.random(DATAWIDTH) for _ in range(NTESTS)])
def test_signed_unary(op, args):
    x = args
    res, _, _, _, _ = pe(op.inst, Data(x))
    assert res == op.func(x)
    rtl_tester(op, x, 0, res=res)


@pytest.mark.parametrize(
    "op",
    [
        op(asm.eq(), lambda x, y: x == y),
        op(asm.ne(), lambda x, y: x != y),
        op(asm.ugt(), lambda x, y: x > y),
        op(asm.uge(), lambda x, y: x >= y),
        op(asm.ult(), lambda x, y: x < y),
        op(asm.ule(), lambda x, y: x <= y),
    ],
)
@pytest.mark.parametrize(
    "args",
    [
        (UIntVector.random(DATAWIDTH), UIntVector.random(DATAWIDTH))
        for _ in range(NTESTS)
    ],
)
def test_unsigned_relation(op, args):
    x, y = args
    _, res_p, _, _, _ = pe(op.inst, Data(x), Data(y))
    assert res_p == op.func(x, y)
    rtl_tester(op, x, y, res_p=res_p)


@pytest.mark.parametrize(
    "op",
    [
        op(asm.sgt(), lambda x, y: x > y),
        op(asm.sge(), lambda x, y: x >= y),
        op(asm.slt(), lambda x, y: x < y),
        op(asm.sle(), lambda x, y: x <= y),
    ],
)
@pytest.mark.parametrize(
    "args",
    [
        (SIntVector.random(DATAWIDTH), SIntVector.random(DATAWIDTH))
        for _ in range(NTESTS)
    ],
)
def test_signed_relation(op, args):
    x, y = args
    _, res_p, _, _, _ = pe(op.inst, Data(x), Data(y))
    assert res_p == op.func(x, y)
    rtl_tester(op, x, y, res_p=res_p)


@pytest.mark.parametrize(
    "op",
    [
        op(asm.sel(), lambda x, y, d: x if d else y),
        op(asm.adc(), lambda x, y, c: x + y + c),
        op(asm.sbc(), lambda x, y, c: x - y + c - 1),
    ],
)
@pytest.mark.parametrize(
    "args",
    [
        (
            UIntVector.random(DATAWIDTH),
            UIntVector.random(DATAWIDTH),
            Bit(random.choice([1, 0])),
        )
        for _ in range(NTESTS)
    ],
)
def test_ternary(op, args):
    inst = op.inst
    d0 = args[0]
    d1 = args[1]
    b0 = args[2]
    res, _, _, _, _ = pe(inst, data0=d0, data1=d1, bit0=b0)
    assert res == op.func(d0, d1, b0)
    rtl_tester(inst, data0=d0, data1=d1, bit0=b0, res=res)


@pytest.mark.parametrize(
    "args",
    [
        (SIntVector.random(DATAWIDTH), SIntVector.random(DATAWIDTH))
        for _ in range(NTESTS)
    ],
)
def test_smult(args):
    def mul(x, y):
        mulx, muly = x.sext(DATAWIDTH), y.sext(DATAWIDTH)
        return mulx * muly

    smult0 = asm.smult0()
    smult1 = asm.smult1()
    smult2 = asm.smult2()
    x, y = args
    xy = mul(x, y)
    res, _, _, _, _ = pe(smult0, Data(x), Data(y))
    assert res == xy[0:DATAWIDTH]
    rtl_tester(smult0, x, y, res=res)
    res, _, _, _, _ = pe(smult1, Data(x), Data(y))
    assert res == xy[DATAWIDTH // 2 : DATAWIDTH // 2 + DATAWIDTH]
    rtl_tester(smult1, x, y, res=res)
    res, _, _, _, _ = pe(smult2, Data(x), Data(y))
    assert res == xy[DATAWIDTH:]
    rtl_tester(smult2, x, y, res=res)


@pytest.mark.parametrize(
    "args",
    [
        (UIntVector.random(DATAWIDTH), UIntVector.random(DATAWIDTH))
        for _ in range(NTESTS)
    ],
)
def test_umult(args):
    def mul(x, y):
        mulx, muly = x.zext(DATAWIDTH), y.zext(DATAWIDTH)
        return mulx * muly

    umult0 = asm.umult0()
    umult1 = asm.umult1()
    umult2 = asm.umult2()
    x, y = args
    xy = mul(x, y)
    res, _, _, _, _ = pe(umult0, Data(x), Data(y))
    assert res == xy[0:DATAWIDTH]
    rtl_tester(umult0, x, y, res=res)
    res, _, _, _, _ = pe(umult1, Data(x), Data(y))
    assert res == xy[DATAWIDTH // 2 : DATAWIDTH // 2 + DATAWIDTH]
    rtl_tester(umult1, x, y, res=res)
    res, _, _, _, _ = pe(umult2, Data(x), Data(y))
    assert res == xy[DATAWIDTH:]
    rtl_tester(umult2, x, y, res=res)


@pytest.mark.parametrize(
    "op",
    [
        op(
            asm.crop(),
            lambda x, y, z: ((x < y).ite(x, y) > z).ite((x < y).ite(x, y), z),
        ),
        op(asm.mulshr(), lambda x, y, z: (x * y) >> z),
        op(asm.taa(), lambda x, y, z: x + y + z),
        op(asm.tas(), lambda x, y, z: x + y - z),
        op(asm.tsa(), lambda x, y, z: x - y + z),
        op(asm.tss(), lambda x, y, z: x - y - z),
        op(asm.muladd(), lambda x, y, z: x * y + z),
        op(asm.mulsub(), lambda x, y, z: x * y - z),
    ],
)
@pytest.mark.parametrize(
    "args",
    [
        (
            UIntVector.random(DATAWIDTH),
            UIntVector.random(DATAWIDTH),
            UIntVector.random(DATAWIDTH),
        )
        for _ in range(NTESTS)
    ],
)
def test_three_input_ops(op, args):
    x, y, z = args
    res, _, _, _, _ = pe(op.inst, Data(x), Data(y), Data(z))
    assert res == op.func(x, y, z)
    rtl_tester(op, x, y, z, res=res)


#
# floating point
#


def BV(val):
    return BFloat16(val)


fp_sign_vec = [BV(2.0), BV(-2.0), BV(3.0), BV(-3.0)]
fp_zero_vec = [BV(0.0), BV("-0.0")]
fp_inf_vec = [BV("inf"), BV("-inf")]


@pytest.mark.parametrize(
    "op",
    [
        op(asm.fp_add(), lambda x, y: x + y),
        op(asm.fp_sub(), lambda x, y: x - y),
        op(asm.fp_mul(), lambda x, y: x * y),
    ],
)
@pytest.mark.parametrize(
    "args",
    [(BFloat16.random(), BFloat16.random()) for _ in range(NTESTS)]
    + list(product(fp_sign_vec + fp_zero_vec, fp_sign_vec + fp_zero_vec)),
)
def test_fp_binary_op(op, args):
    inst = op.inst
    in0 = args[0]
    in1 = args[1]
    out = op.func(in0, in1)
    data0 = BFloat16.reinterpret_as_bv(in0)
    data1 = BFloat16.reinterpret_as_bv(in1)
    res, res_p, _, _, _ = pe(inst, data0, data1)
    assert res == BFloat16.reinterpret_as_bv(out)
    if CAD_ENV:
        rtl_tester(op, data0, data1, res=res)
    else:
        pytest.skip("Skipping since DW not available")


# container for a floating point value easily indexed by sign, exp, and frac
fpdata = namedtuple("fpdata", ["sign", "exp", "frac"])

# Convert fpdata to a BFloat value
def BFloat(fpdata):
    sign = BitVector[1](fpdata.sign)
    exp = BitVector[8](fpdata.exp)
    frac = BitVector[7](fpdata.frac)
    return BitVector.concat(BitVector.concat(sign, exp), frac)


# Generate random bfloat
def random_bfloat():
    return fpdata(BitVector.random(1), BitVector.random(8), BitVector.random(7))


def test_fp_mul():
    # Regression test for https://github.com/StanfordAHA/lassen/issues/111
    inst = asm.fp_mul()
    data0 = Data(0x4040)
    data1 = Data(0x4049)
    res, res_p, _, _, _ = pe(inst, data0, data1)
    if CAD_ENV:
        rtl_tester(inst, data0, data1, res=res)
    else:
        pytest.skip("Skipping since DW not available")


@pytest.mark.parametrize(
    "xy",
    [(BFloat16.random(), BFloat16.random()) for _ in range(NTESTS)]
    + list(
        product(
            fp_sign_vec + fp_zero_vec + fp_inf_vec,
            fp_sign_vec + fp_zero_vec + fp_inf_vec,
        )
    )
    + list(
        product(fp_zero_vec + fp_inf_vec, [BFloat16.random() for _ in range(NTESTS)])
    ),
)
@pytest.mark.parametrize(
    "op",
    [
        op(asm.fp_gt(), lambda x, y: x > y),
        op(asm.fp_ge(), lambda x, y: x >= y),
        op(asm.fp_lt(), lambda x, y: x < y),
        op(asm.fp_le(), lambda x, y: x <= y),
        op(asm.fp_eq(), lambda x, y: x == y),
        op(asm.fp_neq(), lambda x, y: x != y),
    ],
)
def test_fp_cmp(xy, op):
    in0, in1 = xy
    out = op.func(in0, in1)
    data0 = BFloat16.reinterpret_as_bv(in0)
    data1 = BFloat16.reinterpret_as_bv(in1)
    _, res_p, _, _, _ = pe(op.inst, data0, data1)
    assert res_p == out
    if CAD_ENV:
        rtl_tester(op, data0, data1, res_p=out)
    else:
        pytest.skip("Skipping since DW not available")


@pytest.mark.parametrize("lut_code", [UIntVector.random(8) for _ in range(NTESTS)])
def test_lut(lut_code):
    inst = asm.lut(lut_code)
    for i in range(0, 8):
        bit0, bit1, bit2 = int2seq(i, 3)
        expected = (lut_code >> i)[0]
        rtl_tester(inst, bit0=bit0, bit1=bit1, bit2=bit2, res_p=expected)


@pytest.mark.parametrize(
    "args",
    [
        (UIntVector.random(DATAWIDTH), UIntVector.random(DATAWIDTH))
        for _ in range(NTESTS)
    ],
)
def test_reg_delay(args):
    data0, data1 = args
    inst = asm.add(ra_mode=Mode_t.DELAY, rb_mode=Mode_t.DELAY)
    data1_delay_values = [UIntVector.random(DATAWIDTH)]
    rtl_tester(
        inst,
        data0,
        data1,
        res=data0 + data1,
        delay=1,
        data1_delay_values=data1_delay_values,
    )


@pytest.mark.parametrize(
    "args",
    [
        (UIntVector.random(DATAWIDTH), UIntVector.random(DATAWIDTH))
        for _ in range(NTESTS)
    ],
)
def test_reg_const(args):
    data0, const1 = args
    data1 = UIntVector.random(DATAWIDTH)
    inst = asm.add(rb_mode=Mode_t.CONST, rb_const=const1)
    rtl_tester(inst, data0, data1, res=data0 + const1)


@pytest.mark.parametrize(
    "args",
    [
        (UIntVector.random(DATAWIDTH), UIntVector.random(DATAWIDTH))
        for _ in range(NTESTS)
    ],
)
def test_stall(args):
    data0, data1 = args
    inst = asm.add(ra_mode=Mode_t.BYPASS, rb_mode=Mode_t.DELAY)
    data1_delay_values = [UIntVector.random(DATAWIDTH)]
    rtl_tester(
        inst, data0, data1, res=data0, clk_en=0, data1_delay_values=data1_delay_values
    )
