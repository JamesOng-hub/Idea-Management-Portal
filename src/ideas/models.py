import string
import random
from django.db import models
from django.db.models.aggregates import Sum
from django.utils import timezone
from django.urls import reverse
from tinymce.models import HTMLField
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.utils.text import slugify

User = get_user_model()
Q=models.Q

def rand_slug():
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(6))

# Create your models here.
class IdeaView(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    idea = models.ForeignKey('Idea', on_delete=models.CASCADE)

class Tag(models.Model):
    title = models.CharField(max_length=20)

    def __str__(self):
        return self.title

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date_posted = models.DateTimeField(default=timezone.now)
    content= models.TextField()
    idea = models.ForeignKey(
        'Idea', related_name='comments', on_delete=models.CASCADE
    )
    def __str__(self):
        return self.user.username

class Review(models.Model):
    reviewer = models.ForeignKey(User,related_name='user_reviews', on_delete= models.CASCADE)
    idea = models.ForeignKey('Idea',related_name='idea_reviews',on_delete=models.CASCADE)

    def __str__(self):
        return  self.idea.title +" review by "+ self.reviewer.username

    def get_absolute_url(self):
        return reverse('idea-review', kwargs={
            'slug': self.idea.slug
        })
        
    @property
    def get_total(self):
        return self.scores.aggregate(Sum('score'))


SCORE_CHOICE = [(i,str(i)) for i in range (0,11)]
class CriteriaScore(models.Model):
    review = models.ForeignKey(Review,null=True,related_name='scores', on_delete=models.CASCADE)
    criteria = models.ForeignKey('challenges.Criteria',on_delete=models.CASCADE)
    score = models.PositiveIntegerField(choices=SCORE_CHOICE)
    def __str__(self):
        return self.criteria.description

class IdeaManager(models.Manager):
    def draft(self):
        now = timezone.now()
        return self.get_queryset().filter(Q(date_posted__gt=now)|Q(date_posted__isnull=True))
    def approved(self):
        now = timezone.now()
        return self.get_queryset().filter(Q(date_posted__lte=now)&Q(approved=True))
    def unapproved(self):
        now = timezone.now()
        return self.get_queryset().filter(Q(date_posted__lte=now)&Q(approved=False))
    

class Idea(models.Model):
    title = models.CharField(max_length=100)
    approved = models.BooleanField(default=False)
    overview =models.CharField(max_length=255)
    content = HTMLField()
    date_posted = models.DateTimeField(auto_now=False, auto_now_add=False, null=True, blank=True)
    date_modified = models.DateTimeField(auto_now=True)
    date_created = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey('users.Profile', on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tag, related_name='tag_ideas', blank=True)
    challenge = models.ForeignKey('challenges.Challenge', on_delete=models.SET_NULL ,blank=True, null =True,related_name = 'ideas')
    votes = models.ManyToManyField(User,related_name = 'vote', default=None,blank=True)
    vote_count = models.IntegerField(default = 0, validators=[MinValueValidator(0)])
    comment_count = models.IntegerField(default = 0)
    thumbnail = models.ImageField(default='defaultbg.jpg',blank=True)
    slug = models.SlugField(max_length=255, unique=True, null=True)
    objects = IdeaManager()

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('idea-detail', kwargs={
            'pk': self.pk
        })
    
    def get_update_url(self):
        return reverse('idea-update', kwargs={
            'pk': self.pk
        })
    def get_delete_url(self):
        return reverse('idea-delete', kwargs={
            'pk': self.pk
        })
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(rand_slug() + "-" + self.title)
        super(Idea, self).save(*args, **kwargs)

    @property
    def get_comments(self):
        return self.comments.all().order_by('-date_posted') 
    @property
    def comment_count(self):
        return Comment.objects.filter(idea=self).count()
    @property
    def get_criterias(self):
        return self.challenge.criterias.all().order_by('pk')

    def approve(self):
        self.approved=True
        self.save()
        return 