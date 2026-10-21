import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, FallingEdge


@cocotb.test()
async def test_send_one_byte(dut):
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())

    # reset
    dut.rst.value = 1
    dut.start.value = 0
    dut.data.value = 0
    for _ in range(3):
        await RisingEdge(dut.clk)
    dut.rst.value = 0
    await FallingEdge(dut.clk)

    # idle line must be high
    assert int(dut.tx.value) == 1, "tx should be 1 when idle"

    # tell the transmitter to send 0xA5
    dut.data.value = 0xA5
    dut.start.value = 1
    await RisingEdge(dut.clk)
    await FallingEdge(dut.clk)
    dut.start.value = 0

    assert int(dut.busy.value) == 1, "busy should be 1 while sending"

    # start bit: middle of the bit must be 0
    for _ in range(2):
        await FallingEdge(dut.clk)
    assert int(dut.tx.value) == 0, "start bit should be 0"

    # 8 data bits, least significant bit first (4 clocks per bit)
    received = 0
    for i in range(8):
        for _ in range(4):
            await FallingEdge(dut.clk)
        received |= int(dut.tx.value) << i

    # stop bit must be 1
    for _ in range(4):
        await FallingEdge(dut.clk)
    assert int(dut.tx.value) == 1, "stop bit should be 1"

    dut._log.info(f"received = {received:#04x}")
    assert received == 0xA5, f"expected 0xA5 but got {received:#04x}"



async def send_and_read(dut, value):
    dut.data.value = value
    dut.start.value = 1
    await RisingEdge(dut.clk)
    await FallingEdge(dut.clk)
    dut.start.value = 0

    for _ in range(2):
        await FallingEdge(dut.clk)
    assert int(dut.tx.value) == 0, "start bit should be 0"

    received = 0
    for i in range(8):
        for _ in range(4):
            await FallingEdge(dut.clk)
        received |= int(dut.tx.value) << i

    for _ in range(4):
        await FallingEdge(dut.clk)
    assert int(dut.tx.value) == 1, "stop bit should be 1"

    # wait until the transmitter is free again
    while int(dut.busy.value) == 1:
        await FallingEdge(dut.clk)

    return received


@cocotb.test()
async def test_many_bytes(dut):
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())

    dut.rst.value = 1
    dut.start.value = 0
    dut.data.value = 0
    for _ in range(3):
        await RisingEdge(dut.clk)
    dut.rst.value = 0
    await FallingEdge(dut.clk)

    for value in [0x00, 0xFF, 0x55, 0xAA, 0x01, 0x80]:
        got = await send_and_read(dut, value)
        dut._log.info(f"sent {value:#04x}, got {got:#04x}")
        assert got == value, f"sent {value:#04x} but got {got:#04x}"



@cocotb.test()
async def test_frame_length(dut):
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())

    dut.rst.value = 1
    dut.start.value = 0
    dut.data.value = 0
    for _ in range(3):
        await RisingEdge(dut.clk)
    dut.rst.value = 0
    await FallingEdge(dut.clk)

    dut.data.value = 0x3C
    dut.start.value = 1
    await RisingEdge(dut.clk)
    await FallingEdge(dut.clk)
    dut.start.value = 0

    count = 0
    while int(dut.busy.value) == 1:
        count += 1
        await FallingEdge(dut.clk)

    dut._log.info(f"busy lasted {count} clocks")
    assert count == 40, f"frame should be 40 clocks but was {count}"