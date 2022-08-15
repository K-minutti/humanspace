
from multiprocessing import context
import re
from django.shortcuts import render, redirect
from .models import Topic, Entry
from .forms import TopicForm, EntryForm

app_name = 'humanspace_app'

def index(request):
    """Homepage for HumanSpace"""
    return render(request,  app_name + "/index.html") 


##############
#   Topics
##############
def topics(request):
    """Return all topics"""
    topics = Topic.objects.order_by('date_added')
    context = {'topics': topics}
    return render(request, app_name + "/topics.html", context)


def topic(request, topic_id):
    """Display a single topic and all its entries."""
    topic = Topic.objects.get(id=topic_id)
    entries = topic.entry_set.order_by('-date_added')
    context = {'topic':topic, 'entries':entries}
    return render(request, app_name + "/topic.html", context)


def new_topic(request):
    if request.method != 'POST':
        # No data submitted; create a blank form
        form = TopicForm()
    else:
        # POST data submitted; process data
        form = TopicForm(data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('humanspace_app:topics')
    # Send blank or invalid form
    context = {'form': form}
    return render(request, app_name + "/new_topic.html", context)


##############
#   Entries
##############
def new_entry(request, topic_id):
    """Add a new entry for a specific topic"""
    topic = Topic.objects.get(id=topic_id)

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


def edit_entry(request, entry_id):
    """Edit entry"""
    entry = Entry.objects.get(id=entry_id)
    topic = entry.topic

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