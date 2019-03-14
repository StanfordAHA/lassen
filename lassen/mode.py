from peak import Peak, gen_register
from peak.adt import Enum
from .lut import Bit
from hwtypes import BitVector
import magma as m

# Field for specifying register modes
#
class Mode(Enum):
    CONST = 0   # Register returns constant in constant field
    VALID = 1   # Register written with clock enable, previous value returned
    BYPASS = 2  # Register is bypassed and input value is returned
    DELAY = 3   # Register written with input value, previous value returned


def gen_register_mode(T, mode="sim", init=0):
    if mode == "sim":
        family = BitVector.get_family()
    elif mode == "rtl":
        family = m.get_family()
    Reg = gen_register(T, mode=mode, init=init)

    class RegisterMode(Peak):
        def __init__(self):
            self.register: Reg = Reg()

        def __call__(self, mode: Mode, const: T, value: T,
                     clk_en: family.Bit) -> T:
            if mode == Mode.CONST:
                self.register(value, False)
                return const
            elif mode == Mode.BYPASS:
                self.register(value, False)
                return value
            elif mode == Mode.DELAY:
                return self.register(value, True)
            elif mode == Mode.VALID:
                return self.register(value, clk_en)
            else:
                raise NotImplementedError()

    if mode == "sim":
        return RegisterMode
    elif mode == "rtl":
        return m.circuit.sequential(RegisterMode)
    raise NotImplementedError(mode)
