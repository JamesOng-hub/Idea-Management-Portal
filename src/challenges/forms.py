from django import forms
from django.forms.widgets import SelectDateWidget
from tinymce.widgets import TinyMCE
from .models import Challenge
from django.utils.translation import gettext_lazy as _

class TinyMCEWidget(TinyMCE):
    def use_required_attribute(self, *args):
        return False

class ChallengeForm(forms.ModelForm):
    description = forms.CharField(
        widget=TinyMCEWidget(
            attrs={'cols': 30, 'rows': 10}
        ),
        help_text='Give a short description of your idea'
    )
    idea_submission_deadline = forms.DateField(widget=SelectDateWidget(
        attrs ={'style': 'display: inline-block; width: auto;'}
    ) , label='Idea Submission Deadline') 
    class Meta:
        model = Challenge
        fields = ('title', 'description', 'thumbnail', 'idea_submission_deadline','tags')
        help_texts = {
            'tags': _('Choose which topics your challenge belongs to'),
        }
        widgets ={
            'tags': forms.CheckboxSelectMultiple,
        }
    