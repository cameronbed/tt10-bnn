# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles

import serial

@cocotb.test()
async def test_project(dut):
    dut._log.info("Start")

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
    
    dut._log.info("Opening Serial Port")
    
    # Open Serial Port (loopback device or use virtual serial)
    try:
        uart = serial.Serial(
            port='/dev/ttyUSB0',  # Update this based on your setup (use a virtual serial port)
            baudrate=115200,  # Match the UART baudrate in DUT
            timeout=1  # Timeout for read operation
            # print(f"Serial port opened: {uart}"
        )
    except serial.SerialException as e:
        dut._log.error(f"Serial port error: {e}")
        # print(f"Serial port error: {e}")
        return
    
    test_byte = b'\x55'  
    dut._log.info(f"Sending UART data: {test_byte.hex()}")
    uart.write(test_byte)

    dut._log.info("Test project behavior")

    # Set the input values you want to test
    dut.ui_in.value = 20
    dut.uio_in.value = 30

    # Wait for one clock cycle to see the output values
    await ClockCycles(dut.clk, 1)

    # The following assersion is just an example of how to check the output values.
    # Change it to match the actual expected output of your module:
    assert dut.uo_out.value == 50, "Example check"

    # Additional test scenario
    dut._log.info("Testing additional inputs")
    dut.ui_in.value = 40
    dut.uio_in.value = 10
    await ClockCycles(dut.clk, 1)
    assert dut.uo_out.value == 50, "Output should be 50"
    
    uart.close()
    dut._log.info("Serial port closed")

    # Keep testing the module by changing the input values, waiting for
    # one or more clock cycles, and asserting the expected output values.
