/*
 * Copyright (c) 2024 Cameron Bedard and James Xie
 * SPDX-License-Identifier: Apache-2.0
 */

`default_nettype none

module tt_um_bnn (
    input  wire [7:0] ui_in,    // Dedicated inputs
    output wire [7:0] uo_out,   // Dedicated outputs
    input  wire [7:0] uio_in,   // IOs: Input path
    output wire [7:0] uio_out,  // IOs: Output path
    output wire [7:0] uio_oe,   // IOs: Enable path (active high: 0=input, 1=output)
    input  wire       ena,      // always 1 when the design is powered, so you can ignore it
    input  wire       clk,      // clock
    input  wire       rst_n     // reset_n - low to reset
);

// Output
// logic result[0:4];

// Input
wire UART_Rx;
wire UART_RTS;

// Output
wire UART_Tx;
wire UART_CTS;

assign UART_Rx = ui_in[0];
assign UART_RTS = ui_in[1];
assign uo_out[0] = UART_Tx;
assign uo_out[1] = UART_CTS;

bnn_controller bnn_inst (
    .clk(clk),
    .rst(~rst_n),
    .UART_Rx(UART_Rx),
    .UART_RTS(UART_RTS),
    .UART_Tx(UART_Tx),
    .UART_CTS(UART_CTS)
);

// All output pins must be assigned. If not used, assign to 0.
assign uio_oe  = 0;
assign uio_out = 0;

// List all unused inputs to prevent warnings
wire _unused = &{ena, clk, rst_n, 1'b0};


endmodule
