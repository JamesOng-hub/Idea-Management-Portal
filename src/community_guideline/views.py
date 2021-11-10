from django.shortcuts import render
from django.views.generic import ListView, DetailView

from community_guideline.models import Community_guide
# Create your views here.

class GuidelineList (ListView): 
    model = Community_guide 
    def get_queryset(self): 
        return Community_guide.objects.all()


class GuidelineDetail(DetailView): 
    model = Community_guide
