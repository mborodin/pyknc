#!/usr/bin/env python3

from knc import device

boards = device.open_boards()
print(boards[0].get_status())