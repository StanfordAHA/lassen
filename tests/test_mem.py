import lassen.mem as Mem
from hwtypes import BitVector
import coreir
import metamapper as mm
import pytest


def test_rom():
    c = coreir.Context()
    mapper = mm.PeakMapper(c,"pe_ns")
    
    mem = mapper.add_peak_primitive("MEM",Mem.gen_mem)
    
    rom = c.get_namespace("memory").generators['rom2'](width=16,depth=1024)

    def instr_lambda(inst):
        init_json = inst.config["init"].value
        print(init_json)
        assert 0

    #Adds a simple "1 to 1" rewrite rule
    mapper.add_rewrite_rule(mm.Peak1to1(
        rom,
        mem,
        instr_lambda,
        dict(
            rdata = "rdata",
            raddr = "ain",
            ren = "ren"
        )
    ))
    
    app = c.load_from_file("tests/examples/rom.json")
    mapper.map_app(app)
    imap = mapper.extract_instr_map(app)
    assert len(imap) == 3

test_rom()
