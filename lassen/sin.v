module sine (
    input [15:0] a,
    output [15:0] o
);

CW_sin #(
    .A_width(16),
    .sin_width(16)
) sin (
    .A(a),
    .SIN(o)
);

endmodule
