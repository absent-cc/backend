# Run from the root of the project with command:
# python -m unittest discover

import sys
import unittest

from src.api import main as api

from fastapi.testclient import TestClient

from ..tools.googleTokenGen import googleAuth, read_secrets, write_secrets

# from api.v1.main import refresh
app = api.init_app()

client = TestClient(app)

id_token = read_secrets('Login', 'id_token')
token = read_secrets('Login', 'token')
refresh_token = read_secrets('Login', 'refresh_token')

if (id_token or token or refresh_token) is None:
    new_token = googleAuth()
    write_secrets('Login', 'id_token', new_token)

if len(sys.argv) > 1:
    if sys.argv[1] == 'refresh':
        id_token = googleAuth()
        write_secrets('Login', 'id_token', id_token)

class TestLogin(unittest.TestCase):
    def test_login(self):
        response = client.post("v1/login/",
            json={"token": id_token},
        )
        assert response.status_code == 201
        write_secrets('Login', 'token', response.json()['token'])
        write_secrets('Login', 'refresh_token', response.json()['refresh'])
        return response.json()

    def test_refresh(self):
        login_response = self.test_login()
        
        refresh_token = login_response["refresh"]
        response = client.post("v1/refresh/",
            headers={"Authorization": f"Bearer {refresh_token}"},
        )
        assert response.status_code == 201
    
if __name__ == "__main__":
    unittest.main()