import unittest
import json
import logging
from app import app, db

from flask_testing import TestCase

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')

class BaseTest(TestCase):
    
    def create_application(self):
        app.config.from_object('yourapplication.default_settings')
        app.config['TESTing'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        return app

    def setUp(self):
        self.application = app.test_client()
        self.database = db
        self.database.create_all()
        
        logging.info('Database setup complete.')

    def tearDown(self):
        self.database.session.remove()
        self.database.drop_all()
        
        logging.info('Database teardown complete.')

class UserAuthTest(BaseTest):

    def test_register(self):
        with self.application:
            response = self.application.post('/register', data=json.dumps(dict(
                username="john_doe",
                password="password123"
            )), content_type='application/json')
            response_data = json.loads(response.data.decode())
            self.assertTrue(response_data['status'] == 'success')
            self.assertTrue(response_data['message'] == 'Successfully registered.')
            self.assertEqual(response.status_code, 201)
            
            logging.debug('test_register: %s', response_data['message'])

    def test_login(self):
        with self.application:
            response = self.application.post('/login', data=json.dumps(dict(
                username="john_doe",
                password="password123"
            )), content_type='application/json')
            response_data = json.loads(response.data.decode())
            self.assertTrue(response_data['status'] == 'success')
            self.assertTrue(response_data['message'] == 'Successfully logged in.')
            self.assertTrue(response_data['auth_token'])
            self.assertEqual(response.status_code, 200)
            
            logging.debug('test_login: %s', response_data['message'])

class MoodManagementTest(BaseTest):

    def test_add_mood(self):
        with self.application:
            response = self.application.post('/mood', data=json.dumps(dict(
                mood="happy",
                description="Feeling great today!"
            )), content_type='application/json')
            response_data = json.loads(response.data.decode())
            self.assertTrue(response_data['status'] == 'success')
            self.assertEqual(response.status_code, 201)
            
            logging.debug('test_add_mood: %s', response_data['message'])

    def test_retrieve_mood(self):
        with self.application:
            self.application.post('/mood', data=json.dumps(dict(
                mood="happy",
                description="Feeling great today!"
            )), content_type='application/json')
            response = self.application.get('/mood')
            response_data = json.loads(response.data.decode())
            self.assertTrue(len(response_data['moods']) > 0)
            self.assertEqual(response.status_code, 200)
            
            logging.debug('test_retrieve_mood: Retrieved %d moods', len(response_data['moods']))

if __name__ == '__main__':
    unittest.main()