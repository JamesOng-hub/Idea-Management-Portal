from django.core.exceptions import PermissionDenied
from challenges.models import Challenge
from ideas.models import Idea

def is_challenge_creator(function):
    def wrap(request, *args, **kwargs):
        challenge = Challenge.objects.get(pk = kwargs['pk'])
        if challenge.author == request.user:
            return function(request, *args, **kwargs)
        else:
            raise PermissionDenied
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap

def is_idea_creator(function):
    def wrap(request, *args, **kwargs):
        idea = Idea.objects.get(pk = kwargs['pk'])
        if idea.author == request.user.profile:
            return function(request, *args, **kwargs)
        else:
            raise PermissionDenied
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap