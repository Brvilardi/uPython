import time
from upython.OledDisplay import SpiOledDisplay
from upython.WiFi import ESP07
from upython.samples.tabbie import Tabbie
from upython.samples.tabbie.config import WIFI_SSID, WIFI_PASSWORD, SERVER_URL
from upython.samples.tabbie.connection import TabbieConnection

print("[boot] init OLED")
oled = SpiOledDisplay(sck=2, sda=3, res=4, dc=5, cs=6)

print("[boot] init WiFi")
wifi = ESP07(tx=8, rx=9)

# ── WiFi connect ─────────────────────────────────────────────────────────────

oled.clear()
oled.write_text("Connecting WiFi...", 0, 0)
print("[wifi] connecting to {}".format(WIFI_SSID))

if not wifi.connect(WIFI_SSID, WIFI_PASSWORD):
    print("[wifi] FAILED")
    oled.clear()
    oled.write_text("WiFi FAILED", 0, 0)
    oled.write_text("Serial only mode", 0, 12)
    # time.sleep_ms(2000)
    # tabbie = Tabbie(oled)
    # tabbie.start()

ip = wifi.ip()
print("[wifi] connected, ip={}".format(ip))
oled.clear()
oled.write_text("WiFi OK", 0, 0)
oled.write_text(ip or "no ip", 0, 12)
oled.write_text(SERVER_URL, 0, 24)
time.sleep_ms(3000)

# ── Server connection test ───────────────────────────────────────────────────

oled.clear()
oled.write_text("Testing server...", 0, 0)
print("[server] testing {}".format(SERVER_URL))

try:
    body = wifi.get(SERVER_URL + "/api/poll")
    print("[server] response: {!r}".format(body))
    if body is None:
        raise Exception("No response")
    oled.clear()
    oled.write_text("Server OK", 0, 0)
    print("[server] OK")
    time.sleep_ms(800)
except Exception as e:
    print("[server] ERROR: {}".format(e))
    oled.clear()
    oled.write_text("Server ERROR", 0, 0)
    oled.write_text(str(e)[:16], 0, 12)
    oled.write_text("Retrying in 5s...", 0, 24)
    time.sleep_ms(5000)

# ── Tabbie + polling loop ────────────────────────────────────────────────────

print("[main] creating Tabbie")
tabbie = Tabbie(oled)
conn = TabbieConnection(wifi, SERVER_URL)

print("[main] startup animation")
tabbie._startup_animation()

print("[main] entering loop")
while True:
    tabbie.animation.update()
    tabbie._poll_serial()
    conn.poll(tabbie)
