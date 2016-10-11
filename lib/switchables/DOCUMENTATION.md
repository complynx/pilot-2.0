Introduction
============

`switchables` is a library providing simple runtime plug-in interface to your project.

You can load any file to your project as if it was a plugin.
Containing the class providing the same interface, file will be loaded as a module, and
an interface will switch to loaded class.


Plugin switching
================

If you have some interface loaded in your project, just call `switchable_load` with
a filename or a module name, and it will be switched automatically. If possible.

For example, you have next situation:
```python
from my_interface import MyInterface

foo = MyInterface()
```
Now, you use your `foo` and suddenly decide, that you need another implementation of it.
You can just do:
```python
foo.switchable_load('other_interface')
```
Then, the `other_interface` module is loaded and from it the class corresponding to `MyInterface`
is used. Then our `foo` becomes this new class.
Or you downloaded the implementation from elsewhere:
```python
foo.switchable_load('/tmp/dl_234124.py')
```
You may also cast the class to another instance:
```python
bar = MyInterface()
bar.switchable_cast(foo)
```
Or set the downloaded class to default:
```python
foo.switchable_set_default_class()
# or
MyInterface.set_default_class(foo)
```
Or you can drop back to default class:
```python
bar.switchable_to_default()
```
