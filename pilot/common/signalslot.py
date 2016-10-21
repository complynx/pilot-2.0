"""
Module defining the Signal class.
"""

import inspect
import threading
from weakref import WeakSet, WeakKeyDictionary


class DummyLock(object):
    """
    Class that implements a no-op instead of a re-entrant lock.
    """

    def __enter__(self):
        pass

    def __exit__(self, exc_type=None, exc_value=None, traceback=None):
        pass


class Signal(object):
    def __init__(self, threadsafe=True):
        self._functions = WeakSet()
        self._methods = WeakKeyDictionary()
        self._slots_lk = threading.RLock() if threadsafe else DummyLock()

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

    def __call__(self, *args, **kwargs):
        # Call handler functions
        for func in self._functions:
            func(*args, **kwargs)

        # Call handler methods
        for obj, funcs in self._methods.items():
            for func in funcs:
                func(obj, *args, **kwargs)
