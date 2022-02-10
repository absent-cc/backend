from email import header
import unittest
from wsgiref import headers

from src.api import main as api
from fastapi.testclient import TestClient

app = api.init_app()
client = TestClient(app)

class TestUsers(unittest.TestCase):
    def test_get_users(self):
        response = client.get("v1/users/me/info",
        headers= { "Authorization" "Bearer "
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])
    pass