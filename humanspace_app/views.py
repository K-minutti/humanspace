from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import Http404

from .forms import TopicForm, EntryForm
from .decorators import twitter_login_required
from .models import Topic, Entry, TwitterAuthToken, TwitterUser
from .auth import create_update_user_from_twitter, check_token_still_valid
from twitter_api.twitter_api import TwitterAPI

app_name = 'humanspace_app'

##############
#   Views
##############
# def index(request):
#     """Homepage for HumanSpace"""
#     return render(request,  app_name + "/index.html") 

# @login_required
# @twitter_login_required
def index(request):
    return render(request, app_name + "/index.html") 

@login_required
def app_logout(request):
    logout(request)
    return redirect('index')

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

###################
#   Twitter Login
###################
def twitter_login(request):
    twitter_api = TwitterAPI()
    url, oauth_token, oauth_token_secret = twitter_api.twitter_login()
    if url is None or url == '':
        messages.add_message(request, messages.ERROR, 'Unable to login. Please try again.')
        return render(request, app_name + "/error.html")
    else:
        twitter_auth_token = TwitterAuthToken.objects.filter(oauth_token=oauth_token).first()
        if twitter_auth_token is None:
            twitter_auth_token = TwitterAuthToken(oauth_token=oauth_token, oauth_token_secret=oauth_token_secret)
            twitter_auth_token.save()
        else:
            twitter_auth_token.oauth_token_secret = oauth_token_secret
            twitter_auth_token.save()
        return redirect(url)

def twitter_callback(request):
    if 'denied' in request.GET:
        messages.add_message(request, messages.ERROR, 'Unable to login or login canceled. Please try again.')
        return render(request, app_name + "/error.html")
    twitter_api = TwitterAPI()
    oauth_verifier = request.GET.get('oauth_verifier')
    oauth_token = request.GET.get('oauth_token')
    twitter_auth_token = TwitterAuthToken.objects.filter(oauth_token=oauth_token).first()
    if twitter_auth_token is not None:
        access_token, access_token_secret = twitter_api.twitter_callback(oauth_verifier, oauth_token, twitter_auth_token.oauth_token_secret)
        if access_token is not None and access_token_secret is not None:
            twitter_auth_token.oauth_token = access_token
            twitter_auth_token.oauth_token_secret = access_token_secret
            twitter_auth_token.save()
            # Create user
            info = twitter_api.get_me(access_token, access_token_secret)
            if info is not None:
                twitter_user_new = TwitterUser(twitter_id=info[0]['id'], screen_name=info[0]['username'],
                                               name=info[0]['name'], profile_image_url=info[0]['profile_image_url'])
                twitter_user_new.twitter_oauth_token = twitter_auth_token
                user, twitter_user = create_update_user_from_twitter(twitter_user_new)
                if user is not None:
                    login(request, user)
                    return redirect('index')
            else:
                messages.add_message(request, messages.ERROR, 'Unable to get profile details. Please try again.')
                return render(request, app_name + "/error.html")
        else:
            messages.add_message(request, messages.ERROR, 'Unable to get access token. Please try again.')
            return render(request, app_name + "/error.html")
    else:
        messages.add_message(request, messages.ERROR, 'Unable to retrieve access token. Please try again.')
        return render(request, app_name + "/error.html")


