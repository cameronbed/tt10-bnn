// uart_rx.sv
// uart rx module
// Assumes 'clk_freq / baud_rate == BAUD_DIV' is an integer

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

  // states
  typedef enum logic [2:0] {
    IDLE,   // No data, line is high
    START,  // Detected start bit (rx=0)
    RECV,   // Receiving 8 data bits
    STOP,   // Sto
    DONE    // One-cycle state to pulse data_valid
  } state_t;

  state_t   state, next_state;
  logic [7:0] shift_reg;
  logic [2:0] bit_count;
  logic       valid_reg;
  logic [7:0] data_reg;

  // Outputs
  assign data_out      = data_reg;
  assign data_valid    = valid_reg;
  assign rx_buffer_empty = (state == IDLE);

  assign cts = (state == IDLE) && rts;

  // State machine
  always_ff @(posedge clk) begin
    if (rst) begin
      state <= IDLE;
      shift_reg <= 8'h00;
      bit_count <= 3'd0;
      data_reg <= 8'h00;
      valid_reg <= 1'b0;
    end
    else begin
      state <= next_state;
      valid_reg <= 1'b0;

      if (baud_clk) begin
        case (state)
          START: begin
          end

          RECV: begin
            shift_reg <= {rx, shift_reg[7:1]};
            bit_count <= bit_count + 1'b1;
          end

          STOP: begin
          end

          DONE: begin
            data_reg  <= shift_reg;
            valid_reg <= 1'b1;
          end
        endcase
      end
    end
  end

  // Next-state logic
  always_comb begin
    next_state = state;

    case (state)
      IDLE: begin
        if ((rx == 1'b0) && cts) begin
          next_state = START;
        end
      end

      START: begin
        if (baud_clk) begin
          next_state = RECV;
        end
      end

      RECV: begin
        if (baud_clk && (bit_count == 3'd7)) begin
          next_state = STOP;
        end
      end

      STOP: begin
        if (baud_clk) begin
          next_state = DONE;
        end
      end

      DONE: begin
        next_state = IDLE;
      end

      default: next_state = IDLE;
    endcase
  end

endmodule
