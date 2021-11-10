from django.test import SimpleTestCase
from django.urls import reverse, resolve
from ideas.views import (index, dashboard, idea_detail, idea_create, idea_update, idea_delete, review, vote, idea_submit)
from challenges.views import challenge_delete, challenge_update, challenges, subscribe, ChallengeDetailView, challenge_create
from users.views import profile, UserProfile, leaderboard,uclsso
from contact.views import contact_us
from community_guideline.views import GuidelineList, GuidelineDetail

class TestIdeaUrls(SimpleTestCase):
    def test_idea_list_url_resolved(self):
        url = reverse('idea-list')
        self.assertEquals(resolve(url).func, dashboard)

    def test_index_url_resolved(self):
        url = reverse('index')
        self.assertEquals(resolve(url).func, index)

    def test_idea_detail_url_resolved(self):
        url = reverse('idea-detail', args=[1])
        self.assertEquals(resolve(url).func, idea_detail)

    def test_idea_create_url_resolved(self):
        url = reverse('idea-create')
        self.assertEquals(resolve(url).func, idea_create)

    def test_idea_update_url_resolved(self):
        url = reverse('idea-update', args=[1])
        self.assertEquals(resolve(url).func, idea_update)

    def test_idea_delete_url_resolved(self):
        url = reverse('idea-delete', args=[1])
        self.assertEquals(resolve(url).func,idea_delete)

    def test_idea_review_url_resolved(self):
        url = reverse('idea-review', args=['slug'])
        self.assertEquals(resolve(url).func, review)

    def test_vote_url_resolved(self):
        url = reverse('vote')
        self.assertEquals(resolve(url).func, vote)

    def test_idea_submit_url_resolved(self):
        url = reverse('idea-submit', args=[1])
        self.assertEquals(resolve(url).func, idea_submit)   

class TestChallengeUrls(SimpleTestCase):
    def test_challenge_list_url_resolved(self):
        url = reverse('challenge-list')
        self.assertEquals(resolve(url).func, challenges)

    def test_challenge_delete_url_resolved(self):
        url = reverse('challenge-delete', args=[1])
        self.assertEquals(resolve(url).func, challenge_delete)

    def test_challenge_update_url_resolved(self):
        url = reverse('challenge-update',args=[1])
        self.assertEquals(resolve(url).func, challenge_update)

    def test_subscribe_url_resolved(self):
        url = reverse('subscribe')
        self.assertEquals(resolve(url).func, subscribe)

    def test_challenge_detail_url_resolved(self):
        url = reverse('challenge-detail',args=[1])
        self.assertEquals(resolve(url).func.view_class, ChallengeDetailView)
    
    def test_challenge_create_url_resolved(self):
        url = reverse('challenge-create')
        self.assertEquals(resolve(url).func, challenge_create)

class TestUserUrls(SimpleTestCase):
    def test_profile_url_resolved(self):
        url = reverse('profile')
        self.assertEquals(resolve(url).func, profile)

    def test_userprofile_url_resolved(self):
        url = reverse('user-profile', args=['username'])
        self.assertEquals(resolve(url).func.view_class, UserProfile)  

    def test_leaderboard_url_resolved(self):
        url = reverse('leaderboard')
        self.assertEquals(resolve(url).func, leaderboard) 

    def test_uclsso_url_resolved(self):
        url = reverse('uclsso')
        self.assertEquals(resolve(url).func, uclsso)

class TestUrls(SimpleTestCase):
    def test_contact_url_resolved(self):
        url = reverse('contact-us')
        self.assertEquals(resolve(url).func, contact_us)

    def test_guideline_list_url_resolved(self):
        url = reverse('guideline-list')
        self.assertEquals(resolve(url).func.view_class, GuidelineList)

    def test_guideline_detail_url_resolved(self):
        url = reverse('guideline-detail', args=[1])
        self.assertEquals(resolve(url).func.view_class, GuidelineDetail)