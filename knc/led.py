import smbus
import threading
import time

__blinking_leds = []

_LED_RED = '/sys/class/gpio/gpio70/direction'
_LED_GREEN = '/sys/class/gpio/gpio71/direction'

_FPGA_BUS = 2
_FPGA_DEV = 0x71
_LED_RGB = 5

RED = 4
GREEN = 2
BLUE = 1
WHITE = 7
OFF = 0
ON = WHITE

MODE_CONST = 0
MODE_BLINKING = 1


def _add_blinking_led(led):
    __blinking_leds.append(led)


def _remove_blinking_led(led):
    __blinking_leds.remove(led)


def shutdown_blinking_leds():
    while len(__blinking_leds) != 0:
        led = __blinking_leds.pop()
        led.off()


class Led:
    def __init__(self, file):
        self.file = file
        self._on = 'low'
        self._off = 'high'
        self.current_state = self._off
        self.saved_state = self._on
        self.frequency = 2  # 2 Hz is default blinking frequency
        self.is_blinking = False
        self.thread = None
        self.mode = MODE_CONST

    def set_state(self, state):
        fout = open(self.file, 'w')
        fout.write(state)
        fout.close()
        self.current_state = state

    def set_mode(self, mode):
        self.mode = mode

    def on(self):
        if self.mode == MODE_BLINKING:
            self.thread = threading.Thread(target=self._run)
            self.is_blinking = True
            _add_blinking_led(self)
            self.thread.start()
        else:
            self.set_state(self.saved_state)

    def off(self):
        if self.mode == MODE_BLINKING:
            self.is_blinking = False
            self.thread.join()
            _remove_blinking_led(self)
        self.set_state(self._off)

    def set_value(self, v):
        self.saved_state = v
        if v != 0:
            self.on()
        else:
            self.off()

    def invert(self):
        new_state = self._off if self.current_state == self._on else self._on
        self.set_state(new_state)

    def save_state(self):
        self.saved_state = self.current_state

    def restore_state(self):
        if self.saved_state != '':
            self.set_state(self.saved_state)

    def _run(self):
        while self.is_blinking:
            timeout = 1. / self.frequency
            self.invert()
            time.sleep(timeout)


class RGBLed(Led):

    def __init__(self):
        super().__init__('')
        self._on = WHITE
        self._off = OFF
        self.current_state = self._off
        self.saved_state = self._on
        self.bus = smbus.SMBus(_FPGA_BUS)

    def set_state(self, state):
        self.current_state = state
        self.bus.write_byte_data(_FPGA_DEV, _LED_RGB, state)

    def set_value(self, v):
        self.saved_state = v
        self.set_state(v)

    def invert(self):
        new_state = OFF if self.current_state != OFF else self.saved_state
        self.set_state(new_state)


def get_led(led):
    if led == 'green':
        return Led(_LED_GREEN)
    elif led == 'red':
        return Led(_LED_RED)
    elif led == 'rgb':
        return RGBLed()
    return None
