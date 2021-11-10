from django.test import TestCase
from challenges.forms import ChallengeForm
from django.contrib.auth.models import User
from django.urls import reverse
from ideas.models import Tag
import datetime


class ChallengeFormTest(TestCase):

    def setUp(self):
        self.tag = Tag.objects.create(title="testtag")

    def test_challenge_form_description_label(self):
        form = ChallengeForm()
        self.assertTrue(form.fields['description'].label == None or form.fields['description'].label == 'description')

    def test_challenge_form_idea_submission_deadline_label(self):
        form = ChallengeForm()
        self.assertTrue(form.fields['idea_submission_deadline'].label == None or form.fields['idea_submission_deadline'].label == 'Idea Submission Deadline')

    def test_challenge_form_valid(self):
        tag = Tag.objects.get(title="testtag")
        form_data = {
            'title': 'test',
            'description': 'tsettest',
            'thumbnail': 'defaultbg.jpg',
            'idea_submission_deadline': datetime.date(2021, 12, 21),
            'tags': {tag}
        }
        form = ChallengeForm(data=form_data)
        response=self.client.post(reverse('challenge-create'), data=form_data)
        self.assertTrue(response.status_code, 200)
        self.assertTrue(form.is_valid())

    def test_tags_field_help_text(self):
        form = ChallengeForm()
        self.assertEqual(form.fields['tags'].help_text, 'Choose which topics your challenge belongs to')
        
    def test_description_field_help_text(self):
        form = ChallengeForm()
        self.assertEqual(form.fields['description'].help_text, 'Give a short description of your idea')
    
    def test_tags_field_widgets(self):
        form = ChallengeForm()
        self.assertEqual(form.fields['tags'].widget.__class__.__name__, 'CheckboxSelectMultiple')

    def test_description_field_widgets(self):
        form = ChallengeForm()
        self.assertEqual(form.fields['description'].widget.__class__.__name__, 'TinyMCEWidget')

    def test_idea_submission_deadline_field_widgets(self):
        form = ChallengeForm()
        self.assertEqual(form.fields['idea_submission_deadline'].widget.__class__.__name__, 'SelectDateWidget')

