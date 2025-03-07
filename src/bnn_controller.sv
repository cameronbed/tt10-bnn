// controller.v
// Handles state changes and control signals for the BNN

module bnn_controller (
    input  wire clk,
    input wire rst,

    // UART Input
    input logic UART_Rx,
    input logic UART_RTS,

    // UART Output
    output logic UART_Tx,
    output logic UART_CTS
);

// Define system states
    typedef enum logic [1:0] {IDLE, PROCESS_CMD, RESPOND} system_state_t;
    system_state_t state;

    // Internal signals for received data
    logic [7:0] received_byte;
    logic received_dv;

    // Internal signals for response
    logic [7:0] response_byte;
    logic response_dv;

    logic baud_clk_signal;

    logic [7:0] rx_data;
    logic rx_valid;

    // baud_rate_generator #(
    //     .BAUD_RATE(115200),
    //     .CLKS_PER_BIT(868) // Example for ~100MHz / 115200
    // ) baud_inst (
    //     .clk(clk),
    //     .rst(rst),
    //     .baud_clk(baud_clk_signal)
    // );

    uart_rx rx_inst(
        .clk(clk),
        .rst(rst),
        .baud_clk(baud_clk_signal),
        .data_out(rx_data),
        .data_valid(rx_valid),
        .rx(UART_Rx),
        .rx_buffer_empty(),
        .cts(UART_CTS)
    );
    
    uart_tx tx_inst(
        .clk(clk),
        .rst(rst),
        .baud_clk(baud_clk_signal),
        .data_in(response_byte),
        .tx(response_dv),
        .tx_buffer_empty(),
        .cts(UART_CTS)
        //.rts(UART_RTS)
    );

endmodule
