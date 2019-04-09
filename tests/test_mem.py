import lassen.mem as mem 
from hwtypes import BitVector
import coreir
import metamapper as mm
import pytest

      {"clk", c->Named("coreir.clkIn")},
      {"rdata", c->Bit()->Arr(width)},
      {"raddr", c->BitIn()->Arr(awidth)},
      {"ren", c->BitIn()},


def test_mem_rr():
    c = coreir.Context()
    mapper = mm.PeakMapper(c,"pe_ns")
    
    mem = mapper.add_peak_primitive("MEM",mem.gen_mem)
    
    rom = c.get_namespace("memory").generators['rom2'](width=16,depth=1024)

    def instr_lambda(inst):
        init_json = inst.config["init"].value
        return asm.const(cval)
        
    #Adds a simple "1 to 1" rewrite rule
    mapper.add_rewrite_rule(mm.Peak1to1(
        rom,
        PE,
        instr_lambda,
        dict(out="alu_res")
    ))
 

def 
