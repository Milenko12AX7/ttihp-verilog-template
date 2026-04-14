# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles


def get_state(dut):
    return int(dut.uo_out.value) & 0xF


def get_timer_done(dut):
    return (int(dut.uo_out.value) >> 4) & 0x1


@cocotb.test()
async def test_project(dut):
    dut._log.info("Start test")

    clock = Clock(dut.clk, 10, unit="us")
    cocotb.start_soon(clock.start())

    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0

    await ClockCycles(dut.clk, 2)
    assert get_state(dut) == 0b0000, f"Esperaba INICIO, obtuve {get_state(dut):04b}"

    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 1)

    # INICIO con P=1 -> se queda en INICIO
    dut.ui_in.value = 0b00000001   # P=1, A=0
    await ClockCycles(dut.clk, 3)
    assert get_state(dut) == 0b0000, f"Con P=1 debía quedarse en INICIO, obtuvo {get_state(dut):04b}"

    # P=0 -> LLENADO1
    dut.ui_in.value = 0b00000000   # P=0, A=0
    await ClockCycles(dut.clk, 1)
    assert get_state(dut) == 0b0001, f"Esperaba LLENADO1, obtuvo {get_state(dut):04b}"

    # Sigue en LLENADO1 con A=0
    await ClockCycles(dut.clk, 2)
    assert get_state(dut) == 0b0001, f"Debía seguir en LLENADO1, obtuvo {get_state(dut):04b}"

    # A=1 -> LAVADO
    dut.ui_in.value = 0b00000010   # P=0, A=1
    await ClockCycles(dut.clk, 1)
    assert get_state(dut) == 0b0010, f"Esperaba LAVADO, obtuvo {get_state(dut):04b}"

    # Espera 20 ciclos en LAVADO -> VACIADO1
    await ClockCycles(dut.clk, 19)
    assert get_timer_done(dut) == 1, "T debía valer 1 al completar LAVADO"
    await ClockCycles(dut.clk, 1)
    assert get_state(dut) == 0b0011, f"Esperaba VACIADO1, obtuvo {get_state(dut):04b}"

    # Sigue en VACIADO1 con A=1
    dut.ui_in.value = 0b00000010   # P=0, A=1
    await ClockCycles(dut.clk, 2)
    assert get_state(dut) == 0b0011, f"Debía seguir en VACIADO1, obtuvo {get_state(dut):04b}"

    # A=0 -> LLENADO2
    dut.ui_in.value = 0b00000000   # P=0, A=0
    await ClockCycles(dut.clk, 1)
    assert get_state(dut) == 0b0100, f"Esperaba LLENADO2, obtuvo {get_state(dut):04b}"

    # A=1 -> ENJUAGUE
    dut.ui_in.value = 0b00000010   # P=0, A=1
    await ClockCycles(dut.clk, 1)
    assert get_state(dut) == 0b0101, f"Esperaba ENJUAGUE, obtuvo {get_state(dut):04b}"

    # Espera 20 ciclos en ENJUAGUE -> VACIADO2
    await ClockCycles(dut.clk, 19)
    assert get_timer_done(dut) == 1, "T debía valer 1 al completar ENJUAGUE"
    await ClockCycles(dut.clk, 1)
    assert get_state(dut) == 0b0110, f"Esperaba VACIADO2, obtuvo {get_state(dut):04b}"

    # A=0 -> CENTRIF
    dut.ui_in.value = 0b00000000   # P=0, A=0
    await ClockCycles(dut.clk, 1)
    assert get_state(dut) == 0b0111, f"Esperaba CENTRIF, obtuvo {get_state(dut):04b}"

    # Espera 20 ciclos en CENTRIF -> FINALIZAR
    await ClockCycles(dut.clk, 19)
    assert get_timer_done(dut) == 1, "T debía valer 1 al completar CENTRIF"
    await ClockCycles(dut.clk, 1)
    assert get_state(dut) == 0b1000, f"Esperaba FINALIZAR, obtuvo {get_state(dut):04b}"

    # FINALIZAR -> INICIO
    await ClockCycles(dut.clk, 1)
    assert get_state(dut) == 0b0000, f"Esperaba volver a INICIO, obtuvo {get_state(dut):04b}"

    dut._log.info("Test completado correctamente")
