from collections import namedtuple
import lassen.asm as asm
from lassen.sim import gen_pe
from lassen.isa import DATAWIDTH
from hwtypes import SIntVector, UIntVector, BitVector, Bit, FPVector, RoundingMode
import pytest
import magma
import peak
import fault
import os
import itertools
from peak.auto_assembler import generate_assembler


class HashableDict(dict):
    def __hash__(self):
        return hash(tuple(sorted(self.keys())))


Bit = Bit
Data = BitVector[DATAWIDTH]
BFloat16 = FPVector[8,7,RoundingMode.RNE,False]

pe_ = gen_pe(BitVector.get_family())
pe = pe_()

# create these variables in global space so that we can reuse them easily
pe_magma = gen_pe(magma.get_family())
instr_name, inst_type = pe.__call__._peak_isa_
assembler, disassembler, width, layout = \
            generate_assembler(inst_type)
instr_magma_type = type(pe_magma.interface.ports[instr_name])
pe_circuit = peak.wrap_with_disassembler(pe_magma, disassembler, width,
                                         HashableDict(layout),
                                         instr_magma_type)
tester = fault.Tester(pe_circuit, clock=pe_circuit.CLK)
test_dir = "tests/build"
magma.compile(f"{test_dir}/WrappedPE", pe_circuit, output="coreir-verilog")

def rtl_tester(test_op, data0, data1, bit0=None, res=None, res_p=None):
    tester.clear()
    if hasattr(test_op, "inst"):
        tester.circuit.inst = assembler(test_op.inst)
    else:
        tester.circuit.inst = assembler(test_op)
    tester.circuit.CLK = 0
    data0 = BitVector[16](data0)
    data1 = BitVector[16](data1)
    tester.circuit.data0 = data0
    tester.circuit.data1 = data1
    if bit0 is not None:
        tester.circuit.bit0 = BitVector[1](bit0)
    tester.eval()
    if res is not None:
        tester.circuit.O0.expect(res)
    if res_p is not None:
        tester.circuit.O1.expect(res_p)
    # detect if the PE circuit has been built
    skip_verilator = os.path.isfile(os.path.join(test_dir, "obj_dir",
                                                 "VWrappedPE__ALL.a"))
    tester.compile_and_run(target="verilator",
                           directory=test_dir,
                           flags=['-Wno-UNUSED', '-Wno-PINNOCONNECT'],
                           skip_compile=True,
                           skip_verilator=skip_verilator)


op = namedtuple("op", ["inst", "func"])
NTESTS = 16

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
    rtl_tester(op, x, y, res=res)

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
    rtl_tester(op, x, y, res=res)

@pytest.mark.parametrize("op", [
    op(asm.abs(),  lambda x: x if x > 0 else -x),
])
@pytest.mark.parametrize("args",
    [SIntVector.random(DATAWIDTH) for _ in range(NTESTS) ] )
def test_signed_unary(op, args):
    x = args
    res, _, _ = pe(op.inst, Data(x))
    assert res == op.func(x)
    rtl_tester(op, x, 0, res=res)

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
    rtl_tester(op, x, y, res_p=res_p)

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
    rtl_tester(op, x, y, res_p=res_p)

@pytest.mark.parametrize("args", [
    (UIntVector.random(DATAWIDTH), UIntVector.random(DATAWIDTH))
        for _ in range(NTESTS) ] )
def test_sel(args):
    inst = asm.sel()
    x, y = args
    res, _, _ = pe(inst, Data(x), Data(y), Bit(0))
    assert res==y
    rtl_tester(inst, x, y, Bit(0), res=res)
    res, _, _ = pe(inst, Data(x), Data(y), Bit(1))
    assert res==x
    rtl_tester(inst, x, y, Bit(1), res=res)

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
    rtl_tester(smult0, x, y, res=res)
    res, _, _ = pe(smult1, Data(x), Data(y))
    assert res == xy[DATAWIDTH//2:DATAWIDTH//2+DATAWIDTH]
    rtl_tester(smult1, x, y, res=res)
    res, _, _ = pe(smult2, Data(x), Data(y))
    assert res == xy[DATAWIDTH:]
    rtl_tester(smult2, x, y, res=res)

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
    rtl_tester(umult0, x, y, res=res)
    res, _, _ = pe(umult1, Data(x), Data(y))
    assert res == xy[DATAWIDTH//2:DATAWIDTH//2+DATAWIDTH]
    rtl_tester(umult1, x, y, res=res)
    res, _, _ = pe(umult2, Data(x), Data(y))
    assert res == xy[DATAWIDTH:]
    rtl_tester(umult2, x, y, res=res)

#
# floating point
#

@pytest.mark.parametrize("op", [
    op(asm.fp_add(), lambda x, y: x + y),
    op(asm.fp_sub(), lambda x, y: x - y),
    op(asm.fp_mult(), lambda x, y: x * y)
])
@pytest.mark.parametrize("args", [
    (BFloat16.random(), BFloat16.random())
    for _ in range(NTESTS)])
def test_fp_binary_op(op,args):
    inst = op.inst
    in0 = args[0]
    in1 = args[1]
    out = op.func(in0,in1)
    res, res_p, irq = pe(inst, BFloat16.reinterpret_as_bv(in0), BFloat16.reinterpret_as_bv(in1))
    assert res == BFloat16.reinterpret_as_bv(out)

def BV(val):
    return BFloat16(val)

@pytest.mark.parametrize("xy",
    [(BFloat16.random(), BFloat16.random()) for _ in range(NTESTS)] +
    list(itertools.product(*[[BV(2.0),BV(-2.0),BV(3.0),BV(-3.0)] for _ in range(2)])) +
    list(itertools.product(*[[BV(0),BV('-0'),BV('inf'),BV('-inf')] for _ in range(2)])) +
    list(itertools.product([BV(0),BV('-0'),BV('inf'),BV('-inf')],[BFloat16.random() for _ in range(4)]))
)
@pytest.mark.parametrize("op", [
    op('gt',  lambda x, y: x >  y),
    op('ge',  lambda x, y: x >= y),
    op('lt',  lambda x, y: x <  y),
    op('le',  lambda x, y: x <= y),
    op('eq',  lambda x, y: x == y),
    op('ne',  lambda x, y: x != y),
])
def test_fp_cmp(xy,op):
    inst = getattr(asm,f"fp_{op.inst}")()
    in0,in1 = xy
    out = op.func(in0,in1)
    _, res_p, _ = pe(inst, BFloat16.reinterpret_as_bv(in0), BFloat16.reinterpret_as_bv(in1))
    assert res_p == out

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
    assert res==0x80
    assert res_p==0
    assert irq==0

