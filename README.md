\# cocotb-uart



A UART transmitter written in Verilog and verified with cocotb (Python) and Icarus Verilog.



\## What it does

Takes one byte and sends it out one bit at a time on a single wire:

1 start bit, 8 data bits (least significant bit first), 1 stop bit.

Each bit lasts 4 clock cycles (CLKS\_PER\_BIT = 4).



\## Tests

1\. test\_send\_one\_byte - sends 0xA5 and reads the wire bit by bit

2\. test\_many\_bytes - sends 0x00, 0xFF, 0x55, 0xAA, 0x01, 0x80

3\. test\_frame\_length - checks the transmitter stays busy for exactly 40 clocks



\## Bug found by my tests

I planted a bug on purpose: a stop bit that was too short.

The first two tests missed it, because the line is 1 during the stop bit

and also when idle. The timing test caught it. Then I fixed the bug.



\## How to run

make



\## Tools

Verilog, Python, cocotb 2.1.0, Icarus Verilog, make

