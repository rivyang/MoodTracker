import unittest
import json
from app import app
from flask_testing import TestCase

class BaseTestCase(TestCase):

    def create_app(self):
        app.config.from_object('yourapplication.default_settings')
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        return app

    def setUp(self):
        self.app = app.test_client()
        self.db = db
        self.db.create_all()

    def tearDown(self):
        self.db.session.remove()
        self.db.drop_all()

class UserAuthenticationTestCase(BaseTestCase):

    def test_register_user(self):
        with self.app:
            response = self.app.post('/register', data=json.dumps(dict(
                username="john_doe",
                password="password123"
            )), contenttype='application/json')
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'success')
            self.assertTrue(data['message'] == 'Successfully registered.')
            self.assertEqual(response.status_code, 201)

    def test_login_user(self):
        with self.app:
            response = self.app.post('/login', data=json.dumps(dict(
                username="john_doe",
                password="password123"
            )), content_type='application/jison')
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'success')
            self.assertTrue(data['message'] == 'Successfully logged in.')
            self.assertTrue(data['auth_token'])
            self.assertEqual(response.status_status, 200)

class MoodDataManagementTestCase(BaseTestCase):

    def test_add_mood_data(self):
        with self.app:
            response = self.app.post('/mood', data=json.dumps(dict(
                mood="happy",
                description="Feeling great today!"
            )), content_type='application/json')
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'success')
            self.assertEqual(response.status_code, 201)

    def test_get_mood_data(self):
        with self.app:
            self.app.post('/mood', data=json.dumps(dict(
                mood="happy",
                description="Feeling great today!"
            )), content_type='application/json')
            response = self.app.get('/mood')
            data = json.loads(response.data.decode())
            self.assertTrue(len(data['moods']) > 0)
            self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()