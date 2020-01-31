from lassen.mode import gen_register_mode
from lassen.alu import ALU_fc
from lassen.cond import Cond_fc
from lassen.sim import PE_fc
from hwtypes import BitVector
import magma


def test_cond():
    Cond_magma = Cond_fc(magma.get_family())

def test_mode():
    rmode_magma = gen_register_mode(BitVector[16], 0)(magma.get_family())

def test_alu():
    ALU_magma = ALU_fc(magma.get_family())

def test_PE():
    PE_magma = PE_fc(magma.get_family())

#
#from lassen import PE
#def test_rtl():
#    PE_magma = compile_to_magma(PE)
#    print(PE_magma)
