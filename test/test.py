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
    
    # initial reset sequence
    dut.rst.value = 0
    dut.rts.value = 0  # remote side not requesting to send yet
    dut.rx.value  = 1  # idle line (UART is idle-high)
    dut.baud_clk.value = 0
    await ClockCycles(dut.clk, 5)

    dut.rst.value = 1  # assert reset
    await ClockCycles(dut.clk, 5)
    dut.rst.value = 0  # deassert reset
    await ClockCycles(dut.clk, 10)

    # Enable the remote side to send data (rts=1). will assert CTS when idle
    dut.rts.value = 1
    await ClockCycles(dut.clk, 10)

    # test byte, 0xA5 (1010_0101)
    TEST_BYTE = 0xA5

    # transmit a byte into rx by manually w/ rx & baud_clk
    await uart_write_byte(dut, TEST_BYTE)

    # Wait some cycles
    await ClockCycles(dut.clk, 20)

    # Check that data_valid went high and data_out == TEST_BYTE
    received_byte = dut.data_out.value.integer
    if dut.data_valid.value == 1:
        dut._log.info(f"Received byte 0x{received_byte:02X}")
        assert received_byte == TEST_BYTE, f"Mismatch! Expected 0x{TEST_BYTE:02X}, got 0x{received_byte:02X}"
    else:
        raise AssertionError("data_valid never asserted after sending byte")


async def uart_write_byte(dut, byte_val):
    # Start bit (low)
    dut.rx.value = 0
    await pulse_baud(dut)  # one bit time

    # Send 8 data bits, LSB first
    for i in range(8):
        bit_val = (byte_val >> i) & 1
        dut.rx.value = bit_val
        await pulse_baud(dut)

    # Stop bit (high)
    dut.rx.value = 1
    await pulse_baud(dut)


async def pulse_baud(dut):
    # Raise baud_clk for one clk cycle
    dut.baud_clk.value = 1
    await RisingEdge(dut.clk)

    # Lower baud_clk for one clk cycle
    dut.baud_clk.value = 0
    await RisingEdge(dut.clk)
