from configparser import ConfigParser
from requests_oauthlib import OAuth2Session
import configparser
from logging import config
import os

SECRETS_PATH = "tests/tools/testing_config.ini"

def load_google_secrets_into_env():
    configuer = ConfigParser()
    secrets = configuer.read(SECRETS_PATH)
    if secrets == []:
        raise Exception("Could not find secrets file. Please create one in the tests/tools directory.")
    else:
        for key in configuer['Google']:
            os.environ[key.upper()]= configuer['Google'][key]
    
def check_if_secrets_in_env():
    if os.getenv("GOOGLE_CLIENT_ID") is None or os.getenv("GOOGLE_CLIENT_SECRET") is None:
        print("GOOGLE_CLIENT_ID or GOOGLE_CLIENT_SECRET not found in env. Setting now...")
        load_google_secrets_into_env()
    

check_if_secrets_in_env()

CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")

# configuer = ConfigParser()
# secrets = configuer.read(SECRETS_PATH)
# CLIENT_ID = configuer['Google']['CLIENT_ID']
# CLIENT_SECRET = configuer['Google']['CLIENT_SECRET']

redirect_uri = 'https://localhost'

# OAuth endpoints given in the Google API documentation
authorization_base_url = "https://accounts.google.com/o/oauth2/v2/auth"
token_url = "https://www.googleapis.com/oauth2/v4/token"
scope = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile"
]


def googleAuth():
    check_if_secrets_in_env()

    google = OAuth2Session(CLIENT_ID, scope=scope, redirect_uri=redirect_uri)

    # Redirect user to Google for authorization
    authorization_url, state = google.authorization_url(authorization_base_url,
        # offline for refresh token
        # force to always make user click authorize
        access_type="offline", prompt="select_account")
    print('Please go here and authorize:', authorization_url)

    # Get the authorization verifier code from the callback url
    redirect_response = input('Paste the full redirect URL here:')

    print('\n\n')

    # Fetch the access token
    token = google.fetch_token(token_url, client_secret=CLIENT_SECRET,
            authorization_response=redirect_response)['id_token']
    
    return token

 
# if __name__ == "__main__":
#     googleAuth()
    # load_secrets_into_env('Google')