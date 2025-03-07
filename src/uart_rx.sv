module uart_rx (
    input wire rst,
    input wire baud_clk,

    input wire rx,

    input cts,
    output rts,

    output rx_buffer_empty,
    output logic [7:0] data_out,
    output logic data_valid
);
    logic [6:0] rx_buffer;

    logic [3:0] bit_cnt;
    logic [8:0] shift_reg;
    logic receiving;
    
    always @(posedge baud_clk or posedge rst) begin
        if (rst) begin
            bit_cnt <= 0;
            receiving <= 0;
        end
        else begin
            if (!receiving && !rx) begin  // Start bit detected
                receiving <= 1;
                bit_cnt <= 0;
            end
            
            if (receiving) begin
                shift_reg <= {rx, shift_reg[8:1]};
                bit_cnt <= bit_cnt + 1;
                
                if (bit_cnt == 8) begin
                    receiving <= 0;
                    if (shift_reg[0] == 0 && shift_reg[8] == 1) begin // Valid start/stop bits
                        data_out <= shift_reg[7:1];
                        data_valid <= 1;
                    end
                end
            end else begin
            end
        end
    end

    assign rx_buffer_empty = ~receiving; 
endmodule