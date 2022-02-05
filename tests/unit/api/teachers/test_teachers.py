import unittest

from src.api import main as api
from fastapi.testclient import TestClient

app = api.init_app()
client = TestClient(app)

class TestTeachers(unittest.TestCase):
    pass
