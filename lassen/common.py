from hwtypes import make_modifier, BitVector

#__all__  = ['Global', 'Config', 'DATAWIDTH', 'Data']

# Global signal modifier.
Global = make_modifier("Global")
Config = make_modifier("Config")

# Current PE has 16-bit data path
DATAWIDTH = 16
Data = BitVector[DATAWIDTH]

#hard coded addr info about internal peak registers
DATA01_ADDR = 3
BIT012_ADDR = 4
DATA0_START = 0
DATA0_WIDTH = DATAWIDTH
DATA1_START = 16
DATA1_WIDTH = DATAWIDTH
BIT0_START = 0
BIT1_START = 1
BIT2_START = 2


