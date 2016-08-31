# coding=utf-8

from importlib import import_module
from errors import InheritanceError, ClassLookupError
import os
import hashlib
import binascii
import imp
import sys

file_module_prefix = "_file_"


def module_name_from_file(file_name):
    name = os.path.abspath(file_name)
    m = hashlib.md5()
    m.update(name)
    module_name = binascii.hexlify(m.digest())
    return file_module_prefix + module_name


class Switchable(object):
    def __init__(self, previous=None):
        pass

    def __switch__(self):
        pass


class Interface(object):
    __abstract_class__ = None
    __default_class__ = None
    __component__ = None

    def __init__(self, default_class, abstract_class=None):
        if abstract_class is None:
            abstract_class = default_class
        object.__setattr__(self, "__abstract_class__", abstract_class)
        object.__setattr__(self, "__default_class__", abstract_class)
        self.set_default_class_for_interface(default_class)
        comp = object.__getattribute__(self, "__default_class__")()
        object.__setattr__(self, "__component__", comp)

    def set_default_class_for_interface(self, new_class):
        if issubclass(new_class, object.__getattribute__(self, "__abstract_class__")):
            object.__setattr__(self, "__default_class__", new_class)

    def __switch__(self, new_cls):
        if not issubclass(new_cls, object.__getattribute__(self, "__abstract_class__")):
            raise InheritanceError("Presented class «" + new_cls.__name__ +
                                   "» is not the subclass of the abstract class")
        comp = object.__getattribute__(self, "__component__")
        if type(comp) != new_cls:
            comp.__switch__()
            comp = new_cls(comp)
            object.__setattr__(self, "__component__", comp)

    def __load_from_module__(self, module):
        abstract_cls = object.__getattribute__(self, "__abstract_class__")
        for cls_name in dir(module):
            cls = getattr(module, cls_name)
            if issubclass(cls, abstract_cls):
                self.__switch__(cls)
                return
        raise ClassLookupError("Can not find proper class in module «" + module.__name__ + "»")

    def __import_module_or_file__(self, name, base=None):
        if os.path.isfile(name):
            if base is None:
                module = object.__getattribute__(self, "__abstract_class__").__module__
                base = sys.modules[module].__package__
            module_name = base + "." + module_name_from_file(name)
            if module_name not in sys.modules:
                return imp.load_source(module_name, name)
            else:
                return sys.modules[module_name]
        return import_module(name)

    def load_from_module(self, *args, **kwargs):
        for i in args:
            if isinstance(i, str):
                try:
                    module = self.__import_module_or_file__(i, **kwargs)
                    self.__load_from_module__(module)
                    return
                except ImportError or ClassLookupError:
                    pass

    def switch_to_default_class(self):
        self.__switch__(object.__getattribute__(self, "__default_class__"))

    def __getattr__(self, name):
        comp = object.__getattribute__(self, "__component__")
        return getattr(comp, name)

    def __setattr__(self, name, arg):
        comp = object.__getattribute__(self, "__component__")
        return setattr(comp, name, arg)
