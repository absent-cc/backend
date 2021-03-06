from typing import Dict, List
import unittest

import csv
import unittest
from typing import Dict, List

from fastapi.testclient import TestClient

from src.api import main as api
from src.dataTypes import models
from src.dataTypes.schemas import (
    AbsenceCreate,
    AbsenceReturn,
    TeacherCreate,
    TeacherReturn,
)
from src.database import crud
from src.database.database import SessionLocal

app = api.init_app()
client = TestClient(app)


class TestTeachers(unittest.TestCase):
    _db = SessionLocal()

    class Absences(unittest.TestCase):
        def __init__(self, methodName: str = "runTest") -> None:
            super().__init__(methodName)
            self.ABSENCES: Dict[str, AbsenceReturn] = {}
            self.dates: List[
                str
            ] = []  # String versions of the date object. Format: YYYY-MM-DD

        def load_absences(self):
            with open(
                "./tests/unit/data/test_absences.csv", "r"
            ) as f:  # Reads test data
                raw_absences: Dict = csv.DictReader(f)

                for row in raw_absences:

                    stripped_row = {
                        k: v.strip() for k, v in row.items()
                    }  # Strip whitespace from all values.

                    # Add teacher to DB
                    teacherMeta: models.Absence = crud.addAbsence(
                        TestTeachers._db,
                        AbsenceCreate(
                            teacher=TeacherCreate(
                                first=stripped_row["First"],
                                last=stripped_row["Last"],
                                school=stripped_row["School"],
                            ),
                            length=stripped_row["Length"],
                            note=stripped_row["Note"],
                            date=stripped_row["Date"],
                        ),
                    )
                    tid: str = teacherMeta.tid

                    teacherReturn: TeacherReturn = TeacherReturn(
                        tid=tid,
                        first=stripped_row["First"],
                        last=stripped_row["Last"],
                        school=stripped_row["School"],
                    )

                    absenceReturn: AbsenceReturn = AbsenceReturn(
                        length=stripped_row["Length"],
                        teacher=teacherReturn,
                        note=stripped_row["Note"],
                    )
                    self.ABSENCES[tid] = absenceReturn
                    self.dates.append(stripped_row["Date"])

        def runTest(self):
            self.load_absences()
            self.test_get_absences()

        def test_get_absences(self):
            for date in self.dates:
                r = client.get(f"/v1/teachers/absences/?date={date}")
                self.assertEqual(
                    r.status_code, 200
                ), "Failed to return correct status code"
                response = r.json()
                for entry in response["absences"]:
                    test_entry = self.ABSENCES.get(
                        entry["teacher"]["tid"]
                    )  # Lookup the teacher returned in the test data.
                    print(test_entry)
                    self.assertNotEqual(
                        test_entry, None
                    ), "Lookup of response teacher failed."

                    self.assertEqual(
                        entry["length"], test_entry.length
                    ), "Length entry does not match test data."
                    self.assertEqual(
                        entry["teacher"]["first"].upper(),
                        test_entry.teacher.first.upper(),
                    ), "First name entry does not match test data."
                    self.assertEqual(
                        entry["teacher"]["last"].upper(),
                        test_entry.teacher.last.upper(),
                    ), "Last name entry does not match test data."
                    self.assertEqual(
                        entry["teacher"]["school"].upper(), test_entry.teacher.school
                    ), "School name entry does not match test data."
                    self.assertEqual(
                        entry["note"], test_entry.note
                    ), "Note entry does not match test data."

        def test_get_teachers(self):
            pass

    # class AutoComplete(unittest.TestCase):
    #    pass

    def runTest(self):
        absences_test = TestTeachers.Absences()
        absences_test.runTest()


# if __name__ == '__main__':
#     _db = SessionLocal()
#     crud.reset(_db)
#     test = TestTeachers().Absences()
#     test.runTest()
