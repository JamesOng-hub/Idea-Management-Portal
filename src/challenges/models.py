
from django.utils import timezone
from django.db import models
from django.urls import reverse
from ideas.models import Idea
from tinymce.models import HTMLField
from django.contrib.auth import get_user_model
User = get_user_model()
Q= models.Q
# Create your models here.

class Criteria(models.Model):
    description = models.CharField(max_length=100)
    def __str__(self):
        return self.description

class ChallengeManager(models.Manager):
    def posted(self):
        now = timezone.now()
        return self.get_queryset().filter(published_date__lte=now)
    def draft(self):
        now = timezone.now()
        return self.get_queryset().filter(Q(published_date__gt=now)|Q(published_date__isnull=True))

class Challenge(models.Model):
    class State(models.TextChoices):
        ACTIVE = 'ACTIVE'
        ENDED = 'ENDED'

    author = models.ForeignKey(User, null =True,on_delete=models.SET_NULL)
    title = models.CharField(db_index=True, max_length=255)
    description = HTMLField()
    published_date = models.DateTimeField(auto_now=False, auto_now_add=False, null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    idea_submission_deadline = models.DateField()
    tags = models.ManyToManyField(
        'ideas.Tag', related_name='tag_challenges', blank=True
    )
    idea_count = models.IntegerField(default =0)
    criterias = models.ManyToManyField(Criteria)
    thumbnail = models.ImageField(default='defaultbg.jpg',blank=True)
    subscribers = models.ManyToManyField(User,related_name = 'subscriptions', default=None,blank=True)
    subscribers_count = models.IntegerField(default =0)
    state = models.CharField(choices = State.choices, default = State.ACTIVE,max_length=6)
    objects = ChallengeManager()
    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('challenge-detail', kwargs={
            'pk': self.pk
        })  

    def is_active(self):
        return self.state == self.State.ACTIVE  

    @property
    def get_ideas(self):
        return self.ideas.all().order_by('-date_posted')

    @property
    def idea_count(self):
        return Idea.objects.approved().filter(challenge=self).count()


