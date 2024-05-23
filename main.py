from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import joinedload
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

@app.route('/mood/logs', methods=['POST'])
def log_multiple_moods():
    """Endpoint to log multiple moods for a user in one request."""
    data = request.get_json()
    user_id = data.get('user_id')
    logs = data.get('logs')  # Expecting a list of mood and optional description dictionaries
    
    if not user_id or not logs:
        return jsonify({'message': 'User ID and logs data are required'}), 400
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404

    for log in logs:
        new_mood_log = MoodLog(mood=log['mood'], 
                               description=log.get('description'), 
                               user_id=user_id)
        db.session.add(new_mood_log)
        
    db.session.commit()
    
    return jsonify({'message': f'{len(logs)} moods logged successfully'}), 201

@app.route('/mood/report/<string:username>', methods=['GET'])
def generate_user_mood_report(username):
    target_user = User.query.filter_by(username=username).first()
    if not target_user:
        return jsonify({'message': 'User not found'}), 404
    user_mood_logs = MoodLog.query.options(joinedload(MoodLog.user)).filter_by(user_id=target_user.id).all()
    mood_report = {}
    for log in user_mood_logs:
        log_date = log.logged_date.strftime('%Y-%m-%d')
        if log_date not in mood_report:
            mood_report[log_date] = []
        mood_report[log_date].append({'mood': log.mood, 'description': log.description})
    return jsonify(mood_report)

if __name__ == '__main__':
    app.run(debug=True, port=5000)