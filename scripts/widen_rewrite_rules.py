"""Widen (or narrow) lassen's 16-bit integer rewrite rules to a W-bit PE (gen_PE_fc(W)).

usage: python widen_rewrite_rules.py W [jobs]

Writes lassen/rewrite_rules_w<W>/ (IR .py + rule .json) and keeps only rules whose
widened binding passes peak's verify() against gen_PE_fc(W). FP / bf16 / bit8 rules
are skipped (the W-bit PE has no FP units). The PE instruction layout is the same at
every width, so a rule's opcode, modes, lut and cond carry over; only the data0..2
constants widen (all-ones / signed max / signed min are re-derived for W bits).
"""
import importlib
import json
import multiprocessing as mp
import os
import re
import sys
import time
from pathlib import Path

W = int(sys.argv[1])
JOBS = int(sys.argv[2]) if len(sys.argv) > 2 else 16
SRC = Path(__file__).resolve().parent.parent / "lassen" / "rewrite_rules"
DST = SRC.parent / f"rewrite_rules_w{W}"


def int_rule(name):
    py, js = SRC / f"{name}.py", SRC / f"{name}.json"
    if not js.exists():
        return False
    text = py.read_text()
    if re.search(r"BFloat|float|Float", text):
        return False
    return '"fpu"' not in js.read_text() and '"fp_custom"' not in js.read_text()


def widen_py(text):
    # one pass, so a narrowed 2W (e.g. 16 at W=8) is not rewritten again
    text = re.sub(r"\[(16|32)\]", lambda m: f"[{W if m.group(1) == '16' else 2 * W}]", text)
    text = text.replace("sext(16)", f"sext({W})")
    text = text.replace("mul[8:24]", f"mul[{W // 2}:{W // 2 + W}]")
    return text


def widen_value(v):
    if v == 0xFFFF:
        return (1 << W) - 1
    if v == 0x7FFF:
        return (1 << (W - 1)) - 1
    if v == 0x8000:
        return 1 << (W - 1)
    return v & ((1 << W) - 1)  # don't-care values; narrowing masks them


def widen_json(rule):
    for val, path in rule["ibinding"]:
        if isinstance(val, dict) and val.get("type") == "BitVector" and val["width"] == 16:
            val["width"] = W
            val["value"] = widen_value(val["value"])
    return rule


def verify(name):
    t0 = time.time()
    try:
        from peak.mapper import read_serialized_bindings
        from lassen import gen_PE_fc
        mod = importlib.import_module(f"lassen.rewrite_rules_w{W}.{name}")
        ir_fc = getattr(mod, name + "_fc")
        with open(DST / f"{name}.json") as f:
            rr = read_serialized_bindings(json.load(f), ir_fc, gen_PE_fc(W))
        cex = rr.verify()
        return name, ("PASS" if cex is None else f"FAIL counterexample {cex}"), time.time() - t0
    except Exception as e:  # noqa: BLE001 - report every failure kind
        return name, f"ERROR {type(e).__name__}: {e}", time.time() - t0


if __name__ == "__main__":
    DST.mkdir(exist_ok=True)
    (DST / "__init__.py").write_text("")
    names = sorted(p.stem for p in SRC.glob("*.py") if p.stem != "__init__" and int_rule(p.stem))
    for n in names:
        (DST / f"{n}.py").write_text(widen_py((SRC / f"{n}.py").read_text()))
        with open(SRC / f"{n}.json") as f:
            rule = widen_json(json.load(f))
        with open(DST / f"{n}.json", "w") as f:
            json.dump(rule, f)
    print(f"widened {len(names)} integer rules to {W} bits -> {DST}", flush=True)
    results = {}
    with mp.Pool(JOBS) as pool:
        for name, status, secs in pool.imap_unordered(verify, names):
            results[name] = status
            print(f"{status[:4]} {name} ({secs:.0f}s){'' if status == 'PASS' else ': ' + status[:300]}", flush=True)
    bad = [n for n, s in results.items() if s != "PASS"]
    for n in bad:  # keep only verified rules
        (DST / f"{n}.json").rename(DST / f"{n}.json.failed")
    print(f"PASS {len(names) - len(bad)}/{len(names)}; failed: {bad}")
