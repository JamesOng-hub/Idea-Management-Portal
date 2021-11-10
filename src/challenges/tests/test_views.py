from datetime import timedelta
import datetime
from django.core.paginator import Paginator
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from challenges.models import Challenge, Criteria
from challenges.forms import ChallengeForm
import json
from ideas.models import Idea, Tag
from django.db.models import Count, Q
from urllib.parse import urlencode
from users.models import User
from .test_models import BaseModelTestCase
from users.views import redisRank
# from model_bakery import baker

class TestViews(BaseModelTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='username', password='secret')
        cls.published.subscribers.add(cls.user)
        cls.list_url = reverse('challenge-list')
        cls.detail_url = reverse('challenge-detail', args=[2])
        cls.update_url = reverse('challenge-update', args=[1])
        cls.delete_url = reverse('challenge-delete', args=[1])
        cls.create_url = reverse('challenge-create')
        
        
    def test_challenges_GET(self):
        response = self.client.get(self.list_url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'challenges.html')

    def test_challenges_GET_emptypage(self):
        response = self.client.get(self.list_url,{'page' : 3})
        challenge_list = Challenge.objects.posted().all().order_by('-published_date')
        paginator=Paginator(challenge_list,8)
        self.assertEquals(response.context['queryset'].number, paginator.page(paginator.num_pages).number)


    def test_challenge_detail_GET(self):
        response = self.client.get(self.detail_url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'challenge_detail.html')

    def test_challenge_detail_subscribed_GET(self):
        self.client.force_login(user = self.user)
        response = self.client.get(self.detail_url)
        self.assertTrue(response.context['subscribed'])


    def test_challenge_update_GET(self):
        self.client.force_login(user= self.author)
        response = self.client.get(self.update_url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'challenge_create.html')

    def test_challenge_update_no_perm_GET(self):
        self.client.force_login(user= self.user)
        response = self.client.get(self.update_url)
        self.assertEquals(response.status_code, 403)

    def test_challenge_create_GET(self):
        self.client.force_login(user = self.author)
        response = self.client.get(self.create_url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'challenge_create.html')

    def test_challenge_create_no_perm_GET(self):
        self.client.force_login(user = self.user)
        response = self.client.get(self.create_url)
        self.assertEquals(response.status_code, 403)

    def test_challenge_create_no_login_GET(self):
        response = self.client.get(self.create_url)
        redirect_url = "%s?next=%s" % (reverse('account_login'), self.create_url)
        self.assertRedirects(response,redirect_url, status_code=302)

    def test_challenge_delete_GET(self):
        self.client.force_login(user = self.author)
        response = self.client.get(self.delete_url)
        self.assertRedirects(response, self.list_url, status_code=302)

    def test_challenge_delete_no_perm_GET(self):
        self.client.force_login(user = self.user)
        response = self.client.get(self.delete_url)
        self.assertEquals(response.status_code, 403)

    def test_subscribe(self):
        subscriber = User.objects.create_user(username='subscriber', password='secret')
        subscriber_count = self.published.subscribers_count
        self.client.force_login(user = subscriber)
        response = self.client.post(reverse('subscribe'),
        {
          'challengeid': self.published.id,
          'action': 'post'
        }, xhr=True)
        self.assertJSONEqual(response.content, {'result' : subscriber_count + 1, 'subscribed' : True , 'challengeid' : str(self.published.id)})

    def test_unsubscribe(self):
        unsubscriber = User.objects.create_user(username='unscubscriber', password='secret')
        self.published.subscribers.add(unsubscriber)
        subscriber_count = self.published.subscribers_count
        self.client.force_login(user = unsubscriber)
        response = self.client.post(reverse('subscribe'),
        {
          'challengeid': self.published.id,
          'action': 'post'
        }, xhr=True)
        self.assertJSONEqual(response.content, {'result' : subscriber_count - 1, 'subscribed' : False , 'challengeid' : str(self.published.id)})

    def test_create_challenge_get_image(self):
        self.client.force_login(user = self.author)
        formdata = {
            'title' : 'test challenge',
            'description' : 'test',
            'thumbnail' : '',
            'idea_submission_deadline' :'2021-11-11',
            'image-picker' :'gallery-1.jpg',
        }
        response = self.client.post(self.create_url,urlencode(formdata),content_type="application/x-www-form-urlencoded")
        self.assertEqual(Challenge.objects.last().thumbnail, 'gallery-1.jpg' )

    def test_create_challenge_get_new_criterias(self):
        self.client.force_login(user = self.author)
        formdata = {
            'title' : 'test challenge',
            'description' : 'test',
            'thumbnail' : '',
            'idea_submission_deadline' :'2021-11-11',
            'criteria' : 'c1',
        }
        form = ChallengeForm(data=formdata)
        response = self.client.post(self.create_url,urlencode(formdata),content_type="application/x-www-form-urlencoded")
        self.assertTrue(form.is_valid())
        self.assertTrue(Challenge.objects.last().criterias.filter(description='c1').exists())
        self.assertEqual(Criteria.objects.last().description,'c1')

    def test_create_challenge_get_existing_criterias(self):
        exists = Criteria.objects.create( description = "exists")
        self.client.force_login(user = self.author)
        formdata = {
            'title' : 'test challenge',
            'description' : 'test',
            'thumbnail' : '',
            'idea_submission_deadline' :'2021-11-11',
            'criteria' : 'exists',
        }
        response = self.client.post(self.create_url,urlencode(formdata),content_type="application/x-www-form-urlencoded")
        self.assertTrue(Challenge.objects.last().criterias.filter(pk = exists.pk).exists())
        self.assertEqual(Criteria.objects.filter(description='exists').count(),1)

    def test_create_challenge_final(self):
        self.client.force_login(user = self.author)
        formdata = {
            'title' : 'test challenge',
            'description' : 'test',
            'thumbnail' : '',
            'idea_submission_deadline' :'2021-11-11',
            'final' : ''
        }
        response = self.client.post(self.create_url,urlencode(formdata),content_type="application/x-www-form-urlencoded")
        self.assertIsNotNone(Challenge.objects.last().published_date)

    def test_create_challenge_draft(self):
        self.client.force_login(user = self.author)
        formdata = {
            'title' : 'test challenge',
            'description' : 'test',
            'thumbnail' : '',
            'idea_submission_deadline' :'2021-11-11',
        }
        response = self.client.post(self.create_url,urlencode(formdata),content_type="application/x-www-form-urlencoded")
        self.assertIsNone(Challenge.objects.last().published_date)

    def test_update_challenge_final(self):
        self.client.force_login(user = self.author)
        challenge = Challenge.objects.create(
            author=self.author,
            title = "Update",
            description = "update",
            date_created = timezone.now(),
            idea_submission_deadline = datetime.date(2021, 12, 1),
        )
        formdata = {
            'title' : 'Update',
            'description' : 'update',
            'thumbnail' : 'defaultbg.jpg',
            'idea_submission_deadline' :datetime.date(2021, 12, 1),
            'final' : ''
        }
        form = ChallengeForm(data=formdata)
        self.assertTrue(form.is_valid())
        response = self.client.post(reverse('challenge-update', args=[challenge.pk]),urlencode(formdata),content_type="application/x-www-form-urlencoded")
        self.assertIsNotNone(Challenge.objects.last().published_date)

    def test_update_challenge_criteria(self):
        self.client.force_login(user = self.author)
        c1 = Criteria.objects.create(description='c1')
        c3 = Criteria.objects.create(description='c3')
        challenge = Challenge.objects.create(
            author=self.author,
            title = "UpdateCriteria",
            description = "updatecriteria",
            date_created = timezone.now(),
            idea_submission_deadline = datetime.date(2021, 12, 1),
        )
        challenge.criterias.add(c1)
        formdata = {
            'title' : 'UpdateCriteria',
            'description' : 'updatecriteria',
            'thumbnail' : 'defaultbg.jpg',
            'idea_submission_deadline' :datetime.date(2021, 12, 1),
            'criteria' : ['c2','c3']
        }
        response = self.client.post(reverse('challenge-update', args=[challenge.pk]),formdata)
        self.assertFalse(challenge.criterias.filter(description='c1').exists())
        self.assertTrue(challenge.criterias.filter(description='c2').exists())
        self.assertTrue(challenge.criterias.filter(description='c3').exists())
        print(challenge.criterias)

    def test_update_challenge_image(self):
        self.client.force_login(user = self.author)
        challenge = Challenge.objects.create(
            author=self.author,
            title = "UpdateImage",
            description = "updateimage",
            date_created = timezone.now(),
            idea_submission_deadline = datetime.date(2021, 12, 1),
            thumbnail = 'defaultbg.jpg'
        )
        formdata = {
            'title' : 'UpdateImage',
            'description' : 'updateImage',
            'thumbnail' : '',
            'idea_submission_deadline' :datetime.date(2021, 12, 1),
            'image-picker' :'gallery-1.jpg',
        }
        response = self.client.post(reverse('challenge-update', args=[challenge.pk]),urlencode(formdata),content_type="application/x-www-form-urlencoded")
        challenge.refresh_from_db()
        self.assertEqual(challenge.thumbnail, 'gallery-1.jpg' )

    def tearDown(self):
        self.test_redis = redisRank('scoreboard')
        self.test_redis.deleteAll()

class TestQueryViews(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user= User.objects.create_user(
            username='user',
            password='secret'
        )
        cls.challenge1 = Challenge.objects.create(
            author=cls.user,
            title = "Challenge1",
            date_created = timezone.now() - timedelta(days=1),
            idea_submission_deadline = (timezone.now()  + timedelta(days=1)).date(),
            published_date = timezone.now() - timedelta(days=1),
            state = Challenge.State.ACTIVE
        )
        cls.challenge2 = Challenge.objects.create(
            author=cls.user,
            title = "Challenge2",
            date_created = timezone.now(),
            idea_submission_deadline = (timezone.now()  + timedelta(days=1)).date(),
            published_date = timezone.now(),
            state = Challenge.State.ACTIVE
        )
        cls.testidea1 = Idea.objects.create(
            author = cls.user.profile,
            title = "Idea1",
            date_posted = timezone.now(),
            approved = True
        )
        cls.testidea2 = Idea.objects.create(
            author = cls.user.profile,
            title = "Idea2",
            date_posted = timezone.now(),
            approved = True
        )
        cls.challenge1.ideas.set([cls.testidea1,cls.testidea2])

    def test_sort_popularity(self):
        response = self.client.get(reverse('challenge-list'),{ 'sort' : 'popularity'})
        self.assertEqual(response.context['queryset'].object_list,list(Challenge.objects.posted().annotate(icount=Count('ideas',filter=Q(ideas__approved=True))).order_by('-icount')))

    def test_sort_newest(self):
        response = self.client.get(reverse('challenge-list'),{ 'sort' : 'newest'})
        self.assertEqual(response.context['queryset'].object_list,list(Challenge.objects.posted().order_by('-published_date')))

    def test_filter_criteria(self):
        tag = Tag.objects.create(
            title = "tag"
        )
        self.challenge1.tags.add(tag)
        response = self.client.get(reverse('challenge-list'),{ 'category' : ['tag']})
        self.assertEqual(response.context['challenges_count'],1)
        self.assertEqual(response.context['queryset'].object_list,list(Challenge.objects.posted().filter(tags__title = 'tag').distinct()))


    def test_filter_active_challenges(self):
        response = self.client.get(reverse('challenge-list'),{ 'status' : ['active']})
        self.assertEqual(response.context['queryset'].object_list,list(Challenge.objects.posted().order_by('-published_date').filter(state=Challenge.State.ACTIVE)))

    def test_filter_ended_challenges(self):
        challenge = Challenge.objects.create(
            author=self.user,
            title = "ENDED",
            published_date = timezone.now() - timedelta(days=1),
            idea_submission_deadline =timezone.now().date(),
            state = Challenge.State.ENDED
        )
        response = self.client.get(reverse('challenge-list'),{ 'status' : ['ended']})
        self.assertEqual(response.context['queryset'].object_list,list(Challenge.objects.posted().order_by('-published_date').filter(state=Challenge.State.ENDED)))

    def tearDown(self):
        self.test_redis = redisRank('scoreboard')
        self.test_redis.deleteAll()

