# Unit tests for Dark Helmet project
import unittest
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from main import check_virtual_environment, main

class TestMain(unittest.TestCase):
    
    def test_check_virtual_environment(self):
        """Test virtual environment checking function"""
        # This test will pass regardless of environment
        # but will print helpful information
        result = check_virtual_environment()
        self.assertIsInstance(result, bool)
    
    def test_main_function(self):
        """Test that main function runs without errors"""
        try:
            # Capture stdout to avoid cluttering test output
            from io import StringIO
            import contextlib
            
            f = StringIO()
            with contextlib.redirect_stdout(f):
                main()
            
            output = f.getvalue()
            self.assertIn("Dark Helmet", output)
            self.assertTrue(len(output) > 0)
        except Exception as e:
            self.fail(f"main() function raised an exception: {e}")

if __name__ == '__main__':
    print("Running Dark Helmet tests...")
    print("Make sure you're in the SpaceBalls virtual environment!")
    unittest.main()