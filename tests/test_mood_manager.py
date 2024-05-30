import unittest
from unittest.mock import patch
from mood_manager import MoodManager, Mood
import os
from dotenv import load_dotenv

load_dotenv()

class TestMoodManager(unittest.TestCase):

    def setUp(self):
        self.mood_manager = MoodManager()

    def test_record_mood(self):
        mood = Mood.HAPPY
        response = self.mood_manager.record_mood(mood)
        self.assertTrue(response)

    def test_update_mood(self):
        initial_mood = Mood.SAD
        new_mood = Mood.ANGRY
        self.mood_manager.record_mood(initial_mood)
        update_response = self.mood_manager.update_mood(0, new_mood)
        self.assertTrue(update_response)
        self.assertEqual(self.mood_manager.get_mood_history()[0], new_mood)

    def test_mood_history(self):
        moods = [Mood.HAPPY, Mood.SAD, Mood.EXCITED]
        for mood in moods:
            self.mood_manager.record_mood(mood)

        history = self.mood_manager.get_mood_history()
        self.assertEqual(history, moods)

    def test_secure_storage(self):
        secure_storage_method = os.environ.get("SECURE_STORAGE_METHOD")
        self.assertIsNotNone(secure_storage_method)
        self.assertIn(secure_storage_method, ['encryption', 'hashing'])

    @patch('mood_manager.MoodManager.get_mood_history')
    def test_analytical_functionality(self, mock_get_mood_history):
        mock_get_mood_history.return_value = [Mood.HAPPY, Mood.HAPPY, Mood.SAD]
        analytics = self.mood_manager.analyze_moods()
        self.assertIsInstance(analytics, dict)
        self.assertTrue('HAPPY' in analytics and analytics['HAPPY'] == 2)
        self.assertTrue('SAD' in analytics and analytics['SAD'] == 1)

if __name__ == '__main__':
    unittest.main()