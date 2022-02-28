import json
import glob
import os
import importlib
from pathlib import Path

import metamapper.coreir_util as cutil
from metamapper.irs.coreir import gen_CoreIRNodes
from metamapper import CoreIRContext
from peak.mapper import ArchMapper
from lassen.sim import PE_fc
from pysmt.logics import QF_BV

def solve_rules():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    rr_path = f'{dir_path}/../lassen/rewrite_rules'
    rrules = glob.glob(f'{rr_path}/*.py')

    if len(rrules) == 0:
        raise ValueError("No rewrite rule peak specifications found")

    arch_mapper = ArchMapper(PE_fc)

    for idx, rrule in enumerate(rrules):
        op = Path(rrule).stem

        path = Path(f'{rr_path}/{op}.json')

        if not path.is_file():
            if "pipelined" in op:
                print("Can't solve for pipelined rewrite rules")
                continue


            peak_eq = importlib.import_module(f"lassen.rewrite_rules.{op}")

            ir_fc = getattr(peak_eq, op + "_fc")
            simp_formula = "fp_" in op
            ir_mapper = arch_mapper.process_ir_instruction(ir_fc, simple_formula=True)
            
            print(f"Searching for {op}", flush=True)

            if simp_formula:
                rewrite_rule = ir_mapper.solve('z3')
            else:
                rewrite_rule = ir_mapper.solve('btor', logic=QF_BV, external_loop=True, itr_limit=100)
            
            assert rewrite_rule is not None, f"No rewrite rule found for {op}"
           
            print(f"\tFound rewrite rule, {idx}/{len(rrules)} solved")
            serialized_rr = rewrite_rule.serialize_bindings()

            with open(f'{rr_path}/{op}.json', "w") as write_file:
                json.dump(serialized_rr, write_file, indent=2)
        else:
            print("Rewrite rule already found for", op)

def main():
    solve_rules()

if __name__ == '__main__':
    main()
