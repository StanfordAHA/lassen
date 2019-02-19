#include <stdio.h>
#include <math.h>
#include <stdlib.h>
#include "./defines.h"

// Program to compute transcendentals y = f(x)
// Given:
// 1. X's precision = 16 bits
// 2. Four tables of floats computed for
//    the function being implemented
// Algorithm:
// 1. Split incoming word (x) into four nibbles
//    xm[0],xm[1],xm[2],xm[3]
// 2. Use these nibbles to index the tables to
//    get four floats a,b,c,e
// 3. Compute an initial estimate
//    ans = a + b + c + xm[2]*e + xm[3]*(2^-4)*e
// 4. Refine the estimate (if necessary) with 
//    additional floating point ops (eg: NR)

float cast_ieee754(char *str) {
// Creates a floating point number from the 
// table representation. This is needed only
// in C code and wont be present in the 
// hardware implementation
  char curr_ssign[2];
  char curr_sman[__WIDTH_M + 1];
  char curr_sexp[9];
  int sign;
  float man;
  int bias_exp;
  int exp;

  float num;

  sprintf(curr_ssign,"%.*s",1,&str[0]);
  sprintf(curr_sexp,"%.*s",8,&str[1]);
  sprintf(curr_sman,"%.*s",__WIDTH_M,&str[9]);

  //printf ("decoding %s s %s e %s m %s\n", str, curr_ssign, curr_sexp, curr_sman);

  if (curr_ssign[0]=='0') sign = 1;
  else sign = -1;
  
  bias_exp = strtol(curr_sexp,NULL,2);
  if (bias_exp==0) {
    man = 0 + ((double)strtol(curr_sman,NULL,2)/pow(2.0,__WIDTH_M));
  } else {
    man = 1 + ((double)strtol(curr_sman,NULL,2)/pow(2.0,__WIDTH_M));
  }

  exp = bias_exp - 127;
  num = sign * man * pow(2,exp);
  //printf ("s%d e%d m%f: %f\n", sign, exp, man, num);
  return num;
}

void main(int argc, char * argv[]) {
   int mask;
   int a_index, b_index, c_index, e_index;
   int xm[4], xs;
   //var_x is the incoming 16-bit word
   int var_x = atoi(argv[1]);
   int scaled_var_x; 
   float a,b,c,d,e,ans;

   //table.c contains all tables
   //#include "./table.c"
   #include "./table_exp.c"
   //normalize incoming number
   //not needed in hardware as incoming will always be a float
   // Q1. How to deal with denormals (Do we support denormals?)
   // Q2. Integer division is done via this unit, do we need conversion?
   int scale=0;
   for (int i=0;i<8;i++) {
     mask = 1 << i;
     if ((var_x & mask)!=0) {
      scale = i;
     }
   }
   scaled_var_x = var_x << (__WIDTH_M-scale);
   //Done normalizing
   mask = pow(2,(__WIDTH_M))-1;
   a_index = (scaled_var_x & mask);
   a = cast_ieee754(table[a_index]);
   //printf("##%d %d %d: scale: %d: %f\n",var_x,scaled_var_x,a_index, scale, a);

   //Compute an intial estimate using table floats
   ans = a; 

   //This step changes based on the function used
   //For division it involves scaling and NR iterations (if needed)
   //For e^x it involves multiple constant multiplications
   //For log it involves constant multiplication and an addition

   //DIVISION
   //ans = ans / pow(2,scale); //scaling
   
   //LOG
   //ans = (double)scale*log(2) + ans; // use fops

   //EXP
   //Create a bfloat of x/ln(2) and paste it here
   //In the PE, the incoming number is already a bfloat
   int bfloat = 0x40E6 ;//0100 0000 1110 0110 = 5/ln(2);
   int mant = 0xE6;//1110 0110
   int exp = 0x81-0x7F;//1000 0001 - bias (0111 1111)
   int n;
   float term;
   ans = 1.0;
   for (int i=0;i<8;i++) {
     mask = 0x80 >> i;
     if ((mant & mask)!=0) {  //if ith bit is non zero, multiply ans with the term 2^(2^(exp - n))
       n = exp - i;
       term = 1.0;
       printf(">>> i:%d n:%d term:%f ans:%f\n",i,n,term,ans);
       if (n >= 0) {
          //inner leftshift is int shift, outer modifies float exp, so easy
          //this allows for large powers of 2
          term = (1 << (1 << n)); 
       } else if (n >= -6) { 
          //for (exp-n) = -1,-2,... use LUT to get 2^(2^(exp-n)) - only 6 entries needed.
          //only 6 entries needed as 2^(2^-6) and below needs more precision than 8 bits,
          //but 2^(2^n) will always be in (1,2] for n < 0 i.e. exp=0 for all n < 0
          term = cast_ieee754(table[abs(n)]); 
       }
       ans = ans * term;
       printf("i:%d n:%d term:%f ans:%f\n",i,n,term,ans);
     }
   }
   // DONE POST PROCESSING

   //Print results obtained with the table method
   printf("TABLE : %.4a ( %f )\n", ans, ans);
   //Print double precision results obtained using C operator
   //for comparison
   //double gres = 1.0/(double) var_x;
   double gres = log((double) var_x);
   printf("GOLDEN: %.4a ( %f )\n",gres,gres);

   float delta = fabs(gres - ans);
   float ulp = 1.0/256.0;
   float delta_ulp = delta/ulp;
   printf("ULP delta: %.1f\n", delta_ulp);
}
