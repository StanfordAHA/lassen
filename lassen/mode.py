from peak import Peak, gen_register
from hwtypes.adt import Enum
from .family import gen_pe_type_family
import magma as m
from functools import lru_cache


@lru_cache()
def gen_mode_type(family):
    """
    Field for specifying register modes
    """
    class Mode(family.Enum):
        CONST = 0   # Register returns constant in constant field
        BYPASS = 2  # Register is bypassed and input value is returned
        DELAY = 3   # Register written with input value, previous value returned
    return Mode


def gen_register_mode(T, init=None):
    if init is None:
        init = T(0)
    family = gen_pe_type_family(T.get_family())
    Reg = gen_register(family, T, init=init)
    Mode = gen_mode_type(family)

    class RegisterMode(Peak):
        def __init__(self):
            self.register: Reg = Reg()

        def __call__(self, mode: Mode, const_: T, value: T,
                     clk_en: family.Bit) -> T:
            if mode == Mode.CONST:
                self.register(value, False)
                return const_
            elif mode == Mode.BYPASS:
                self.register(value, False)
                return value
            elif mode == Mode.DELAY:
                return self.register(value, True)
            else:
                raise PeakNotImplementedError(mode)

    if family.Bit is m.Bit:
        RegisterMode = m.circuit.sequential(RegisterMode)
    return RegisterMode
