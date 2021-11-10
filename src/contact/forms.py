from django import forms
from .models import  Enquiry


class ContactUsForm(forms.ModelForm):
    class Meta:
        model = Enquiry
        fields =['name','email','phone','enquiry']