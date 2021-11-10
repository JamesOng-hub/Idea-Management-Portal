from typing import Set
from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django.utils import timezone
from .models import Profile
from ideas.models import CriteriaScore, Tag, Idea, Comment,Review
from challenges.models import Challenge,Criteria
from django.utils import timezone
# Register your models here.

admin.site.register(Profile)
admin.site.register(Tag)
admin.site.register(Comment)
admin.site.register(Challenge)
admin.site.register(Criteria)
admin.site.register(Review)
admin.site.register(CriteriaScore)

@admin.register(Idea)
class IdeaAdmin(admin.ModelAdmin):
    def get_queryset(self,request):
        now = timezone.now()
        qs = super(IdeaAdmin, self).get_queryset(request).filter(date_posted__lte=now)
        return qs
    
    list_display = ('title', 'approved')
