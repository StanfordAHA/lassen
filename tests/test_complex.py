from lassen.stdlib.fma import gen_FMA
from lassen.isa import DATAWIDTH
from hwtypes import BitVector, Bit
from lassen.utils import float2bfbin, bfbin2float, get_random_float
from hwtypes import BitVector, Bit, SIntVector
from lassen.sim import gen_pe
import pytest
from lassen.tlut import tlut
import lassen.asm as asm
import math
import random


#Hack
#random.seed(10)

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

def test_div():
    test_vectors = []
    for vector_count in range(50):
        divident_sp = get_random_float()
        divisor_sp = get_random_float()
        divident_bfloat_str = float2bfbin(divident_sp)
        divisor_bfloat_str = float2bfbin(divisor_sp)
        divident_bfp = bfbin2float(divident_bfloat_str)
        divisor_bfp = bfbin2float(divisor_bfloat_str)
        quotient_bfp = bfbin2float(float2bfbin(divident_bfp / divisor_bfp))
        quotient_bfloat_str = float2bfbin(quotient_bfp)
        min_accuracy = 2
        test_vectors.append(
            [divident_bfloat_str, divisor_bfloat_str, quotient_bfloat_str, min_accuracy])

    # START_TEST result = op_a / op_b
    pe_get_mant = gen_pe(BitVector.get_family())()
    mem_lut = tlut()
    pe_scale_res = gen_pe(BitVector.get_family())()
    pe_mult = gen_pe(BitVector.get_family())()

    inst1 = asm.fgetmant()
    inst2 = asm.fsubexp()
    inst3 = asm.fp_mult()

    for test_vector in test_vectors:
        op_a = Data(int(test_vector[0], 2))
        op_b = Data(int(test_vector[1], 2))
        exp_res = int(test_vector[2], 2)
        acc = test_vector[3]

        mant, d1, d2 = pe_get_mant(inst1, op_b, Data(0))
        lookup_result = mem_lut.div_lut(mant)
        scaled_result, d3, d4 = pe_scale_res(inst2, lookup_result, op_b)
        result, d5, d6 = pe_mult(inst3, scaled_result, op_a)

        print("div", bfbin2float(test_vector[0]), bfbin2float(test_vector[1]), bfbin2float(
            test_vector[2]), bfbin2float("{:016b}".format(int(result))))
        assert abs(exp_res-int(result)) <= acc

def test_ln():
    test_vectors = []
    for vector_count in range(50):
        num = math.fabs(get_random_float())
        num_bfloat_str = float2bfbin(num)
        num_bfp = bfbin2float(num_bfloat_str)
        res_bfp = bfbin2float(float2bfbin(math.log(num_bfp)))
        res_bfloat_str = float2bfbin(res_bfp)
        min_accuracy = 3
        test_vectors.append(
            [num_bfloat_str, float2bfbin(0), res_bfloat_str, min_accuracy])

    test_vectors.append([float2bfbin(2.0), float2bfbin(
        0), float2bfbin(math.log(2)), min_accuracy])
    # START_TEST result = ln(op_a)
    pe_get_mant = gen_pe(BitVector.get_family())()
    pe_get_exp = gen_pe(BitVector.get_family())()
    mem_lut = tlut()
    pe_mult = gen_pe(BitVector.get_family())()
    pe_add = gen_pe(BitVector.get_family())()

    inst1 = asm.fgetmant()
    inst2 = asm.fcnvexp2f()
    inst3 = asm.fp_mult()
    inst4 = asm.fp_add()

    ln2 = math.log(2)
    ln2_bf = int(float2bfbin(ln2), 2)

    for test_vector in test_vectors:
        op_a = Data(int(test_vector[0], 2))
        op_b = Data(int(test_vector[1], 2))
        exp_res = int(test_vector[2], 2)
        acc = test_vector[3]

        const1 = Data(ln2_bf)

        mant, d1, d2 = pe_get_mant(inst1, op_a, op_b)
        fexp, d1, d2 = pe_get_exp(inst2, op_a, op_b)
        lut_res = mem_lut.ln_lut(mant)
        mult, d1, d2 = pe_mult(inst3, fexp, const1)
        result, d1, d2 = pe_mult(inst4, Data(lut_res), mult)
        print("ln", bfbin2float(test_vector[0]), bfbin2float(test_vector[1]), bfbin2float(
            test_vector[2]), bfbin2float("{:016b}".format(int(result))))
        assert abs(exp_res-int(result)) <= acc

def test_exp():
    test_vectors = []
    for vector_count in range(50):
        num = get_random_float(2)
        num_bfloat_str = float2bfbin(num)
        num_bfp = bfbin2float(num_bfloat_str)
        res_bfp = bfbin2float(float2bfbin(math.exp(num_bfp)))
        res_bfloat_str = float2bfbin(res_bfp)
        min_accuracy = 3
        test_vectors.append(
            [num_bfloat_str, float2bfbin(0), res_bfloat_str, min_accuracy])

    test_vectors.append([float2bfbin(2.0), float2bfbin(
        0), float2bfbin(math.exp(2)), min_accuracy])
    test_vectors.append([float2bfbin(-2.0), float2bfbin(0),
                         float2bfbin(math.exp(-2)), min_accuracy])
    test_vectors.append([float2bfbin(1.0), float2bfbin(
        0), float2bfbin(math.exp(1.0)), min_accuracy])
    test_vectors.append([float2bfbin(0.0), float2bfbin(
        0), float2bfbin(math.exp(0)), min_accuracy])
    test_vectors.append([float2bfbin(-10.0), float2bfbin(0),
                         float2bfbin(math.exp(-10)), min_accuracy])
    test_vectors.append([float2bfbin(5.0), float2bfbin(
        0), float2bfbin(math.exp(5)), min_accuracy])
    # START_TEST result = exp(op_a)
    pe_get_int = gen_pe(BitVector.get_family())()
    pe_get_frac = gen_pe(BitVector.get_family())()
    mem_lut = tlut()
    pe_incr_exp = gen_pe(BitVector.get_family())()

    pe_div_mult = gen_pe(BitVector.get_family())()

    ln2_inv = 1.4453125  # 1.0/math.log(2)
    ln2_inv_bf = int(float2bfbin(ln2_inv), 2)
    const1 = Data(ln2_inv_bf)

    for test_vector in test_vectors:
        op_a = Data(int(test_vector[0], 2))
        op_b = Data(int(test_vector[1], 2))
        exp_res = int(test_vector[2], 2)
        acc = test_vector[3]

        # Perform op_a/ln(2)
        inst1 = asm.fp_mult()
        div_res, d5, d6 = pe_div_mult(inst1, const1, op_a)

        # Compute 2**op_a
        inst2 = asm.fgetfint()
        inst3 = asm.fgetffrac()
        inst4 = asm.faddiexp()

        fint, d1, d2 = pe_get_int(inst2, div_res, op_b)
        ffrac, d1, d2 = pe_get_frac(inst3, div_res, op_b)
        lut_res = mem_lut.exp_lut(ffrac)
        result, d1, d2 = pe_incr_exp(inst4, lut_res, fint)
        print("exp", bfbin2float(test_vector[0]), bfbin2float(test_vector[1]), bfbin2float(
            test_vector[2]), bfbin2float("{:016b}".format(int(result))))
        assert abs(exp_res-int(result)) <= acc
