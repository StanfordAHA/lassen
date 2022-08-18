signs = ["s", "u"]
ops = ["AA", "AS", "SA", "SS"]

code = """
from peak import Peak, family_closure, Const
from peak import family
from peak.family import AbstractFamily

@family_closure
def {0}_fc(family: AbstractFamily):
    Data = family.BitVector[16]
    Data32 = family.Unsigned[32]
    SInt = family.Signed[16]
    UInt = family.Unsigned[16]
    Bit = family.Bit
    @family.assemble(locals(), globals())
    class {0}(Peak):
        def __call__(self, in2: Data, in1 : Data, in0 : Data) -> Data:
            
            return Data({1})
    
    return {0}
"""

compute = "({0}Int(in{3}) {1} {0}Int(in{4})) {2} {0}Int(in{5})"

s = [0, 1, 2]

for sign in signs:
    for op in ops:
        for shape in ["0", "1"]:
            rule_name = sign + "t" + op.lower() + "_s" + shape
            op0 = "+" if op[0] == "A" else "-"
            op1 = "+" if op[1] == "A" else "-"
            if shape == "0":
                s = [0, 1, 2]
            else:
                s = [1, 2, 0]
            str_compute = compute.format(sign.upper(), op0, op1, s[0], s[1], s[2])
            str_code = code.format(rule_name, str_compute)
            # print(f"sign={sign}, op={op}, shape={shape}========")
            # print(str_code)
            file_name = rule_name + ".py"
            with open(file_name, "w") as fd:
                fd.write(str_code)
