from lassen.mode import gen_register_mode
from lassen.alu import ALU_fc
from lassen.cond import Cond_fc
from lassen.sim import PE_fc
import lassen.asm as asm
from hwtypes import BitVector, UIntVector
import magma
import functools
import pdb

#def debug_on(exception):
#    def decorator(f):
#        @functools.wraps(f)
#        def wrapper(*args,**kwargs):
#            try:
#                return f(*args,**kwargs)
#            except exception:
#                pdb.post_mortem(sys.exec_info()[2])
#        return wrapper
#    return decorator

def test_cond():
    Cond_magma = Cond_fc(magma.get_family())

def test_mode():
    rmode_magma = gen_register_mode(BitVector[16], 0)(magma.get_family())

def test_alu():
    ALU_magma = ALU_fc(magma.get_family())

def test_PE():
    PE_magma = PE_fc(magma.get_family())

from rtl_utils import rtl_tester
UData = UIntVector[16]
def test_UGE():
    op = asm.uge()
    x, y = UData(10), UData(5)
    gold = (x >= y)
    rtl_tester(op, x, y, res_p=gold)


#def test_uge
#    @family_closure
#    def PE_fc(family):
#        Bit = family.Bit
#
#        @assemble(family, locals(), globals())
#        class PESimple(Peak, typecheck=True):
#            def __call__(self, in0: Bit, in1: Bit) -> Bit:
#                return in0 & in1
#
#        return PESimple
#
#    #verify BV works
#    PE_bv = PE_fc(Bit.get_family())
#    vals = [Bit(0), Bit(1)]
#    for i0, i1 in itertools.product(vals, vals):
#        assert PE_bv()(i0, i1) == i0 & i1
#
#    #verify SMT works
#    PE_smt = PE_fc(SMTBit.get_family())
#    vals = [SMTBit(0), SMTBit(1), SMTBit(), SMTBit()]
#    for i0, i1 in itertools.product(vals, vals):
#        assert PE_smt()(i0, i1) == i0 & i1
#
#    #verify magma works
#    PE_magma = PE_fc(magma.get_family())
#    print(PE_magma)
#    tester = fault.Tester(PE_magma)
#    vals = [0, 1]
#    for i0, i1 in itertools.product(vals, vals):
#        tester.circuit.in0 = i0
#        tester.circuit.in1 = i1
#        tester.eval()
#        tester.circuit.O.expect(i0 & i1)
#    tester.compile_and_run("verilator", flags=["-Wno-fatal"])

