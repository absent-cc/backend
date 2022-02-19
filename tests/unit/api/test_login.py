# Run from the root of the project with command:
# python -m unittest discover

import sys
import time
import unittest

from sqlalchemy import false

from src.api import main as api

from fastapi.testclient import TestClient

from tests.tools.googleTokenGen import googleAuth

import os

## UNCOMMENT BELOW CODE IF YOU WANT TO TEST LOGIN

# # from api.v1.main import refresh

# UNCOMMENT ABOVE CODE IF YOU WANT TO TEST LOGIN
# @unittest.skip("Only test when you want to use test login")
class TestLogin(unittest.TestCase):

    app = api.init_app()

    client = TestClient(app)
    
    id_token = os.getenv("GOOGLE_ID_TOKEN")
    token = os.getenv("TOKEN")
    refresh_token = os.getenv("REFRESH_TOKEN")

    def login_init(self):
        new_token = googleAuth()
        os.environ["GOOGLE_ID_TOKEN"] = new_token
        self.id_token = new_token
        time.sleep(1) # Delay because for some reason the tokens do not update in the env quick enough. It seems like it is a non-blocking action. Thus, we need to add in a delay to let the system catch up with the tokens its received. I hate env vars!

    def test_login(self):
        if os.getenv("GOOGLE_ID_TOKEN") is None:
            print("HERE!", os.getenv("GOOGLE_ID_TOKEN"))
            self.login_init()
        print(os.getenv("GOOGLE_ID_TOKEN"))
        
        response = self.client.post("v1/login/",
            json={"token": os.getenv("GOOGLE_ID_TOKEN")},
        )
        print(response.json())
        assert response.status_code == 201
        os.environ["TOKEN"] = response.json()["token"]
        os.environ["REFRESH_TOKEN"] = response.json()["refresh"] 
        return response.json()

    def test_refresh(self):
        login_response = self.test_login()
        
        refresh_token = login_response["refresh"]
        response = self.client.post("v1/refresh/",
            headers={"Authorization": f"Bearer {refresh_token}"},
        )
        assert response.status_code == 201
    
    def runTest(self):
        self.test_refresh()

if __name__ == "__main__":
    unittest.main()