from lassen.sim import gen_pe
import lassen.asm as asm
from hwtypes import BitVector
import coreir
import metamapper as mm
import pytest
import json
from lassen import rules as Rules
from lassen import LassenMapper

@pytest.mark.skip("This takes a long time")
def test_discover():
    c = coreir.Context()
    mapper = mm.PeakMapper(c,"pe_ns")
    mapper.add_peak_primitive("PE",gen_pe)

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
    app = c.load_from_file("tests/examples/add4.json")
    mapper.map_app(app)
    imap = mapper.extract_instr_map(app)
    assert len(imap) == 3

@pytest.mark.skip("Broken due to addition of mapper ports")
def test_const():
    c = coreir.Context()
    mapper = mm.PeakMapper(c,"pe_ns")

    PE = mapper.add_peak_primitive("PE",gen_pe)

    const16 = c.get_namespace("coreir").generators['const'](width=16)

    def instr_lambda(inst):
        cval = inst.config["value"].value
        return asm.const(cval)

    #Adds a simple "1 to 1" rewrite rule
    mapper.add_rewrite_rule(mm.Peak1to1(
        const16,
        PE,
        instr_lambda,
        dict(out="alu_res")
    ))


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



    #test the mapper on simple const app
    app = c.load_from_file("tests/examples/const.json")
    mapper.map_app(app)
    imap = mapper.extract_instr_map(app)
    assert len(imap) == 4
    assert imap["c1$inst"] == asm.const(1)
    c.run_passes(['printer'])
    #This should have the c1$inst op attached with the ALUOP metadata


@pytest.mark.skip("Broken due to addition of mapper ports")
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
    mapper.add_peak_primitive("PE",gen_pe)
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
    mapper.discover_peak_rewrite_rules(width=16,coreir_primitives=["add","mul"])
    app = c.load_from_file("tests/examples/add4.json")
    mapper.map_app(app)
    imap = mapper.extract_instr_map(app)
    assert len(imap) == 3
    print("instance map",imap)
    app.save_to_file("tests/_mapped_add4.json")
    app.print_()

def test_float():
    c = coreir.Context()
    c.load_library("float")
    mapper = mm.PeakMapper(c,"alu_ns")

    pe = mapper.add_peak_primitive("PE",gen_pe)
    bfloat_add = c.get_namespace("float").generators['add'](exp_bits=8,frac_bits=7)

    #Adds a simple "1 to 1" rewrite rule
    mapper.add_rewrite_rule(mm.Peak1to1(
        bfloat_add, #Coreir module
        pe, #coreir pe
        asm.fp_add(), #Instruction for PE
        dict(in0='data0',in1='data1',out="alu_res") #Port Mapping
    ))


    #test the mapper on simple add4 app
    app = c.load_from_file("tests/examples/fpadd4.json")
    mapper.map_app(app)
    imap = mapper.extract_instr_map(app)
    assert len(imap) == 3
    print("instance map",imap)

def test_fp_pointwise():
    c = coreir.Context()
    c.load_library("float")
    #mapper = mm.PeakMapper(c,"alu_ns")
    mapper = LassenMapper(c)

    #test the mapper on simple add4 app
    app = c.load_from_file("tests/examples/fp_pointwise.json")
    mapper.map_app(app)
    imap = mapper.extract_instr_map(app)
    assert len(imap) == 2 # expect to see a multiplier and const
    print("instance map",imap)
    app.save_to_file("tests/examples/fp_pointwise.mapped.json")

@pytest.mark.parametrize("op", ["and","or","xor"])
def test_binary_lut(op):
    c = coreir.Context()
    #Create app that contains some all the binary and unary ops
    g = c.global_namespace
    mod_type = c.Record({
        "in": c.Array(4,c.BitIn()),
        "out":c.Bit()
    })
    app = g.new_module("app",mod_type)
    mdef = app.new_definition()
    bin_op = c.get_namespace("corebit").modules[op]
    binst00 = mdef.add_module_instance(name="i00",module=bin_op)
    binst01 = mdef.add_module_instance(name="i01",module=bin_op)
    binst1 = mdef.add_module_instance(name="i1",module=bin_op)
    io = mdef.interface
    mdef.connect(io.select("in").select('0'),binst00.select("in0"))
    mdef.connect(io.select("in").select('1'),binst00.select("in1"))
    mdef.connect(io.select("in").select('2'),binst01.select("in0"))
    mdef.connect(io.select("in").select('3'),binst01.select("in1"))
    mdef.connect(binst00.select("out"),binst1.select("in0"))
    mdef.connect(binst01.select("out"),binst1.select("in1"))
    mdef.connect(binst1.select("out"),io.select("out"))
    app.definition = mdef

    mapper = LassenMapper(c)
    mapper.map_app(app)
    imap = mapper.extract_instr_map(app)
    assert len(imap) == 3

def make_single_op_app(c : coreir.Context,namespace : str, op : str,**genargs):
    g = c.global_namespace
    coreir_op = c.get_namespace(namespace).generators[op](**genargs)
    mod_type = coreir_op.type
    app = g.new_module("app",mod_type)
    mdef = app.new_definition()
    op_inst = mdef.add_module_instance(name="i",module=coreir_op)
    io = mdef.interface
    for pname,ptype in mod_type.items():
        mdef.connect(io.select(pname),op_inst.select(pname))
    app.definition = mdef
    return app

@pytest.mark.parametrize("op",["lt","le","gt","ge","eq","neq","add","sub","mul"])
def test_fp_ops(op):
    c = coreir.Context()
    c.load_library("float")
    app = make_single_op_app(c,"float",op,exp_bits=8,frac_bits=7)
    mapper = LassenMapper(c)
    for rule in Rules:
        mapper.add_rr_from_description(rule)
    mapper.map_app(app)
    imap = mapper.extract_instr_map(app)
    assert len(imap) == 1

@pytest.mark.parametrize("op",["ult","ule","ugt","uge","eq","neq","add","sub","mul","mux"])
def test_coreir_ops(op):
    c = coreir.Context()
    app = make_single_op_app(c,"coreir",op,width=16)
    mapper = LassenMapper(c)
    for rule in Rules:
        mapper.add_rr_from_description(rule)
    mapper.map_app(app)
    imap = mapper.extract_instr_map(app)
    assert len(imap) == 1

@pytest.mark.parametrize("rule",Rules)
def test_rules(rule):
    if rule['kind'] != "1to1":
        pytest.skip()
    namespace,op = rule["coreir_prim"]
    c = coreir.Context()
    if namespace == "coreir":
        genargs = dict(width=16)
    elif namespace == "float":
        genargs = dict(exp_bits=8,frac_bits=7)
    app = make_single_op_app(c,namespace,op,**genargs)
    app.print_()
    mapper = LassenMapper(c)
    for rule in Rules:
        mapper.add_rr_from_description(rule)

    try:
        mapper.map_app(app)
    except:
        raise NotImplementedError("You probably need to regenerate rules by running the scripts/gen_rules.py script")

    imap = mapper.extract_instr_map(app)
    assert len(imap) == 1

def test_init():
    c = coreir.Context()
    mapper = LassenMapper(c)
    for rr in Rules:
        mapper.add_rr_from_description(rr)

    #test the mapper on simple add4 app
    app = c.load_from_file("tests/examples/add4.json")
    mapper.map_app(app)
    imap = mapper.extract_instr_map(app)
    assert len(imap) == 3
