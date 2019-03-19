from lassen.sim import gen_pe
from hwtypes import BitVector
import coreir
import metamapper as mm
import pytest


#@pytest.mark.skip("This takes a long time")
def test_discover():
    c = coreir.Context()
    mapper = mm.PeakMapper(c,"pe_ns")
    Alu = mapper.add_peak_primitive("PE",gen_pe)
    
    def bypass_mode(inst):
        return (
            inst.rega == type(inst.rega).BYPASS and
            inst.regb == type(inst.regb).BYPASS and
            inst.regd == type(inst.regd).BYPASS and
            inst.rege == type(inst.rege).BYPASS and 
            inst.regf == type(inst.regf).BYPASS and
            (inst.cond == type(inst.cond).Z or inst.cond == type(inst.cond).Z_n)
        )
    mapper.add_discover_constraint(bypass_mode)
    
    mapper.discover_peak_rewrite_rules(width=16)
    #test the mapper on simple add4 app
    app = c.load_from_file("tests/add4.json")
    print(app)
    print("instance map",mapper.map_app(app))
    c.run_passes(['printer'])

def test_io():
    c = coreir.Context()
    mapper = mm.PeakMapper(c,"alu_ns")
    #This adds a peak primitive 
    io16 = mapper.add_io_primitive("io16",16,"tofab","fromfab")
    mapper.add_rewrite_rule(mm.PeakIO(
        width=16,
        is_input=True,
        io_prim=io16
    ))
    mapper.add_rewrite_rule(mm.PeakIO(
        width=16,
        is_input=False,
        io_prim=io16
    ))
    Alu = mapper.add_peak_primitive("PE",gen_pe)
    def bypass_mode(inst):
        return (
            inst.rega == type(inst.rega).BYPASS and
            inst.regb == type(inst.regb).BYPASS and
            inst.regd == type(inst.regd).BYPASS and
            inst.rege == type(inst.rege).BYPASS and 
            inst.regf == type(inst.regf).BYPASS and
            inst.cond == type(inst.cond).Z
        )
    mapper.add_discover_constraint(bypass_mode)
    mapper.discover_peak_rewrite_rules(width=16,coreir_primitives=["add"])
    app = c.load_from_file("tests/add4.json")
    print("instance map",mapper.map_app(app))
    app.save_to_file("tests/_mapped_add4.json")
    app.print_()

#test_discover()
#test_io()
