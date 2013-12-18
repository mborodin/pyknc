import time

_PMBUS_VOUT_MODE = 0x20
_PMBUS_STATUS_WORD = 0x79
_PMBUS_STATUS_VOUT = 0x7a
_PMBUS_STATUS_IOUT = 0x7b
_PMBUS_READ_VIN = 0x88
_PMBUS_READ_VOUT = 0x8b
_PMBUS_READ_IOUT = 0x8c
_PMBUS_STATUS_VOUT_FAULT = (1 << 15)
_PMBUS_STATUS_IOUT_FAULT = (1 << 14)
_PMBUS_STATUS_POWER_GOOD = (1 << 11)
_PMBUS_STATUS_BUSY = (1 << 7)
_PMBUS_STATUS_OFF = (1 << 6)
_PMBUS_STATUS_VOUT_OV = (1 << 5)
_PMBUS_STATUS_IOUT_OC = (1 << 4)
_PMBUS_STATUS_VIN_UV = (1 << 3)
_PMBUS_STATUS_TEMPERATUREB = (1 << 2)
_PMBUS_STATUS_CMLB = (1 << 1)
_PMBUS_STATUS_NONE = (1 << 0)
_PMBUS_STATUS_VOUT_FAULT_OV = (1 << 7)
_PMBUS_STATUS_VOUT_FAULT_UV = (1 << 4)
_PMBUS_STATUS_IOUT_FAULT = (1 << 7)
_PMBUS_STATUS_IOUT_WARN = (1 << 5)


def _convert_from_pmbus_float(exp, mant):
    exp = exp if exp <= 0xf else -(~(exp - 1) & 0x1f)
    if exp < 0:
        res = float(mant) / float(1 << (-exp))
    else:
        res = float(mant) * float(1 << exp)
    return res


def _float_from_linear(v):
    tmp = v
    exp = tmp >> 11
    mant = (tmp << 5) & 0xFFFF
    mant >>= 5
    return _convert_from_pmbus_float(exp, mant)


def _convert_vout(mant, mode):
    exp = mode << 3
    exp >>= 3
    return _convert_from_pmbus_float(exp, mant)


class PMBus:
    def __init__(self, bus=None, timeout=0.1):
        """
            @type bus smbus.SMBus
            @type addr int
        """
        self.bus = bus
        self.timeout = timeout

    def get_status(self, addr=0x10):
        vin = self.bus.read_word_data(addr, _PMBUS_READ_VIN)
        time.sleep(self.timeout)
        vout = self.bus.read_word_data(addr, _PMBUS_READ_VOUT)
        time.sleep(self.timeout)
        vout_mode = self.bus.read_byte_data(addr, _PMBUS_VOUT_MODE)
        time.sleep(self.timeout)
        iout = self.bus.read_word_data(addr, _PMBUS_READ_IOUT)
        time.sleep(self.timeout)
        status_word = self.bus.read_word_data(addr, _PMBUS_STATUS_WORD)
        time.sleep(self.timeout)
        status_vout = self.bus.read_byte_data(addr, _PMBUS_STATUS_VOUT)
        time.sleep(self.timeout)
        status_iout = self.bus.read_byte_data(addr, _PMBUS_STATUS_IOUT)
        time.sleep(self.timeout)

        vin_status = {
            'value': _float_from_linear(vin),
            'uv': 1 if status_word & _PMBUS_STATUS_VIN_UV else 0
        }

        vout_status = {
            'value': _convert_vout(vout, vout_mode),
            'fault': 1 if status_word & _PMBUS_STATUS_VOUT_FAULT else 0,
            'ov': 1 if status_word & _PMBUS_STATUS_VOUT_OV else 0,
            'ov_fault': 1 if status_vout & _PMBUS_STATUS_VOUT_FAULT_OV else 0,
            'uv_fault': 1 if status_vout & _PMBUS_STATUS_VOUT_FAULT_UV else 0
        }

        iout_status = {
            'value': _float_from_linear(iout),
            'fault': 1 if status_iout & _PMBUS_STATUS_IOUT_FAULT else 0,
            'warn': 1 if status_iout & _PMBUS_STATUS_IOUT_WARN else 0,
            'oc': 1 if status_word & _PMBUS_STATUS_IOUT_OC else 0
        }

        status = {
            'addr': addr,
            'power_good': 1 if ~ (status_word & _PMBUS_STATUS_POWER_GOOD) else 0,
            'busy': 1 if status_word & _PMBUS_STATUS_BUSY else 0,
            'off': 1 if status_word & _PMBUS_STATUS_OFF else 0,
            'none': 1 if status_word & _PMBUS_STATUS_NONE else 0,
            'temp': 1 if status_word & _PMBUS_STATUS_TEMPERATUREB else 0,
            'cml': 1 if status_word & _PMBUS_STATUS_CMLB else 0,
            'vin': vin_status,
            'vout': vout_status,
            'iout': iout_status
        }
        return status
