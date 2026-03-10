import json
import time


def _ts():
    """Timestamp as MM:SS since boot."""
    s = time.ticks_ms() // 1000
    return "{}:{:02d}".format(s // 60, s % 60)


class TabbieConnection:
    """Polls FastAPI server for commands and dispatches them to Tabbie."""

    def __init__(self, wifi, server_url, poll_ms=1000):
        """
        @param wifi: ESP07 instance (already connected).
        @param server_url: Base URL of the FastAPI server (e.g. "http://192.168.1.10:8000").
        @param poll_ms: Milliseconds between polls (default 1000).
        """
        self.wifi = wifi
        self.server_url = server_url.rstrip("/")
        self.poll_ms = poll_ms
        self._last_poll = time.ticks_ms()
        self._poll_count = 0

    def poll(self, tabbie):
        """Call every frame. Only does HTTP request every poll_ms milliseconds."""
        now = time.ticks_ms()
        if time.ticks_diff(now, self._last_poll) >= self.poll_ms:
            self._last_poll = now
            self._fetch_and_dispatch(tabbie)

    def _fetch_and_dispatch(self, tabbie):
        """GET /api/poll, parse JSON, dispatch commands to Tabbie."""
        self._poll_count += 1
        url = self.server_url + "/api/poll"
        print("[{}s poll #{}] GET {}".format(_ts(), self._poll_count, url))

        try:
            t0 = time.ticks_ms()
            body = self.wifi.get(url)
            elapsed = time.ticks_diff(time.ticks_ms(), t0)
            print("[{}s poll #{}] response in {}ms: {!r}".format(_ts(), self._poll_count, elapsed, body))

            if body is None:
                print("[{}s poll #{}] ERROR: body is None".format(_ts(), self._poll_count))
                self._show_error(tabbie, "No response")
                return

            # ESP07 response may have trailing AT junk (e.g. "CLOSED\r\n")
            start = body.find("{")
            end = body.rfind("}") + 1
            if start == -1 or end == 0:
                print("[{}s poll #{}] ERROR: no JSON in body".format(_ts(), self._poll_count))
                self._show_error(tabbie, "No JSON found")
                return

            json_str = body[start:end]
            data = json.loads(json_str)
            commands = data.get("commands", [])

            if commands:
                print("[{}s poll #{}] commands: {}".format(_ts(), self._poll_count, commands))
                for cmd in commands:
                    print("[{}s poll #{}] dispatch: {!r}".format(_ts(), self._poll_count, cmd))
                    tabbie._handle_command(cmd)
            else:
                print("[{}s poll #{}] queue empty".format(_ts(), self._poll_count))

        except Exception as e:
            print("[{}s poll #{}] EXCEPTION: {}".format(_ts(), self._poll_count, e))
            self._show_error(tabbie, str(e))

    @staticmethod
    def _show_error(tabbie, msg):
        """Briefly show an error on the OLED, then resume animation."""
        fb = tabbie.oled.display
        fb.fill(0)
        fb.text("Poll error:", 0, 20)
        fb.text(msg[:16], 0, 34)
        fb.show()
        time.sleep_ms(1000)
