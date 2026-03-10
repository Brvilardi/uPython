import sys
import time
from .Face import Face
from .Animation import Animation
from .expressions import EXPRESSIONS

try:
    import select
    _poll_available = True
except ImportError:
    _poll_available = False


class Tabbie:
    """Tabbie desk companion — animated face on SSD1306 OLED.

    Controls expression states via serial (USB REPL) commands.
    """

    ONE_SHOT_STATES = {'love': 4000, 'complete': 5000}

    def __init__(self, oled):
        """
        @param oled: SpiOledDisplay (or any object with a .display SSD1306 framebuf).
        """
        self.oled = oled
        self.face = Face(oled.display)
        self.animation = Animation(self.face, fps=12)
        self.state = 'idle'
        self._buf = ''

        if _poll_available:
            self._poller = select.poll()
            self._poller.register(sys.stdin, select.POLLIN)
        else:
            self._poller = None

    def start(self):
        """Run startup animation then enter main loop."""
        self._startup_animation()
        self.run()

    def _startup_animation(self):
        """Quick startup: blink on, show idle."""
        fb = self.oled.display
        fb.fill(0)
        fb.show()
        time.sleep_ms(300)

        # draw eyes appearing one step at a time
        for r in range(1, 11):
            fb.fill(0)
            self.face._circle(40, 25, r, fill=True)
            self.face._circle(88, 25, r, fill=True)
            fb.show()
            time.sleep_ms(40)

        time.sleep_ms(200)
        self.animation.set_expression('idle')

    def run(self):
        """Main loop: update animation + poll serial commands."""
        while True:
            self.animation.update()
            self._poll_serial()

    def _poll_serial(self):
        """Non-blocking read from serial/REPL."""
        if self._poller is None:
            return

        while self._poller.poll(0):
            ch = sys.stdin.read(1)
            if ch in ('\n', '\r'):
                cmd = self._buf.strip()
                self._buf = ''
                if cmd:
                    self._handle_command(cmd)
            else:
                self._buf += ch

    def _handle_command(self, cmd):
        """Process a serial command."""
        parts = cmd.split(None, 1)
        action = parts[0].lower()

        if action == 'status':
            print('state: {}'.format(self.state))
            return

        if action == 'pomodoro':
            task = parts[1] if len(parts) > 1 else ''
            print('pomodoro: {}'.format(task))
            self.state = 'focus'
            self.animation.set_expression('focus')
            self._show_text_overlay(task, 1500)
            return

        if action == 'notify':
            text = parts[1] if len(parts) > 1 else ''
            print('notify: {}'.format(text))
            self._show_text_overlay(text, 3000)
            return

        # map paused -> angry
        if action == 'paused':
            action = 'angry'

        if action in EXPRESSIONS and action != 'blink':
            self.state = action
            one_shot_ms = self.ONE_SHOT_STATES.get(action, 0)
            self.animation.set_expression(action, one_shot_ms)
            if one_shot_ms:
                self.state = 'idle'
            print('-> {}'.format(action))
        else:
            print('unknown: {}'.format(cmd))

    def _show_text_overlay(self, text, duration_ms):
        """Show centered text on OLED for duration_ms, then resume animation."""
        fb = self.oled.display
        fb.fill(0)
        label = text[:16]
        x = (128 - len(label) * 8) // 2
        fb.text(label, x, 28)
        fb.show()
        time.sleep_ms(duration_ms)
