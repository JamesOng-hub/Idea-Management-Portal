from django.db import models
from django.urls import reverse
from tinymce.models import HTMLField
# Create your models here.
class Community_guide(models.Model): 
    # admin can edit. 
    title= models.CharField(max_length=255)
    overview = models.TextField()
    content = HTMLField()

    def __str__(self) :
        return self.title

    def get_absolute_url(self):
        return reverse('guideline-detail', kwargs={
            'pk': self.pk
        })