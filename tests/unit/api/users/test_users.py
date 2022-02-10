from email import header
import unittest
from wsgiref import headers

from src.api import main as api
from fastapi.testclient import TestClient

from ..trojan_horse import TrojanHorse

app = api.init_app()
client = TestClient(app)

class TestUsers(unittest.TestCase):
    def test_get_users(self):
        response = client.get("v1/users/me/info",
        headers= { "Authorization": f"Bearer {TrojanHorse.token}" }
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["first"], TrojanHorse.pseudo_info["first"])
        self.assertEqual(response.json()["last"], TrojanHorse.pseudo_info["last"])
        self.assertEqual(response.json()["gid"], TrojanHorse.pseudo_info["gid"])
    
    def test_get_users_not_authorized(self):
        response = client.get("v1/users/me/info")
        self.assertEqual(response.status_code, 403)
    
if __name__ == "__main__":
    unittest.main()