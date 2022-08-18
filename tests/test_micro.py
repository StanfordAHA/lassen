from collections import namedtuple
import random

import pytest

from hwtypes import SIntVector, UIntVector, BitVector, Bit
from peak.family import PyFamily

import lassen.asm as asm
from lassen import PE_fc, Inst_fc
from lassen.common import DATAWIDTH, BFloat16_fc
from lassen.utils import float2bfbin, bfbin2float
from rtl_utils import rtl_tester

Inst = Inst_fc(PyFamily())
Mode_t = Inst.rega

PE = PE_fc(PyFamily())
pe = PE()

BFloat16 = BFloat16_fc(PyFamily())
Data = BitVector[DATAWIDTH]

op = namedtuple("op", ["inst", "func"])
NTESTS = 16

# container for a floating point value easily indexed by sign, exp, and frac
fpdata = namedtuple("fpdata", ["sign", "exp", "frac"])


def is_nan_or_inf(fpdata):
    return fpdata.exp == BitVector[8](-1)


# Convert fpdata to a BFloat value
def BFloat(fpdata):
    sign = BitVector[1](fpdata.sign)
    exp = BitVector[8](fpdata.exp)
    frac = BitVector[7](fpdata.frac)
    return BitVector.concat(BitVector.concat(frac, exp), sign)


# Generate random bfloat
def random_bfloat():
    return fpdata(BitVector.random(1), BitVector.random(8), BitVector.random(7))


@pytest.mark.parametrize("fpdata", [random_bfloat() for _ in range(NTESTS)])
def test_bfloat_construct(fpdata):
    fp = BFloat(fpdata)
    assert fp[-1] == fpdata.sign
    assert fp[7:-1] == fpdata.exp
    assert fp[:7] == fpdata.frac


@pytest.mark.parametrize(
    "args", [(random_bfloat(), SIntVector.random(DATAWIDTH)) for _ in range(NTESTS)]
)
def test_get_mant(args):
    # output = input.mantissa (7 bit)
    fp0 = args[0]
    in0 = BFloat(fp0)
    in1 = args[1]
    inst = asm.fgetmant()
    res, res_p, _, _, _ = pe(inst, in0, in1)
    assert res == Data(fp0.frac)
    rtl_tester(inst, in0, in1, res=Data(fp0.frac))


def test_add_exp_imm_targeted():
    inst = asm.faddiexp()
    data0 = Data(0x7F8A)
    data1 = Data(0x0005)
    res, res_p, _, _, _ = pe(inst, data0, data1)
    # 7F8A => Sign=0; Exp=0xFF; Mant=0x0A
    # Add 5 to exp => Sign=0; Exp=0x04; Mant=0x0A i.e. float  = 0x020A
    assert res == 0x020A
    rtl_tester(inst, data0, data1, res=0x020A)


@pytest.mark.parametrize(
    "args", [(random_bfloat(), SIntVector.random(8)) for _ in range(NTESTS)]
)
def test_add_exp_imm(args):
    if is_nan_or_inf(args[0]):
        pytest.skip("skipping nan")
    # input[0].exponent += input[1] (SIGNED)
    fp0 = args[0]
    sint1 = args[1]
    in0 = Data(BFloat(fp0))
    in1 = Data(sint1)
    out = BFloat(fpdata(fp0.sign, fp0.exp + sint1, fp0.frac))
    inst = asm.faddiexp()
    res, res_p, _, _, _ = pe(inst, in0, in1)
    assert res == out
    rtl_tester(inst, in0, in1, res=out)


@pytest.mark.parametrize(
    "args", [(random_bfloat(), random_bfloat()) for _ in range(NTESTS)]
)
def test_sub_exp(args):

    fp0 = args[0]
    fp1 = args[1]
    if is_nan_or_inf(fp0) or is_nan_or_inf(fp1):
        pytest.skip("skipping nan")

    in0 = Data(BFloat(fp0))
    in1 = Data(BFloat(fp1))
    # input[0].exponent -= input[1].exponent AND or sign bits
    out = fpdata(fp0.sign | fp1.sign, (fp0.exp - fp1.exp + 127) % 256, fp0.frac)
    inst = asm.fsubexp()
    res, res_p, _, _, _ = pe(inst, in0, in1)
    assert res == BFloat(out)
    rtl_tester(inst, in0, in1, res=BFloat(out))


def test_sub_exp_targeted():
    inst = asm.fsubexp()
    data0 = Data(0x7F8A)
    data1 = Data(0x4005)
    res, res_p, _, _, _ = pe(inst, data0, data1)
    # 7F8A => Sign=0; Exp=0xFF; Mant=0x0A
    # 4005 => Sign=0; Exp=0x80; Mant=0x05 (0100 0000 0000 0101)
    # res: 7F0A => Sign=0; Exp=0xFE; Mant=0x0A (0111 1111 0000 1010)
    assert res == 0x7F0A
    rtl_tester(inst, data0, data1, res=0x7F0A)


# @pytest.mark.skip("Not sure the exact op semantics")
@pytest.mark.parametrize(
    "args", [(random_bfloat(), SIntVector.random(DATAWIDTH)) for _ in range(NTESTS)]
)
def test_cnvt_exp_to_float(args):

    fp0 = args[0]
    if is_nan_or_inf(fp0):
        pytest.skip("skipping nan")

    in0 = BFloat(fp0)
    in1 = args[1]
    # output = (float)(input1.exp) (UNBIASED)
    unbiased_expa = int(fp0.exp) - 127
    out = int(float2bfbin(unbiased_expa), 2)
    inst = asm.fcnvexp2f()

    res, res_p, _, _, _ = pe(inst, in0, in1)
    assert res == out
    rtl_tester(inst, in0, in1, res=out)


def test_cnvt_exp_to_float_targeted():
    inst = asm.fcnvexp2f()
    # data0 = Data(0x4005)
    data0 = Data(65525)
    data1 = Data(0x0000)
    res, res_p, _, _, _ = pe(inst, data0, data1)
    # 4005 => Sign=0; Exp=0x80; Mant=0x05 (0100 0000 0000 0101) i.e. unbiased exp = 1
    # res: 3F80 => Sign=0; Exp=0x7F; Mant=0x00 (0011 1111 1000 0000)
    # assert res == 0x3F80
    assert res == 17152
    # rtl_tester(inst, data0, data1, res=17152)


@pytest.mark.parametrize(
    "args", [(random_bfloat(), SIntVector.random(DATAWIDTH)) for _ in range(NTESTS)]
)
def test_get_float_int(args):
    fp0 = args[0]
    if is_nan_or_inf(fp0):
        pytest.skip("skipping nan")

    in0 = BFloat(fp0)
    in1 = Data(args[1])
    # output = int(input1) SIGNED, VALID for input1<256.0
    inst = asm.fgetfint()
    fstr = "".join(
        [
            "{:01b}".format(int(fp0.sign)),
            "{:08b}".format(int(fp0.exp)),
            "{:07b}".format(int(fp0.frac)),
        ]
    )
    out = int(bfbin2float(fstr))
    if abs(out) < ((2**8) - 1):
        out_overflow = 0
    else:
        out_overflow = 1
    res, res_p, _, _, _ = pe(inst, in0, in1)
    # assert V==out_overflow
    if out_overflow == 0:
        assert res == out
        rtl_tester(inst, in0, in1, res=out)


def test_get_float_int_targeted():
    # pytest.skip("SKIP");
    inst = asm.fgetfint()
    data0 = Data(0x4020)
    data1 = Data(0x0000)
    res, res_p, _, _, _ = pe(inst, data0, data1)
    # 2.5 = 10.1 i.e. exp = 1 with 1.01 # biased exp = 128 i.e 80
    # float is 0100 0000 0010 0000 i.e. 4020
    # res: int(2.5) =  2
    assert res == 0x2
    assert res_p == 0
    rtl_tester(inst, data0, data1, res=0x2)


@pytest.mark.parametrize(
    "args", [(random_bfloat(), SIntVector.random(DATAWIDTH)) for _ in range(NTESTS)]
)
def test_get_float_frac(args):

    fp0 = args[0]
    if is_nan_or_inf(fp0):
        pytest.skip("skipping nan")

    in0 = BFloat(fp0)
    in1 = Data(args[1])
    # output = frac(input1) SIGNED
    inst = asm.fgetffrac()
    fstr = "".join(
        [
            "{:01b}".format(int(fp0.sign)),
            "{:08b}".format(int(fp0.exp)),
            "{:07b}".format(int(fp0.frac)),
        ]
    )
    frac = bfbin2float(fstr) - int(bfbin2float(fstr))
    out = int(frac * (2**7))
    res, res_p, _, _, _ = pe(inst, in0, in1)
    assert res == out
    rtl_tester(inst, in0, in1, res=out)


def test_get_float_frac_targeted():
    # pytest.skip("SKIP");
    inst = asm.fgetffrac()
    data0 = Data(0x4020)
    data1 = Data(0x0000)
    res, res_p, _, _, _ = pe(inst, data0, data1)
    # 2.5 = 10.1
    # float is 0100 0000 0010 0000 i.e. 4020
    # res: frac(2.5) = 0.5D = 0.1B i.e. 100 0000
    assert res == 0x40
    rtl_tester(inst, data0, data1, res=res)


@pytest.mark.parametrize(
    "args",
    [
        (random.randint(-(2**8), 2**8), BitVector.random(DATAWIDTH))
        for _ in range(NTESTS)
    ],
)
def test_sint_to_float(args):
    inst = asm.fcnvsint2f()
    in0 = SIntVector[16](args[0])
    in1 = args[1]
    correct = BFloat16(float(args[0])).reinterpret_as_bv()
    res, _, _, _, _ = pe(inst, in0, in1)
    assert correct == res
    rtl_tester(inst, in0, in1, res=correct)


@pytest.mark.parametrize(
    "args",
    [(random.randint(0, 2**8), BitVector.random(DATAWIDTH)) for _ in range(NTESTS)],
)
def test_uint_to_float(args):
    inst = asm.fcnvuint2f()
    in0 = UIntVector[16](args[0])
    in1 = args[1]
    correct = BFloat16(float(args[0])).reinterpret_as_bv()
    res, _, _, _, _ = pe(inst, in0, in1)
    assert correct == res
    rtl_tester(inst, in0, in1, res=correct)
