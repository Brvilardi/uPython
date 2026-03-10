"""Tabbie WiFi-enabled entry point.

Upload this file to the Pico alongside the upython/ package.
Update config.py with your WiFi credentials and server IP.
"""
import time

from upython.OledDisplay import SpiOledDisplay
from upython.WiFi import ESP07

from .Tabbie import Tabbie
from .config import WIFI_SSID, WIFI_PASSWORD, SERVER_URL
from .connection import TabbieConnection

# ── Hardware init ────────────────────────────────────────────────────────────

oled = SpiOledDisplay(sck=2, sda=3, res=4, dc=5, cs=6)
wifi = ESP07(tx=8, rx=9)

# ── WiFi connect (show status on screen) ─────────────────────────────────────

oled.clear()
oled.write_text("Connecting WiFi...", 0, 0)

if wifi.connect(WIFI_SSID, WIFI_PASSWORD):
    ip = wifi.ip()
    oled.clear()
    oled.write_text("WiFi OK", 0, 0)
    oled.write_text(ip or "no ip", 0, 12)
    oled.write_text(SERVER_URL, 0, 24)
    time.sleep_ms(1500)
else:
    oled.clear()
    oled.write_text("WiFi FAILED", 0, 0)
    time.sleep_ms(2000)

# ── Tabbie + connection ──────────────────────────────────────────────────────

tabbie = Tabbie(oled)
conn = TabbieConnection(wifi, SERVER_URL)

# Run startup animation
tabbie._startup_animation()

# ── Main loop ────────────────────────────────────────────────────────────────

while True:
    tabbie.animation.update()
    tabbie._poll_serial()
    conn.poll(tabbie)
