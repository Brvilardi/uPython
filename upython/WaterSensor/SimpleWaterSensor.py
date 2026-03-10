from machine import Pin, ADC

class WaterSensor:
    """Class to control a water sensor"""
    pin: Pin
    adc: ADC

    def __init__(self, pin_number: int = 26):
        """Constructor
        @param pin_number: The number
        of the pin where the water sensor is connected. Default is 26 (ADC0 on Raspberry Pi Pico)
        """
        self.pin = Pin(pin_number, Pin.IN)
        self.adc = ADC(self.pin)  # Initialize ADC on the pin

    def read(self) -> int:
        """Read the value from the water sensor.
        @return: The value read from the water sensor.
        """
        return self.adc.read_u16()

