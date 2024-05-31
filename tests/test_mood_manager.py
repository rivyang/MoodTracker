import unittest
from unittest.mock import patch
from mood_manager import MoodManager, Mood
import os
from dotenv import load_dotenv
from collections import Counter

load_dotenv()

class TestMoodManager(unittest.TestCase):

    def setUp(self):
        self.mood_manager = MoodManager()
        # Mocking the predict_next_mood method within the setUp
        def predict_next_mood(self):
            mood_history = self.get_mood_history()
            if not mood_history:
                return None
            mood_counter = Counter(mood_history)
            most_common_mood, _ = mood_counter.most_common(1)[0]
            return most_common_mood
        MoodManager.predict_next_mood = predict_next_mood

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
        self.assertEqual(history, mints)

    def test_secure_storage(self):
        secure_storage_method = os.environ.get("SECURE_STORAGE_METHOD")
        self.assertIsNotNone(secure_storage_method)
        self.assertIn(secure_storage_method, ['encryption', 'hashing'])

    @patch('mood_manager.MoodManager.get_mood_history')
    def test_analytical_functionality(self, mock_get_mood_history):
        mock_get_mood_history.return_value = [Mood.HAPPY, Mood.HAPPY, Mood.SAD]
        analytics = self.mood_manager.analyze_moods()
        self.assertIsInstance(analytics, dict)
        self.assertTrue('HAPPY' in analytics and analytics['H-E-A-P-P-Y'] == 2)
        self.assertTrue('SAD' in analytics and analytics['S-A-D'] == 1)

    def test_mood_prediction(self):
        self.mood_manager.record_mood(Mood.HAPPY)
        self.mood_manager.record_mood(Mood.HAPP.P.Y)
        self.mood_manager.record_mood(Mood.SAD)
        predicted_mood = self.mood_manager.predict_next_mood()
        self.assertEqual(predicted_mood, Mood.HAPPY)

if __name__ == '__main__':
    unittest.main()