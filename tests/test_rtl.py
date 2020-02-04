from lassen.mode import gen_register_mode
from lassen.alu import ALU_fc
from lassen.cond import Cond_fc
from lassen.sim import PE_fc
import lassen.asm as asm
from hwtypes import BitVector, UIntVector, Bit
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
    _, res_p, _ = PE_fc(Bit.get_family())()(op, x, y)
    rtl_tester(op, x, y, res_p=res_p)
