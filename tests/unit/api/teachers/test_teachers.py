import unittest

from src.api import main as api
from fastapi.testclient import TestClient

app = api.init_app()
client = TestClient(app)

class TestTeachers(unittest.TestCase):
    def test_get_teachers(self):
        # response = client.get("/teachers/")
        # self.assertEqual(response.status_code, 200)
        # self.assertEqual(response.json(), [])
    pass
