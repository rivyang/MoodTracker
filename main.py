from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import datetime

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///moodtracker.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    moods = db.relationship('MoodLog', backref='user', lazy=True)

class MoodLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mood = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    date_logged = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

@app.before_first_request
def create_tables():
    db.create_all()

@app.route('/register', methods=['POST'])
def register_user():
    data = request.get_json()
    username = data.get('username')
    if not username:
        return jsonify({'message': 'Username is required'}), 400
    if User.query.filter_by(username=username).first():
        return jsonify({'message': 'Username is already taken'}), 409
    user = User(username=username)
    db.session.add(user)
    db.session.commit()
    return jsonify({'message': f'User {username} successfully registered'}), 201

@app.route('/log_mood', methods=['POST'])
def log_mood():
    data = request.get_json()
    username = data.get('username')
    mood = data.get('mood')
    description = data.get('description', None)
    if not all([username, mood]):
        return jsonify({'message': 'Username and mood are required'}), 400
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({'message': 'User not found'}), 404
    mood_log = MoodLog(mood=mood, description=description, user_id=user.id)
    db.session.add(mood_log)
    db.session.commit()
    return jsonify({'message': 'Mood logged successfully'}), 201

@app.route('/mood_report/<string:username>', methods=['GET'])
def mood_report(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({'message': 'User not found'}), 404
    mood_logs = MoodLog.query.filter_by(user_id=user.id).all()
    report = {}
    for log in mood_logs:
        date = log.date_logged.strftime('%Y-%m-%d')
        if date not in report:
            report[date] = []
        report[date].append({'mood': log.mood, 'description': log.description})
    return jsonify(report)

if __name__ == '__main__':
    app.run(debug=True, port=5000)