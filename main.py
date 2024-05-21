from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import datetime

app = Flask(__name__)

db_url = os.environ.get('DATABASE_URL', 'sqlite:///moodtracker.db')
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)
app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    mood_logs = db.relationship('MoodLog', backref='user', lazy=True)

class MoodLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mood = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    logged_date = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

@app.before_first_request
def create_database_tables():
    db.create_all()

@app.route('/user/register', methods=['POST'])
def register_user():
    data = request.get_json()
    new_username = data.get('username')
    if not new_username:
        return jsonify({'message': 'Username is required'}), 400
    if User.query.filter_by(username=new_username).first():
        return jsonify({'message': 'Username is already taken'}), 409
    new_user = User(username=new_username)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': f'User {new_username} successfully registered'}), 201

@app.route('/mood/log', methods=['POST'])
def log_user_mood():
    data = request.get_json()
    user_username = data.get('username')
    user_mood = data.get('mood')
    mood_description = data.get('description', None)
    if not all([user_username, user_mood]):
        return jsonify({'message': 'Username and mood are required'}), 400
    registered_user = User.query.filter_by(username=user_username).first()
    if not registered_user:
        return jsonify({'message': 'User not found'}), 404
    new_mood_log = MoodLog(mood=user_mood, description=mood_description, user_id=registered_user.id)
    db.session.add(new_mood_log)
    db.session.commit()
    return jsonify({'message': 'Mood logged successfully'}), 201

@app.route('/mood/report/<string:username>', methods=['GET'])
def generate_user_mood_report(username):
    target_user = User.query.filter_by(username=username).first()
    if not target_user:
        return jsonify({'message': 'User not found'}), 404
    user_mood_logs = MoodLog.query.filter_by(user_id=target_user.id).all()
    mood_report = {}
    for log in user_mood_logs:
        log_date = log.logged_date.strftime('%Y-%m-%d')
        if log_date not in mood_report:
            mood_report[log_date] = []
        mood_report[log_date].append({'mood': log.mood, 'description': log.description})
    return jsonify(mood_report)

if __name__ == '__main__':
    app.run(debug=True, port=5000)