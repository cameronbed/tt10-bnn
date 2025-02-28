`include "baud_generator.sv"

module uart_tx (
    input wire rst,
    input wire baud_clk,

    input logic [6:0] data_in,

    input wire tx,

    input cts,
    output rts,

    output tx_buffer_empty,   
);
    logic [6:0] tx_buffer;

    logic [3:0] bit_cnt;
    logic [8:0] shift_reg;
    logic transmitting;
    
    always @(posedge baud_clk or posedge rst) begin
        if (rst) begin
            bit_cnt <= 0;
            transmitting <= 0;
        end
        else begin
            if (!transmitting && tx) begin
                transmitting <= 1;
                bit_cnt <= 0;
            end
            
            if (transmitting) begin
                shift_reg <= {1'b1, shift_reg[8:1]}; // Shift out data
                bit_cnt <= bit_cnt + 1;
                
                if (bit_cnt == 8) begin
                    transmitting <= 0;
                end
            end else begin
            end
        end
    end

    assign tx_buffer_empty = ~transmitting;
endmodule