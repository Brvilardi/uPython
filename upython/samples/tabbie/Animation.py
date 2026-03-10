import time
from .expressions import EXPRESSIONS


def _lerp(a, b, t):
    """Linear interpolation between a and b."""
    return a + (b - a) * t


def _lerp_dict(src, dst, t):
    """Recursively interpolate numeric values in nested dicts.
    Non-numeric and None values snap to dst when t >= 0.5."""
    result = {}
    for key in dst:
        sv = src.get(key)
        dv = dst[key]
        if sv is None or dv is None:
            result[key] = dv if t >= 0.5 else sv
        elif isinstance(dv, dict):
            result[key] = _lerp_dict(sv if isinstance(sv, dict) else {}, dv, t)
        elif isinstance(dv, (int, float)):
            result[key] = _lerp(sv if isinstance(sv, (int, float)) else dv, dv, t)
        elif isinstance(dv, tuple) and len(dv) == 2:
            sx = sv[0] if isinstance(sv, tuple) else dv[0]
            sy = sv[1] if isinstance(sv, tuple) else dv[1]
            result[key] = (int(_lerp(sx, dv[0], t)), int(_lerp(sy, dv[1], t)))
        elif isinstance(dv, str):
            result[key] = dv if t >= 0.5 else (sv if isinstance(sv, str) else dv)
        else:
            result[key] = dv if t >= 0.5 else sv
    return result


class Animation:
    """Manages face animation: blinking, transitions, idle behaviors."""

    TRANSITION_MS = 300

    def __init__(self, face, fps=12):
        """
        @param face: Face renderer instance.
        @param fps: Target frames per second.
        """
        self.face = face
        self.frame_ms = 1000 // fps
        self.tick = 0
        self.last_frame = time.ticks_ms()

        self.current_name = 'idle'
        self.current_expr = self._copy_expr(EXPRESSIONS['idle'])
        self.target_name = 'idle'
        self.target_expr = self.current_expr

        self.transitioning = False
        self.transition_start = 0
        self.transition_from = self.current_expr

        # blink state
        self.blink_active = False
        self.blink_until = 0
        self.next_blink = time.ticks_ms() + 3000

        # one-shot expressions return to idle
        self.one_shot = False
        self.one_shot_until = 0

        # shake effect for angry
        self.offset_x = 0
        self.offset_y = 0

    @staticmethod
    def _copy_expr(expr):
        """Shallow-ish copy of an expression dict."""
        result = {}
        for k, v in expr.items():
            if isinstance(v, dict):
                result[k] = dict(v)
            else:
                result[k] = v
        return result

    def set_expression(self, name, one_shot_ms=0):
        """Transition to a new expression.
        @param name: Expression name from EXPRESSIONS.
        @param one_shot_ms: If > 0, return to idle after this many ms.
        """
        if name not in EXPRESSIONS:
            return
        self.target_name = name
        self.target_expr = self._copy_expr(EXPRESSIONS[name])
        self.transition_from = self._copy_expr(self.current_expr)
        self.transitioning = True
        self.transition_start = time.ticks_ms()

        if one_shot_ms > 0:
            self.one_shot = True
            self.one_shot_until = time.ticks_ms() + one_shot_ms
        else:
            self.one_shot = False

    def update(self):
        """Called each tick. Returns True if a frame was drawn."""
        now = time.ticks_ms()
        if time.ticks_diff(now, self.last_frame) < self.frame_ms:
            return False
        self.last_frame = now
        self.tick += 1

        # handle transition interpolation
        if self.transitioning:
            elapsed = time.ticks_diff(now, self.transition_start)
            if elapsed >= self.TRANSITION_MS:
                self.current_expr = self._copy_expr(self.target_expr)
                self.current_name = self.target_name
                self.transitioning = False
            else:
                t = elapsed / self.TRANSITION_MS
                self.current_expr = _lerp_dict(self.transition_from, self.target_expr, t)
                self.current_name = self.target_name

        # handle one-shot timeout
        if self.one_shot and time.ticks_diff(now, self.one_shot_until) >= 0:
            self.one_shot = False
            self.set_expression('idle')

        # idle behaviors
        self._handle_blink(now)
        self._handle_shake(now)

        draw_expr = self.current_expr

        # overlay blink (just close the eyes, keep mouth/brows)
        if self.blink_active:
            draw_expr = self._copy_expr(draw_expr)
            blink_eyes = dict(EXPRESSIONS['blink']['eyes'])
            # preserve current eye positions
            blink_eyes['left'] = draw_expr['eyes']['left']
            blink_eyes['right'] = draw_expr['eyes']['right']
            blink_eyes['radius'] = draw_expr['eyes']['radius']
            draw_expr['eyes'] = blink_eyes

        self.face.draw(draw_expr, self.offset_x, self.offset_y, self.tick)
        return True

    def _handle_blink(self, now):
        """Periodic blinking."""
        if self.blink_active:
            if time.ticks_diff(now, self.blink_until) >= 0:
                self.blink_active = False
                self.next_blink = now + 3000 + (self.tick % 2000)
        elif not self.transitioning:
            if time.ticks_diff(now, self.next_blink) >= 0:
                self.blink_active = True
                self.blink_until = now + 150

    def _handle_shake(self, now):
        """Shake effect for angry expression."""
        if self.current_name == 'angry' and not self.transitioning:
            self.offset_x = (self.tick % 3) - 1  # -1, 0, 1
        else:
            self.offset_x = 0
        self.offset_y = 0
