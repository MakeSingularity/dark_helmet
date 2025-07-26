# Unit tests for Dark Helmet project
import unittest
import sys
import os
from unittest.mock import patch, MagicMock
from io import StringIO
import contextlib

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Import modules to test
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
            f = StringIO()
            with contextlib.redirect_stdout(f):
                main()
            
            output = f.getvalue()
            self.assertIn("Dark Helmet", output)
            self.assertTrue(len(output) > 0)
        except Exception as e:
            self.fail(f"main() function raised an exception: {e}")

class TestVoiceChanger(unittest.TestCase):
    """Tests for the voice changer module"""
    
    def setUp(self):
        """Set up test environment"""
        # Mock audio libraries to avoid hardware dependencies
        self.audio_mocks = {}
        
    def test_voice_changer_import(self):
        """Test that voice_changer module can be imported"""
        try:
            import voice_changer
            self.assertTrue(hasattr(voice_changer, 'check_virtual_environment'))
            self.assertTrue(hasattr(voice_changer, 'apply_effects'))
            self.assertTrue(hasattr(voice_changer, 'audio_callback'))
        except ImportError as e:
            # This is expected if audio libraries aren't installed
            if 'sounddevice' in str(e) or 'sox' in str(e):
                self.skipTest(f"Audio dependencies not available: {e}")
            else:
                self.fail(f"Unexpected import error: {e}")
    
    @patch('voice_changer.sd')  # Mock sounddevice
    @patch('voice_changer.sox')  # Mock sox
    def test_virtual_environment_check(self, mock_sox, mock_sd):
        """Test virtual environment checking in voice changer"""
        try:
            import voice_changer
            result = voice_changer.check_virtual_environment()
            self.assertIsInstance(result, bool)
        except ImportError:
            self.skipTest("Voice changer module not available")
    
    def test_audio_settings(self):
        """Test that audio settings are properly defined"""
        try:
            import voice_changer
            self.assertTrue(hasattr(voice_changer, 'SAMPLE_RATE'))
            self.assertTrue(hasattr(voice_changer, 'BLOCK_SIZE'))
            self.assertTrue(hasattr(voice_changer, 'CHANNELS'))
            
            # Verify reasonable values
            self.assertEqual(voice_changer.SAMPLE_RATE, 44100)
            self.assertEqual(voice_changer.BLOCK_SIZE, 1024)
            self.assertEqual(voice_changer.CHANNELS, 2)
        except ImportError:
            self.skipTest("Voice changer module not available")

class TestRunVoiceChanger(unittest.TestCase):
    """Tests for the voice changer launcher"""
    
    def test_launcher_import(self):
        """Test that run_voice_changer module can be imported"""
        try:
            import run_voice_changer
            self.assertTrue(hasattr(run_voice_changer, 'check_spaceBalls_environment'))
            self.assertTrue(hasattr(run_voice_changer, 'check_dependencies'))
        except ImportError as e:
            self.skipTest(f"Launcher module not available: {e}")
    
    def test_spaceBalls_environment_check(self):
        """Test SpaceBalls environment detection"""
        try:
            import run_voice_changer
            is_spaceBalls, venv_path = run_voice_changer.check_spaceBalls_environment()
            self.assertIsInstance(is_spaceBalls, bool)
            self.assertIsInstance(venv_path, str)
        except ImportError:
            self.skipTest("Launcher module not available")

def run_audio_tests():
    """Run tests that require audio hardware (optional)"""
    try:
        import sounddevice as sd
        devices = sd.query_devices()
        print(f"\n🎵 Audio devices found: {len(devices)}")
        for i, device in enumerate(devices):
            print(f"  {i}: {device['name']}")
        return True
    except Exception as e:
        print(f"\n⚠️  Audio hardware tests skipped: {e}")
        return False

if __name__ == '__main__':
    print("🎭 Running Dark Helmet Voice Changer Tests...")
    print("=" * 50)
    
    # Check environment
    venv_path = os.environ.get('VIRTUAL_ENV', '')
    if 'SpaceBalls' in venv_path:
        print(f"✅ Running in SpaceBalls environment: {venv_path}")
    else:
        print("⚠️  Not running in SpaceBalls environment")
        if venv_path:
            print(f"   Current: {venv_path}")
    
    print("\n🧪 Running unit tests...")
    
    # Run the main test suite
    unittest.main(verbosity=2, exit=False)
    
    # Run optional audio tests
    print("\n🎵 Testing audio hardware (optional)...")
    run_audio_tests()
    
    print("\n🎭 Tests complete! May the Schwartz be with you!")