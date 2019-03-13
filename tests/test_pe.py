import whitney.asm as asm
from whitney.sim import PE, Bit, Data

def test_and():
    # instantiate an PE - calls PE.__init__
    pe = PE()
    # format an 'and' instruction
    inst = asm.and_() 
    # execute PE instruction with the arguments as inputs -  call PE.__call__
    res, res_p, irq = pe(inst, Data(1), Data(3))
    assert res==1
    assert res_p==0
    assert irq==0

def test_or():
    pe = PE()
    inst = asm.or_()
    res, res_p, irq = pe(inst, Data(1),Data(3))
    assert res==3
    assert res_p==0
    assert irq==0

def test_xor():
    pe = PE()
    inst = asm.xor()
    res, res_p, irq = pe(inst, Data(1),Data(3))
    assert res==2
    assert res_p==0
    assert irq==0

def test_inv():
    pe = PE()
    inst = asm.sub()
    res, res_p, irq = pe(inst, Data(0xffff),Data(1))
    assert res==0xfffe
    assert res_p==0
    assert irq==0

def test_neg():
    pe = PE()
    inst = asm.neg()
    res, res_p, irq = pe(inst, Data(0),Data(1))
    assert res==0xffff
    assert res_p==0
    assert irq==0

def test_add():
    pe = PE()
    inst = asm.add()
    res, res_p, irq = pe(inst, Data(1),Data(3))
    assert res==4
    assert res_p==0
    assert irq==0

def test_sub():
    pe = PE()
    inst = asm.sub()
    res, res_p, irq = pe(inst, Data(1),Data(3))
    assert res==-2
    assert res_p==0
    assert irq==0

def test_mult0():
    pe = PE()

    inst = asm.umult0()
    res, res_p, irq = pe(inst, Data(2),Data(3))
    assert res==6
    assert res_p==0
    assert irq==0

    inst = asm.smult0()
    res, res_p, irq = pe(inst, Data(-2),Data(3))
    assert res==-6
    assert res_p==0
    assert irq==0

def test_mult1():
    pe = PE()

    inst = asm.umult1()
    res, res_p, irq = pe(inst, Data(0x200),Data(3))
    assert res==6
    assert res_p==0
    assert irq==0

    inst = asm.smult1()
    res, res_p, irq = pe(inst, Data(-512),Data(3))
    assert res==-6
    assert res_p==0
    assert irq==0

def test_mult2():
    pe = PE()

    inst = asm.umult2()
    res, res_p, irq = pe(inst, Data(0x200),Data(0x300))
    assert res==6
    assert res_p==0
    assert irq==0

    inst = asm.smult2()
    res, res_p, irq = pe(inst, Data(-2*256),Data(3*256))
    assert res==-6
    assert res_p==0
    assert irq==0


def test_lsl():
    pe = PE()
    inst = asm.lsl()
    res, res_p, irq = pe(inst, Data(2),Data(1))
    assert res==4
    assert res_p==0
    assert irq==0

def test_lsr():
    pe = PE()
    inst = asm.lsr()
    res, res_p, irq = pe(inst, Data(2),Data(1))
    assert res==1
    assert res_p==0
    assert irq==0

def test_asr():
    pe = PE()
    inst = asm.asr()
    res, res_p, irq = pe(inst, Data(-2),Data(1))
    assert res==65535
    assert res_p==0
    assert irq==0

def test_sel():
    pe = PE()
    inst = asm.sel()
    res, res_p, irq = pe(inst, Data(1),Data(2),Bit(0))
    assert res==2
    assert res_p==0
    assert irq==0

def test_umin():
    pe = PE()
    inst = asm.umin()
    res, res_p, irq = pe(inst, Data(1),Data(2))
    assert res==1
    assert res_p==0
    assert irq==0

def test_umax():
    pe = PE()
    inst = asm.umax()
    res, res_p, irq = pe(inst, Data(1),Data(2))
    assert res==2
    assert res_p==0
    assert irq==0

def test_smin():
    pe = PE()
    inst = asm.smin()
    res, res_p, irq = pe(inst, Data(1),Data(2))
    assert res==1
    assert res_p==0
    assert irq==0

def test_smax():
    pe = PE()
    inst = asm.smax()
    res, res_p, irq = pe(inst, Data(1),Data(2))
    assert res==2
    assert res_p==0
    assert irq==0

def test_abs():
    pe = PE()
    inst = asm.abs()
    res, res_p, irq = pe(inst,Data(-1))
    assert res==1
    assert res_p==0
    assert irq==0

def test_eq():
    pe = PE()
    inst = asm.eq()
    res, res_p, irq = pe(inst,Data(1),Data(1))
    assert res_p==1

def test_ne():
    pe = PE()
    inst = asm.ne()
    res, res_p, irq = pe(inst,Data(1),Data(1))
    assert res_p==0

def test_uge():
    pe = PE()
    inst = asm.uge()
    res, res_p, irq = pe(inst,Data(1),Data(1))
    assert res_p==1

def test_ule():
    pe = PE()
    inst = asm.ule()
    res, res_p, irq = pe(inst,Data(1),Data(1))
    assert res_p==1

def test_ugt():
    pe = PE()
    inst = asm.ugt()
    res, res_p, irq = pe(inst,Data(1),Data(1))
    assert res_p==0

def test_ult():
    pe = PE()
    inst = asm.ult()
    res, res_p, irq = pe(inst,Data(1),Data(1))
    assert res_p==0

def test_sge():
    pe = PE()
    inst = asm.sge()
    res, res_p, irq = pe(inst,Data(1),Data(1))
    assert res_p==1

def test_sle():
    pe = PE()
    inst = asm.sle()
    res, res_p, irq = pe(inst,Data(1),Data(1))
    assert res_p==1

def test_sgt():
    pe = PE()
    inst = asm.sgt()
    res, res_p, irq = pe(inst,Data(1),Data(1))
    assert res_p==0

def test_slt():
    pe = PE()
    inst = asm.slt()
    res, res_p, irq = pe(inst,Data(1),Data(1))
    assert res_p==0

def test_fadd():
    # instantiate an PE - calls PE.__init__
    pe = PE()
    # format an 'and' instruction
    inst = asm.fadd() 
    # execute PE instruction with the arguments as inputs -  call PE.__call__
    res, res_p, irq = pe(inst, Data(0x000A), Data(0x0001))
    assert res==0x0085
    assert res_p==0
    assert irq==0

def test_fmul():
    # instantiate an PE - calls PE.__init__
    pe = PE()
    # format an 'and' instruction
    inst = asm.fmul() 
    # execute PE instruction with the arguments as inputs -  call PE.__call__
    res, res_p, irq = pe(inst, Data(0x4000), Data(0x4040))
    # 4000 => Sign=0; Exp=0x80; Mant=0x00 (0100 0000 0000 0000) (num 2)
    # 4040 => Sign=0; Exp=0x80; Mant=0x40 (0100 0000 0100 0000) (num 3)
    # es:40C0 => Sign=0; Exp=0x81; Mant=0x40 (0100 0000 1100 0000) (num 6)
    assert res==0x40C0
    assert res_p==0
    assert irq==0

def test_get_mant():
    # instantiate an PE - calls PE.__init__
    pe = PE()
    # format an 'and' instruction
    inst = asm.fgetmant() 
    # execute PE instruction with the arguments as inputs -  call PE.__call__
    res, res_p, irq = pe(inst, Data(0x7F8A), Data(0x0000))
    assert res==0xA
    assert res_p==0
    assert irq==0

def test_add_exp_imm():
    # instantiate an PE - calls PE.__init__
    pe = PE()
    # format an 'and' instruction
    inst = asm.faddiexp() 
    # execute PE instruction with the arguments as inputs -  call PE.__call__
    res, res_p, irq = pe(inst, Data(0x7F8A), Data(0x0005))
    # 7F8A => Sign=0; Exp=0xFF; Mant=0x0A
    # Add 5 to exp => Sign=0; Exp=0x04; Mant=0x0A i.e. float  = 0x020A
    assert res==0x020A
    assert res_p==0
    assert irq==0

def test_sub_exp():
    # instantiate an PE - calls PE.__init__
    pe = PE()
    # format an 'and' instruction
    inst = asm.fsubexp() 
    # execute PE instruction with the arguments as inputs -  call PE.__call__
    res, res_p, irq = pe(inst, Data(0x7F8A), Data(0x4005))
    # 7F8A => Sign=0; Exp=0xFF; Mant=0x0A
    # 4005 => Sign=0; Exp=0x80; Mant=0x05 (0100 0000 0000 0101)
    # res: 7F0A => Sign=0; Exp=0xFE; Mant=0x0A (0111 1111 0000 1010)
    assert res==0x7F0A
    assert res_p==0
    assert irq==0

def test_cnvt_exp_to_float():
    # instantiate an PE - calls PE.__init__
    pe = PE()
    # format an 'and' instruction
    inst = asm.fcnvexp2f() 
    # execute PE instruction with the arguments as inputs -  call PE.__call__
    res, res_p, irq = pe(inst, Data(0x4005), Data(0x0000))
    # 4005 => Sign=0; Exp=0x80; Mant=0x05 (0100 0000 0000 0101) i.e. unbiased exp = 1
    # res: 3F80 => Sign=0; Exp=0x7F; Mant=0x00 (0011 1111 1000 0000)
    assert res==0x3F80
    assert res_p==0
    assert irq==0

def test_get_float_int():
    # instantiate an PE - calls PE.__init__
    pe = PE()
    # format an 'and' instruction
    inst = asm.fgetfint() 
    # execute PE instruction with the arguments as inputs -  call PE.__call__
    res, res_p, irq = pe(inst, Data(0x4020), Data(0x0000))
    #2.5 = 10.1 i.e. exp = 1 with 1.01 # biased exp = 128 i.e 80
    #float is 0100 0000 0010 0000 i.e. 4020
    # res: int(2.5) =  2
    assert res==0x2
    assert res_p==0
    assert irq==0

def test_get_float_frac():
    # instantiate an PE - calls PE.__init__
    pe = PE()
    # format an 'and' instruction
    inst = asm.fgetffrac() 
    # execute PE instruction with the arguments as inputs -  call PE.__call__
    res, res_p, irq = pe(inst, Data(0x4020), Data(0x0000))
    #2.5 = 10.1 i.e. exp = 1 with 1.01 # biased exp = 128 i.e 80
    #float is 0100 0000 0010 0000 i.e. 4020
    # res: frac(2.5) = 0.5D = 0.1B i.e. 1000 0000
    assert res==0x80
    assert res_p==0
    assert irq==0
