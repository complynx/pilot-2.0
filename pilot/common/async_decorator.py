import threading
from exception_formatter import caught
from functools import wraps
import logging


class TimeoutError(RuntimeError):
    pass


class AsyncCall(threading.Thread):
    Result = None
    args = []
    kwargs = {}

    def __init__(self, fnc, callback=None, daemon=False):
        super(AsyncCall, self).__init__()
        self.Callable = fnc
        self.Callback = callback
        self.daemon = daemon

    def __call__(self, *args, **kwargs):
        func = self.Callable
        self.name = "%s:%d:%s" % (func.func_globals["__name__"], func.func_code.co_firstlineno, func.__name__)

        current = threading.currentThread()
        self.parent = (current.getName(), current.ident)

        self.args = args
        self.kwargs = kwargs
        self.start()
        return self

    def wait(self, timeout=None):
        self.join(timeout)
        if self.isAlive():
            raise TimeoutError()
        else:
            return self.Result

    def run(self):
        logging.debug("Thread: %s(%d), called from: %s(%d)" % (self.getName(), self.ident,
                                                               self.parent[0], self.parent[1]))
        try:
            self.Result = self.Callable(*self.args, **self.kwargs)
            if self.Callback:
                self.Callback(self.Result)
        except Exception as e:
            caught(e)


def async(fnc=None, callback=None, daemon=False):
    if fnc is None:
        def add_async_callback(fnc1):
            return async(fnc1, callback, daemon)
        return add_async_callback
    else:
        @wraps(fnc)
        def async_caller(*args, **kwargs):
            return AsyncCall(fnc, callback, daemon)(*args, **kwargs)
        return async_caller
