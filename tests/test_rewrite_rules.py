import pytest
import json

import metamapper.coreir_util as cutil
from metamapper import CoreIRContext
from metamapper.irs.coreir import gen_CoreIRNodes
from peak.mapper import read_serialized_bindings

from lassen.sim import PE_fc

c = CoreIRContext(reset=True)
cutil.load_libs(["commonlib"])
CoreIRNodes = gen_CoreIRNodes(16)

lassen_ops = [
    "coreir.or_",
    "coreir.mul",
    "coreir.and_",
    "commonlib.smax",
    "commonlib.smin",
    "commonlib.umax",
    "commonlib.umin",
    "coreir.add",
    "coreir.ule",
    "coreir.sle",
    "coreir.ult",
    "coreir.slt",
    "coreir.ugt",
    "coreir.sgt",
    "corebit.not_",
    "corebit.mux",
    "corebit.or_",
    "corebit.and_",
    "corebit.xor",
    "coreir.sub",
    "commonlib.abs",
    "coreir.eq",
    "coreir.lshr",
    "coreir.ashr",
    "coreir.shl",
    "coreir.mux",
]

with open("scripts/rewrite_rules/lassen_rewrite_rules.json", "r") as read_file:
    rrs = json.loads(read_file.read())

@pytest.mark.parametrize("op", lassen_ops)
def test_rewrite_rule(op):
    ir_fc = CoreIRNodes.peak_nodes[op]
    new_rewrite_rule = read_serialized_bindings(rrs[op], ir_fc, PE_fc)
    counter_example = new_rewrite_rule.verify()

    assert counter_example == None
