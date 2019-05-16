from collections import namedtuple
import operator
import lassen.asm as asm
from lassen.sim import gen_pe
from lassen.isa import DATAWIDTH
from lassen.utils import float2bfbin, bfbin2float, get_random_float
from hwtypes import SIntVector, UIntVector, BitVector, Bit
import pytest
import math
import random

Bit = Bit
Data = BitVector[DATAWIDTH]

random.seed(10)
pe = gen_pe(BitVector.get_family())()
op = namedtuple("op", ["inst", "func"])

NTESTS = 16

def bfloat16(sign, exponent, mantissa):
    sign &= 0x1
    exponent &= 0xff
    mantissa &= 0x7f
    return Data((sign << 15) | (exponent << 7) | mantissa)

@pytest.mark.parametrize("op", [
    op(asm.and_(),  lambda x, y: x&y),
    op(asm.or_(),   lambda x, y: x|y),
    op(asm.xor(),   lambda x, y: x^y),
    op(asm.add(),   lambda x, y: x+y),
    op(asm.sub(),   lambda x, y: x-y),
    op(asm.lsl(),   lambda x, y: x << y),
    op(asm.lsr(),   lambda x, y: x >> y),
    op(asm.umin(),  lambda x, y: (x < y).ite(x, y)),
    op(asm.umax(),  lambda x, y: (x > y).ite(x, y))
])
@pytest.mark.parametrize("args", [
    (UIntVector.random(DATAWIDTH), UIntVector.random(DATAWIDTH))
        for _ in range(NTESTS) ] )
def test_unsigned_binary(op, args):
    x, y = args
    res, _, _ = pe(op.inst, Data(x), Data(y))
    assert res==op.func(x,y)

@pytest.mark.parametrize("op", [
    op(asm.lsl(),   lambda x, y: x << y),
    op(asm.asr(),   lambda x, y: x >> y),
    op(asm.smin(),  lambda x, y: (x < y).ite(x, y)),
    op(asm.smax(),  lambda x, y: (x > y).ite(x, y)),
])
@pytest.mark.parametrize("args", [
    (SIntVector.random(DATAWIDTH), SIntVector.random(DATAWIDTH))
        for _ in range(NTESTS) ] )
def test_signed_binary(op, args):
    x, y = args
    res, _, _ = pe(op.inst, Data(x), Data(y))
    assert res==op.func(x,y)

@pytest.mark.parametrize("op", [
    op(asm.abs(),  lambda x: x if x > 0 else -x),
])
@pytest.mark.parametrize("args",
    [SIntVector.random(DATAWIDTH) for _ in range(NTESTS) ] )
def test_signed_unary(op, args):
    x = args
    res, _, _ = pe(op.inst, Data(x))
    assert res == op.func(x)

@pytest.mark.parametrize("op", [
    op(asm.eq(),   lambda x, y: x == y),
    op(asm.ne(),   lambda x, y: x != y),
    op(asm.ugt(),  lambda x, y: x >  y),
    op(asm.uge(),  lambda x, y: x >= y),
    op(asm.ult(),  lambda x, y: x <  y),
    op(asm.ule(),  lambda x, y: x <= y),
])
@pytest.mark.parametrize("args", [
    (UIntVector.random(DATAWIDTH), UIntVector.random(DATAWIDTH))
        for _ in range(NTESTS) ] )
def test_unsigned_relation(op, args):
    x, y = args
    _, res_p, _ = pe(op.inst, Data(x), Data(y))
    assert res_p==op.func(x,y)

@pytest.mark.parametrize("op", [
    op(asm.sgt(),  lambda x, y: x >  y),
    op(asm.sge(),  lambda x, y: x >= y),
    op(asm.slt(),  lambda x, y: x <  y),
    op(asm.sle(),  lambda x, y: x <= y),
])
@pytest.mark.parametrize("args", [
    (SIntVector.random(DATAWIDTH), SIntVector.random(DATAWIDTH))
        for _ in range(NTESTS) ] )
def test_signed_relation(op, args):
    x, y = args
    _, res_p, _ = pe(op.inst, Data(x), Data(y))
    assert res_p==op.func(x,y)

@pytest.mark.parametrize("args", [
    (UIntVector.random(DATAWIDTH), UIntVector.random(DATAWIDTH))
        for _ in range(NTESTS) ] )
def test_sel(args):
    inst = asm.sel()
    x, y = args
    res, _, _ = pe(inst, Data(x), Data(y), Bit(0))
    assert res==y
    res, _, _ = pe(inst, Data(x), Data(y), Bit(1))
    assert res==x

@pytest.mark.parametrize("args", [
    (SIntVector.random(DATAWIDTH), SIntVector.random(DATAWIDTH))
        for _ in range(NTESTS) ] )
def test_smult(args):
    def mul(x,y):
        mulx, muly = x.sext(DATAWIDTH), y.sext(DATAWIDTH)
        return mulx * muly
    smult0 = asm.smult0()
    smult1 = asm.smult1()
    smult2 = asm.smult2()
    x, y = args
    xy = mul(x,y)
    res, _, _ = pe(smult0, Data(x), Data(y))
    assert res == xy[0:DATAWIDTH]
    res, _, _ = pe(smult1, Data(x), Data(y))
    assert res == xy[DATAWIDTH//2:DATAWIDTH//2+DATAWIDTH]
    res, _, _ = pe(smult2, Data(x), Data(y))
    assert res == xy[DATAWIDTH:]

@pytest.mark.parametrize("args", [
    (UIntVector.random(DATAWIDTH), UIntVector.random(DATAWIDTH))
        for _ in range(NTESTS) ] )
def test_umult(args):
    def mul(x,y):
        mulx, muly = x.zext(DATAWIDTH), y.zext(DATAWIDTH)
        return mulx * muly
    umult0 = asm.umult0()
    umult1 = asm.umult1()
    umult2 = asm.umult2()
    x, y = args
    xy = mul(x,y)
    res, _, _ = pe(umult0, Data(x), Data(y))
    assert res == xy[0:DATAWIDTH]
    res, _, _ = pe(umult1, Data(x), Data(y))
    assert res == xy[DATAWIDTH//2:DATAWIDTH//2+DATAWIDTH]
    res, _, _ = pe(umult2, Data(x), Data(y))
    assert res == xy[DATAWIDTH:]

def test_fp_add():
    pe = gen_pe(BitVector.get_family())()
    inst = asm.fp_add()
    # [sign, exponent (decimal), mantissa (binary)]:
    # a   = [0, -111, 1.0000001]
    # b   = [0, -112, 1.0000010]
    # res = [0, -111, 1.1000010]
    res, res_p, irq = pe(inst, Data(0x801),Data(0x782))
    assert res==0x842
    assert res_p==0
    assert irq==0

def test_fp_add2():
    pe = gen_pe(BitVector.get_family())()
    inst = asm.fp_add()
    in0 = Data(int(float2bfbin(2.0)))
    in1 = Data(int(float2bfbin(3.0)))
    out = Data(int(float2bfbin(5.0)))
    print(in0.as_binary_string())
    print(in1.as_binary_string())
    print(out.as_binary_string())
    res, res_p, irq = pe(inst, in0,in1)
    assert res==out
    assert res_p==0
    assert irq==0

def test_fp_sub():
    pe = gen_pe(BitVector.get_family())()
    inst = asm.fp_add()
    in0 = Data(int(float2bfbin(2.0)))
    in1 = Data(int(float2bfbin(3.0)))
    out = Data(int(float2bfbin(-1.0)))
    print(in0.as_binary_string())
    print(in1.as_binary_string())
    print(out.as_binary_string())
    res, res_p, irq = pe(inst, in0,in1)
    assert res==out
    assert res_p==0
    assert irq==0


def test_fp_mult():
    pe = gen_pe(BitVector.get_family())()
    inst = asm.fp_mult()
    # [sign, exponent (decimal), mantissa (binary)]:
    # a   = [0, 2, 1.0000000]
    # b   = [0, 1, 1.0000001]
    # res = [0, 3, 1.0000001]
    # mant = mant(a) * mant(b)
    # exp = exp(a) + exp(b)
    res, res_p, irq = pe(inst, Data(0x4080),Data(0x4001))
    assert res==0x4101
    assert res_p==0
    assert irq==0


#TODO these tests are likely captured by the tests above. Keep them for now
def test_lsl():
    pe = gen_pe(BitVector.get_family())()
    inst = asm.lsl()
    res, res_p, irq = pe(inst, Data(2),Data(1))
    assert res==4
    assert res_p==0
    assert irq==0

def test_lsr():
    pe = gen_pe(BitVector.get_family())()
    inst = asm.lsr()
    res, res_p, irq = pe(inst, Data(2),Data(1))
    assert res==1
    assert res_p==0
    assert irq==0

def test_asr():
    pe = gen_pe(BitVector.get_family())()
    inst = asm.asr()
    res, res_p, irq = pe(inst, Data(-2),Data(1))
    assert res==65535
    assert res_p==0
    assert irq==0

def test_sel():
    pe = gen_pe(BitVector.get_family())()
    inst = asm.sel()
    res, res_p, irq = pe(inst, Data(1),Data(2),Bit(0))
    assert res==2
    assert res_p==0
    assert irq==0

def test_umin():
    pe = gen_pe(BitVector.get_family())()
    inst = asm.umin()
    res, res_p, irq = pe(inst,Data(1),Data(1))
    assert res_p == 1
    res, res_p, _ = pe(inst, Data(1), Data(2))
    assert res_p == 1
    res, res_p, _ = pe(inst, Data(2), Data(1))
    assert res_p == 0

def test_umax():
    pe = gen_pe(BitVector.get_family())()
    inst = asm.umax()
    res, res_p, irq = pe(inst, Data(1), Data(2))
    assert res == 2
    assert res_p == 0
    res, res_p, irq = pe(inst, Data(2), Data(1))
    assert res == 2
    assert res_p == 1

def test_smin():
    pe = gen_pe(BitVector.get_family())()
    inst = asm.smin()
    res, res_p, irq = pe(inst, Data(-1), Data(2))
    assert res == Data(-1)
    assert res_p == 1
    res, res_p, irq = pe(inst, Data(2), Data(-1))
    assert res == Data(-1)
    assert res_p == 0
    res, res_p, irq = pe(inst, Data(-1), Data(-1))
    assert res == Data(-1)
    assert res_p == 1

def test_smax():
    pe = gen_pe(BitVector.get_family())()
    inst = asm.smax()
    res, res_p, irq = pe(inst, Data(-1), Data(2))
    assert res == 2
    assert res_p == 0
    res, res_p, irq = pe(inst, Data(2), Data(-1))
    assert res == 2
    assert res_p == 1
    res, res_p, irq = pe(inst, Data(-1), Data(-1))
    assert res == Data(-1)
    assert res_p == 1

def test_abs():
    pe = gen_pe(BitVector.get_family())()
    inst = asm.abs()
    res, res_p, irq = pe(inst,Data(-1))
    assert res==1
    assert res_p==0
    assert irq==0

def test_eq():
    pe = gen_pe(BitVector.get_family())()
    inst = asm.eq()
    res, res_p, irq = pe(inst,Data(1),Data(1))
    assert res_p==1

def test_ne():
    pe = gen_pe(BitVector.get_family())()
    inst = asm.ne()
    res, res_p, irq = pe(inst,Data(1),Data(1))
    assert res_p==0

def test_uge():
    pe = gen_pe(BitVector.get_family())()
    inst = asm.uge()
    res, res_p, irq = pe(inst,Data(1),Data(1))
    assert res_p==1

def test_ule():
    pe = gen_pe(BitVector.get_family())()
    inst = asm.ule()
    res, res_p, irq = pe(inst,Data(1),Data(1))
    assert res_p == 1
    res, res_p, _ = pe(inst, Data(1), Data(2))
    assert res_p == 1
    res, res_p, _ = pe(inst, Data(2), Data(1))
    assert res_p == 0

def test_ugt():
    pe = gen_pe(BitVector.get_family())()
    inst = asm.ugt()
    res, res_p, irq = pe(inst,Data(1),Data(1))
    assert res_p==0

def test_ult():
    pe = gen_pe(BitVector.get_family())()
    inst = asm.ult()
    res, res_p, irq = pe(inst,Data(1),Data(1))
    assert res_p==0

def test_sge():
    pe = gen_pe(BitVector.get_family())()
    inst = asm.sge()
    res, res_p, irq = pe(inst,Data(1),Data(1))
    assert res_p==1

def test_sle():
    pe = gen_pe(BitVector.get_family())()
    inst = asm.sle()
    res, res_p, irq = pe(inst,Data(1),Data(1))
    assert res_p==1

def test_sgt():
    pe = gen_pe(BitVector.get_family())()
    inst = asm.sgt()
    res, res_p, irq = pe(inst,Data(1),Data(1))
    assert res_p==0

def test_slt():
    pe = gen_pe(BitVector.get_family())()
    inst = asm.slt()
    res, res_p, irq = pe(inst,Data(1),Data(1))
    assert res_p==0

#
# floating point
#

def test_fp_add():
    inst = asm.fp_add()
    # [sign, exponent (decimal), mantissa (binary)]:
    # a   = [0, -111, 1.0000001]
    # b   = [0, -112, 1.0000010]
    # res = [0, -111, 1.1000010]
    res, res_p, irq = pe(inst, Data(0x801),Data(0x782))
    assert res==0x842
    assert res_p==0
    assert irq==0

def test_fp_mult():
    inst = asm.fp_mult()
    # [sign, exponent (decimal), mantissa (binary)]:
    # a   = [0, 2, 1.0000000]
    # b   = [0, 1, 1.0000001]
    # res = [0, 3, 1.0000001]
    # mant = mant(a) * mant(b)
    # exp = exp(a) + exp(b)
    res, res_p, irq = pe(inst, Data(0x4080),Data(0x4001))
    assert res==0x4101
    assert res_p==0
    assert irq==0

def test_get_mant():
    inst = asm.fgetmant()
    res, res_p, irq = pe(inst, Data(0x7F8A), Data(0x0000))
    assert res==0xA
    assert res_p==0
    assert irq==0

def test_add_exp_imm():
    inst = asm.faddiexp()
    res, res_p, irq = pe(inst, Data(0x7F8A), Data(0x0005))
    # 7F8A => Sign=0; Exp=0xFF; Mant=0x0A
    # Add 5 to exp => Sign=0; Exp=0x04; Mant=0x0A i.e. float  = 0x020A
    assert res==0x020A
    assert res_p==0
    assert irq==0

def test_sub_exp():
    inst = asm.fsubexp()
    res, res_p, irq = pe(inst, Data(0x7F8A), Data(0x4005))
    # 7F8A => Sign=0; Exp=0xFF; Mant=0x0A
    # 4005 => Sign=0; Exp=0x80; Mant=0x05 (0100 0000 0000 0101)
    # res: 7F0A => Sign=0; Exp=0xFE; Mant=0x0A (0111 1111 0000 1010)
    assert res==0x7F0A
    assert res_p==0
    assert irq==0

def test_cnvt_exp_to_float():
    inst = asm.fcnvexp2f()
    res, res_p, irq = pe(inst, Data(0x4005), Data(0x0000))
    # 4005 => Sign=0; Exp=0x80; Mant=0x05 (0100 0000 0000 0101) i.e. unbiased exp = 1
    # res: 3F80 => Sign=0; Exp=0x7F; Mant=0x00 (0011 1111 1000 0000)
    assert res==0x3F80
    assert res_p==0
    assert irq==0

def test_get_float_int():
    inst = asm.fgetfint()
    res, res_p, irq = pe(inst, Data(0x4020), Data(0x0000))
    #2.5 = 10.1 i.e. exp = 1 with 1.01 # biased exp = 128 i.e 80
    #float is 0100 0000 0010 0000 i.e. 4020
    # res: int(2.5) =  2
    assert res==0x2
    assert res_p==0
    assert irq==0

def test_get_float_frac():
    inst = asm.fgetffrac()
    res, res_p, irq = pe(inst, Data(0x4020), Data(0x0000))
    #2.5 = 10.1 i.e. exp = 1 with 1.01 # biased exp = 128 i.e 80
    #float is 0100 0000 0010 0000 i.e. 4020
    # res: frac(2.5) = 0.5D = 0.1B i.e. 1000 0000
    assert res==0x40
    assert res_p==0
    assert irq==0

def test_int_to_float():
    test_vectors = []
    for vector_count in range(50):
      num            = int(math.floor(get_random_float(3)))
      num_bfloat_str = float2bfbin(float(num))
      min_accuracy = 2
      test_vectors.append([num, float2bfbin(0),num_bfloat_str, min_accuracy])

    test_vectors.append([2, float2bfbin(0), float2bfbin(2.0), min_accuracy])
    test_vectors.append([1, float2bfbin(0), float2bfbin(1.0), min_accuracy])
    test_vectors.append([0, float2bfbin(0), float2bfbin(0.0), min_accuracy])
    test_vectors.append([-9, float2bfbin(0), float2bfbin(-9.0), min_accuracy])
    # START_TEST result = i2f(op_a)
    pe_signed  = gen_pe(BitVector.get_family())()
    inst1 = asm.fcnvsi2f()

    for test_vector in test_vectors:
      op_a    = Data(test_vector[0])
      op_b    = Data(int(test_vector[1],2))
      exp_res =      int(test_vector[2],2)
      acc     =          test_vector[3]

      result         ,d1, d2   = pe_signed(inst1, op_a, op_b)
      assert abs(exp_res-int(result)) <= acc
