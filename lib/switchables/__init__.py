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
    """
    This function creates a distinct module name for a certain file if it is imported by name.
    :param file_name:
    :return str:  new distinct module name
    """
    name = os.path.abspath(file_name)
    m = hashlib.md5()
    m.update(name)
    module_name = binascii.hexlify(m.digest())
    return file_module_prefix + module_name


class Switchable(object):
    """
    This is a base interface for any switchable module. It presents two major functions: initializer and switcher
    these two functions must have the same signature.

    To create a switchable class, just inherit from this and register it in the appropriate interface.
    ```
    import switchables

    class ExampleClass(switchables.Switchable):
        def __init__(self, previous=None):
            Switchable.__init__(self, previous)
            if previous:
                ...fetch values from previous...
            else:
                ...init default values...

        def __switch__(self):
            Switchable.__switch__(self)
            ...serialize all...

        def __switched__(self):
            Switchable.__switched__(self)
            ...close unclosed descriptors...

    # register it as follows
    class ExampleInterface(switchables.Interface):
        def __init__(self):
            Interface.__init__(self, ExampleClass)
    ```

    """
    def __init__(self, previous=None):
        """
        Initializer abstraction.

        Every initializer is provided with a previous object instance, that is at this time prepared for change
        (serialized) by means of `__switch__`. If none passed, this is the default initialization.

        This function is designed to either initialize the object with default values or import the previous values
        from the previous class.
        :param previous: previous instance or none.
        """
        pass

    def __switch__(self):
        """
        Serializer abstraction.

        This function is called upon an object when it is switching class. To switch for a new one, an object must
        serialize all it's internals into a unified way common for all the classes in this instance.
        For instance, it should end all specific connections, close all descriptors and update all the modified configs.
        It may live unclosed descriptors if
            1) these descriptors are a part of a config and will be maintained either by user or by each and every
               implementation
            2) they are closed in `__switched__` of the same object.
        After serialization this object will be passed to the initialization of a new class (it's `__init__`) as an
        argument.

        At this point the new class is unknown.
        """
        pass

    def __switched__(self):
        """
        Remover abstraction.

        At this point a new class is already invoked and set up. At this point an old class _must_ close all left
        descriptors, unlock semaphores and so on, if they haven't been passed to a new class.

        At this point the new class is working, this class is obsolete and removed. It may still persist while there
        would be some lost hanging links, etc... Thus you shouldn't rely on `__del__`
        """
        pass

    @classmethod
    def same(cls, obj):
        """
        This method duplicates an object interface and initializes it with default values saving only the class of the
        passed object.
        :param obj: interface to an object.
        :return: the same type of the interface with the same class initialized.
        """
        if not issubclass(obj, Interface):
            raise InheritanceError("Presented object is not a Switchable interface")
        ret = type(obj)()
        ret.switchable_cast(obj)
        return ret


class Interface(object):
    """
    This is an abstraction over the switchable interface providing all necessary functionality.


    To create a switchable class, just inherit from this and register it in the appropriate interface.
    ```
    import switchables

    class ExampleClass(switchables.Switchable):
        def __init__(self, previous=None):
            Switchable.__init__(self, previous)
            if previous:
                ...fetch values from previous...
            else:
                ...init default values...

        def __switch__(self):
            Switchable.__switch__(self)
            ...serialize all...

        def __switched__(self):
            Switchable.__switched__(self)
            ...close unclosed descriptors...

    # register it as follows
    class ExampleInterface(switchables.Interface):
        def __init__(self):
            Interface.__init__(self, ExampleClass)
    ```

    """
    __switchable__abstract_class__ = None
    __switchable__default_class__ = None
    __switchable__component__ = None

    def __init__(self, default_class, abstract_class=None):
        if abstract_class is None:
            abstract_class = default_class
        object.__setattr__(self, "__switchable__abstract_class__", abstract_class)
        object.__setattr__(self, "__switchable__default_class__", abstract_class)
        self.switchable_set_default_class(default_class)
        comp = object.__getattribute__(self, "__switchable__default_class__")()
        object.__setattr__(self, "__switchable__component__", comp)

    def switchable_set_default_class(self, new_class):
        if issubclass(new_class, object.__getattribute__(self, "__switchable__abstract_class__")):
            object.__setattr__(self, "__switchable__default_class__", new_class)

    def __switch__(self, new_cls):
        if not issubclass(new_cls, object.__getattribute__(self, "__switchable__abstract_class__")):
            raise InheritanceError("Presented class «" + new_cls.__name__ +
                                   "» is not the subclass of the provided abstract class")
        comp = object.__getattribute__(self, "__switchable__component__")
        if type(comp) != new_cls:
            comp.__switch__()
            newcmp = new_cls(comp)
            object.__setattr__(self, "__switchable__component__", newcmp)
            comp.__switched__()

    def __switchable__load_from_module__(self, module):
        abstract_cls = object.__getattribute__(self, "__switchable__abstract_class__")
        for cls_name in dir(module):
            cls = getattr(module, cls_name)
            if issubclass(cls, abstract_cls):
                self.__switch__(cls)
                return
        raise ClassLookupError("Can not find proper class in module «" + module.__name__ + "»")

    def switchable_cast(self, other_interface):
        other_cls = type(object.__getattribute__(other_interface, "__switchable__component__"))
        self.__switch__(other_cls)

    def __switchable__import_module_or_file__(self, name, base=None):
        if os.path.isfile(name):
            if base is None:
                module = object.__getattribute__(self, "__switchable__abstract_class__").__module__
                base = sys.modules[module].__package__
            module_name = base + "." + module_name_from_file(name)
            if module_name not in sys.modules:
                return imp.load_source(module_name, name)
            else:
                return sys.modules[module_name]
        return import_module(name)

    def switchable_load(self, *args, **kwargs):
        for i in args:
            if isinstance(i, str):
                try:
                    module = self.__switchable__import_module_or_file__(i, **kwargs)
                    self.__switchable__load_from_module__(module)
                    return
                except ImportError or ClassLookupError:
                    pass

    def switchable_default(self):
        self.__switch__(object.__getattribute__(self, "__switchable__default_class__"))

    def __getattr__(self, name):
        comp = object.__getattribute__(self, "__switchable__component__")
        return getattr(comp, name)

    def __setattr__(self, name, arg):
        comp = object.__getattribute__(self, "__switchable__component__")
        return setattr(comp, name, arg)
