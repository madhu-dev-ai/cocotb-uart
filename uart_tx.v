module uart_tx #(parameter CLKS_PER_BIT = 4) (
    input clk,
    input rst,
    input start,
    input [7:0] data,
    output reg tx,
    output reg busy
);
    localparam IDLE = 2'd0, START = 2'd1, DATA = 2'd2, STOP = 2'd3;

    reg [1:0] state;
    reg [3:0] clk_count;
    reg [2:0] bit_index;
    reg [7:0] shift;

    always @(posedge clk) begin
        if (rst) begin
            state <= IDLE;
            tx <= 1'b1;
            busy <= 1'b0;
            clk_count <= 0;
            bit_index <= 0;
            shift <= 0;
        end else begin
            case (state)
                IDLE: begin
                    tx <= 1'b1;
                    busy <= 1'b0;
                    clk_count <= 0;
                    bit_index <= 0;
                    if (start) begin
                        shift <= data;
                        busy <= 1'b1;
                        tx <= 1'b0;
                        state <= START;
                    end
                end
                START: begin
                    if (clk_count == CLKS_PER_BIT - 1) begin
                        clk_count <= 0;
                        tx <= shift[0];
                        state <= DATA;
                    end else
                        clk_count <= clk_count + 1;
                end
                DATA: begin
                    if (clk_count == CLKS_PER_BIT - 1) begin
                        clk_count <= 0;
                        if (bit_index == 7) begin
                            tx <= 1'b1;
                            state <= STOP;
                        end else begin
                            bit_index <= bit_index + 1;
                            tx <= shift[bit_index + 1];
                        end
                    end else
                        clk_count <= clk_count + 1;
                end
                STOP: begin
                    if (clk_count == CLKS_PER_BIT - 1) begin
                        clk_count <= 0;
                        busy <= 1'b0;
                        state <= IDLE;
                    end else
                        clk_count <= clk_count + 1;
                end
            endcase
        end
    end
endmodule