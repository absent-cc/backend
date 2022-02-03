import sys
import unittest
from api import main
from tests.googleTokenGen import googleAuth, write_secrets, read_secrets

from fastapi.testclient import TestClient

# from api.v1.main import refresh

app = main.absent

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

class TestMain(unittest.TestCase):
    def test_login(self):
        print(id_token)
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