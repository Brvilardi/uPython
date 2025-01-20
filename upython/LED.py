import time

from machine import Pin, Timer


class LED:
    """Class to control a LED"""
    pin: Pin

    def __init__(self, pin_number: int = 25):
        """Constructor
        @param pin_number: The number of the pin where the LED is connected. Default is 25 (built-in LED on Raspberry Pi Pico)
        """
        self.pin =  Pin(pin_number, Pin.OUT)
        self.timer = Timer()

    def turn_on(self):
        """Turn the LED on"""
        self.pin.value(1)

    def turn_off(self):
        """Turn the LED off"""
        self.pin.value(0)


    def blink(self, interval: int = 1):
        """Blink the LED.
        @param interval: The interval in seconds. Default is 1 second.
        """
        self.turn_on()
        time.sleep(interval)
        self.turn_off()
        time.sleep(interval)

    def blink_indefinitely(self, interval: int = 1000):
        """Blink the LED indefinitely.
        @param interval: The interval in ms. Default is 1000 seconds.
        """
        self.timer.init(period=interval, mode=Timer.PERIODIC, callback=lambda t: self.pin.toggle())


