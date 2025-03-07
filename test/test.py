# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles

import serial

@cocotb.test()
async def test_project(dut):
    dut._log.info("Starting")

    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units="us")
    cocotb.start_soon(clock.start())

    # Reset
    dut._log.info("Reset")
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 10)  # Added delay for outputs to settle

    # Basic functionality test
    dut.ui_in.value = 1
    await ClockCycles(dut.clk, 5)   # Allow time for signals to become valid
    assert dut.uo_out.value == 0, "Basic functionality test failed"

@cocotb.test()
async def test_uart_rx(dut):
    dut._log.info("Testing UART RX")
    dut.ui_in.value = 1  # Idle high on Rx
    await ClockCycles(dut.clk, 10)

    # Simulate start bit
    dut.ui_in.value = 0
    await ClockCycles(dut.clk, 16)

    # Simulate data bits (example: 0x55)
    # ...existing code...
    # End with stop bit
    dut.ui_in.value = 1
    await ClockCycles(dut.clk, 16)

    # Optionally check if bnn_controller captured data
    # ...existing code...
