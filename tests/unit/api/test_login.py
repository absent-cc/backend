# Run from the root of the project with command:
# python -m unittest discover

import sys
import unittest

from src.api import main as api

from fastapi.testclient import TestClient

from tests.tools.googleTokenGen import googleAuth

import os

# from api.v1.main import refresh
app = api.init_app()

client = TestClient(app)

id_token = os.getenv("GOOGLE_ID_TOKEN")
token = os.getenv("TOKEN")
refresh_token = os.getenv("REFRESH_TOKEN")

if id_token is None or token is None or refresh_token is None:
    new_token = googleAuth()
    os.environ["GOOGLE_ID_TOKEN"] = new_token
    id_token = new_token

if len(sys.argv) > 1:
    if sys.argv[1] == 'refresh':
        id_token = googleAuth()
        os.environ["GOOGLE_ID_TOKEN"] = id_token

@unittest.skip("Only test when you want to use test login")
class TestLogin(unittest.TestCase):
    def test_login(self):
        response = client.post("v1/login/",
            json={"token": id_token},
        )
        assert response.status_code == 201
        os.environ["TOKEN"] = response.json()["token"]
        os.environ["REFRESH_TOKEN"] = response.json()["refresh"] 
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