from datetime import datetime
from datetime import timedelta
from typing import Dict
import unittest

from src.api import main as api
from fastapi.testclient import TestClient

from ....tools.trojan_horse import TrojanHorse

app = api.init_app()
client = TestClient(app)

class Users(unittest.TestCase):
    class HeaderAuth(unittest.TestCase):
        def header_not_authorized(self, command: str, status_code: int):
            print(command)
            print(status_code)
            response = client.get(f"v1/users/me/{command}")
            print("RUN 1:", response)
            self.assertEqual(response.status_code, status_code)
            response = client.get("v1/users/me/sessions", headers = {"Authorization": "Bearing Trojan_Horse"})
            print("RUN 2:", response)
            self.assertEqual(response.status_code, status_code), "Failed to return 403 when no Authorization header is present"

        def check(self, commands: Dict[str, int]):
            for command, status_code in commands.items():
                self.header_not_authorized(command, status_code)
        
        def runTest(self):
            commands = {
                    "info" : 403, 
                    "sessions" : 403,
                    "delete" : 405,
                    "update" : 405,
                    "update/profile" : 422,
                    "update/schedule" : 422,
                    "update/fcm" : 422,
                    "session/revoke": 422,
            }
            self.check(commands)
    
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

            self.assertEqual(uid, TrojanHorse.user.uid), "Failed to return correct uid" # Check uid
            self.assertEqual(sid, TrojanHorse.session.sid), "Failed to return correct sid" # Check sid
            self.assertAlmostEqual(last_accessed, TrojanHorse.session.last_accessed, delta=timedelta(100)), "Failed to return correct last_accessed" # Aprox. time check for last_accessed. 
            
        def runTest(self):
            self.test_get_sessions()


    def runTest(self):
        self.GetInfo().runTest()
        self.Sessions().runTest()
        self.HeaderAuth().runTest()
    
if __name__ == "__main__":
    unittest.main()