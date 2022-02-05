module fp_div (
    input [15:0] a,
    input [15:0] b,
    output [15:0] o
);

wire [2:0] rnd = 3'b0;
wire [7:0] status;

DW_fp_div #(
    .sig_width(7),
    .exp_width(8),
    .ieee_compliance(1'b1)
) div (
    .a(a),
    .b(b),
    .rnd(rnd),
    .z(o),
    .status(status)
);

endmodule
