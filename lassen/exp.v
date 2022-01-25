module fp_exp (
    input [15:0] a,
    output [15:0] o
);

wire [7:0] status;

CW_fp_exp #(
    .sig_width(10),
    .exp_width(5),
    .ieee_compliance(1'b1)
) exp (
    .a(a),
    .z(o),
    .status(status)
);

endmodule
