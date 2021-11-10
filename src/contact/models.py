from django.db import models
from django.urls import reverse

# Create your models here.
class Enquiry(models.Model): 
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=255)
    enquiry = models.TextField()

    def get_absolute_url(self):
        return reverse("enquiry_complete")
        
    def __str__(self):
        return self.enquiry