from django.test import TestCase
from users.views import redisRank
from django.contrib.auth.models import User
from ideas_portal.settings import leaderBoard
from django.urls import reverse

class LeaderboardTest(TestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', 
            email='testemail@example.com',
            password='secret'
        )
        self.test_redis = redisRank('scoreboard')
        self.test_redis.addAll()

    def test_view_url_exists_at_desired_location(self):
        response = self.client.post('/leaderboard/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.post(reverse('leaderboard'))
        self.assertEqual(response.status_code, 200)
        
    @classmethod
    def tearDownClass(self):
        self.test_redis = redisRank('scoreboard')
        self.test_redis.deleteAll()


class ProfileTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', 
            email='testemail@example.com',
            password='secret'
        )
        self.client.force_login(self.user)

    def test_view_url_exists_at_desired_location(self):
        response = self.client.post('/profile/', data={
            'length' : 1,
            'toplist': [('testuser', 0.0)],
            'user_rank' : 1
        })
        username = 'testuser'
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.post(reverse('profile'), data={
            'length' : 1,
            'toplist': [('testuser', 0.0)],
            'user_rank' : 1
        })
        username = 'testuser'
        url = f'/user/{username}/'
        self.assertEqual(response.status_code, 200)
    
    def test_profile(self):
        u_formdata={
            'username': 'testuser', 
            'email': 'testuser@email.com',
            'bio': 'testuser', 
            'occupation': '',
            'location': '',
            'image': 'default.jpg'
        }
        response = self.client.post('/profile/', u_formdata)
        username = 'testuser'
        self.assertEqual(response.status_code, 302)

    def tearDown(self):
        self.test_redis = redisRank('scoreboard')
        self.test_redis.deleteAll()

class UCLSSOTest(TestCase):
    def test_ucl_sso(self):
        data = {
            'result': 'test', 
            'code': 'tset',
            'state': 'testuser'
        }
        response = self.client.post('/callback/', data)
        self.assertEqual(response.status_code, 302)