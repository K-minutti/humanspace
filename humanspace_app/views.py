from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import Http404

from twitter_api.twitter_api import TwitterAPI

from .forms import TopicForm, EntryForm
from .decorators import twitter_login_required
from .models import Topic, Entry
from users.models import TwitterUser

app_name = 'humanspace_app'

##############
#   Views
##############
def index(request):
    """Homepage for HumanSpace"""
    return render(request,  app_name + "/index.html") 

@login_required
@twitter_login_required
def home(request):
    return render(request, app_name + "/home.html")


@login_required
def app_logout(request):
    logout(request)
    return redirect('humanspace_app:index') 

##############
#   Topics
##############
@login_required
def topics(request):
    """Return all topics"""
    topics = Topic.objects.filter(owner=request.user).order_by('date_added')
    context = {'topics': topics}
    return render(request, app_name + "/topics.html", context)

@login_required
def topic(request, topic_id):
    """Display a single topic and all its entries."""
    topic = Topic.objects.get(id=topic_id)
    if topic.owner != request.user:
        raise Http404
    entries = topic.entry_set.order_by('-date_added')
    context = {'topic':topic, 'entries':entries}
    return render(request, app_name + "/topic.html", context)

@login_required
def new_topic(request):
    if request.method != 'POST':
        # No data submitted; create a blank form
        form = TopicForm()
    else:
        # POST data submitted; process data
        form = TopicForm(data=request.POST)
        if form.is_valid():
            new_topic = form.save(commit=False)
            new_topic.owner = request.user
            new_topic.save()
            return redirect('humanspace_app:topics')
    # Send blank or invalid form
    context = {'form': form}
    return render(request, app_name + "/new_topic.html", context)


##############
#   Entries
##############
@login_required
def new_entry(request, topic_id):
    """Add a new entry for a specific topic"""
    topic = Topic.objects.get(id=topic_id)
    if topic.owner != request.user:
        raise Http404
        
    if request.method != 'POST':
        # No data submitted create blank form
        form = EntryForm()
    else:
        # POST data submitted process data
        form = EntryForm(data=request.POST)
        if form.is_valid():
            new_entry = form.save(commit=False)
            new_entry.topic = topic
            new_entry.save()
            return redirect('humanspace_app:topic', topic_id=topic_id)
    # Display a blank or invalid form
    context = {'topic': topic, 'form': form}
    return render(request, app_name + "/new_entry.html", context)

@login_required
def edit_entry(request, entry_id):
    """Edit entry"""
    entry = Entry.objects.get(id=entry_id)
    topic = entry.topic
    if topic.owner != request.user:
        raise Http404

    if request.method != 'POST':
        # Initial request pre-fill form with current entry
        form = EntryForm(instance=entry)
    else:
        # POST data submitted and process data
        form = EntryForm(instance=entry, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('humanspace_app:topic', topic_id=topic.id)
    context = {'entry': entry, 'topic': topic, 'form': form}
    return render(request, app_name + "/edit_entry.html", context)


@login_required
@twitter_login_required
def bookmarks(request):
    """Return all bookmarks"""
    twitter_user = TwitterUser.objects.filter(user=request.user).first()
    if twitter_user is not None:
        if twitter_user.twitter_oauth_token is not None:
            twitter_api = TwitterAPI()
            token = twitter_user.twitter_oauth_token.oauth_token
            topics = twitter_api.get_bookmarks(oauth_access_token=token)
    context = {'topics': topics}
    return render(request, app_name + "/bookmarks.html", context)
