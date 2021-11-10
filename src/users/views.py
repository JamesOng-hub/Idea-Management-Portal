from django.contrib.auth.models import User
from django.dispatch import receiver
from allauth.account.signals import user_signed_up
from django.shortcuts import get_object_or_404, render,redirect
from django.contrib import messages 
from django.contrib.auth.decorators import login_required
from challenges.models import Challenge
from ideas.models import Idea

from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.contrib.auth import login

from django.core.mail import EmailMessage
from django.urls import reverse
from users.models import Profile
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm

from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string

from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib.auth.middleware import MiddlewareMixin

from django.core.mail import EmailMessage
from django.urls import reverse

from django.views.generic import ListView
import ideas

from ideas_portal.settings import leaderBoard, ucl_client_secret
from django_redis import get_redis_connection

from django.http import HttpResponseRedirect, HttpResponseForbidden

import requests
from django.contrib import auth




def leaderboard(request):    
    scoreboard = redisRank('scoreboard')
    # # rewrite redis database, but would let user logout
    # scoreboard.tearDown()
    # scoreboard.addAll()
    length = scoreboard.get_rank_len()
    rank = scoreboard.get_rank(1, 9)
    user_name = request.user.username
    user_rank = scoreboard.get_user_rank(user_name)
    user_score = scoreboard.get_score(user_name)
    if user_rank < 10:
        user_is_not_top = False
    else:
        user_is_not_top = True

    context ={
        'length' : length,
        'toplist': rank,
        'user_rank' : user_rank,
        'user_score' : user_score,
        'user_name' : user_name,
        'user_is_not_top' : user_is_not_top
    }
    
    return render(request,'leaderboard.html',context)


class redisRank:
    def __init__(self, name):
        self.name = name

    def get_rank(self, start, end):
        # get rank from start to end with user and score
        return leaderBoard.zrevrange(self.name, start-1, end-1, withscores=1)

    def set_score(self, user, score) -> None:
        # add or update user score
        mapping = {user: score}
        leaderBoard.zadd(self.name, mapping)

    # def set_many_score(self, mapping: dict):
    #     # add or update many user score
    #     leaderBoard.zadd(self.name, mapping)

    def get_score(self, user) -> int:
        # get user score
        user_score = leaderBoard.zscore(self.name, user)
        if user_score is None:
            return -1
        else:
            return user_score

    def get_user_rank(self, user) -> int:
        # get user rank (inverted order)
        user_rank = leaderBoard.zrevrank(self.name, user)
        if user_rank is None:
            return -1
        else:
            # zervrank starts at 0
            return user_rank + 1

    def get_rank_len(self):
        # get num of elements in leaderboard
        return leaderBoard.zcard(self.name)

    def tearDown(self):
        # clean all data in redis
        # can run addAll() to recover all data
        get_redis_connection("default").flushall()

    def addAll(self):
        # add all data in redis
        user_list = User.objects.all()
        for user in user_list:
            score = user.profile.score
            user = user.username
            mapping = {user: score}
            leaderBoard.zadd(self.name, mapping)

    def deleteAll(self):
        user_list = User.objects.all()
        for user in user_list:
            leaderBoard.zrem(self.name, user.username)

    def deleteUser(self, instance):
        username=instance.username
        leaderBoard.zrem( self.name , username)
            

@login_required
def profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)

        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            #to return a success message feedback
            messages.success(request, f"Your account has been updated!")
            return HttpResponseRedirect('/profile')
            #after this update html to show the message
        
    else:
        #arg to link form to database n to display prev data in form
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'u_form' : u_form,
        'p_form' : p_form
    }
    return render(request,'users/profile.html', context)

class UserProfile(ListView):
    model: Idea
    template_name='users/user_profile.html'
    context_object_name='ideas'
    paginate_by = 3

    def get_queryset(self):
        user_obj= get_object_or_404(User, username=self.kwargs.get('username'))
        return Idea.objects.approved().filter(author =user_obj.profile).order_by('-date_posted')
        
    def get_context_data(self, **kwargs):
        user_obj= get_object_or_404(User, username=self.kwargs.get('username'))
        drafts = Idea.objects.draft().filter(author =user_obj.profile)
        challenge_drafts = Challenge.objects.draft().filter(author = user_obj)
        unapproved = Idea.objects.unapproved().filter(challenge__author = user_obj)

        context = super().get_context_data(**kwargs)
        context['user_obj'] = user_obj.profile
        context['drafts'] = drafts
        context['challenge_drafts'] = challenge_drafts
        context['unapproved'] = unapproved

        return context
   
def uclsso(request):

    info = receive_callback(request)
    
    try:
        #department = info.get("department")
        email = info.get("email")
        full_name = info.get("full_name")
        #cn = info.get("cn") #UCL username
        #given_name = info.get("given_name")
        #upi = info.get("upi")
        is_student = info.get("is_student")
    except:
        print("info error!")
        return HttpResponseRedirect('/accounts/login')
    

    if full_name == None or email == None: #if full_name is null, just goes back to login page
        print("sso fail, full_name is null")
        return HttpResponseRedirect('/accounts/login')

    full_name = full_name.replace(" ","")

    # get user object if created
    try:
        user = User.objects.get(username=full_name)    
    except User.DoesNotExist: #create new user if not exist
        user = User(username=full_name)
        user.email = email
        user.email_confirmed = True
        user.is_staff = False
        user.is_active = True
        user.is_valid = True
        user.save()

    #login user  
    try:
        AutomaticUserLoginMiddleware.process_view(user, request)
    except:
        print("sso login error")
        return HttpResponseRedirect('/accounts/login')

    return HttpResponseRedirect('/')

class AutomaticUserLoginMiddleware(MiddlewareMixin):

    def process_view(user, request, backend='allauth.account.auth_backends.AuthenticationBackend'):
        if not AutomaticUserLoginMiddleware._is_user_authenticated(user):
            user = auth.authenticate(user)
            if user is None:
                return HttpResponseForbidden()

        request.user = user
        auth.login(request, user, backend)
        messages.success(request, f"Login successfully!")

    @staticmethod
    def _is_user_authenticated(user):
        return user.is_authenticated


def receive_callback(request):
    client_secret = ucl_client_secret

    try:
        result = request.GET.get('result')
        code = request.GET.get('code')
        state = request.GET.get('state')
    except:
        print("get request error!")
        return HttpResponseRedirect('/accounts/login')

    params1 = {
        "client_id": "0761046984609257.7533240572162003",
        "code": code,
        "client_secret": client_secret,
    }
    r1 = requests.get("https://uclapi.com/oauth/token", params=params1)
    data = r1.json()
    print(data)
    token = data.get("token")

    params2 = {
        "token": token,
        "client_secret": client_secret,
    }
    r2 = requests.get("https://uclapi.com/oauth/user/data", params=params2)
    info = r2.json()
    print(info)

    return info
