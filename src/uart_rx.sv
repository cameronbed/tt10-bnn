module uart_rx (
    input  wire clk,
    input  wire rst,
    input  wire baud_clk,
    output wire [7:0] data_out,
    output wire data_valid,
    input  wire rx,
    output wire cts,
    input  wire rts,
    output wire rx_buffer_empty
);

    // UART receiver logic here

endmodule