from configparser import ConfigParser

SECRETS_PATH = "tests/tools/testing_config.ini"

configuer = ConfigParser()
secrets = configuer.read(SECRETS_PATH)
client_id = configuer['Google']['client_id']
client_secret = configuer['Google']['client_secret']

redirect_uri = 'https://localhost'

# OAuth endpoints given in the Google API documentation
authorization_base_url = "https://accounts.google.com/o/oauth2/v2/auth"
token_url = "https://www.googleapis.com/oauth2/v4/token"
scope = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile"
]

from requests_oauthlib import OAuth2Session

def googleAuth():
    google = OAuth2Session(client_id, scope=scope, redirect_uri=redirect_uri)

    # Redirect user to Google for authorization
    authorization_url, state = google.authorization_url(authorization_base_url,
        # offline for refresh token
        # force to always make user click authorize
        access_type="offline", prompt="select_account")
    print('Please go here and authorize:', authorization_url)

    # Get the authorization verifier code from the callback url
    redirect_response = input('Paste the full redirect URL here: ')

    print('\n\n')

    # Fetch the access token
    token = google.fetch_token(token_url, client_secret=client_secret,
            authorization_response=redirect_response)['id_token']
    print(token)
    return token

def write_secrets(section, key, value):
    configuer[section][key] = value
    with open(SECRETS_PATH, 'w') as config_file:
        configuer.write(config_file)

def read_secrets(section, key):
    return configuer[section][key]

if __name__ == "__main__":
    googleAuth()