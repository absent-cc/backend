from datetime import datetime
from datetime import timedelta
from typing import Dict, Tuple
import unittest

from src.api import main as api
from fastapi.testclient import TestClient

from tests.tools.trojanHorse import TrojanHorse

app = api.init_app()
client = TestClient(app)


class Users(unittest.TestCase):
    class HeaderAuth(unittest.TestCase):
        def header_not_authorized(self, command: str, status_codes: Tuple[int, int]):
            def incorrect_header(self, status_code: int):
                response = client.get(f"v1/users/me/{command}")
                print("RUN 1:", response)
                self.assertEqual(
                    response.status_code, status_code
                ), "Failed to return correct status code when no Authorization header is present"

            def no_header(self, status_code: int):
                response = client.get(
                    "v1/users/me/sessions", headers={"Absent-Auth": "Trojan_Horse"}
                )
                print("RUN 2:", response)
                self.assertEqual(
                    response.status_code, status_code
                ), "Failed to return correct status code when no Authorization header is present"

            print("COMMAND", command)
            incorrect_header(self, status_codes[0])
            print("_____")
            no_header(self, status_codes[1])

        def check(self, commands: Dict[str, Tuple[int, int]]):
            for command, status_code in commands.items():
                self.header_not_authorized(command, status_code)

        def runTest(self):
            commands = {
                "info": (403, 401),
                "sessions": (403, 401),
                "delete": (405, 401),
                "update": (405, 401),
                "update/profile": (405, 401),
                "update/schedule": (405, 401),
                "update/fcm": (405, 401),
                "session/revoke": (404, 401),
            }
            self.check(commands)

    class GetInfo(unittest.TestCase):
        TROJANHORSE = TrojanHorse()

        def test_get_users(self):
            response = client.get(
                "v1/users/me/info", headers={"Absent-Auth": f"{self.TROJANHORSE.token}"}
            )
            print(response.json())
            print(self.TROJANHORSE.pseudo_info)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(
                response.json()["profile"]["first"],
                self.TROJANHORSE.pseudo_info["first"],
            )
            self.assertEqual(
                response.json()["profile"]["last"], self.TROJANHORSE.pseudo_info["last"]
            )
            self.assertEqual(
                response.json()["profile"]["gid"], self.TROJANHORSE.pseudo_info["gid"]
            )

        def runTest(self):
            self.test_get_users()

    class Sessions(unittest.TestCase):
        TROJANHORSE = TrojanHorse()

        def test_get_sessions(self):
            response = client.get(
                "v1/users/me/sessions",
                headers={"Absent-Auth": f"{self.TROJANHORSE.token}"},
            )
            self.assertEqual(
                response.status_code, 200
            ), "Failed to return 200 when Authorization header is present"

            raw_response = response.json()
            sessions_info = raw_response["sessions"][0]
            uid = sessions_info["uid"]
            sid = sessions_info["sid"]
            raw_last_accessed = sessions_info["last_accessed"]
            last_accessed = datetime.strptime(raw_last_accessed, "%Y-%m-%dT%H:%M:%S.%f")

            self.assertEqual(
                uid, self.TROJANHORSE.user.uid
            ), "Failed to return correct uid"  # Check uid
            self.assertEqual(
                sid, self.TROJANHORSE.session.sid
            ), "Failed to return correct sid"  # Check sid
            self.assertAlmostEqual(last_accessed, self.TROJANHORSE.session.last_accessed, delta=timedelta(100)), "Failed to return correct last_accessed"  # type: ignore # Aprox. time check for last_accessed.

        def runTest(self):
            self.test_get_sessions()

    def runTest(self):
        self.GetInfo().runTest()
        self.Sessions().runTest()
        self.HeaderAuth().runTest()


# if __name__ == "__main__":
#     unittest.main()
