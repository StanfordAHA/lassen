module fp_ln (
    input [15:0] a,
    output [15:0] o
);

wire [7:0] status;

CW_fp_ln #(
    .sig_width(10),
    .exp_width(5),
    .ieee_compliance(1'b1)
) ln (
    .a(a),
    .z(o),
    .status(status)
);

endmodule
