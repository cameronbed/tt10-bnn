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
    dut.rst_n.value = 0  
    dut.ui_in[1].value = 0  # rts (was dut.rts)
    dut.ui_in[0].value  = 1  # rx (was dut.rx)
    dut.uio_in[0].value = 0  # baud_clk (was dut.baud_clk)
    await ClockCycles(dut.clk, 5)

    dut.rst_n.value = 1  
    await ClockCycles(dut.clk, 5)
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)

    # Enable the remote side to send data (rts=1). will assert CTS when idle
    dut.ui_in[1].value = 1
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
    dut.ui_in[0].value = 0  # rx (was dut.rx)
    await pulse_baud(dut)  # one bit time

    # Send 8 data bits, LSB first
    for i in range(8):
        bit_val = (byte_val >> i) & 1
        dut.ui_in[0].value = bit_val  # rx (was dut.rx)
        await pulse_baud(dut)

    # Stop bit (high)
    dut.ui_in[0].value = 1  # rx (was dut.rx)
    await pulse_baud(dut)


async def pulse_baud(dut):
    # Raise baud_clk for one clk cycle
    dut.uio_in[0].value = 1  # baud_clk (was dut.baud_clk)
    await RisingEdge(dut.clk)

    # Lower baud_clk for one clk cycle
    dut.uio_in[0].value = 0  # baud_clk (was dut.baud_clk)
    await RisingEdge(dut.clk)
