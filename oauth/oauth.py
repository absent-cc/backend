# Credentials you get from registering a new application
client_id = '349911558418-5joq5quivkmpbkl8nnu89rn8upa6itr1.apps.googleusercontent.com'
client_secret = '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'
redirect_uri = 'http://localhost'

# OAuth endpoints given in the Google API documentation
authorization_base_url = "https://accounts.google.com/o/oauth2/v2/auth"
token_url = "https://www.googleapis.com/oauth2/v4/token"
scope = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile"
]

from requests_oauthlib import OAuth2Session
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
print(google.fetch_token(token_url, client_secret=client_secret,
        authorization_response=redirect_response)['id_token'])

print('\n\n')

# Fetch a protected resource, i.e. user profile
r = google.get('https://www.googleapis.com/oauth2/v1/userinfo')
print(r.content)
