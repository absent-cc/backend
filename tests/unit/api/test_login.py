# Run from the root of the project with command:
# python -m unittest discover

import sys
import unittest

from src.api import main as api

from fastapi.testclient import TestClient

from tests.tools.googleTokenGen import googleAuth

import os

## UNCOMMENT BELOW CODE IF YOU WANT TO TEST LOGIN

# # from api.v1.main import refresh

# UNCOMMENT ABOVE CODE IF YOU WANT TO TEST LOGIN
# @unittest.skip("Only test when you want to use test login")
class TestLogin(unittest.TestCase):
    def init(self, methodName="runTest"):
        super().init(methodName)
        app = api.init_app()

        self.client = TestClient(app)

        self.id_token = os.getenv("GOOGLE_ID_TOKEN")
        self.token = os.getenv("TOKEN")
        self.refresh_token = os.getenv("REFRESH_TOKEN")

        if self.id_token is None or self.token is None or self.refresh_token is None:
            new_token = googleAuth()
            os.environ["GOOGLE_ID_TOKEN"] = new_token
            self.id_token = new_token

        if len(sys.argv) > 1:
            if sys.argv[1] == 'refresh':
                self.id_token = googleAuth()
                os.environ["GOOGLE_ID_TOKEN"] = self.id_token

    def test_login(self):
        response = self.client.post("v1/login/",
            json={"token": self.id_token},
        )
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
        self.init()
        self.test_login()
        self.test_refresh()
if __name__ == "__main__":
    unittest.main()