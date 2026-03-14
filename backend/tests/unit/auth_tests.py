import unittest
from unittest.mock import Mock


class AuthTests(unittest.TestCase):
    validUser = Mock()

    def setUp(self):
        print ("Running Auth Tests...")

    def tearDown(self):
        print ("Finished Running Auth Tests.")

    def test_authenticate_success(self):
        """Returns "success"."""

    def test_authenticate_fail(self):
        """Returns "failure"."""