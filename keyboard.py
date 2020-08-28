import logging
import asyncio

from pynput import keyboard


log = logging.getLogger()


class KeyboardListenerTask:

    def __init__(self, track_control, power_toggle_key, barrier_trigger_key):
        self.listener = keyboard.Listener(
            on_press=self.on_press_threadsafe)
        self._tc = track_control
        self.power_key = power_toggle_key
        self.barrier_key = barrier_trigger_key
        self._loop = None


    def on_press_threadsafe(self, key):
        self._loop.call_soon_threadsafe(self._on_press, key)

    def _on_press(self, key):
        key_string = None
        try:
            key_string = key.char
        except AttributeError:
            key_string = key_string

        if key_string == self.power_key:
            func = self._tc.toggle_power
            log.debug(f"Registered keypress: {key}. Toggled power.")
        elif key_string == self.barrier_key:
            func = self._tc.trigger_barrier()
            log.debug(f"Registered keypress: {key}. Triggered barrier.")
        else:
            log.debug(f"Registered keypress: {key}. Ignoring.")

    def run(self):
        self._loop = asyncio.get_running_loop()
        self.listener.start()
        log.info(f"KeyboardListenerTask started. Barrier-key: {self.barrier_key}, Power-key: {self.power_key}")

    def stop(self):
        self.listener.stop()
