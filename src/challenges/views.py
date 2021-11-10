from django.contrib.auth.decorators import login_required ,permission_required
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db import models
from django.http.response import JsonResponse
from django.shortcuts import get_object_or_404, render,redirect,reverse
from django.db.models import Count, Q
from django.utils import timezone
from ideas_portal.decorators import is_challenge_creator
from users.models import Profile
from .models import Challenge, Criteria
from .forms import ChallengeForm
from django.views.generic import DetailView
# Create your views here.

    
def get_category_count():
    queryset = Challenge .objects .values('tags__title').exclude(tags__title__isnull=True) .annotate(Count('tags__title'))
    return queryset

def is_valid_queryparam(param):
    return param != '' and param is not None and param

def get_criterias():
    return Criteria.objects.all()

def challenges(request):
    category_count = get_category_count()
    challenge_list = Challenge.objects.posted().all().order_by('-published_date')
    categories = request.GET.getlist('category')
    sort = request.GET.get('sort')
    status = request.GET.getlist('status')

    if is_valid_queryparam(sort):
        if sort == "popularity":
            challenge_list= challenge_list.annotate(icount=Count('ideas',filter=models.Q(ideas__approved=True))).order_by('-icount')
        elif sort == "newest":
            challenge_list=challenge_list.order_by('-published_date')
    else:
        sort = "newest"
        
    if is_valid_queryparam(categories):
        challenge_list = challenge_list.filter(tags__title__in=categories).distinct()

    if is_valid_queryparam(status):
        if len(status)==1:
            if status[0] == 'active':
                challenge_list = challenge_list.filter(state=Challenge.State.ACTIVE)
                
            else:
                challenge_list = challenge_list.filter(state=Challenge.State.ENDED)
                
    
    paginator=Paginator(challenge_list,9)
    page_req_var = 'page'
    page = request.GET.get(page_req_var)
    
    try:
        paginated_queryset = paginator.page(page)
    except PageNotAnInteger:
        paginated_queryset = paginator.page(1)
    except EmptyPage:
        #return last page
        paginated_queryset = paginator.page(paginator.num_pages)

    context = {
        'challenges_count' : challenge_list.count(),
        'queryset': paginated_queryset,
        'page_request_var' : page_req_var,
        'category_count' : category_count,
        'categories' : categories,
        'sort' : sort,
        'status' : status
    }
    return render(request,'challenges.html',context)

class ChallengeDetailView(DetailView):
    model = Challenge
    template_name = 'challenge_detail.html'
    context_object_name = 'challenge'
    def get_context_data(self, **kwargs):
        challenge = super().get_object()
        idea_list = challenge.ideas.all().filter(Q(approved=True))
        
        # try:
        if challenge.subscribers.filter(id=self.request.user.id).exists():
            subscribed =True
        else:
            subscribed =False
        # except:
        #     pass
       
        context = super().get_context_data(**kwargs)
        context['page_request_var'] = "page"
        context['subscribed'] = subscribed
        context['idea_list'] = idea_list
        context['next_url'] = reverse("challenge-detail", kwargs={
                'pk': challenge.pk
            })
        return context

img1 = 'gallery-1.jpg'
img2 = 'gallery-2.jpg'
img3 = 'gallery-3.jpg'
img4 = 'gallery-4.jpg'
image_bank = [img1,img2,img3,img4]
@ login_required
@ permission_required('challenges.add_challenge',raise_exception=True)
def challenge_create(request):
    title = 'Create'
    criterias = get_criterias()

    form = ChallengeForm(request.POST or None, request.FILES or None)
    print(form.data)
    if request.method == "POST":
        if form.is_valid():
            form.instance.author = request.user
            image = request.POST.get('image-picker')
            fcriterias = request.POST.getlist('criteria')

            form.save()
            if image:
                form.instance.thumbnail = image
            if 'final' in request.POST:
                form.instance.published_date = timezone.now()
            
            for criteria in fcriterias:
                if Criteria.objects.filter(description=criteria).exists():
                    object= get_object_or_404(Criteria, description=criteria)
                    form.instance.criterias.add(object)
                elif criteria:
                    form.instance.criterias.create(description=criteria)
            form.instance.save()

            return redirect(reverse("challenge-detail", kwargs={
                'pk': form.instance.pk
            }))
            

    context = {
        'title': title,
        'form': form,
        'image_bank' : image_bank,
        'criterias' : criterias
    }
    return render(request, "challenge_create.html", context)

@ login_required
@ is_challenge_creator
def challenge_update(request, pk):
    title = 'Update'
    challenge = get_object_or_404(Challenge, pk = pk)
    form = ChallengeForm(request.POST or None, request.FILES or None, instance=challenge)
    posted = challenge.published_date
    set_criterias = challenge.criterias.all()
    fcriterias = request.POST.getlist('criteria')
    image = request.POST.get('image-picker')

    if request.method == "POST":
        if form.is_valid():
            if image:
                form.instance.thumbnail = image
            if 'final' in request.POST:
                form.instance.published_date = timezone.now()
            form.save()
            for c in set_criterias:
                if c not in fcriterias:
                    form.instance.criterias.remove(c)
                else:
                    fcriterias.remove(c)
            for criteria in fcriterias:
                if Criteria.objects.filter(description=criteria).exists():
                    object= get_object_or_404(Criteria, description=criteria)
                    form.instance.criterias.add(object)
                elif criteria:
                    form.instance.criterias.create(description=criteria)
            form.instance.save()

            return redirect(reverse("challenge-detail", kwargs={
                'pk': form.instance.id
            })) 
    context = {
    'title': title,
    'form': form,
    'posted' : posted,
    'set_criterias' : set_criterias,
    'image_bank' : image_bank,
    }
    return render(request, "challenge_create.html", context)

@ login_required
@ is_challenge_creator
def challenge_delete(request, pk):
    challenge = get_object_or_404(Challenge, pk=pk)
    challenge.delete()
    return redirect(reverse("challenge-list"))


@ login_required
def subscribe(request):
    if request.POST.get('action') == 'post':
        result = ''
        challengeid = request.POST.get('challengeid') 
        id = int(request.POST.get('challengeid'))
        challenge = get_object_or_404(Challenge, id=id)

        if challenge.subscribers.filter(id=request.user.id).exists():
            challenge.subscribers.remove(request.user)
            challenge.subscribers_count -= 1
            subscribed=False
            result = challenge.subscribers_count
            challenge.save()
        else:
            challenge.subscribers.add(request.user)
            challenge.subscribers_count += 1
            subscribed=True
            result = challenge.subscribers_count
            challenge.save()

        return JsonResponse({'result': result,'subscribed' : subscribed, 'challengeid' : challengeid})
