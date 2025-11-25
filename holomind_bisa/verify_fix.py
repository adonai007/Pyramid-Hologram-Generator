import sys
import unittest
from unittest.mock import MagicMock

# Mock heavy dependencies before importing the module
sys.modules['anthropic'] = MagicMock()
sys.modules['openai'] = MagicMock()
sys.modules['speech_recognition'] = MagicMock()
sys.modules['pyttsx3'] = MagicMock()
sys.modules['transformers'] = MagicMock()
sys.modules['cv2'] = MagicMock()
sys.modules['opensimplex'] = MagicMock()

# Import the module to test
# We'll test holomind-core.py as that was the one in the traceback
import importlib.util
spec = importlib.util.spec_from_file_location("holomind_core", "holomind-core.py")
holomind_core = importlib.util.module_from_spec(spec)
sys.modules["holomind_core"] = holomind_core
spec.loader.exec_module(holomind_core)

class TestEmotionalToneFix(unittest.TestCase):
    def test_concerned_attribute_exists(self):
        """Test that EmotionalTone has the CONCERNED attribute"""
        print("\nTesting EmotionalTone.CONCERNED existence...")
        try:
            tone = holomind_core.EmotionalTone.CONCERNED
            print(f"Success: EmotionalTone.CONCERNED exists with value {tone.value}")
            self.assertIsNotNone(tone)
        except AttributeError:
            self.fail("EmotionalTone has no attribute 'CONCERNED'")

    def test_analyze_emotion_returns_concerned(self):
        """Test that _analyze_emotion returns CONCERNED for negative sentiment"""
        print("\nTesting _analyze_emotion with negative input...")
        
        # Setup the agent core with mocks
        agent = holomind_core.AgentCore(api_key="test_key", use_claude=True)
        
        # Mock the emotion detector pipeline
        mock_detector = MagicMock()
        mock_detector.return_value = [{'label': 'NEGATIVE', 'score': 0.9}]
        agent.emotion_detector = mock_detector
        
        # Test the method
        result = agent._analyze_emotion("I am very worried about this error.")
        
        print(f"Result: {result}")
        self.assertEqual(result, holomind_core.EmotionalTone.CONCERNED)

if __name__ == '__main__':
    unittest.main()