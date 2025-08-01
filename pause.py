import time
from time import sleep

class PauseController:
    """Pause automation when user moves the mouse in the UI."""

    def __init__(self, idle_seconds: int = 3):
        self.idle_seconds = idle_seconds
        self.paused = False
        self._last_motion = time.time()

    def on_motion(self, event=None):
        """Callback to be bound to <Motion> events."""
        self.paused = True
        self._last_motion = time.time()

    def check(self):
        """Block while there is recent user interaction."""
        while self.paused:
            if time.time() - self._last_motion >= self.idle_seconds:
                self.paused = False
                break
            sleep(0.5)
