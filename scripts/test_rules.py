
import json
import glob
import importlib
from pathlib import Path
import jsonpickle
import metamapper.coreir_util as cutil
from metamapper.irs.coreir import gen_CoreIRNodes
from metamapper import CoreIRContext
from peak.mapper import ArchMapper, read_serialized_bindings
from lassen.sim import PE_fc

rrules = glob.glob(f'./lassen/rewrite_rules/fp_sub*.json')

arch_mapper = ArchMapper(PE_fc)

for rrule in rrules:
    if "pipelined" not in rrule and "middle" not in rrule:
        rule_name = Path(rrule).stem
        print(rule_name)
        peak_eq = importlib.import_module(f"lassen.rewrite_rules.{rule_name}")
        ir_fc = getattr(peak_eq, rule_name + "_fc")

        with open(rrule, "r") as json_file:
            rewrite_rule_in = jsonpickle.decode(json_file.read())

        rewrite_rule = read_serialized_bindings(rewrite_rule_in, ir_fc, PE_fc)
        counter_example = rewrite_rule.verify()
        assert counter_example == None, f"{rule_name} failed"
