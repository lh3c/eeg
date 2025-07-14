import unittest
from unittest.mock import patch
from brain_plotter import check_focus_threshold

class MockController:
    def click(self, button):
        pass

class MockButton:
    left = "left"

class TestBrainPlotter(unittest.TestCase):
    @patch('brain_plotter.Controller', MockController)
    @patch('brain_plotter.Button', MockButton)
    def test_check_focus_threshold(self):
        # Test case 1: Focus threshold should be met
        vals = [100, 100, 100, 100, 100, 10, 10, 10, 10, 10]
        self.assertTrue(check_focus_threshold(vals))

        # Test case 2: Focus threshold should not be met
        vals = [10, 10, 10, 10, 10, 10, 10, 10, 10, 10]
        self.assertFalse(check_focus_threshold(vals))

if __name__ == "__main__":
    unittest.main()
