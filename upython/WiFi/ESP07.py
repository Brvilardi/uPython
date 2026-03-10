from machine import UART, Pin
import time


class ESP07:
    """ESP-07 (ESP8266) WiFi module driver using AT commands over UART."""

    def __init__(self, uart_id=1, tx=8, rx=9, baudrate=115200):
        self.uart = UART(uart_id, baudrate=baudrate, tx=Pin(tx), rx=Pin(rx))

    def connect(self, ssid, password, timeout=10):
        """Connect to a WiFi network. Returns True on success."""
        if not self._send_cmd("AT", timeout=2):
            return False
        if not self._send_cmd("AT+CWMODE=1"):
            return False
        resp = self._send_cmd(
            'AT+CWJAP="{}","{}"'.format(ssid, password),
            expected="WIFI GOT IP",
            timeout=timeout,
        )
        return resp

    def is_connected(self):
        """Check if connected to WiFi."""
        response = self._read_cmd("AT+CIPSTATUS")
        if response is None:
            return False
        return "STATUS:2" in response or "STATUS:3" in response

    def disconnect(self):
        """Disconnect from WiFi."""
        return self._send_cmd("AT+CWQAP")

    def ip(self):
        """Returns current IP address or None."""
        response = self._read_cmd("AT+CIFSR")
        if response is None:
            return None
        for line in response.split("\n"):
            if "+CIFSR:STAIP" in line:
                start = line.find('"')
                end = line.rfind('"')
                if start != -1 and end != -1 and start != end:
                    addr = line[start + 1 : end]
                    if addr != "0.0.0.0":
                        return addr
        return None

    def get(self, url):
        """HTTP GET request. Returns response body as string."""
        host, port, path, use_ssl = self._parse_url(url)
        request = "GET {} HTTP/1.1\r\nHost: {}\r\nConnection: close\r\n\r\n".format(
            path, host
        )
        return self._http_request(host, port, request, use_ssl)

    def post(self, url, body, content_type="application/json"):
        """HTTP POST request. Returns response body as string."""
        host, port, path, use_ssl = self._parse_url(url)
        request = (
            "POST {} HTTP/1.1\r\n"
            "Host: {}\r\n"
            "Content-Type: {}\r\n"
            "Content-Length: {}\r\n"
            "Connection: close\r\n"
            "\r\n"
            "{}"
        ).format(path, host, content_type, len(body), body)
        return self._http_request(host, port, request, use_ssl)

    def _http_request(self, host, port, request, use_ssl):
        conn_type = "SSL" if use_ssl else "TCP"
        cmd = 'AT+CIPSTART="{}","{}",{}'.format(conn_type, host, port)
        if not self._send_cmd(cmd, expected="OK", timeout=5):
            return None

        send_cmd = "AT+CIPSEND={}".format(len(request))
        if not self._send_cmd(send_cmd, expected=">", timeout=3):
            self._send_cmd("AT+CIPCLOSE", timeout=1)
            return None

        self.uart.write(request)
        response = self._read_response(timeout=5, stop_on="CLOSED")
        if response is None or "CLOSED" not in response:
            self._send_cmd("AT+CIPCLOSE", timeout=1)

        if response is None:
            return None
        return self._extract_body(response)

    def _send_cmd(self, cmd, expected="OK", timeout=5):
        self.uart.write(cmd + "\r\n")
        response = self._read_response(timeout=timeout)
        if response is None:
            return False
        return expected in response

    def _read_cmd(self, cmd, timeout=5):
        self.uart.write(cmd + "\r\n")
        return self._read_response(timeout=timeout)

    def _read_response(self, timeout=5, stop_on=None):
        start = time.ticks_ms()
        deadline = timeout * 1000
        idle_start = start
        data = b""
        while time.ticks_diff(time.ticks_ms(), start) < deadline:
            if self.uart.any():
                chunk = self.uart.read()
                if chunk:
                    data += chunk
                    idle_start = time.ticks_ms()
                    if stop_on and stop_on in data.decode("utf-8", "ignore"):
                        break
            else:
                # Only wait 500ms of silence after receiving data
                if data and time.ticks_diff(time.ticks_ms(), idle_start) > 500:
                    break
                time.sleep_ms(10)
        if not data:
            return None
        try:
            return data.decode()
        except Exception:
            return None

    def _extract_body(self, response):
        ipd_marker = "+IPD,"
        idx = response.find(ipd_marker)
        if idx == -1:
            return None
        colon = response.find(":", idx)
        if colon == -1:
            return None
        http_data = response[colon + 1 :]
        header_end = http_data.find("\r\n\r\n")
        if header_end == -1:
            return http_data
        return http_data[header_end + 4 :]

    @staticmethod
    def _parse_url(url):
        use_ssl = url.startswith("https://")
        url = url.replace("https://", "").replace("http://", "")

        path = "/"
        slash = url.find("/")
        if slash != -1:
            path = url[slash:]
            url = url[:slash]

        port = 443 if use_ssl else 80
        colon = url.find(":")
        if colon != -1:
            port = int(url[colon + 1 :])
            url = url[:colon]

        host = url
        return host, port, path, use_ssl
