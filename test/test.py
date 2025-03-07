# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, RisingEdge

import serial
import numpy as np


DIGIT_3_IMAGE = np.array([
    "0000000000000000000000000000",
    "0000111111100000000000000000",
    "0001100000110000000000000000",
    "0011000000011000000000000000",
    "0011000000011000000000000000",
    "0000000000011000000000000000",
    "0000000000110000000000000000",
    "0000000001100000000000000000",
    "0000000011000000000000000000",
    "0000000110000000000000000000",
    "0000001100000000000000000000",
    "0000011111100000000000000000",
    "0000000000110000000000000000",
    "0000000000011000000000000000",
    "0000000000011000000000000000",
    "0000000000011000000000000000",
    "0000000000011000000000000000",
    "0000000000011000000000000000",
    "0011000000011000000000000000",
    "0011000000011000000000000000",
    "0001100000110000000000000000",
    "0000111111100000000000000000",
    "0000000000000000000000000000",
    "0000000000000000000000000000",
    "0000000000000000000000000000",
    "0000000000000000000000000000",
    "0000000000000000000000000000",
    "0000000000000000000000000000",
], dtype=str)

# Convert to binary (2D NumPy array of 1s and 0s)
DIGIT_3_BINARY = np.array([[int(c) for c in row] for row in DIGIT_3_IMAGE])

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
    dut.ui_in[1].value = 0 
    dut.ui_in[0].value  = 1  
    dut.uio_in[0].value = 0  
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

    dut._log.info("Preparing to send a test byte over UART")
    # transmit a byte into rx by manually w/ rx & baud_clk
    dut._log.info(f"Sending 0x{TEST_BYTE:02X}")
    await uart_write_byte(dut, TEST_BYTE)

    # Wait some cycles
    await ClockCycles(dut.clk, 20)

    # Check that rx_valid went high and rx_data == TEST_BYTE
    received_byte = dut.user_project.bnn_inst.rx_data.value.integer
    if dut.user_project.bnn_inst.rx_valid.value == 1:
        dut._log.info(f"Received byte 0x{received_byte:02X} successfully")
        assert received_byte == TEST_BYTE, f"Mismatch! Expected 0x{TEST_BYTE:02X}, got 0x{received_byte:02X}"
    else:
        raise AssertionError("data_valid never asserted after sending byte")

    # # Reset
    # dut.rst.value = 1
    # dut.rx.value = 1   # UART idle state
    # dut.rts.value = 1  # Indicate that the sender is ready
    # dut.baud_clk.value = 0
    # await ClockCycles(dut.clk, 10)

    # dut.rst.value = 0  # Release reset
    # await ClockCycles(dut.clk, 20)

    # # Convert 28x28 binary image into a serialized 1D list (LSB first)
    # serialized_bits = DIGIT_3_BINARY.flatten().tolist()

    # # Send the image bit-by-bit
    # await send_uart_image(dut, serialized_bits)

    # # Wait enough time for the DUT to store the image into the buffer
    # await ClockCycles(dut.clk, 1000)

    # # Read back the stored image from the image buffer
    # received_image = await read_image_from_buffer(dut)

    # # Print the received image as a binary grid
    # print("\nReceived Image:")
    # for row in received_image:
    #     print("".join(str(bit) for bit in row))

    # # Compare the received image with the original
    # assert np.array_equal(received_image, DIGIT_3_BINARY), "Received image does not match expected!"

async def send_uart_image(dut, bitstream):
    """Send a serialized bitstream (list of 1s and 0s) through UART."""
    for bit in bitstream:
        dut.rx.value = bit
        await pulse_baud(dut)
        
async def read_image_from_buffer(dut):
    """Read the stored image from image_buffer.sv."""
    received_bits = []
    for i in range(28 * 28):  # Read 784 bits from the buffer
        bit = dut.image_buffer[i].value.integer  # Read each bit
        received_bits.append(bit)

    # Reshape into 28x28 matrix
    return np.array(received_bits).reshape((28, 28))

async def uart_write_byte(dut, byte_val):
    dut._log.info(f"Transmitting byte 0x{byte_val:02X}")
    # Start bit (low)
    dut.ui_in[0].value = 0  # rx (was dut.rx)
    await pulse_baud(dut)  # one bit time

    # Send 8 data bits, LSB first
    for i in range(8):
        bit_val = (byte_val >> i) & 1
        dut.ui_in[0].value = bit_val  
        await pulse_baud(dut)

    # Stop bit (high)
    dut.ui_in[0].value = 1 
    await pulse_baud(dut)
    dut._log.info("Completed UART write operation")

async def pulse_baud(dut):
    # Raise baud_clk for one clk cycle
    dut.uio_in[0].value = 1  
    await RisingEdge(dut.clk)

    # Lower baud_clk for one clk cycle
    dut.uio_in[0].value = 0 
    await RisingEdge(dut.clk)