from lassen.sim import gen_pe
import magma as m

PE = gen_pe(m.get_family())
m.compile(f"examples/build/PE", PE, output="coreir-verilog")
