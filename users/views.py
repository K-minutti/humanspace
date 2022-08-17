from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm

from .models import  TwitterAuthToken, TwitterUser
from .auth import create_update_user_from_twitter
from twitter_api.twitter_api import TwitterAPI

app_name = 'registration'

def register(request):
    """Register a new user."""
    if request.method != 'POST':
        #Display blank registration form.
        form = UserCreationForm()
    else:
        # Process form 
        form = UserCreationForm(data=request.POST)

        if form.is_valid():
            new_user = form.save()
            # Log the user in and redirect to home page
            login(request, new_user)
            return redirect('humanspace_app:index')
    # Display blank/invalid form
    context = {"form" : form}   
    return render(request, app_name +'/register.html', context) 


###################
#   Twitter Login
###################
def twitter_login(request):
    twitter_api = TwitterAPI()
    url = twitter_api.twitter_login()
    if url is None or url == '':
        messages.add_message(request, messages.ERROR, 'Unable to login. Please try again.')
        return render(request, app_name + "/error.html")
    else:
        return redirect(url)

def twitter_callback(request):
    print(request)
    if 'denied' in request.GET:
        messages.add_message(request, messages.ERROR, 'Unable to login or login canceled. Please try again.')
        return render(request, app_name + "/error.html")

    # Get auth access token
    twitter_api = TwitterAPI()
    url_path =  request.build_absolute_uri()
    url_path = url_path.replace('http', 'https')# TODO: REMOVE HACK - before deploy
    try: 
        access_token = twitter_api.twitter_callback(url_path) # Pass response url
    except Exception as error:
        messages.add_message(request, messages.ERROR, 'Invalid request. Please try again.')
        return render(request, app_name + "/error.html")

    if access_token is None:
        messages.add_message(request, messages.ERROR, 'Unable to retrieve access token. Please try again.')
        return render(request, app_name + "/error.html")

    # Save token for user
    token = access_token["access_token"]
    twitter_auth_token = TwitterAuthToken(oauth_token=token)
    twitter_auth_token.save()

    # Get user details and validate token
    data = twitter_api.get_me(token)
    if data is None:
        messages.add_message(request, messages.ERROR, 'Unable to retrieve access token. Please try again.')
        return render(request, app_name + "/error.html") 
    
    #Create user
    twitter_user_new = TwitterUser(twitter_id=data[0]['id'], 
                                        screen_name=data[0]['username'],
                                        name=data[0]['name'], 
                                        profile_image_url=data[0]['profile_image_url'])
    twitter_user_new.twitter_oauth_token = twitter_auth_token
    user, twitter_user = create_update_user_from_twitter(twitter_user_new)
    if user is None:
        messages.add_message(request, messages.ERROR, 'Unable to get profile details. Please try again.')
        return render(request, app_name + "/error.html")

    login(request, user) 
    return render(request, 'humanspace_app/index.html')