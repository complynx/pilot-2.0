from unittest import TestCase


class TestMock(TestCase):

    def test_mock(self):
        """ Assert that true is not false """
        self.assertTrue(True)
        self.assertFalse(False)
