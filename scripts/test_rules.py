import json
import glob
import metamapper.coreir_util as cutil
from metamapper.irs.coreir import gen_CoreIRNodes
from metamapper import CoreIRContext
from peak.mapper import ArchMapper

from lassen.sim import PE_fc

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
