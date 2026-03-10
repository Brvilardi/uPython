import math


class Face:
    """Renders face expressions on an SSD1306 framebuf-based display."""

    def __init__(self, display):
        """
        @param display: SSD1306_SPI (or compatible framebuf) instance.
        """
        self.fb = display

    # ── Drawing primitives ──────────────────────────────────────────

    def _circle(self, cx, cy, r, fill=False):
        """Midpoint circle algorithm."""
        x = r
        y = 0
        err = 1 - r
        while x >= y:
            if fill:
                self.fb.hline(cx - x, cy + y, 2 * x + 1, 1)
                self.fb.hline(cx - x, cy - y, 2 * x + 1, 1)
                self.fb.hline(cx - y, cy + x, 2 * y + 1, 1)
                self.fb.hline(cx - y, cy - x, 2 * y + 1, 1)
            else:
                for sx, sy in ((x, y), (-x, y), (x, -y), (-x, -y),
                               (y, x), (-y, x), (y, -x), (-y, -x)):
                    self.fb.pixel(cx + sx, cy + sy, 1)
            y += 1
            if err < 0:
                err += 2 * y + 1
            else:
                x -= 1
                err += 2 * (y - x) + 1

    def _filled_ellipse(self, cx, cy, rx, ry):
        """Draw a filled ellipse using horizontal scan lines."""
        if rx <= 0 or ry <= 0:
            return
        for dy in range(-ry, ry + 1):
            # ellipse equation: (dx/rx)^2 + (dy/ry)^2 <= 1
            dx = int(rx * math.sqrt(max(0, 1 - (dy * dy) / (ry * ry))))
            if dx > 0:
                self.fb.hline(cx - dx, cy + dy, 2 * dx + 1, 1)

    def _arc(self, cx, cy, half_w, curvature):
        """Draw a curved line (mouth). Positive curvature = smile, negative = frown."""
        if abs(curvature) < 0.01:
            self.fb.hline(cx - half_w, cy, 2 * half_w + 1, 1)
            return
        for dx in range(-half_w, half_w + 1):
            t = dx / half_w  # -1..1
            dy = int(curvature * half_w * (1 - t * t) * 0.5)
            self.fb.pixel(cx + dx, cy + dy, 1)
            # thicken the arc
            self.fb.pixel(cx + dx, cy + dy + 1, 1)

    def _heart(self, cx, cy, size):
        """Draw a small filled heart shape."""
        r = max(2, size // 3)
        self._circle(cx - r, cy - r, r, fill=True)
        self._circle(cx + r, cy - r, r, fill=True)
        # triangle bottom
        for row in range(0, size):
            half = max(0, 2 * r + 1 - row)
            self.fb.hline(cx - half, cy + row, 2 * half + 1, 1)

    def _line_angled(self, cx, cy, length, angle_deg):
        """Draw a 1px line from center at given angle."""
        rad = math.radians(angle_deg)
        dx = math.cos(rad) * length / 2
        dy = math.sin(rad) * length / 2
        x0, y0 = int(cx - dx), int(cy - dy)
        x1, y1 = int(cx + dx), int(cy + dy)
        self._line(x0, y0, x1, y1)

    def _line(self, x0, y0, x1, y1):
        """Bresenham's line algorithm."""
        steep = abs(y1 - y0) > abs(x1 - x0)
        if steep:
            x0, y0 = y0, x0
            x1, y1 = y1, x1
        if x0 > x1:
            x0, x1 = x1, x0
            y0, y1 = y1, y0
        dx = x1 - x0
        dy = abs(y1 - y0)
        err = dx // 2
        ystep = 1 if y0 < y1 else -1
        y = y0
        for x in range(x0, x1 + 1):
            if steep:
                self.fb.pixel(y, x, 1)
            else:
                self.fb.pixel(x, y, 1)
            err -= dy
            if err < 0:
                y += ystep
                err += dx

    # ── Face component drawing ──────────────────────────────────────

    def _draw_eye(self, data, pos, offset_x=0, offset_y=0):
        """Draw a single eye."""
        cx = int(pos[0]) + offset_x
        cy = int(pos[1]) + offset_y
        r = int(data['radius'])
        openness = data['openness']
        shape = data['shape']

        if shape == 'heart':
            self._heart(cx, cy, r)
        elif shape == 'line' or openness <= 0.05:
            # closed eye — horizontal line
            self.fb.hline(cx - r, cy, 2 * r + 1, 1)
            self.fb.hline(cx - r, cy + 1, 2 * r + 1, 1)
        elif openness < 1.0:
            # partially open — filled ellipse (squished vertically)
            ry = max(2, int(r * openness))
            self._filled_ellipse(cx, cy, r, ry)
        else:
            # fully open circle
            self._circle(cx, cy, r, fill=True)

    def _draw_mouth(self, data, offset_x=0, offset_y=0):
        """Draw the mouth."""
        cx = int(data['center'][0]) + offset_x
        cy = int(data['center'][1]) + offset_y
        half_w = int(data['width']) // 2
        curvature = data['curvature']

        if data['shape'] == 'line':
            self.fb.hline(cx - half_w, cy, 2 * half_w + 1, 1)
            self.fb.hline(cx - half_w, cy + 1, 2 * half_w + 1, 1)
        else:
            self._arc(cx, cy, half_w, curvature)

    def _draw_eyebrow(self, cx, cy, length, angle_deg, is_right, offset_x=0, offset_y=0):
        """Draw a single eyebrow. Angle is mirrored for the right side."""
        cx = int(cx) + offset_x
        cy = int(cy) + offset_y
        length = int(length)
        actual_angle = -angle_deg if is_right else angle_deg
        self._line_angled(cx, cy, length, actual_angle)
        # thicken
        self._line_angled(cx, cy - 1, length, actual_angle)

    def _draw_sparkles(self, tick):
        """Draw animated sparkle particles."""
        positions = [
            (10, 8), (118, 10), (15, 55), (110, 52),
            (25, 5), (100, 5), (8, 35), (120, 38),
        ]
        for i, (px, py) in enumerate(positions):
            if (tick + i * 3) % 6 < 3:
                # small cross sparkle
                self.fb.pixel(px, py, 1)
                self.fb.pixel(px - 1, py, 1)
                self.fb.pixel(px + 1, py, 1)
                self.fb.pixel(px, py - 1, 1)
                self.fb.pixel(px, py + 1, 1)

    def _draw_hearts(self, tick):
        """Draw small floating hearts."""
        base_positions = [(8, 15), (120, 12), (12, 50), (116, 48)]
        for i, (bx, by) in enumerate(base_positions):
            if (tick + i * 4) % 8 < 5:
                offset = (tick + i * 7) % 6 - 3
                self._heart(bx, by + offset, 5)

    # ── Main draw method ────────────────────────────────────────────

    def draw(self, expr, offset_x=0, offset_y=0, tick=0):
        """Draw a complete face from expression data.
        @param expr: Expression dict (from expressions.py).
        @param offset_x: Horizontal offset for shake effects.
        @param offset_y: Vertical offset.
        @param tick: Animation tick counter for extras.
        """
        self.fb.fill(0)

        eyes = expr['eyes']
        self._draw_eye(eyes, eyes['left'], offset_x, offset_y)
        self._draw_eye(eyes, eyes['right'], offset_x, offset_y)

        mouth = expr.get('mouth')
        if mouth is not None:
            self._draw_mouth(mouth, offset_x, offset_y)

        brows = expr.get('eyebrows')
        if brows is not None and brows.get('visible', True):
            self._draw_eyebrow(
                brows['left'][0], brows['left'][1],
                brows['length'], brows['angle'], False,
                offset_x, offset_y,
            )
            self._draw_eyebrow(
                brows['right'][0], brows['right'][1],
                brows['length'], brows['angle'], True,
                offset_x, offset_y,
            )

        extras = expr.get('extras')
        if extras == 'sparkles':
            self._draw_sparkles(tick)
        elif extras == 'hearts':
            self._draw_hearts(tick)

        self.fb.show()
