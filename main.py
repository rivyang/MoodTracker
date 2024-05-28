from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import joinedload
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import os
import logging
import jwt

app = Flask(__name__)

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s:%(message)s')

# Secret key for JWT encoding & decoding. In production, prefer using a more secure and random secret.
app.config['SECRET_KEY'] = 'your_secret_key'

db_url = os.environ.get('DATABASE_URL', 'sqlite:///moodtracker.db')
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)
app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    mood_logs = db.relationship('MoodLog', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

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
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        logging.warning('Username and password are required for registration')
        return jsonify({'message': 'Username and password are required'}), 400
    if User.query.filter_by(username=username).first():
        logging.info(f'Registration failed - Username {username} is already taken')
        return jsonify({'message': 'Username already taken'}), 409
    new_user = User(username=username)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': f'User {username} successfully registered'}), 201

@app.route('/user/login', methods=['POST'])
def login_user():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return make_response('Could not verify', 401, {'WWW.Authentication': 'Basic realm: "Login required"'})
    
    user = User.query.filter_by(username=username).first()
    
    if not user or not user.check_password(password):
        return make_response('Could not verify', 401, {'WWW.Authentication': 'Basic realm: "Login required"'})
    
    token = jwt.encode({'user_id': user.id, 'exp': datetime.utcnow() + timedelta(hours=24)}, app.config['SECRET_KEY'], algorithm="HS256")

    return jsonify({'token': token})

def token_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]
        
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = User.query.get(data['user_id'])
        except:
            return jsonify({'message': 'Token is invalid!'}), 401
        
        return f(current_user, *args, **kwargs)

    return decorated

@app.route('/mood/logs', methods=['POST'])
@token_required
def log_multiple_moods(current_user):
    data = request.get_json()
    logs = data.get('logs')
    
    if not logs:
        logging.warning('Attempt to log moods without specifying logs')
        return jsonify({'message': 'Logs data are required'}), 400
    
    for log in logs:
        new_mood_log = MoodLog(mood=log['mood'],
                               description=log.get('description'),
                               user_id=current_user.id)
        db.session.add(new_mood_log)
        
    db.session.commit()
    logging.info(f'Successfully logged {len(logs)} moods for user {current_user.username}')
    return jsonify({'message': f'{len(logs)} moods logged successfully'}), 201

@app.route('/mood/analysis/<string:username>', methods=['GET'])
@token_required
def generate_analysis(current_user, username):
    if current_user.username != username:
        return jsonify({'message': "Unauthorized"}), 403
    
    moods = MoodLog.query.filter_by(user_id=current_user.id).all()
    
    if not moods:
        return jsonify({'message': 'No mood logs found'}), 404
    
    mood_frequency = {}
    for mood in moods:
        if mood.mood in mood_frequency:
            mood_frequency[mood.mood] += 1
        else:
            mood_frequency[mood.mood] = 1
            
    most_frequent_mood = max(mood_frequency, key=mood_frequency.get)
    
    analysis_result = {
        'most_frequent_mood': most_frequent_mood,
        'mood_frequency': mood_frequency,
    }
    
    return jsonify(analysis_result)

if __name__ == '__main__':
    app.run(debug=True, port=5000)