from unittest import TestCase
from example_class.interface import ExampleInterface


class TestSwitchable(TestCase):

    def test_switchable(self):
        """ test successful init """
        t = ExampleInterface()
        t.foo()

    def test_changing(self):
        """ test changing """
        t = ExampleInterface()
        self.assertEqual(t.foo(), __package__+'.example_class.interface.ExampleSwitchable')
        t.load_from_module(__package__+'.example_class.example_extended')
        self.assertEqual(t.foo(), __package__+'.example_class.example_extended.ExampleExtended test')
        t.switch_to_default_class()
        self.assertEqual(t.foo(), __package__+'.example_class.interface.ExampleSwitchable')

    def test_changing_to_undefined(self):
        """ test changing to undefined """
        t = ExampleInterface()
        self.assertEqual(t.foo(), __package__+'.example_class.interface.ExampleSwitchable')
        t.load_from_module('undefined')
        self.assertEqual(t.foo(), __package__+'.example_class.interface.ExampleSwitchable')

    def test_other_stuff(self):
        """ test other stuff """
        t = ExampleInterface()

        self.assertEqual(t.ti(1), 1)
        self.assertEqual(t.ci(1), 1)
        self.assertEqual(t.si(1), 1)

        self.assertEqual(t.prop, 'prop test')
        t.prop = 'setted prop'
        self.assertEqual(t.prop, 'setted prop')
        self.assertEqual(t.smth, None)
        t.smth = 1
        self.assertEqual(t.smth, 1)
