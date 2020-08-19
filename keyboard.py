from pynput import keyboard


class KeyboardListenerTask:

    def __init__(self, track_control, power_toggle_key, barrier_trigger_key):
        self.listener = keyboard.Listener(
            on_press=self._on_press_callback)
        self._tc = track_control
        self.power_key = power_toggle_key
        self.barrier_key = barrier_trigger_key


    def _on_press_callback(self, key):
        key_string = None
        try:
            key_string = key.char
        except AttributeError:
            key_string = key_string

        if key_string == self.power_key:
            self._tc.toggle_power()
        elif key_string == self.barrier_key:
            self._tc.trigger_barrier()
        else:
            pass

    def run(self):
        self.listener.start()

    def stop(self):
        self.listener.stop()
