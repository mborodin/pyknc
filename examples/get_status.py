#!/usr/bin/env python3

from knc import ASICBoard

board = ASICBoard(0, 'B', 'G')
print(board.get_status())