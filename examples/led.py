#!/usr/bin/env python3

from knc import led

import time


def on_off_red_led():
    red = led.get_led('red')
    red.on()
    time.sleep(30)
    red.off()


def blink_rgb():
    rgb = led.get_led('rgb')
    rgb.set_mode(led.MODE_BLINKING)
    rgb.on()
    time.sleep(30)
    rgb.off()


def blink_leds():
    l = led.get_led('green')
    l.set_mode(led.MODE_BLINKING)
    l.frequency = 5
    l.on()

    l = led.get_led('rgb')
    l.set_mode(led.MODE_BLINKING)
    l.frequency = 10
    l.on()

    time.sleep(15)
    l.frequency = 20

    time.sleep(15)
    led.shutdown_blinking_leds()


if __name__ == '__main__':
    on_off_red_led()
    blink_rgb()
    blink_leds()
