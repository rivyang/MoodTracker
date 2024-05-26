import os
from datetime import datetime, timedelta
import json
import uuid

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

def filter_moods_by_date(moods, start_date=None, end_date=None):
    if not start_date and not end_date:
        return moods
    filtered_moods = []
    for mood in moods:
        mood_date = datetime.fromisoformat(mood['timestamp'])
        if start_date and mood_date < start_date:
            continue
        if end_date and mood_date > end_date:
            continue
        filtered_moods.append(mood)
    return filtered_moods

class MoodTracker:
    @staticmethod
    def record_mood(mood, recorded_at=None):
        if recorded_at is None:
            recorded_at = datetime.now().isoformat()
        moods = load_moods_from_file()
        moods.append({'id': str(uuid.uuid4()), 'mood': mood, 'timestamp': recorded_at})
        save_moods_to_file(moods)
        return True

    @staticmethod
    def delete_mood(mood_id):
        moods = load_moods_from_file()
        moods = [entry for entry in moods if entry['id'] != mood_id]
        save_moods_to_file(moods)
        return True

    @staticmethod
    def change_mood(mood_id, updated_mood):
        moods = load_moods_from_file()
        for entry in moods:
            if entry['id'] == mood_id:
                entry['mood'] = updated_mood
                save_moods_to_file(moods)
                return True
        return False

    @staticmethod
    def display_all_moods(start_date=None, end_date=None):
        moods = load_moods_from_file()
        filtered_moods = filter_moods_by_date(moods, start_date, end_date)
        return filtered_moods

    @staticmethod
    def filter_moods_by_type(mood_type, start_date=None, end_date=None):
        moods = load_moods_from_file()
        filtered_moods = filter_moods_by_date(moods, start_date, end_date)
        return [mood for mood in filtered_moods if mood['mood'] == mood_type]

    @staticmethod
    def summarize_moods(start_date=None, end_date=None):
        moods = load_moods_from_file()
        filtered_moods = filter_moods_by_date(moods, start_date, end_date)
        mood_frequency = {}
        for entry in filtered_moods:
            mood = entry['mood']
            if mood in mood_frequency:
                mood_frequency[mood] += 1
            else:
                mood_frequency[mood] = 1
        summary = {
            'total_entries': len(filtered_moods),
            'mood_distribution': mood_frequency
        }
        return summary

    @staticmethod
    def generate_mood_insights(start_date=None, end_date=None):
        summary = MoodTracker.summarize_moods(start_date, end_date)
        mood_distribution = summary['mood_distribution']
        total_mood_entries = summary['total_entries']
        prevalent_mood = max(mood_distribution, key=mood_distribution.get) if mood_distribution else 'None'
        insights = {
            'most_common_mood': prevalent_mood,
            'entries_analyzed': total_mood_entries,
        }
        insights['insight_message'] = f'Your most common mood from {start_date} to {end_date} is {prevalent_mood}.'
        return insights

    @staticmethod
    def export_moods_to_readable_file(start_date=None, end_date=None, file_path="exported_moods.txt"):
        moods = MoodTracker.display_all_moods(start_date, end_date)
        with open(file_path, 'w') as file:
            for mood in moods:
                file.write(f"Date: {mood['timestamp']}, Mood: {mood['mood']}\n")
        print(f"Moods successfully exported to {file_path}")

MoodTracker.export_moods_to_readable_file("2021-01-01", "2021-12-31")