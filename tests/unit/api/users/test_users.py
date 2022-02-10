from datetime import datetime
from datetime import timedelta
import unittest

from src.api import main as api
from fastapi.testclient import TestClient

from ....tools.trojan_horse import TrojanHorse

app = api.init_app()
client = TestClient(app)

class Users(unittest.TestCase):
    class header_authorization(unittest.TestCase):
        def header_not_authorized(self, command):
            response = client.get(f"v1/users/{command}")
            self.assertEqual(response.status_code, 403)
            response = client.get("v1/users/me/sessions", headers= {"Authorization": "Bearing Trojan_Horse"})
            self.assertEqual(response.status_code, 403), "Failed to return 403 when no Authorization header is present"

        def check(self, commands: list[str]):
            for command in commands:
                self.header_not_authorized(command)
        
        def runTest(self):
            self.check()
    
    class GetInfo(unittest.TestCase):
        def test_get_users(self):
            response = client.get("v1/users/me/info",
            headers= { "Authorization": f"Bearer {TrojanHorse.token}" }
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["first"], TrojanHorse.pseudo_info["first"])
            self.assertEqual(response.json()["last"], TrojanHorse.pseudo_info["last"])
            self.assertEqual(response.json()["gid"], TrojanHorse.pseudo_info["gid"])
        
        def runTest(self):
            self.test_get_users()

    class Sessions(unittest.TestCase):
        def test_get_sessions(self):
            response = client.get("v1/users/me/sessions",
            headers= { "Authorization": f"Bearer {TrojanHorse.token}" }
            )
            self.assertEqual(response.status_code, 200), "Failed to return 200 when Authorization header is present"
            raw_response = response.json()
            sessions_info = raw_response['sessions'][0]
            uid = sessions_info['uid']
            sid = sessions_info['sid']
            raw_last_accessed = sessions_info['last_accessed']
            last_accessed = datetime.strptime(raw_last_accessed, "%Y-%m-%dT%H:%M:%S.%f")
            self.assertEqual(uid, TrojanHorse.user.uid), "Failed to return correct uid"
            self.assertEqual(sid, TrojanHorse.session.sid), "Failed to return correct sid"
            self.assertAlmostEqual(last_accessed, TrojanHorse.session.last_accessed, delta=timedelta(100)), "Failed to return correct last_accessed"
            
        
        def runTest(self):
            self.test_get_sessions()

    def runTest(self):
        self.GetInfo().runTest()
        self.Sessions().runTest()
    
if __name__ == "__main__":
    unittest.main()