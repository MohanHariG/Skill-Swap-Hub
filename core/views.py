from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseBadRequest
from django.db.models import Q

from .forms import RegisterForm, ProfileForm, SkillPostForm, SkillForm
from .models import Skill, SkillPost, MatchRequest, Session

def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Welcome! Profile created with 5 credits.")
            return redirect('feed')
    else:
        form = RegisterForm()
    return render(request, 'auth/register.html', {'form': form})

def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('feed')
    else:
        form = AuthenticationForm()
    return render(request, 'auth/login.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def feed(request):
    q = request.GET.get('q', '').strip()
    kind = request.GET.get('kind', '').strip()

    # Start with all posts except your own
    posts = SkillPost.objects.exclude(user=request.user).order_by('-created_at')

    # Apply search filter (skill name, description, or category)
    if q:
        posts = posts.filter(
            Q(skill__name__icontains=q) |
            Q(description__icontains=q) |
            Q(skill__category__icontains=q)
        )

    # Apply kind filter
    if kind in ('OFFER', 'REQUEST'):
        posts = posts.filter(kind=kind)

    skills = Skill.objects.all().order_by('name')

    return render(request, 'feed.html', {'posts': posts, 'skills': skills, 'q': q, 'kind': kind})


@login_required
def post_create_view(request):
    if request.method == 'POST':
        if 'add_skill' in request.POST:
            sform = SkillForm(request.POST)
            if sform.is_valid():
                sform.save()
                messages.success(request, "Skill added.")
            return render(request, 'post_form.html', {'form': SkillPostForm(), 'skill_form': SkillForm()})
        form = SkillPostForm(request.POST)
        if form.is_valid():
            form.save(user=request.user)
            messages.success(request, "Post published!")
            return redirect('feed')
    else:
        form = SkillPostForm()
    return render(request, 'post_form.html', {'form': form, 'skill_form': SkillForm()})

@login_required
def profile_view(request):
    if request.method == 'POST':
        pform = ProfileForm(request.POST, instance=request.user.profile)
        if pform.is_valid():
            pform.save()
            messages.success(request, "Profile updated.")
            return redirect('profile')
    else:
        pform = ProfileForm(instance=request.user.profile)
    my_posts = SkillPost.objects.filter(user=request.user)
    return render(request, 'profile.html', {'pform': pform, 'my_posts': my_posts})

@login_required
def send_match_request(request, post_id):
    post = get_object_or_404(SkillPost, pk=post_id)
    
    if post.user == request.user:
        messages.error(request, "You can't connect to your own post.")
        return redirect('feed')

    mr, created = MatchRequest.objects.get_or_create(
        from_user=request.user, to_user=post.user, post=post, skill=post.skill
    )

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        # If AJAX request, return JSON
        if created:
            return JsonResponse({'ok': True, 'status': 'PENDING'})
        else:
            return JsonResponse({'ok': True, 'status': mr.status})
    else:
        # Normal form submission
        if created:
            messages.success(request, "Match request sent! Status: PENDING")
        else:
            messages.info(request, f"Request already {mr.status}")
        return redirect('feed')


@login_required
def matches_view(request):
    incoming = MatchRequest.objects.filter(to_user=request.user, status='PENDING')
    outgoing = MatchRequest.objects.filter(from_user=request.user).exclude(status='REJECTED')
    return render(request, 'matches.html', {'incoming': incoming, 'outgoing': outgoing})

@login_required
def accept_match(request, pk):
    if request.method != 'POST':
        return HttpResponseBadRequest("POST only")
    mr = get_object_or_404(MatchRequest, pk=pk, to_user=request.user, status='PENDING')

    if mr.post.kind == 'OFFER':
        teacher = mr.post.user
        learner = mr.from_user
    else:
        teacher = mr.from_user
        learner = mr.post.user

    if learner.profile.credits < 1:
        messages.error(request, f"{learner.username} doesn't have enough credits.")
        return redirect('matches')

    learner.profile.credits -= 1
    learner.profile.save()
    teacher.profile.credits += 1
    teacher.profile.save()

    mr.status = 'ACCEPTED'
    mr.save()

    Session.objects.get_or_create(
        teacher=teacher, learner=learner, skill=mr.skill,
        defaults={'status': 'ACTIVE'}
    )

    messages.success(request, "Match accepted and session created.")
    return redirect('sessions')

@login_required
def reject_match(request, pk):
    if request.method != 'POST':
        return HttpResponseBadRequest("POST only")
    mr = get_object_or_404(MatchRequest, pk=pk, to_user=request.user, status='PENDING')
    mr.status = 'REJECTED'
    mr.save()
    messages.info(request, "Request rejected.")
    return redirect('matches')

@login_required
def sessions_view(request):
    sess = Session.objects.filter(Q(teacher=request.user) | Q(learner=request.user)).order_by('-created_at')
    return render(request, 'sessions.html', {'sessions': sess})
