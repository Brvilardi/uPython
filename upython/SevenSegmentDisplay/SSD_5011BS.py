import time
from machine import Pin


class SSD_5011BS:
    """Seven Segment Display 5011BS.
    This is a display that has each connection to a segment of the display (a-g) and the dot.
    """

    NUMBER_MAP = {
        0: {"a": 1, "b": 1, "c": 1, "d": 1, "e": 1, "f": 1, "g": 0, "dot": 0},
        1: {"a": 0, "b": 1, "c": 1, "d": 0, "e": 0, "f": 0, "g": 0, "dot": 0},
        2: {"a": 1, "b": 1, "c": 0, "d": 1, "e": 1, "f": 0, "g": 1, "dot": 0},
        3: {"a": 1, "b": 1, "c": 1, "d": 1, "e": 0, "f": 0, "g": 1, "dot": 0},
        4: {"a": 0, "b": 1, "c": 1, "d": 0, "e": 0, "f": 1, "g": 1, "dot": 0},
        5: {"a": 1, "b": 0, "c": 1, "d": 1, "e": 0, "f": 1, "g": 1, "dot": 0},
        6: {"a": 1, "b": 0, "c": 1, "d": 1, "e": 1, "f": 1, "g": 1, "dot": 0},
        7: {"a": 1, "b": 1, "c": 1, "d": 0, "e": 0, "f": 0, "g": 0, "dot": 0},
        8: {"a": 1, "b": 1, "c": 1, "d": 1, "e": 1, "f": 1, "g": 1, "dot": 0},
        9: {"a": 1, "b": 1, "c": 1, "d": 1, "e": 0, "f": 1, "g": 1, "dot": 0}
    }

    segments: dict

    def __init__(self, a: int = 19, b: int = 18, c: int = 12, d: int = 15, e: int = 14, f: int = 16, g: int = 17, dot: int = 13, common_cathode: bool = True):
        """Constructor
        @param a: The number of the pin where the a segment is connected.
        @param b: The number of the pin where the b segment is connected.
        @param c: The number of the pin where the c segment is connected.
        @param d: The number of the pin where the d segment is connected.
        @param e: The number of the pin where the e segment is connected.
        @param f: The number of the pin where the f segment is connected.
        @param g: The number of the pin where the g segment is connected.
        @param dot: The number of the pin where the dot is connected.
        """
        self.segments = {
            "a": Pin(a, Pin.OUT),
            "b": Pin(b, Pin.OUT),
            "c": Pin(c, Pin.OUT),
            "d": Pin(d, Pin.OUT),
            "e": Pin(e, Pin.OUT),
            "f": Pin(f, Pin.OUT),
            "g": Pin(g, Pin.OUT),
            "dot": Pin(dot, Pin.OUT)
        }

        self.common_cathode = common_cathode

        self.set_number(0) #default value


    def set_number(self, number: int):
        """Set the number to display
        @param number: The number to display. Must be between 0 and 9.
        """
        if number < 0 or number > 9:
            raise ValueError("Number must be between 0 and 9")

        for i in self.segments:
            # Get correct value
            value = self.NUMBER_MAP[number][i]

            # Invert the value if it is common anode
            value = value if self.common_cathode else not value

            # Set the value
            self.segments[i].value(value)


    def get_state(self):
        sorted_segments = list(self.segments.keys())
        sorted_segments.sort()
        for seg in sorted_segments:
            print(f"{seg} = {self.segments[seg].value()}")

    def set_decimal_point(self, state: bool):
        """Set the state of the decimal point
        @param state: True to turn the decimal point on, False to turn it off
        """
        self.segments["dot"].value(state if self.common_cathode else not state)



