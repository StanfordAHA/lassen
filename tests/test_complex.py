from lassen.stdlib.fma import gen_FMA
from lassen.stdlib.fpops import gen_fdiv, gen_fln, gen_fexp
from collections import namedtuple
from lassen.stdlib import gen_FMA, gen_Add32, gen_Sub32
from lassen.isa import DATAWIDTH
from hwtypes import BitVector, Bit, SIntVector
from lassen.sim import gen_pe
from lassen.utils import float2bfbin, bfbin2float
import pytest
import lassen.asm as asm
import math
import random

Bit = Bit
Data = BitVector[DATAWIDTH]
SData = SIntVector[DATAWIDTH]
Data32 = SIntVector[DATAWIDTH*2]

NTESTS = 16

FMA = gen_FMA(BitVector.get_family())
DIV = gen_fdiv(BitVector.get_family())
LN  = gen_fln(BitVector.get_family())
EXP = gen_fexp(BitVector.get_family())
Add32 = gen_Add32(BitVector.get_family())
Sub32 = gen_Sub32(BitVector.get_family())

@pytest.mark.parametrize("args", [
    (random.randint(-10,10),
     random.randint(-10,10),
     random.randint(-10,10))
    for _ in range(NTESTS) ] )
def test_fma(args):
    fma = FMA()
    assert SData(args[0]*args[1]+args[2]) == fma(SData(args[0]), SData(args[1]), SData(args[2]))

def get_random_float(power_range = 50):
    sign = -1 if (random.random() < 0.5) else 1
    mant = float(random.random()+1.0)
    power = (-1 * power_range) + int(random.random()*(power_range * 2))
    res = sign * mant * float((2**power))
    return res

def test_div():
    test_vectors = []
    eps = (2**-8)
    #Corner case test vectors
    #Random test vectors
    for vector_count in range(200):
        divident_sp = get_random_float()
        divisor_sp = get_random_float()
        divident_bfloat_str = float2bfbin(divident_sp)
        divisor_bfloat_str = float2bfbin(divisor_sp)
        divident_bfp = bfbin2float(divident_bfloat_str)
        divisor_bfp = bfbin2float(divisor_bfloat_str)
        quotient = bfbin2float(float2bfbin(divident_bfp / divisor_bfp))
        quotient_bfloat_str = float2bfbin(quotient)

        divisor_exp = int(divisor_bfloat_str[1:9],2)-127
        max_error =  2*math.fabs(eps*(divident_bfp/divisor_bfp))
        test_vectors.append(
            [divident_bfloat_str, divisor_bfloat_str, quotient_bfloat_str, max_error])

    #result = op_a / op_b
    for test_vector in test_vectors:
        op_a = Data(int(test_vector[0], 2))
        op_b = Data(int(test_vector[1], 2))
        exp_res = int(test_vector[2], 2)
        max_error = test_vector[3]
        div = DIV()
        result = div(op_a, op_b)
        golden_res = bfbin2float(test_vector[2])
        actual_res = bfbin2float("{:016b}".format(int(result)))
        delta = math.fabs(golden_res - actual_res)
        #print("div", bfbin2float(test_vector[0]), bfbin2float(test_vector[1]),
        #      golden_res,actual_res,delta,max_error)
        assert delta <= max_error

def test_ln():
    test_vectors = []
    eps = (2**-8)
    #Corner case test vectors
    test_vectors.append([float2bfbin(2.0), float2bfbin(0), float2bfbin(math.log(2)), 2*eps])
    #Random test vectors
    for vector_count in range(200):
        num = math.fabs(get_random_float())
        num_bfloat_str = float2bfbin(num)
        num_bfp = bfbin2float(num_bfloat_str)
        res = bfbin2float(float2bfbin(math.log(num_bfp)))
        res_bfloat_str = float2bfbin(res)

        num_exp = int(num_bfloat_str[1:9],2)-127
        res_exp = int(res_bfloat_str[1:9],2)-127
        max_error =  2*(eps + math.fabs(eps*num_exp) + eps)
        test_vectors.append([num_bfloat_str, float2bfbin(0), res_bfloat_str,max_error])

    #result = ln(op_a)
    for test_vector in test_vectors:
        op_a = Data(int(test_vector[0], 2))
        op_b = Data(int(test_vector[1], 2))
        exp_res = int(test_vector[2], 2)
        max_error = test_vector[3]

        ln = LN()
        result = ln(op_a)
        golden_res = bfbin2float(test_vector[2])
        actual_res = bfbin2float("{:016b}".format(int(result)))
        delta = math.fabs(golden_res - actual_res)
        #print("ln", bfbin2float(test_vector[0]), bfbin2float(test_vector[1]),
        #      golden_res,actual_res,delta, max_error)

        assert delta <= max_error

def test_exp():
    test_vectors = []
    eps = (2**-8)
    #Corner case test vectors
    test_vectors.append([float2bfbin(2.0), float2bfbin(
        0), float2bfbin(math.exp(2)), 3])
    test_vectors.append([float2bfbin(-2.0), float2bfbin(0),
                         float2bfbin(math.exp(-2)), 3])
    test_vectors.append([float2bfbin(1.0), float2bfbin(
        0), float2bfbin(math.exp(1.0)), 3])
    test_vectors.append([float2bfbin(0.0), float2bfbin(
        0), float2bfbin(math.exp(0)), 3])
    test_vectors.append([float2bfbin(-10.0), float2bfbin(0),
                         float2bfbin(math.exp(-10)), 3])
    test_vectors.append([float2bfbin(5.0), float2bfbin(
        0), float2bfbin(math.exp(5)), 3])

    #Random test vectors    
    for vector_count in range(50):
        num = get_random_float(4)
        num_bfloat_str = float2bfbin(num)
        num_bfp = bfbin2float(num_bfloat_str)
        res_bfp = bfbin2float(float2bfbin(math.exp(num_bfp)))
        res_bfloat_str = float2bfbin(res_bfp)
        max_error = 2.0*res_bfp*(math.fabs(2**(2*num*eps)-1) + eps)
        test_vectors.append(
            [num_bfloat_str, float2bfbin(0), res_bfloat_str, max_error])

    #result = exp(op_a)
    for test_vector in test_vectors:
        op_a = Data(int(test_vector[0], 2))
        op_b = Data(int(test_vector[1], 2))
        exp_res = int(test_vector[2], 2)
        max_error = test_vector[3]

        exp = EXP()
        result = exp(op_a)
        golden_res = bfbin2float(test_vector[2])
        actual_res = bfbin2float("{:016b}".format(int(result)))
        delta = math.fabs(golden_res - actual_res)
        #print("ln", bfbin2float(test_vector[0]), bfbin2float(test_vector[1]),
        #      golden_res,actual_res,delta, max_error)

        assert delta <= max_error

def test_add32_targeted():
    add32 = Add32()
    assert Data32(10) == add32(Data32(2),Data32(8))
    assert Data32(100000) == add32(Data32(20000),Data32(80000))
    assert Data32(2**17-2) == add32(Data32(2**16-1),Data32(2**16-1))
    assert Data32(2**31-2) == add32(Data32(2**30-1),Data32(2**30-1))

op = namedtuple("op", ["complex", "func"])
@pytest.mark.parametrize("op",[
    op(Add32,lambda x, y : x + y),
    op(Sub32,lambda x, y : x - y),
])
@pytest.mark.parametrize("args", [
    (SIntVector.random(32),SIntVector.random(32))
        for _ in range(NTESTS)
])
def test_addsub(op,args):
    cop = op.complex()
    in0 = args[0]
    in1 = args[1]
    res = cop(in0,in1)
    assert res == op.func(in0,in1)

