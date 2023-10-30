import magma as m
import sys, os
from peak import family
from lassen.sim import PE_fc

PE = PE_fc(family.MagmaFamily())

d = os.path.realpath(os.path.dirname(__file__)) + "/build"

if not os.path.exists(d):
    os.makedirs(d)
m.compile(d + "/PE", PE, output="coreir-verilog",coreir_libs={"float_CW"})
