import tweepy
from decouple import config

from urllib import parse
from users.models import TwitterAuthFlowState

class TwitterAPI:
    def __init__(self):
        self.api_key = config('TWITTER_API_KEY')
        self.api_secret = config('TWITTER_API_SECRET')
        self.client_id = config('TWITTER_CLIENT_ID')
        self.client_secret = config('TWITTER_CLIENT_SECRET')
        self.oauth_callback_url = config('TWITTER_OAUTH_CALLBACK_URL')
        self.scopes =  ["tweet.read", "tweet.write", "bookmark.read", "bookmark.write", "users.read", "list.read", "list.write"]

    def twitter_login(self):
        oauth2_user_handler = tweepy.OAuth2UserHandler(client_id=self.client_id,   
                                                        redirect_uri=self.oauth_callback_url,
                                                        scope=self.scopes,
                                                        client_secret=self.client_secret)
        url = oauth2_user_handler.get_authorization_url()
        state_value = parse.parse_qs(parse.urlparse(url).query)['state'][0]
        auth_flow_state =  TwitterAuthFlowState.objects.filter(state=state_value).first()
        if auth_flow_state is None:
            auth_flow_state = TwitterAuthFlowState(state=state_value, code_verifier=oauth2_user_handler._client.code_verifier)
            auth_flow_state.save()
        return url 

    def twitter_callback(self, authorization_response):
        oauth2_user_handler = tweepy.OAuth2UserHandler(client_id=self.client_id,   
                                                        redirect_uri=self.oauth_callback_url,
                                                        scope=self.scopes,
                                                        client_secret=self.client_secret)
        state_value = parse.parse_qs(parse.urlparse(authorization_response).query)['state'][0]
        auth_flow_state =  TwitterAuthFlowState.objects.filter(state=state_value).first() 
        if auth_flow_state is not None:
            oauth2_user_handler._client.code_verifier = auth_flow_state.code_verifier

        access_token = oauth2_user_handler.fetch_token(authorization_response)
        return access_token 

    def get_me(self, oauth_access_token):
        try:
            client = tweepy.Client(oauth_access_token)
            data = client.get_me(user_auth=False, expansions='pinned_tweet_id')
            return data
        except Exception as e:
            print(e)
            return None
    
    def get_bookmarks(self, oauth_access_token):
        try:
            client = tweepy.Client(oauth_access_token)
            data = client.get_bookmarks()
            return data
        except Exception as e:
            print(e)
            return None