from django.test import TestCase
from users.models import Profile
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from challenges.models import Challenge, ChallengeManager
import datetime

class ProfileModelTest(TestCase):

    @classmethod
    def setUpTestData(self):
        # Set up non-modified objects used by all test methods
        self.user = User.objects.create_user(
            username='testuser', 
            email='testemail@example.com',
            password='secret'
        )
        self.challenge = Challenge.objects.create(
            author=self.user,
            title='testchallenge',
            description='testdescription',
            idea_submission_deadline=datetime.date(2021, 12, 1)
        )
        self.challenge2 = Challenge.objects.create(
            author=self.user,
            title='testchallenge222',
            description='testdescription22',
            published_date=None,
            idea_submission_deadline=datetime.date(2021, 12, 21),
        )
        self.challenge.subscribers.add(self.user)

    def test_user_label(self):
        profile = User.objects.last().profile
        field_label = profile._meta.get_field('user').verbose_name
        self.assertEqual(field_label, 'user')

    def test_occupation_max_length(self):
        profile = User.objects.last().profile
        max_length = profile._meta.get_field('occupation').max_length
        self.assertEqual(max_length, 255)

    def test_location_max_length(self):
        profile = User.objects.last().profile
        max_length = profile._meta.get_field('location').max_length
        self.assertEqual(max_length, 255)

    def test_bio_max_length(self):
        profile = User.objects.last().profile
        max_length = profile._meta.get_field('bio').max_length
        self.assertEqual(max_length, 255)

    def test_image_default(self):
        profile = User.objects.last().profile
        default = profile._meta.get_field('image').default
        self.assertEqual(default, 'default.jpg')

    def test_image_upload(self):
        profile = User.objects.last().profile
        upload_to = profile._meta.get_field('image').upload_to
        self.assertEqual(upload_to, 'profile_pics')

    def test_score_default(self):
        profile = User.objects.last().profile
        default = profile._meta.get_field('score').default
        self.assertEqual(default, 0)

    def test_score_validators(self):
        profile = User.objects.last().profile
        validators = profile._meta.get_field('score').validators
        self.assertEqual(validators, [MinValueValidator(0)])

    def test_profile_save(self):
        profile = User.objects.last().profile
        self.assertEqual(profile.bio, "") #bio initally is ""
        profile.bio = "testbio"
        profile = User.objects.last().profile
        self.assertEqual(profile.bio, "") #bio is still "" without save()
        profile.bio = "testbio"
        profile.save()
        profile = User.objects.last().profile
        self.assertEqual(profile.bio, "testbio") #bio updated to "testbio" after save()

    def get_subscriptions(self):
        user = User.objects.last()
        challenge = Challenge.objects.get(title='testchallenge')
        profile = user.profile
        
        self.assertEqual(profile.get_subscriptions, challenge)
    
    def get_challenges(self):
        user = User.objects.last()
        challenges = []
        challenges.append(Challenge.objects.get(title='testchallenge'))
        challenges.append(Challenge.objects.get(title='testchallenge2'))

        profile = user.profile
        self.assertEqual(profile.get_subscriptions, challenges)

    def get_challenges_draft(self):
        user = User.objects.last()
        profile = user.profile
        challenge = Challenge.objects.get(title='testchallenge2')
        self.assertEqual(profile.get_subscriptions, challenge)