from lassen.sim import PE
from lassen.isa import Inst
from hwtypes import BitVector
import coreir
import metamapper as mm

def ttest_discover():
    c = coreir.Context()
    mapper = mm.PeakMapper(c,"pe_ns")
    Alu = mapper.add_peak_primitive("PE",PE)
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
    Alu = mapper.add_peak_primitive("PE",PE)
    mapper.discover_peak_rewrite_rules(width=16,coreir_primitives=["add"])
    
    app = c.load_from_file("tests/add4.json")
    print(app)
    app.print_()
    print("instance map",mapper.map_app(app))
    app.print_()

#test_discover()
#test_io()
