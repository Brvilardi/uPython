from machine import Pin, SPI
from .ssd1306 import SSD1306_SPI


class SpiOledDisplay:
    """OLED Display using SSD1306 over SPI (SCK/SDA/RES/DC/CS)."""

    def __init__(self, sck: int = 2, sda: int = 3, res: int = 4, dc: int = 5, cs: int = 6,
                 width: int = 128, height: int = 64, spi_id: int = 0):
        """Constructor
        @param sck: The pin number for SCK (clock).
        @param sda: The pin number for SDA (MOSI/data).
        @param res: The pin number for RES (reset).
        @param dc: The pin number for DC (data/command).
        @param cs: The pin number for CS (chip select).
        @param width: Display width in pixels.
        @param height: Display height in pixels.
        @param spi_id: The SPI bus id.
        """
        spi = SPI(spi_id, baudrate=10_000_000, sck=Pin(sck), mosi=Pin(sda))
        self.width = width
        self.height = height
        self.display = SSD1306_SPI(width, height, spi, Pin(dc), Pin(res), Pin(cs))
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