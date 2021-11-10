"""ideas_portal URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf import settings
from django.urls import path, include
from django.conf.urls.static import static
from users import views as user_views
from users.views import uclsso
from ideas.views import (index, dashboard, idea_detail, idea_create, idea_update, idea_delete, review, search, vote, idea_submit)
from challenges.views import challenge_delete, challenge_update, challenges, subscribe, ChallengeDetailView, challenge_create
from contact import views as contact_views
from community_guideline import views as community_view

import django_cas_ng.views as cas_views
import allauth.account.views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index, name="index"),
    path('ideas/', dashboard, name='idea-list'),
    path('challenges/', challenges, name='challenge-list'),
    path('challenge/<pk>/',ChallengeDetailView.as_view(), name = 'challenge-detail'),
    path('challenge-create/',challenge_create, name = 'challenge-create'),
    path('challenge/<pk>/update/', challenge_update, name='challenge-update'),
    path('challenge/<pk>/delete/', challenge_delete, name='challenge-delete'),
    path('challenge/<pk>/create/',idea_submit, name = 'idea-submit'),
    path('idea/<pk>/', idea_detail, name = 'idea-detail'),
    path('idea/<slug:slug>/review', review, name = 'idea-review'),
    path('create/', idea_create, name = 'idea-create'),
    path('idea/<pk>/update/', idea_update, name='idea-update'),
    path('idea/<pk>/delete/', idea_delete, name='idea-delete'),
    path('profile/', user_views.profile,name='profile'),
    path('user/<str:username>', user_views.UserProfile.as_view(), name='user-profile'),
    path('search/', search, name='search'),
    path('tinymce/', include('tinymce.urls')),
    path('accounts/', include('allauth.urls')), #allauth views, including signup, login, logout, reset password
    path('vote/', vote, name='vote'),
    path('subscribe/', subscribe , name='subscribe'),
    path('leaderboard/', user_views.leaderboard, name='leaderboard'),
    path('callback/', uclsso, name='uclsso' ),
    path('contact/', contact_views.contact_us, name='contact-us'),
    path('community_guide/', community_view.GuidelineList.as_view(), name= 'guideline-list'),
    path('community_guide/<pk>/', community_view.GuidelineDetail.as_view(template_name  = 'community_guideline/community_guide_detail.html'), name= 'guideline-detail'),
    path('account/login', cas_views.LoginView.as_view(), name='cas_ng_login'),
    path('account/login', cas_views.LogoutView.as_view(), name='cas_ng_logout'),
    path('accounts/login/', auth_views.LoginView ,name='login'),
    
    #path('', include('loaderio.urls'))
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
