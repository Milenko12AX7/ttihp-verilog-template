/*
 * Copyright (c) 2024 Milenko12AX7
 * SPDX-License-Identifier: Apache-2.0
 */

`default_nettype none

module tt_um_Milenko12AX7_ciclo_lavadora_4bit (
    input  wire [7:0] ui_in,    // Dedicated inputs
    output wire [7:0] uo_out,   // Dedicated outputs
    input  wire [7:0] uio_in,   // IOs: Input path
    output wire [7:0] uio_out,  // IOs: Output path
    output wire [7:0] uio_oe,   // IOs: Enable path (active high: 0=input, 1=output)
    input  wire       ena,      // Always 1 when powered
    input  wire       clk,      // Clock = 1 Hz
    input  wire       rst_n     // Active-low reset
);

    // =========================
    // Entradas
    // =========================
    wire P = ui_in[0];   // sensor de peso: 1 = exceso de peso
    wire A = ui_in[1];   // sensor de agua: 1 = lleno, 0 = vacio

    // =========================
    // Codificación de estados
    // =========================
    localparam [3:0] INICIO    = 4'b0000;
    localparam [3:0] LLENADO1  = 4'b0001;
    localparam [3:0] LAVADO    = 4'b0010;
    localparam [3:0] VACIADO1  = 4'b0011;
    localparam [3:0] LLENADO2  = 4'b0100;
    localparam [3:0] ENJUAGUE  = 4'b0101;
    localparam [3:0] VACIADO2  = 4'b0110;
    localparam [3:0] CENTRIF   = 4'b0111;
    localparam [3:0] FINALIZAR = 4'b1000;

    reg [3:0] state;
    reg [3:0] next_state;

    // =========================
    // Temporizador de 20 s
    // =========================
    reg  [4:0] sec_cnt;
    wire timed_state;
    wire T;

    assign timed_state = (state == LAVADO)   ||
                         (state == ENJUAGUE) ||
                         (state == CENTRIF);

    // T = 1 cuando ya se cumplieron 20 ciclos
    assign T = timed_state && (sec_cnt == 5'd19);

    // =========================
    // Lógica de próximo estado
    // =========================
    always @(*) begin
        case (state)
            INICIO: begin
                if (P)
                    next_state = INICIO;
                else
                    next_state = LLENADO1;
            end

            LLENADO1: begin
                if (A)
                    next_state = LAVADO;
                else
                    next_state = LLENADO1;
            end

            LAVADO: begin
                if (T)
                    next_state = VACIADO1;
                else
                    next_state = LAVADO;
            end

            VACIADO1: begin
                if (!A)
                    next_state = LLENADO2;
                else
                    next_state = VACIADO1;
            end

            LLENADO2: begin
                if (A)
                    next_state = ENJUAGUE;
                else
                    next_state = LLENADO2;
            end

            ENJUAGUE: begin
                if (T)
                    next_state = VACIADO2;
                else
                    next_state = ENJUAGUE;
            end

            VACIADO2: begin
                if (!A)
                    next_state = CENTRIF;
                else
                    next_state = VACIADO2;
            end

            CENTRIF: begin
                if (T)
                    next_state = FINALIZAR;
                else
                    next_state = CENTRIF;
            end

            FINALIZAR: begin
                next_state = INICIO;
            end

            default: begin
                next_state = INICIO;
            end
        endcase
    end

    // =========================
    // Registro de estado + temporizador
    // =========================
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            state   <= INICIO;
            sec_cnt <= 5'd0;
        end else begin
            state <= next_state;

            // Si cambia de estado, reinicia contador
            if (state != next_state) begin
                sec_cnt <= 5'd0;
            end
            // Si sigue en un estado temporizado, cuenta hasta 19
            else if (timed_state && (sec_cnt < 5'd19)) begin
                sec_cnt <= sec_cnt + 5'd1;
            end
            // En cualquier otro caso, el contador vuelve a 0
            else begin
                sec_cnt <= 5'd0;
            end
        end
    end

    // =========================
    // Salidas
    // =========================
    assign uo_out[3:0] = state;  // estado actual
    assign uo_out[4]   = T;      // temporizador cumplido
    assign uo_out[7:5] = 3'b000;

    assign uio_out = 8'b00000000;
    assign uio_oe  = 8'b00000000;

    // =========================
    // Entradas no usadas
    // =========================
    wire _unused = &{ena, uio_in, ui_in[7:2], 1'b0};

endmodule
