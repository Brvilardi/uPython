from machine import Pin, I2C
from .ssd1306 import SSD1306_I2C


class OledDisplay:
    """OLED Display using SSD1306 over I2C (SCL/SDA).
    Requires the ssd1306 MicroPython driver to be installed on the board.
    """

    display: SSD1306_I2C

    def __init__(self, sda: int = 0, scl: int = 1, width: int = 128, height: int = 64, i2c_id: int = 0):
        """Constructor
        @param sda: The pin number for SDA.
        @param scl: The pin number for SCL.
        @param width: Display width in pixels.
        @param height: Display height in pixels.
        @param i2c_id: The I2C bus id.
        """
        i2c = I2C(i2c_id, sda=Pin(sda), scl=Pin(scl))
        self.width = width
        self.height = height
        self.display = SSD1306_I2C(width, height, i2c)
        self.clear()

    def clear(self):
        """Clear the display."""
        self.display.fill(0)
        self.display.show()

    def write_text(self, text: str, x: int = 0, y: int = 0):
        """Write text at a given position and update the display.
        @param text: The text to display.
        @param x: Horizontal position in pixels.
        @param y: Vertical position in pixels.
        """
        self.display.text(text, x, y)
        self.display.show()

    def write_lines(self, lines: list, start_x: int = 0, start_y: int = 0, line_spacing: int = 10):
        """Write multiple lines of text.
        @param lines: A list of strings, one per line.
        @param start_x: Horizontal position in pixels.
        @param start_y: Vertical position of the first line in pixels.
        @param line_spacing: Vertical spacing between lines in pixels.
        """
        for i, line in enumerate(lines):
            self.display.text(line, start_x, start_y + i * line_spacing)
        self.display.show()

    def invert(self, state: bool):
        """Invert the display colors.
        @param state: True to invert, False for normal.
        """
        self.display.invert(state)

    def set_pixel(self, x: int, y: int, color: int = 1):
        """Set a single pixel.
        @param x: Horizontal position.
        @param y: Vertical position.
        @param color: 1 for on, 0 for off.
        """
        self.display.pixel(x, y, color)
        self.display.show()
