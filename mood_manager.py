import os
from datetime import datetime
import json

MOOD_DATA_FILE = os.getenv('MOOD_DATA_FILE', 'mood_data.json')

def read_data_from_file():
    try:
        with open(MOOD_DATA_FILE, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return []

def write_data_to_file(data):
    with open(MOOD_DATA_FILE, 'w') as file:
        json.dump(data, file, indent=4)

class MoodManager:
    @staticmethod
    def add_mood(mood, timestamp=None):
        if timestamp is None:
            timestamp = datetime.now().isoformat()
        data = read_data_from_file()
        data.append({'mood': mood, 'timestamp': timestamp})
        write_data_to_file(data)
        return True

    @staticmethod
    def remove_mood(timestamp):
        data = read_data_from_file()
        data = [entry for entry in data if entry['timestamp'] != timestamp]
        write_data_to_file(data)
        return True

    @staticmethod
    def update_mood(timestamp, new_mood):
        data = read_data_from_file()
        for entry in data:
            if entry['timestamp'] == timestamp:
                entry['mood'] = new_mood
                write_data_to_file(data)
                return True
        return False

    @staticmethod
    def list_all_moods():
        return read_data_from_file()

    @staticmethod
    def analyze_moods():
        data = read_data_from_file()
        mood_count = {}
        for entry in data:
            mood = entry['mood']
            if mood in mood_count:
                mood_count[mood] += 1
            else:
                mood_count[mood] = 1
        analysis = {
            'total_entries': len(data),
            'mood_distribution': mood_count
        }
        return analysis

    @staticmethod
    def generate_insights():
        analysis = MoodManager.analyze_moods()
        mood_dist = analysis['mood_distribution']
        total_entries = analysis['total_entries']
        most_common_mood = max(mood_dist, key=mood_dist.get) if mood_dist else 'None'
        insights = {
            'most_common_mood': most_common_mood,
            'entries_analyzed': total_entries,
        }
        insights['personalized_insight'] = f'Your most common mood is {most_common_mood}.'
        return insights