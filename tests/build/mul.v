// Stub impl until coreir supports bfloat verilog generation
module mul (
  input [15:0] in0,
  input [15:0] in1,
  output [15:0] out
);
  wire [2:0] fmul_res_x;

  CW_fp_mult #(.sig_width(10), .exp_width(8), .ieee_compliance(0)) mul1 (.a({in0,3'd0}),.b({in1,3'd0}),.rnd(3'd0),.z({fmul_res,fmul_res_x}),.status());


endmodule
