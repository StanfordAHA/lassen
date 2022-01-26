module sine (
    input [15:0] a,
    output [15:0] o
);

wire [7:0] status;

DW_fp_sincos #(
    .sig_width(7),
    .exp_width(8),
    .ieee_compliance(1'b1)
) sin (
    .a(a),
    .sin_cos(1'b0),
    .z(o),
    .status(status)
);

endmodule
