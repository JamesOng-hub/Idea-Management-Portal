from django import forms
from crispy_forms.helper import FormHelper
from tinymce.widgets import TinyMCE
from .models import Idea, Comment, CriteriaScore
from django.utils.translation import gettext_lazy as _



class TinyMCEWidget(TinyMCE):
    def use_required_attribute(self, *args):
        return False

SCORE_CHOICE = [(i,str(i)) for i in range (0,11)]
class CriteriaScoreForm(forms.ModelForm):
    class Meta:
        model = CriteriaScore
        fields = ('score',)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class ='form-horizontal'
        self.helper.label_class = 'col-lg-5'
        self.helper.field_class = 'col-lg-4'
        self.helper.form_tag = False


class IdeaForm(forms.ModelForm):
    content = forms.CharField(
        widget=TinyMCEWidget(
            attrs={'required': False, 'cols': 30, 'rows': 10}
        )
    )
    class Meta:
        model = Idea
        fields = ('title', 'overview', 'content', 'thumbnail', 
        'tags')
        help_texts = {
            'tags': _('Choose which topics your idea belongs to'),
            'overview':_('Give a short description of your idea'),
        }
        widgets ={
            'tags': forms.CheckboxSelectMultiple
        }

class CommentForm(forms.ModelForm):
    content = forms.CharField(widget=forms.Textarea(attrs={
        'class': 'form-control',
        'placeholder': 'Type your comment',
        'id': 'usercomment',
        'rows': '4'
    }))
    class Meta:
        model = Comment
        fields = ('content', )