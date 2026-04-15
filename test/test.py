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
    clock = Clock(dut.clk, 10, unit="us")
    cocotb.start_soon(clock.start())

    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0

    await ClockCycles(dut.clk, 2)
    assert get_state(dut) == 0b0000

    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 1)

    dut.ui_in.value = 0b00000001  # P=1, A=0
    await ClockCycles(dut.clk, 2)
    assert get_state(dut) == 0b0000

    dut.ui_in.value = 0b00000000  # P=0, A=0
    await ClockCycles(dut.clk, 1)
    assert get_state(dut) == 0b0001

    await ClockCycles(dut.clk, 1)
    assert get_state(dut) == 0b0001

    dut.ui_in.value = 0b00000010  # P=0, A=1
    await ClockCycles(dut.clk, 1)
    assert get_state(dut) == 0b0010

    await ClockCycles(dut.clk, 19)
    assert get_timer_done(dut) == 1
    await ClockCycles(dut.clk, 1)
    assert get_state(dut) == 0b0011

    dut.ui_in.value = 0b00000000  # A=0
    await ClockCycles(dut.clk, 1)
    assert get_state(dut) == 0b0100

    dut.ui_in.value = 0b00000010  # A=1
    await ClockCycles(dut.clk, 1)
    assert get_state(dut) == 0b0101

    await ClockCycles(dut.clk, 19)
    assert get_timer_done(dut) == 1
    await ClockCycles(dut.clk, 1)
    assert get_state(dut) == 0b0110

    dut.ui_in.value = 0b00000000  # A=0
    await ClockCycles(dut.clk, 1)
    assert get_state(dut) == 0b0111

    await ClockCycles(dut.clk, 19)
    assert get_timer_done(dut) == 1
    await ClockCycles(dut.clk, 1)
    assert get_state(dut) == 0b1000

    await ClockCycles(dut.clk, 1)
    assert get_state(dut) == 0b0000
