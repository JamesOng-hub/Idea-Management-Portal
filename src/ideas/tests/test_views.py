from datetime import timedelta
from django.db.models.aggregates import Count, Sum
from django.db.models.query_utils import Q
from django.test import TestCase
from django.utils import timezone
from django.urls import reverse
from challenges.models import Challenge, Criteria
from ideas.models import Comment, CriteriaScore, Idea, Review, Tag
from users.models import User
from users.views import redisRank


class TestNotLoggedInViews(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user= User.objects.create_user(
            username='user',
            password='secret'
        )
        cls.idea= Idea.objects.create(
            author = cls.user.profile,
            title = "Idea One",
            date_posted = timezone.now(),
            approved = True
        )

    def test_index_GET(self):
        response = self.client.get(reverse('index'))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'index.html')

    def test_ideas_GET(self):
        response = self.client.get(reverse('idea-list'))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'ideas.html')

    def test_idea_detail_GET(self):
        response = self.client.get(reverse('idea-detail', args=[1]))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'idea.html')

    def test_idea_update_no_login_GET(self):
        response = self.client.get(reverse('idea-update', args=[1]))
        redirect_url = "%s?next=%s" % (reverse('account_login'), reverse('idea-update', args=[1]))
        self.assertRedirects(response,redirect_url, status_code=302)

    def test_idea_create_no_login_GET(self):
        response = self.client.get(reverse('idea-create'))
        redirect_url = "%s?next=%s" % (reverse('account_login'),reverse('idea-create'))
        self.assertRedirects(response,redirect_url, status_code=302)

    def test_idea_delete_no_login_GET(self):
        response = self.client.get(reverse('idea-delete', args=[1]))
        redirect_url = "%s?next=%s" % (reverse('account_login'), reverse('idea-delete', args=[1]))
        self.assertRedirects(response,redirect_url, status_code=302)

    def test_vote_no_login(self):
        response = self.client.get(reverse('vote'))
        redirect_url = "%s?next=%s" % (reverse('account_login'), reverse('vote'))
        self.assertRedirects(response,redirect_url, status_code=302)

    @classmethod
    def tearDownClass(self):
        self.test_redis = redisRank('scoreboard')
        self.test_redis.deleteAll()


class TestLoggedInViews(TestCase):
    @classmethod
    def setUpTestData(cls):
        #challenge author
        cls.challenge_author = User.objects.create_user(
            username='author',
            email='testemail@example.com',
            password='secret'
        )
        #idea1 author
        cls.idea1_author = User.objects.create_user(
            username='testuser',
            password='secret'
        )
        cls.tag = Tag.objects.create(
            title = "tag"
        )
        #active,published
        cls.challenge = Challenge.objects.create(
            author=cls.challenge_author,
            title = "Challenge One",
            date_created = timezone.now() - timedelta(days=1),
            idea_submission_deadline = (timezone.now()  + timedelta(days=1)).date(),
            state = Challenge.State.ACTIVE,
            published_date = timezone.now() - timedelta(days=1)
        )
        cls.criteria1 = Criteria.objects.create(
            description = "criteria1description"
        )
        cls.criteria2 = Criteria.objects.create(
            description = "criteria2description"
        )
        cls.challenge.criterias.set([cls.criteria1,cls.criteria2])
        cls.idea1 = Idea.objects.create(
            author = cls.idea1_author.profile,
            title = "Idea One",
            date_posted = timezone.now(),
            approved = True,
            challenge = cls.challenge
        )
        cls.idea2 = Idea.objects.create(
            author = cls.idea1_author.profile,
            title = "Idea Two",
            date_posted = timezone.now(),
            approved = True,
            challenge = cls.challenge
        )
        cls.comment = Comment.objects.create(
            user = cls.challenge_author,
            date_posted = timezone.now(),
            content = 'test comment',
            idea = cls.idea1
        )
        cls.review = Review.objects.create(
            reviewer = cls.challenge_author,
            idea = cls.idea1
        )
        cls.cs1 = CriteriaScore.objects.create(
            review = cls.review,
            criteria = cls.criteria1,
            score = 1
        )
        cls.cs2 = CriteriaScore.objects.create(
            review = cls.review,
            criteria = cls.criteria2,
            score = 2
        )

    def test_idea_update_GET(self):
        self.client.force_login(user= self.idea1.author.user)
        response = self.client.get(reverse('idea-update', args=[self.idea1.pk]))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'idea_create.html')

    def test_idea_update_no_perm_GET(self):
        self.client.force_login(user= self.challenge_author)
        response = self.client.get(reverse('idea-update', args=[self.idea1.pk]))
        self.assertEquals(response.status_code, 403)

    def test_idea_create_GET(self):
        self.client.force_login(user = self.idea1_author)
        response = self.client.get(reverse('idea-create'))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'idea_create.html')

    def test_idea_delete_GET(self):
        self.client.force_login(user = self.idea1_author)
        response = self.client.get(reverse('idea-delete', args=[self.idea1.pk]))
        self.assertRedirects(response,reverse('idea-list'),status_code=302 )

    def test_vote(self):
        voter = User.objects.create_user(username='voter', password='secret')
        vote_count = self.idea1.vote_count
        self.client.force_login(user = voter)
        response = self.client.post(reverse('vote'),
        {
          'ideaid': self.idea1.id,
          'action': 'post'
        }, xhr=True)
        self.assertJSONEqual(response.content, {'result' : vote_count + 1, 'voted' : True , 'ideaid' : str(self.idea1.id)})

    def test_unvote(self):
        unvoter = User.objects.create_user(username='unvoter', password='secret')
        self.client.force_login(user = unvoter)
        self.idea1.votes.add(unvoter)
        unvoter.profile.score +=1
        self.idea1_author.profile.score +=1
        unvoter.profile.save()
        self.idea1_author.profile.save()
        vote_count = self.idea1.vote_count + 1
        self.idea1.save()
        response = self.client.post(reverse('vote'),
        {
          'ideaid': self.idea1.id,
          'action': 'post'
        }, xhr=True)
        self.assertJSONEqual(response.content, {'result' : vote_count - 1, 'voted' : False , 'ideaid' : str(self.idea1.id)})

    def test_review_GET(self):
        self.client.force_login(user = self.challenge_author)
        response = self.client.get(reverse('idea-review',kwargs={'slug': self.idea1.slug}))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'review.html')

    def test_review_update(self):
        self.client.force_login(user = self.challenge_author)
        idea = self.idea1
        criteria_list = idea.get_criterias
        formdata_list = []
        data = {'score' : 1 }
        for c in criteria_list:
            formdata_list.append(data)
        response = self.client.post(reverse('idea-review', kwargs={'slug': self.idea1.slug}),data=data)
        review = Review.objects.filter(idea=self.idea1).last()
        self.assertEqual(review.get_total.get('score__sum'), len(criteria_list))
        # self.assertTrue(review.exists())

    def test_review_new(self):
        self.client.force_login(user = self.challenge_author)
        idea = self.idea2
        criteria_list = idea.get_criterias
        formdata_list = []
        data = {'score' : 1 }
        for c in criteria_list:
            formdata_list.append(data)
        response = self.client.post(reverse('idea-review', kwargs={'slug': self.idea2.slug}),data=data)
        # review = Review.objects.filter(idea=self.idea2)
        self.assertTrue(Review.objects.filter(idea=self.idea2).exists())
    
    def test_idea_submit_draft(self):
        user = User.objects.create_user(
            username='username',
            password='secret'
        )
        self.client.force_login(user = user)
        data = {
            'title' : 'Submit Idea',
            'overview' : 'overview',
            'content' : 'content',
            'thumbnail' : ''
        }
        response = self.client.post(reverse('idea-submit', kwargs={'pk': self.challenge.pk }),data=data)
        self.assertEqual(Idea.objects.last().title, 'Submit Idea' )
        self.assertTrue(self.challenge.ideas.filter(title='Submit Idea').exists())

    def test_idea_submit_GET(self):
        user = User.objects.create_user(
            username='username',
            password='secret'
        )
        self.client.force_login(user = user)
        response = self.client.get(reverse('idea-submit', kwargs={'pk': self.challenge.pk }))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'idea_create.html')

    def test_idea_submit_posted(self):
        user = User.objects.create_user(
            username='username',
            password='secret'
        )
        self.client.force_login(user = user)
        data = {
            'title' : 'Submit Idea',
            'overview' : 'overview',
            'content' : 'content',
            'thumbnail' : '',
            'final' : ''
        }
        response = self.client.post(reverse('idea-submit', kwargs={'pk': self.challenge.pk }),data=data)
        self.assertFalse(Idea.objects.draft().filter(title = 'Submit Idea').exists())
        self.assertIsNotNone(Idea.objects.last().date_posted)

    def test_idea_create_final(self):
        self.client.force_login(user = self.idea1_author)
        data = {
            'title' : 'Create Idea',
            'overview' : 'overview',
            'content' : 'content',
            'thumbnail' : '',
            'final' : ''
        }
        response = self.client.post(reverse('idea-create') ,data=data)
        self.assertTrue(Idea.objects.last().title == 'Create Idea')
        self.assertFalse(Idea.objects.draft().filter(title = 'Create Idea').exists())
        self.assertIsNotNone(Idea.objects.last().date_posted)

    def test_idea_create_draft(self):
        self.client.force_login(user = self.idea1_author)
        data = {
            'title' : 'Create Draft',
            'overview' : 'overview',
            'content' : 'content',
            'thumbnail' : '',
        }
        response = self.client.post(reverse('idea-create'),data=data)
        self.assertTrue(Idea.objects.draft().filter(title = 'Create Draft').exists())
    
    def test_create_comment_not_loggedin(self):
        response = self.client.post(reverse('idea-detail',args=[1]) )
        redirect_url = "%s?next=%s" % (reverse('account_login'),reverse('idea-detail',args=[1]))
        self.assertRedirects(response,redirect_url, status_code=302)

    def test_create_comment(self):
        self.client.force_login(user = self.idea1_author)
        data = {
            'content' : 'new comment'
        }
        response = self.client.post(reverse('idea-detail',args=[self.idea1.pk]), data=data)
        self.assertEqual(self.idea1.comments.last().content,'new comment')

    def test_idea_update(self):
        self.client.force_login(user = self.idea1_author)
        idea = Idea.objects.create(
            title = 'Update Idea',
            overview = 'overview',
            content = 'update',
            author = self.idea1_author.profile
        )
        data = {
            'title' : 'Update Idea',
            'overview' : 'overview',
            'content' : 'updated',
            'thumbnail' : '',
            'final' : ''
        }
        response = self.client.post(reverse('idea-update', args=[idea.pk]) ,data=data)
        idea.refresh_from_db()
        self.assertEqual(idea.content , 'updated')
        self.assertIsNotNone(idea.date_posted)
        self.assertRedirects(response,reverse('idea-detail', args=[idea.pk]), status_code=302)
    
    def test_sort_popularity(self):
        response = self.client.get(reverse('idea-list'),{ 'sort' : 'popularity'})
        self.assertEqual(response.context['queryset'].object_list,list(Idea.objects.approved().order_by('-vote_count')))

    def test_sort_newest(self):
        response = self.client.get(reverse('idea-list'),{ 'sort' : 'newest'})
        self.assertEqual(response.context['queryset'].object_list,list(Idea.objects.approved().order_by('-date_posted')))

    def test_filter_tags(self):
        self.idea1.tags.add(self.tag)
        self.idea2.tags.add(self.tag)
        response = self.client.get(reverse('idea-list'),{ 'category' : [self.tag]})    
        self.assertEqual(Idea.objects.approved().filter(tags__title__in=[self.tag]).distinct().count(),2)  
        self.assertEqual(response.context['queryset'].object_list,list(Idea.objects.approved().filter(tags__title__in=[self.tag])))

    def test_search(self):
        response = self.client.get(reverse('search'),data={'q' : 'One'})
        self.assertEqual(response.context['queryset'].count(),1 )

    def tearDown(self):
        self.test_redis = redisRank('scoreboard')
        self.test_redis.deleteAll()