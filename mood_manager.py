import os
from datetime import datetime
import json

MOOD_DATA_FILE_PATH = os.getenv('MOOD_DATA_FILE', 'mood_data.json')

def load_moods_from_file():
    try:
        with open(MOOD_DATA_FILE_PATH, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return []

def save_moods_to_file(moods):
    with open(MOOD_DATA_FILE_PATH, 'w') as file:
        json.dump(moods, file, indent=4)

class MoodTracker:
    @staticmethod
    def record_mood(mood, recorded_at=None):
        if recorded_at is None:
            recorded_at = datetime.now().isoformat()
        moods = load_moods_from_file()
        moods.append({'mood': mood, 'timestamp': recorded_at})
        save_moods_to_file(moods)
        return True

    @staticmethod
    def delete_mood(recorded_at):
        moods = load_moods_from_file()
        moods = [entry for entry in moods if entry['timestamp'] != recorded_at]
        save_moods_to_file(moods)
        return True

    @staticmethod
    def change_mood(recorded_at, updated_mood):
        moods = load_moods_from_file()
        for entry in moods:
            if entry['timestamp'] == recorded_at:
                entry['mood'] = updated_mood
                save_moods_to_file(moods)
                return True
        return False

    @staticmethod
    def display_all_moods():
        return load_moods_from_file()

    @staticmethod
    def summarize_moods():
        moods = load_moods_from_file()
        mood_frequency = {}
        for entry in moods:
            mood = entry['mood']
            if mood in mood_frequency:
                mood_frequency[mood] += 1
            else:
                mood_frequency[mood] = 1
        summary = {
            'total_entries': len(moods),
            'mood_distribution': mood_frequency
        }
        return summary

    @staticmethod
    def generate_mood_insights():
        summary = MoodTracker.summarize_moods()
        mood_distribution = summary['mood_distribution']
        total_mood_entries = summary['total_entries']
        prevalent_mood = max(mood_distribution, key=mood_distribution.get) if mood_distribution else 'None'
        insights = {
            'most_common_mood': prevalent_mood,
            'entries_analyzed': total_mood_entries,
        }
        insights['insight_message'] = f'Your most common mood is {prevalent_mood}.'
        return insights