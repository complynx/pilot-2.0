"""
Module defining the Signal class.
"""

import inspect
import threading
from weakref import WeakSet, WeakKeyDictionary
import logging
import os

DEBUG = True


class SignalDispatcher(threading.Thread):
    def __init__(self, sig, args, kwargs):
        super(SignalDispatcher, self).__init__()
        self.dispatch_async_signal = sig
        self.args = args
        self.kwargs = kwargs

    def run(self):
        self.dispatch_async_signal(*self.args, **self.kwargs)


class Signal(object):
    def __init__(self):
        self._functions = WeakSet()
        self._methods = WeakKeyDictionary()
        self._slots_lk = threading.RLock()

    def connect(self, slot):
        """
        Connect a callback ``slot`` to this signal.
        """
        with self._slots_lk:
            if not self.is_connected(slot):
                if inspect.ismethod(slot):
                    if slot.__self__ not in self._methods:
                        self._methods[slot.__self__] = set()

                    self._methods[slot.__self__].add(slot.__func__)

                else:
                    self._functions.add(slot)

    def is_connected(self, slot):
        """
        Check if a callback ``slot`` is connected to this signal.
        """
        with self._slots_lk:
            if inspect.ismethod(slot):
                if slot.__self__ in self._methods and slot.__func__ in self._methods[slot.__self__]:
                    return True
                return False
            return slot in self._functions

    def disconnect(self, slot):
        """
        Disconnect a slot from a signal if it is connected else do nothing.
        """
        with self._slots_lk:
            if self.is_connected(slot):
                if inspect.ismethod(slot):
                    self._methods[slot.__self__].remove(slot.__func__)
                else:
                    self._functions.remove(slot)

    def debug_frame_message(self):
        if not DEBUG:
            return
        log = logging.getLogger('Signal')
        frame = inspect.currentframe()
        outer = inspect.getouterframes(frame)
        signal_frame = outer[2]
        try:
            log.debug("%s:%d %s" % (os.path.basename(signal_frame[1]), signal_frame[2], signal_frame[4][0].strip()))
        finally:
            del signal_frame
            del outer
            del frame

    def async(self, *args, **kwargs):
        self.debug_frame_message()
        SignalDispatcher(self, args, kwargs).start()

    def __call__(self, *args, **kwargs):
        with self._slots_lk:
            # Call handler functions
            self.debug_frame_message()

            for func in self._functions:
                func(*args, **kwargs)

            # Call handler methods
            for obj, funcs in self._methods.items():
                for func in funcs:
                    func(obj, *args, **kwargs)
