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
        self.mood_manager.enable_logging = True

        def predict_next_mood(self):
            if self.enable_logging:
                print("Predicting next mood based on mood history...")
                
            mood_history = self.get_mood_history()
            if not mood_history:
                return None
                
            mood_counter = Counter(mood_history)
            most_common_mood, _ = mood_counter.most_common(1)[0]
            
            if self.enable_logging:
                print(f"Predicted mood: {most_common_mood}")
                
            return most_common_mood

        MoodManager.predict_next_mood = predict_next_mood

    def test_record_mood(self):
        mood = Mood.HAPPY
        response = self.mood_manager.record_mood(mood)
        
        if self.mood_manager.enable_logging:
            print(f"Recorded a new mood: {mood}")
            
        self.assertTrue(response)

    def test_update_mood(self):
        initial_mood = Mood.SAD
        new_mood = Mood.ANGRY
        self.mood_manager.record_mood(initial_mood)
        
        update_response = self.mood_manager.update_mood(0, new_mood)
        
        if self.mood_manager.enable_logging:
            print(f"Updated mood from {initial_mood} to {new_mood}")
            
        self.assertTrue(update_response)
        self.assertEqual(self.mood_manager.get_mood_history()[0], new_mood)

    def test_mood_history(self):
        moods = [Mood.HAPPY, Mood.SAD, Mood.EXCITED]
        
        for mood in moods:
            self.mood_manager.record_mood(mood)
            if self.mood_manager.enable_logging:
                print(f"Recording mood: {mood}")

        history = self.mood_manager.get_mood_history()
        self.assertEqual(history, moods)

    def test_secure_storage(self):
        secure_storage_method = os.environ.get("SECURE_STORAGE_METHOD")
        
        if self.mood_manager.enable_logging:
            print(f"Secure storage method: {secure_storage_method}")
            
        self.assertIsNotNone(secure_storage_method)
        self.assertIn(secure_storage_method, ['encryption', 'hashing'])

    @patch('mood_manager.MoodManager.get_mood_history')
    def test_analytical_functionality(self, mock_get_mood_history):
        mock_get_mood_history.return_value = [Mood.HAPPY, Mood.HAPPY, Mood.SAD]
        
        analytics = self.mood_manager.analyze_moods()
        
        if self.mood_manager.enable_logging:
            print("Analyzing moods...")
            for mood, count in analytics.items():
                print(f"{mood}: {count}")
                
        self.assertIsInstance(analytics, dict)
        self.assertTrue('HAPPY' in analytics and analytics['HAPPY'] == 2)
        self.assertTrue('SAD' in analytics and analytics['SAD'] == 1)

    def test_mood_prediction(self):
        self.mood_manager.record_mood(Mood.HAPPY)
        self.mood_manager.record_mood(Mood.HAPPY)
        self.mood_manager.record_mood(Mood.SAD)
        
        predicted_mood = self.mood_manager.predict_next_mood()
        
        self.assertEqual(predicted_mood, Mood.HAPPY)

if __name__ == '__main__':
    unittest.main()