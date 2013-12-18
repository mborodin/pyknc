import smbus

from knc import PMBus

import re

_BASE_BOARD_ADDR = 3
_FIRST_DCDC = 0x10
_LAST_DCDC = 0x17

_LM75_TEMPERATURE = 0
_LM75_ID = 7
_LM75_ID_HIGH_NIBBLE = 0xA0
_LM75_ADDR = 0x48

_REVISION_FILE = '/etc/revision'


def _bswap(a):
    t1 = 0xFF & a
    t2 = a >> 8
    return (t1 << 8) | t2


def _temp_from_int(i):
    return float(i >> 7) * 0.5


class ASICBoard:
    def __init__(self, board, revision, dcdcmfr):
        self.revision = revision
        self.dcdcmfr = 'Ericsson' if dcdcmfr == 'E' else 'GE'
        self.board = board
        self.bus = smbus.SMBus(_BASE_BOARD_ADDR + self.board)
        self.pmbus = PMBus(self.bus)

    def close(self):
        self.bus.close()

    def get_temperature(self):
        """
        @type bus SMBus
        """
        id = self.bus.read_word_data(_LM75_ADDR, _LM75_ID) & 0xF0
        if id == _LM75_ID_HIGH_NIBBLE:
            temp = _temp_from_int(
                _bswap(self.bus.read_word_data(_LM75_ADDR, _LM75_TEMPERATURE))
            )
        else:
            temp = 0.0
        return temp

    def get_status(self):
        dcdc_status = []
        for dcdc in range(_FIRST_DCDC, _LAST_DCDC + 1):
            dcdc_status.append(self.pmbus.get_status(dcdc))
        status = {
            'id': self.board,
            'rev': self.revision,
            'dcdc_mfr': self.dcdcmfr,
            'dcdc': dcdc_status,
            'temperature': self.get_temperature()
        }
        return status

    def __str__(self):
        return 'ASIC%i rev %s with %s DC/DC' % (self.board, self.revision, self.dcdcmfr)

    def __repr__(self):
        return str(self)


def open_boards():
    fin = open(_REVISION_FILE)
    boards = fin.readlines()
    fin.close()

    regex = re.compile('(?:(?:BOARD)(?P<id>[0-5]))=(?:(?P<revision>[AB])(?P<mfr>[GE])|OFF)')

    asics = []

    for board in boards:
        r = regex.search(board)
        if r is not None:
            params = r.groupdict()
            if params['revision'] is not None:
                asics.append(ASICBoard(int(params['id']), params['revision'], params['mfr']))

    return asics
