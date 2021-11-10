from django.db.models import Count, Q
from django.http.response import JsonResponse
from django.shortcuts import render, get_object_or_404,redirect, reverse
from django.utils import timezone
from ideas_portal import settings
from challenges.models import Challenge
from ideas_portal.decorators import is_idea_creator
from .models import Idea, IdeaView, Review
from users.models import Profile
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .forms import CommentForm, CriteriaScoreForm,IdeaForm
from django.contrib.auth.decorators import login_required

from ideas_portal.settings import leaderBoard
import traceback

from .signals import signal_comment, signal_idea, signal_vote

# Create your views here.
def get_author(user):
    qs = Profile.objects.filter(user=user)
    if qs.exists():
        return qs[0]
    return None

def search(request):
    queryset= Idea.objects.approved()
    query=request.GET.get('q')
    if query:
        queryset = queryset.filter(
            Q(title__icontains=query) | Q(overview__icontains=query)
        ).distinct()
    context = {
        'queryset' : queryset
    }
    return render(request, 'search_results.html', context)

def get_category_count():
    queryset = Idea .objects .approved().values('tags__title') .exclude(tags__title__isnull=True) .annotate(Count('tags__title'))
    return queryset
    
def index(request):
    return render(request,'index.html')

def is_valid_queryparam(param):
    return param != '' and param is not None and param

def dashboard(request):
    category_count = get_category_count()
    idea_list = Idea.objects.approved().all().order_by('-vote_count')
    latest = idea_list.order_by('-date_posted')[:3]
    categories = request.GET.getlist('category')
    sort = request.GET.get('sort')

    if is_valid_queryparam(sort):
        if sort == "popularity":
            idea_list=Idea.objects.approved().order_by('-vote_count')
            
        elif sort == "newest":
            idea_list=idea_list.order_by('-date_posted')
    else:
        sort = "popularity"

    if is_valid_queryparam(categories):
        idea_list=idea_list.filter(tags__title__in=categories).distinct()

    paginator=Paginator(idea_list, 6)
    page_req_var = 'page'
    page = request.GET.get(page_req_var)
    
    try:
        paginated_queryset = paginator.page(page)
    except PageNotAnInteger:
        paginated_queryset = paginator.page(1)
    except EmptyPage:
        #return last page
        paginated_queryset = paginator.page(paginator.num_pages)

    context ={
        'idea_count': idea_list.__len__,
        'queryset': paginated_queryset,
        'page_request_var' : page_req_var,
        'latest' : latest,
        'category_count' : category_count,
        'categories' : categories,
        'sort' : sort
        
    }
    return render(request,'ideas.html',context)

def idea_detail(request, pk):
    category_count = get_category_count()
    latest = Idea.objects.approved().order_by('-date_posted')[:3]
    idea= get_object_or_404(Idea, pk=pk)
    next_idea = None
    prev_idea = None
    challenge = idea.challenge
    reviews = Review.objects.filter(idea=idea)
    if reviews:
        total = sum(review.get_total.get('score__sum') for review in reviews)
    else:
        total=0 

    if idea.date_posted:
        next_idea = Idea.objects.approved().filter( id__gt=idea.pk, date_posted__gte = idea.date_posted).order_by('pk','-date_posted').first()
        prev_idea = Idea.objects.approved().filter( id__lt=idea.pk, date_posted__lte = idea.date_posted).order_by('-date_posted','pk').first()

    if idea.votes.filter(id=request.user.id).exists():
        voted=True
    else:
        voted=False

    if request.user.is_authenticated:
        IdeaView.objects.get_or_create(user=request.user, idea=idea)

    if request.GET.get('approve'):
        idea.approve()
    elif request.GET.get('unapprove'):
        idea.approved = False
        idea.save()

    form = CommentForm(request.POST or None)
    if request.method =="POST":
        if not request.user.is_authenticated:
            return redirect('%s?next=%s' % (reverse(settings.LOGIN_URL), request.path))

        if form.is_valid():
            form.instance.user = request.user
            form.instance.idea = idea
            changeScore(request, 'add', request.user.profile)
            form.save()
            signal_comment.send(sender="CommentForm", instance=form) #send notification for comments

            return redirect(reverse("idea-detail", kwargs={
                'pk': idea.pk
            }))
    context = {
        'idea' :idea,
        'latest' : latest,
        'category_count': category_count,
        'next_idea' : next_idea,
        'prev_idea' : prev_idea,
        'form' : form,
        'voted' : voted,
        'challenge' : challenge,
        'score' : total
    }
    return render(request,'idea.html',context)

@ login_required
def idea_create(request):
    title = 'Create'
    form = IdeaForm(request.POST or None, request.FILES or None)
    author = get_author(request.user)

    if request.method == "POST":
        if form.is_valid():
            form.instance.author = author
            if 'final' in request.POST:
                form.instance.date_posted = timezone.now()
            form.save()
            changeScore(request, 'add', request.user.profile)
            return redirect(reverse("idea-detail", kwargs={
                'pk': form.instance.pk
            }))
    context = {
        'title': title,
        'form': form
    }
    return render(request, "idea_create.html", context)

@login_required
@is_idea_creator
def idea_update(request, pk):
    title = 'Update'
    idea = get_object_or_404(Idea, pk=pk)
    form = IdeaForm(
        request.POST or None, 
        request.FILES or None, 
        instance=idea)
    posted = idea.date_posted
    if request.method == "POST":
        if form.is_valid():
            if 'final' in request.POST:
                form.instance.date_posted = timezone.now()
            form.save()
            return redirect(reverse("idea-detail", kwargs={
                'pk': form.instance.id
            }))
    context = {
        'title': title,
        'form': form,
        'posted' : posted
    }
    return render(request, "idea_create.html", context)

@login_required
@is_idea_creator
def idea_delete(request, pk):
    idea = get_object_or_404(Idea, pk=pk)
    idea.delete()
    changeScore(request, 'minus', request.user.profile)
    return redirect(reverse("idea-list"))

@ login_required
def vote(request):
    if request.POST.get('action') == 'post':
        result = ''
        ideaid = request.POST.get('ideaid') 
        id = int(request.POST.get('ideaid'))
        idea = get_object_or_404(Idea, id=id)
        if idea.votes.filter(id=request.user.id).exists():
            idea.votes.remove(request.user)
            if(idea.vote_count >= 1):
                idea.vote_count -= 1
            else:
                idea.vote_count = 0
            voted=False
            result = idea.vote_count
            changeScore(request, 'minus', request.user.profile) #minus 1 point to user
            changeScore(request, 'minus', idea.author) #minus 1 point to author
            idea.save()
        else:
            idea.votes.add(request.user)
            idea.vote_count += 1
            voted=True
            changeScore(request, 'add', request.user.profile) #add 1 point to user
            changeScore(request, 'add', idea.author) #add 1 point to author
            result = idea.vote_count
            idea.save()
            signal_vote.send(sender="Idea", instance=idea, voter=request.user)#send notification for votes

        return JsonResponse({'result': result,'voted' : voted, 'ideaid' : ideaid})

def idea_submit(request, pk):
    challenge = get_object_or_404(Challenge, pk=pk)
    title = 'Create'
    form = IdeaForm(request.POST or None, 
    request.FILES or None, initial={'challenge': challenge})
    author = get_author(request.user)
    if request.method == "POST":
        if form.is_valid():
            form.instance.author = author
            form.instance.challenge = challenge
            if 'final' in request.POST:
                form.instance.date_posted = timezone.now()
            form.save()
            changeScore(request, 'add', request.user.profile)
            signal_idea.send(sender="IdeaForm", instance=form) # send notification for ideas

            return redirect(reverse("idea-detail", kwargs={
                'pk': form.instance.pk
            }))
    context = {
        'title': title,
        'form': form
    }
    return render(request, "idea_create.html", context)

def changeScore(request, operation, profile):
    try:
        if(operation == 'add'):
            profile.score += 1
            if(profile.score < 0):
                profile.score = 1
        elif(operation == 'minus' and profile.score >= 1):
            profile.score -= 1
        elif(operation == 'minus' and profile.score <= 0):
            profile.score = 0
        else:
            raise ValueError("Only 'add' or 'minus' are allowed")
    except:
        traceback.print_exc()
    profile.save()
    leaderBoard.zadd('scoreboard', {profile.user.username : profile.score})
    
@login_required
def review(request, slug):
    idea = get_object_or_404(Idea, slug=slug)
    user = request.user
    review= Review(idea=idea,reviewer = user)
    criteria_list = idea.get_criterias
    form_list = []
    if user.user_reviews.filter(idea=idea).exists():
        review = get_object_or_404(Review,reviewer=user,idea=idea)

    for criteria in criteria_list:
        if review:
            f = CriteriaScoreForm(request.POST or None,initial={'criteria': criteria,}, instance=review.scores.filter(criteria=criteria).first())
        else:
            f = CriteriaScoreForm(request.POST or None,initial={'criteria': criteria,})
        f.fields['score'].label = criteria
        form_list.append(f)

    if request.method == "POST":
        if all(form.is_valid for form in form_list):
            review.save()
            for form in form_list:
                form.save(commit=False)
                form.instance.criteria = form.fields['score'].label 
                form.instance.review = review
                form.save()
            return redirect(reverse("idea-detail", kwargs={
                'pk': idea.pk
            }))
        
    context = {
        'form_list': form_list,
        'idea': idea
    }
    return render(request, "review.html", context)
