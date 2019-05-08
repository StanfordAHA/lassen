from codecs import decode
import struct

def float2bfbin(fnum):
   if (fnum=='NaN'):
     sign = '0'
     exp  = '11111111'
     lfrac = '11111111'
   elif (fnum=='-NaN'):
     sign = '1'
     exp  = '11111111'
     lfrac = '11111111'
   elif (fnum=='Inf'):
     sign = '0'
     exp  = '11111111'
     lfrac = '00000000'
   elif (fnum=='-Inf'):
     sign = '1'
     exp  = '11111111'
     lfrac = '00000000'
   else:
     fstr  = ''.join("{:08b}".format(elem) for elem in struct.pack('!f', fnum))
     sign  = fstr[0]
     exp   = fstr[1:9]
     lfrac = fstr[9:16]
     hfrac = fstr[16:]
   return fstr[0:16] 

def bfbin2float(bfstr):
   sign  = bfstr[0]
   exp   = bfstr[1:9]
   lfrac = bfstr[9:16]
   if (sign=='0' and exp == '11111111' and lfrac!='0000000'):
     return 'NaN'
   elif (sign=='1' and exp == '11111111' and lfrac!='0000000'):
     return '-NaN'
   elif (sign=='0' and exp == '11111111' and lfrac=='0000000'):
     return 'Inf'
   elif (sign=='1' and exp == '11111111' and lfrac=='0000000'):
     return '-Inf'
   else:
     mult = 1
     if (sign=='1'):
        mult = -1
     nexp = int(exp,2) - 127
     if (exp!=0):
       lfrac = '1' + lfrac
     else:
       lfrac = '0' + lfrac
     nfrac = int(lfrac,2)
     return mult * nfrac * (2 ** (nexp - 7))
