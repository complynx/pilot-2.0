"""
Module defining the Signal class.
"""

import inspect
import threading
from weakref import WeakSet, WeakKeyDictionary
import logging
import os
from exception_formatter import caught

DEBUG = True


class SignalDispatcher(threading.Thread):
    def __init__(self, sig, args, kwargs):
        super(SignalDispatcher, self).__init__()
        self.dispatch_async_signal = sig
        self.args = args
        self.kwargs = kwargs

        frame = inspect.currentframe()
        outer = inspect.getouterframes(frame)
        self.emmitter = Signal.emmitter_object(outer[2][0])
        del outer
        del frame

    def run(self):
        try:
            self.dispatch_async_signal(*self.args, **self.kwargs)
        except Exception as e:
            caught(e)


class Signal(object):
    def __init__(self, emmitter=None):
        self._functions = WeakSet()
        self._methods = WeakKeyDictionary()
        self._slots_lk = threading.RLock()
        self.__emmitter = emmitter

    def set_emmitter(self, emmitter=None):
        self.__emmitter = emmitter

    def connect(self, slot):
        """
        Connect a callback ``slot`` to this signal.
        """
        with self._slots_lk:
            if not self.is_connected(slot):
                if inspect.ismethod(slot):
                    if slot.im_self not in self._methods:
                        self._methods[slot.im_self] = set()

                    self._methods[slot.im_self].add(slot.im_func)

                else:
                    self._functions.add(slot)

    def is_connected(self, slot):
        """
        Check if a callback ``slot`` is connected to this signal.
        """
        with self._slots_lk:
            if inspect.ismethod(slot):
                if slot.im_self in self._methods and slot.im_func in self._methods[slot.im_self]:
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
                    self._methods[slot.im_self].remove(slot.im_func)
                else:
                    self._functions.remove(slot)

    @staticmethod
    def emitter():
        frame = inspect.currentframe()
        outer = inspect.getouterframes(frame)
        call_frame = None
        self = None  # type: Signal
        for i in outer:
            if i[3] == '__call__' and 'self' in i[0].f_locals and isinstance(i[0].f_locals['self'], Signal):
                self = i[0].f_locals['self']
                call_frame = i[0]
                break

        if self and self.__emmitter:
            return self.__emmitter

        del frame
        del outer
        return Signal.emmitter_object(call_frame)

    @staticmethod
    def emmitter_object(call_frame):
        outer = inspect.getouterframes(call_frame)
        outer = outer[1][0]
        if len(outer.f_locals) == 0:
            return None

        obj = outer.f_locals[outer.f_locals.keys()[0]]
        del call_frame
        del outer

        if isinstance(obj, SignalDispatcher):
            return obj.emmitter

        return obj

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
