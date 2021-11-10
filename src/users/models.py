from django.db import models
from django.contrib.auth import get_user_model
from PIL import Image
from django.core.validators import MinValueValidator
# Create your models here.
User = get_user_model()

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    occupation = models.CharField(max_length=255, blank=True)
    location =models.CharField(max_length=255, blank=True)
    image = models.ImageField(default= 'default.jpg', upload_to='profile_pics')
    bio = models.CharField(max_length=255, blank=True)
    score = models.IntegerField(default=0, validators=[MinValueValidator(0)])

    def __str__(self):
        return self.user.username


    #overwrite save method to scale images 
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        #resize
        img = Image.open(self.image.path)
        if img.height >300 or img.width >300:
            output_size =(300,300)
            img.thumbnail(output_size)
            img.save(self.image.path) #overwrite

    @property
    def get_subscriptions(self):
        return self.user.subscriptions.all()

    @property
    def get_challenges(self):
        return self.user.challenge_set.all()

    @property
    def get_challenges_draft(self):
        return self.user.challenge_set.draft()