from hwtypes import SMTBitVector, SMTBit
from lassen.sim import gen_pe
import lassen.smt_asm as asm

smt_family = SMTBitVector.get_family()
PE = gen_pe(smt_family)

smt_expression = PE()(
    inst=asm.add(),
    data0=SMTBitVector[16](),
    data1=SMTBitVector[16](),
    bit0=SMTBit(),
    bit1=SMTBit(),
    bit2=SMTBit()
)

print()
print("======" * 5)
print()

print(smt_expression)

print(smt_expression[0]._value)
print(smt_expression[0]._value.serialize())

print()
print("======" * 5)
print()

smt_expression = PE()(
    inst=asm.add(),
    data0=SMTBitVector[16](0xDE),
    data1=SMTBitVector[16](0xBE),
    bit0=SMTBit(),
    bit1=SMTBit(),
    bit2=SMTBit()
)

print(smt_expression)
print(f"0xDE + 0xBE = {0xDE + 0xBE}")

print(smt_expression[0]._value)
print(smt_expression[0]._value.serialize())

print()
print("======" * 5)
print()
