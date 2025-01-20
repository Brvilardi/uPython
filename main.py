from time import sleep

from machine import Pin

print("Hello World!")

from upython.LED import LED
print("LED imported")

# Create a Pin object for the built-in LED
led = LED()

# Turn the LED on
while(1):
    print("Blinking!!!!")
    led.blink()


# Turn the LED off

