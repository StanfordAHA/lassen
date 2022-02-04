import json
import glob
import importlib
from pathlib import Path

import metamapper.coreir_util as cutil
from metamapper.irs.coreir import gen_CoreIRNodes
from metamapper import CoreIRContext
from peak.mapper import ArchMapper
from lassen.sim import PE_fc

rrules = glob.glob(f'./lassen/rewrite_rules/zext.py')

arch_mapper = ArchMapper(PE_fc)

for rrule in rrules:
    op = Path(rrule).stem

    path = Path(f'./lassen/rewrite_rules/{op}.json')

    if not path.is_file():

        print(f"Searching for {op}", flush=True)
        peak_eq = importlib.import_module(f"lassen.rewrite_rules.{op}")

        ir_fc = getattr(peak_eq, op + "_fc")

        ir_mapper = arch_mapper.process_ir_instruction(ir_fc, simple_formula=True)
        rewrite_rule = ir_mapper.solve('z3')
        print(f"Found", flush=True)
        assert rewrite_rule is not None
        counter_example = rewrite_rule.verify()
        assert counter_example == None, f"{op} failed"
        serialized_rr = rewrite_rule.serialize_bindings()

        with open(f'./lassen/rewrite_rules/{op}.json', "w") as write_file:
            json.dump(serialized_rr, write_file, indent=2)
