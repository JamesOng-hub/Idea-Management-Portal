
from django.db.models.signals import post_save, pre_delete #signal that fires after object is saved
from django.contrib.auth.models import User #the sender
from django.dispatch import receiver #a function that gets the signal and performs some tasks
from .models import Profile 
from .views import redisRank

#create profile for each new user
#when a user is saved, then send this signal, signal received by receiver(the create_profile function)
#args passed by signal to receiver
@receiver(post_save, sender=User)
def create_profile(sender,instance,created, **kwargs):
    #everytime a user is created
    if created:
        Profile.objects.create(user=instance)
#save profile whenever user object is saved
@receiver(post_save, sender=User)
def save_profile(sender,instance,**kwargs):
    instance.profile.save()

#after this import signals in apps.py

#add user in redis whenever user object is saved
@receiver(post_save, sender=User)
def scoreboard_createuser(sender,instance,created, **kwargs):
    #everytime a user is created
    if created:
        scoreboard = redisRank('scoreboard')
        score = instance.profile.score
        user = instance.username
        scoreboard.set_score(user, score)

@receiver(pre_delete, sender=User)
def scoreboard_deleteuser(sender,instance,**kwargs):
    scoreboard = redisRank('scoreboard')
    scoreboard.deleteUser(instance)
#after this import signals in apps.py
