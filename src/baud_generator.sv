module baud_generator #(
    parameter int BAUD_RATE = 8,  // UART Baud Rate Clock rate
    parameter int CLKS_PER_BIT = 8 // CLKS_PER_BIT = clk / BaudRate
)(
    input  logic clk,      // System clock
    input  logic rst,    // Active-low reset
    output logic baud_clk  // Baud rate clock enable
);

    logic [15:0] clk_count; // Counter for clock division

    always_ff @(posedge clk or negedge rst) begin
        if (!rst) begin
            clk_count  <= 0;
            baud_clk <= 0;
        end else begin
            if (clk_count == (CLKS_PER_BIT - 1)) begin
                clk_count  <= 0;
                baud_clk <= 1;  // Pulse at baud rate
            end else begin
                clk_count  <= clk_count + 1;
                baud_clk <= 0;
            end
        end
    end

endmodule
