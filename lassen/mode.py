from peak import Peak, gen_register
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
    Bit = family.Bit

    class RegisterMode(Peak):
        def __init__(self):
            self.register: Reg = Reg()

        #Outputs <based on mode>, register_value
        def __call__(self, mode: Mode, const_: T, value: T,
                clk_en: family.Bit, config_we : Bit, config_data : T) -> (T,T):
            if config_we==Bit(1):
                reg_val = self.register(config_data,Bit(1))
                return reg_val,reg_val
            elif mode == Mode.CONST:
                reg_val = self.register(value, Bit(False))
                return const_, reg_val
            elif mode == Mode.BYPASS:
                reg_val = self.register(value, Bit(False))
                return value, reg_val
            elif mode == Mode.DELAY:
                reg_val = self.register(value, clk_en)
                return reg_val, reg_val
            #else:
            #    raise PeakNotImplementedError(mode)

    if family.Bit is m.Bit:
        RegisterMode = m.circuit.sequential(RegisterMode)
    return RegisterMode
