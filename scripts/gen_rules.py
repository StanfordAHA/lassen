import json

import metamapper.coreir_util as cutil
from metamapper.irs.coreir import gen_CoreIRNodes
from metamapper import CoreIRContext
from peak.mapper import ArchMapper

from lassen.sim import PE_fc

c = CoreIRContext(reset=True)
cutil.load_libs(["commonlib"])
CoreIRNodes = gen_CoreIRNodes(16)

lassen_ops = (
    "coreir.const",
    "corebit.const",
    "corebit.and_",
    "coreir.ule",
    "coreir.sle",
    "coreir.ult",
    "coreir.slt",
    "coreir.ugt",
    "coreir.sgt",
    "coreir.uge",
    "coreir.sge",
    "coreir.or_",
    "coreir.mul",
    "coreir.and_",
    "commonlib.smax",
    "commonlib.smin",
    "commonlib.umax",
    "commonlib.umin",
    "coreir.add",
    "corebit.not_",
    "corebit.mux",
    "corebit.or_",
    "corebit.xor",
    "coreir.sub",
    "commonlib.abs",
    "coreir.eq",
    "coreir.lshr",
    "coreir.ashr",
    "coreir.shl",
    "coreir.mux",
)

all_rrs = {}
arch_mapper = ArchMapper(PE_fc)

for op in lassen_ops:
    print(f"Searching for {op}", flush=True)
    ir_fc = CoreIRNodes.peak_nodes[op]
    ir_mapper = arch_mapper.process_ir_instruction(ir_fc)
    rewrite_rule = ir_mapper.solve()
    assert rewrite_rule is not None
    serialized_rr = rewrite_rule.serialize_bindings()
    all_rrs[op] = serialized_rr

with open("scripts/rewrite_rules/lassen_rewrite_rules.json", "w") as write_file:
    json.dump(all_rrs, write_file, indent=2)
