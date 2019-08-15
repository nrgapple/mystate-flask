import os
import unittest
from flask import json
from app import create_app, db
from app.models import User, POI
from base64 import b64encode

TEST_DB = 'test.db'
BASEDIR = os.path.abspath(os.path.dirname(__file__))



class BasicTestConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASEDIR, TEST_DB)
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = False

class BasicTests(unittest.TestCase):
    
    def setUp(self):
        self.app = create_app(BasicTestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        db.drop_all()
        db.create_all()

        self.assertEqual(self.app.debug, False)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_hashing(self):
        n = 'ag'
        p = 'test'
        u = self.create_user(n, p)
        self.assertFalse(u.check_password('dog'))
        self.assertTrue(u.check_password(p))
    
    def test_get_token(self):
        n = 'ag'
        p = 'test'
        self.commit_user(n, p)
        response = self.request_basic('POST', 'api/tokens', auth=(n, p))
        self.assertEqual(response.status_code, 200)

    def test_get_users_with_token(self):
        n = 'ag'
        p = 'test'
        t = self.commit_user_and_get_token(n, p)
        response = self.request_bearer('GET', 'api/users', token=t)
        self.assertEqual(response.status_code, 200)

    def test_main_page(self):
        response = self.client.get('/', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_get_users_without_token(self):
        response = self.client.get('api/users', follow_redirects=True)

        # Look for authentication error code: 401
        self.assertEqual(response.status_code, 401)

    def test_get_user_1(self):
        n = 'ag'
        p = 'test'
        t = self.commit_user_and_get_token(n, p)
        response = self.request_bearer('GET', 'api/users/1', token=t)
        self.assertEqual(response.status_code, 200)

    def test_post_user(self):
        longMessage = True
        
        n = 'ag'
        p = 'test'
        e = 'ag@test.com'
        response = self.client.post('api/users', data=json.dumps(dict(username=n, email=e, password=p)), content_type='application/json')
        # Request has been fulfilled and resulted in new resources: 201
        self.assertEqual(response.status_code, 201, response.get_json())

    def test_put_user(self):
        n = 'ag'
        p = 'test'
        t = self.commit_user_and_get_token(n, p)
        response = self.request_bearer('PUT', 'api/users/1', token=t, data=json.dumps(dict(username='tim')), content_type='application/json')
        self.assertEqual(response.status_code, 200)

    def test_get_pois(self):
        n = 'ag'
        p = 'test'
        t = self.commit_user_and_get_token(n, p)
        self.commit_pois()
        response = self.request_bearer('GET', 'api/pois', token=t)
        self.assertEqual(response.status_code, 200)

    def test_get_poi_1(self):
        n = 'ag'
        p = 'test'
        t = self.commit_user_and_get_token(n, p)
        self.commit_pois()
        response = self.request_bearer('GET', 'api/pois/1', token=t)
        self.assertEqual(response.status_code, 200)

    def test_cant_post_poi_if_not_user(self):
        n = 'new place'
        d = 'here is a new place'
        lat = 23.3208373
        lng = 93.2937837
        response = self.client.post('api/pois', data=json.dumps(dict(name=n, details=d, lat=lat, lng=lng)), content_type='application/json')
        # Request has been fulfilled and resulted in new resources: 201
        self.assertEqual(response.status_code, 401, response.get_json())

    def test_can_post_poi_if_user(self):
        n = 'new place'
        d = 'here is a new place'
        lat = 23.3208373
        lng = 93.2937837
        un = 'ag'
        p = 'test'
        t = self.commit_user_and_get_token(un, p)
        response = self.request_bearer('POST', 'api/pois', token=t, data=json.dumps(dict(name=n, details=d, lat=lat, lng=lng)), content_type='application/json')
        # Request has been fulfilled and resulted in new resources: 201
        self.assertEqual(response.status_code, 201, response.get_json())
    
    def test_post_poi_bad_name(self):
        self.commit_pois()
        n = 'here' # same name as pois/1
        d = 'here is a new place'
        lat = 23.3208373
        lng = 93.2937837
        un = 'ag'
        p = 'test'
        t = self.commit_user_and_get_token(un, p)
        response = self.request_bearer('POST', 'api/pois', token=t, data=json.dumps(dict(name=n, details=d, lat=lat, lng=lng)), content_type='application/json')
        self.assertEqual(response.status_code, 400, response.get_json())

    def test_put_poi(self):
        self.commit_pois()
        n = 'different name'
        d = 'here is a new place'
        lat = 23.3208373
        lng = 93.2937837
        un = 'ag'
        p = 'test'
        t = self.commit_user_and_get_token(un, p)
        response = self.request_bearer('PUT', 'api/pois/1', token=t, data=json.dumps(dict(name=n, details=d, lat=lat, lng=lng)), content_type='application/json')
        self.assertEqual(response.status_code, 200, response.get_json())

    '''
    Helper Functions
    '''
    def request_basic(self, method, url, auth=None, **kwargs):
        headers = kwargs.get('headers', {})
        if auth:
            headers['Authorization'] = 'Basic ' + b64encode(auth[0] + ':' + auth[1])

        kwargs['headers'] = headers

        return self.client.open(url, method=method, **kwargs)

    def request_bearer(self, method, url, token=None, **kwargs):
        headers = kwargs.get('headers', {})
        if token:
            headers['Authorization'] = 'Bearer ' + token

        kwargs['headers'] = headers

        return self.client.open(url, method=method, **kwargs)

    def create_user(self, username, password):
        u = User(username=username)
        p = password
        u.set_password(p)
        return u

    def commit_user(self, username, password):
        u = self.create_user(username, password)
        db.session.add(u)
        db.session.commit()
        return u

    def commit_pois(self):
        p1 = POI(name='here', details='testings the details', lat=20.23938476, lng=43.239474663)
        p2 = POI(name='there', details='this is it', lat=15.14948, lng=3.23211)
        p3 = POI(name='some-place', details='some time we will get there', lat=50.26509, lng=17.67160)
        p4 = POI(name='the-other-place', details='what up', lat=68.72700, lng=142.14045)
        p5 = POI(name='tower town', details='done is this stuff.', lat=62.54924, lng=-42.78576)
        db.session.add_all([p1, p2, p3, p4, p5])
        db.session.commit()
    

    def commit_user_and_get_token(self, username, password):
        self.commit_user(username, password)
        response = self.request_basic('POST', 'api/tokens', auth=(username, password))
        return response.get_json()['token']

if __name__ == "__main__":
    unittest.main(verbosity=2)