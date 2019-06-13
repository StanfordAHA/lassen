module DW_fp_mult(a, b, rnd, status, z);

parameter sig_width = 23;
parameter exp_width = 8;
parameter ieee_compliance = 1;

input [sig_width + exp_width:0] a;
input [sig_width + exp_width:0] b;
input [2:0] rnd;
output [sig_width + exp_width:0] z;
output [7:0] status;

assign status = 8'h0;
assign z = {(sig_width+exp_width+1){1'b0}};

endmodule
