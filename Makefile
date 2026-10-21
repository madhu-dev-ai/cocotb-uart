SIM = icarus
TOPLEVEL_LANG = verilog
VERILOG_SOURCES = $(CURDIR)/uart_tx.v
COCOTB_TOPLEVEL = uart_tx
COCOTB_TEST_MODULES = test_uart_tx

include $(shell cocotb-config --makefiles)/Makefile.sim