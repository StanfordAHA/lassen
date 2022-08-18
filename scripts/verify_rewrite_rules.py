import json
import glob
import os
import importlib
from pathlib import Path
import multiprocessing

import metamapper.coreir_util as cutil
from metamapper.irs.coreir import gen_CoreIRNodes
from metamapper import CoreIRContext
from peak.mapper import ArchMapper, read_serialized_bindings
from lassen.sim import PE_fc
from pysmt.logics import QF_BV


def test_rule(rrule):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    rr_path = f"{dir_path}/../lassen/rewrite_rules"
    arch_mapper = ArchMapper(PE_fc)
    op = Path(rrule).stem
    path = Path(f"{rr_path}/{op}.json")

    if path.is_file():
        if "pipelined" in op:
            print("Can't test pipelined rewrite rules")
            return

        peak_eq = importlib.import_module(f"lassen.rewrite_rules.{op}")

        ir_fc = getattr(peak_eq, op + "_fc")

        with open(path, "r") as json_file:
            rewrite_rule_in = json.load(json_file)

        rewrite_rule = read_serialized_bindings(rewrite_rule_in, ir_fc, PE_fc)

        print(f"Verifying {op}", flush=True)

        counter_example = rewrite_rule.verify()
        assert counter_example == None, f"{op} failed"
        print(f"\t{op} passed", flush=True)
    else:
        print("No rewrite rule found for", op)


def test_rules():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    rr_path = f"{dir_path}/../lassen/rewrite_rules"
    rrules = glob.glob(f"{rr_path}/*.py")

    if len(rrules) == 0:
        raise ValueError("No rewrite rule peak specifications found")

    pool = multiprocessing.Pool(16)
    pool.map(test_rule, rrules)


def main():
    test_rules()


if __name__ == "__main__":
    main()
