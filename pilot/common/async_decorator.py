import threading


class TimeoutError(RuntimeError):
    pass


class AsyncCall(threading.Thread):
    Result = None
    args = []
    kwargs = {}

    def __init__(self, fnc, callback=None):
        super(AsyncCall, self).__init__()
        self.Callable = fnc
        self.Callback = callback

    def __call__(self, *args, **kwargs):
        self.name = self.Callable.__name__
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
        self.Result = self.Callable(*self.args, **self.kwargs)
        if self.Callback:
            self.Callback(self.Result)


def async(fnc=None, callback=None):
    if fnc is None:
        def add_async_callback(fnc1):
            return async(fnc1, callback)
        return add_async_callback
    else:
        def async_caller(*args, **kwargs):
            return AsyncCall(fnc, callback)(*args, **kwargs)
        return async_caller
