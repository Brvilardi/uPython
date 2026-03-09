# WiFi — ESP-07 (ESP8266)

This module provides a driver for the ESP-07 (ESP8266) WiFi module, communicating via AT commands over UART.

## How to set up the connections

Connect the ESP-07 to the Raspberry Pi Pico using 4 wires:

Pico | ESP-07 | Description
--- | --- | ---
GP8 (UART1 TX) | RX | Data from Pico to ESP
GP9 (UART1 RX) | TX | Data from ESP to Pico
3V3 | VCC | Power supply
GND | GND | Ground

    Note: UART1 is used to avoid conflict with UART0 (REPL). GP4-GP6 are reserved for the SPI OLED display.

## How to use the module

```python
from upython.WiFi import ESP07

wifi = ESP07(tx=4, rx=5)

# Connect to WiFi
wifi.connect("MyNetwork", "password123")

# Check IP address
print(wifi.ip())  # '192.168.1.42'

# HTTP GET
response = wifi.get("http://api.example.com/tasks")
print(response)

# HTTP POST
wifi.post("http://api.example.com/done", '{"task": "study"}')

# Check connection
wifi.is_connected()  # True

# Disconnect
wifi.disconnect()
```
