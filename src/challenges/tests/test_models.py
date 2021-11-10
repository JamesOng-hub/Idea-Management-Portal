from datetime import timedelta
from django.contrib.auth.models import Permission
from django.utils import timezone
from django.test import TestCase
from django.urls import reverse
from challenges.models import Criteria, Challenge
from ideas.models import Idea
from users.models import User
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

content_type = ContentType.objects.get_for_model(Challenge)
permission = Permission.objects.get(content_type=content_type, codename='add_challenge')

class BaseModelTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super(BaseModelTestCase, cls).setUpClass()
        cls.author = User.objects.create_user(
            username='testuser',
            email='testemail@example.com',
            password='secret'
        )
        cls.idea1 = Idea.objects.create(
            author = cls.author.profile,
            title = "Idea One",
            date_posted = timezone.now()- timedelta(days = 1),
            approved = True
        )
        cls.idea2 = Idea.objects.create(
            author = cls.author.profile,
            title = "Idea Two",
            date_posted = timezone.now() 
        )
        cls.challenge = Challenge.objects.create(
            author=cls.author,
            title = "Challenge One",
            date_created = timezone.now(),
            idea_submission_deadline = (timezone.now()  + timedelta(days=1)).date(),
            state = Challenge.State.ACTIVE
        )
        cls.published = Challenge.objects.create(
            author=cls.author,
            title = "Challenge Two",
            date_created = timezone.now(),
            idea_submission_deadline = (timezone.now()  + timedelta(days=1)).date(),
            published_date = timezone.now()
        )
        cls.criteria1 = Criteria.objects.create(
            description = "criteria1description"
        )
        cls.criteria2 = Criteria.objects.create(
            description = "criteria2description"
        )
        cls.challenge.ideas.set([cls.idea1,cls.idea2])
        cls.author.user_permissions.add(permission)

class ChallengeModelTest(BaseModelTestCase):
    def test_author_label(self):
        field_label = self.challenge._meta.get_field('author').verbose_name
        self.assertEqual(field_label, 'author')

    def test_state_max_length(self):
        max_length = self.challenge._meta.get_field('state').max_length
        self.assertEqual(max_length, 6)

    def test_title_max_length(self):
        max_length = self.challenge._meta.get_field('title').max_length
        self.assertEqual(max_length, 255)

    def test_absolute_url(self):
        self.assertEqual(self.challenge.get_absolute_url(),  reverse('challenge-detail', kwargs={'pk': self.challenge.pk}))

    def test_is_active(self):
        # self.assertTrue(self.challenge.is_active)
        self.assertEqual(self.challenge.is_active(), self.challenge.state == Challenge.State.ACTIVE)
 
    #check we didnt forget to add m2m field, given a challenge we want to count 1..* criterias
    def test_challenge_has_criterias(self):
        self.challenge.criterias.set([self.criteria1, self.criteria2])
        self.assertEqual(self.challenge.criterias.count(), 2)

    def test_challenge_str(self):
        self.assertEqual(str(self.challenge), self.challenge.title)

    def test_criteria_str(self):
        self.assertEqual(str(self.criteria1), self.criteria1.description)

    def test_challenge_draft(self):
        self.assertTrue(self.challenge in Challenge.objects.draft().all())

    def test_challenge_posted(self):
        self.assertTrue(self.published in Challenge.objects.posted().all())
        
    def test_get_ideas(self):
        self.assertQuerysetEqual(self.challenge.get_ideas, self.challenge.ideas.all().order_by('-date_posted'),transform=lambda x:x)

    def test_idea_count(self):
        self.assertEqual(self.challenge.idea_count, 1)

