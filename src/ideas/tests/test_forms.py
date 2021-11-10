from django.test import TestCase
from ideas.forms import CriteriaScoreForm, IdeaForm, CommentForm
from ideas.models import Tag

class IdeaFormTest(TestCase):
    def setUp(self):
        self.tag = Tag.objects.create(title="testtag")

    def test_idea_form_content_label(self):
        form = IdeaForm()
        self.assertTrue(form.fields['content'].label == None or form.fields['content'].label == 'content')

    def test_content_field_widgets(self):
        form = IdeaForm()
        self.assertEqual(form.fields['content'].widget.__class__.__name__, 'TinyMCEWidget')

    def test_idea_form_valid(self):
        tag = Tag.objects.get(title="testtag")
        form_data = {
            'title': 'test',
            'overview': 'tsettest',
            'content': 'testtesttest',
            'thumbnail': 'defaultbg.jpg',
            'tags': {tag}
        }
        form = IdeaForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_tags_field_help_text(self):
        form = IdeaForm()
        self.assertEqual(form.fields['tags'].help_text, 'Choose which topics your idea belongs to')

    def test_overview_field_help_text(self):
        form = IdeaForm()
        self.assertEqual(form.fields['overview'].help_text, 'Give a short description of your idea')


    def test_content_field_widgets(self):
        form = IdeaForm()
        self.assertEqual(form.fields['tags'].widget.__class__.__name__, 'CheckboxSelectMultiple')

class CriteriaScoreFormTest(TestCase):

    def test_Criteria_Score_form_valid(self):
        form_data = {
            'score': 10,
        }
        form = CriteriaScoreForm(data=form_data)
        self.assertTrue(form.is_valid())

class CommentFormTest(TestCase):

    def test_comment_form_content_label(self):
        form = CommentForm()
        self.assertTrue(form.fields['content'].label == None or form.fields['content'].label == 'content')

    def test_content_field_widgets(self):
        form = CommentForm()
        self.assertEqual(form.fields['content'].widget.__class__.__name__, 'Textarea')

    def test_Comment_form_valid(self):
        form_data = {
            'content': 'testtest',
        }
        form = CommentForm(data=form_data)
        self.assertTrue(form.is_valid())
