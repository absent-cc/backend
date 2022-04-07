from enum import Enum
from dataclasses import dataclass
from typing import List, Tuple, Dict, Union, Optional
from pydantic import BaseModel, schema_of
from pydantic.fields import ModelField

from datetime import date, time
import configparser

#
# SCHOOL ENUMS (BLOCK AND NAME)
#


class SchoolNameMapper(dict):
    def __init__(self):
        super().__init__()
        self.update(
            {
                "NSHS": SchoolName.NEWTON_SOUTH,
                "NNHS": SchoolName.NEWTON_NORTH,
                None: None,
            }
        )


class SchoolName(str, Enum):
    NEWTON_SOUTH: str = "NSHS"
    NEWTON_NORTH: str = "NNHS"


class SchoolBlock(str, Enum):
    A: str = "A"
    ADV: str = "ADVISORY"
    B: str = "B"
    C: str = "C"
    D: str = "D"
    E: str = "E"
    F: str = "F"
    G: str = "G"
    EXTRA: str = "EXTRA"  # Lion/Tiger block

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value

    WIN: str = "WIN"
    LUNCH: str = "LUNCH"  # Will only need during short day since lunch is seperate from a block, unlike in the normal situation. This should not be in use yet!


class LunchBlock(str, Enum):
    L1 = "L1"
    L2 = "L2"
    L3 = "L3"


class SchoolBlocksOnDay(Dict[int, SchoolBlock]):
    def __init__(self):
        super().__init__()
        self.update(
            {
                0: [
                    SchoolBlock.A,
                    SchoolBlock.ADV,
                    SchoolBlock.B,
                    SchoolBlock.C,
                    SchoolBlock.D,
                    SchoolBlock.E,
                ],
                1: [SchoolBlock.A, SchoolBlock.B, SchoolBlock.F, SchoolBlock.G],
                2: [SchoolBlock.C, SchoolBlock.D, SchoolBlock.E, SchoolBlock.F],
                3: [SchoolBlock.A, SchoolBlock.B, SchoolBlock.G, SchoolBlock.E],
                4: [SchoolBlock.C, SchoolBlock.D, SchoolBlock.F, SchoolBlock.G],
                5: [],
                6: [],
            }
        )


class Grade(int, Enum):
    NINE: int = 9
    TEN: int = 10
    ELEVEN: int = 11
    TWELEE: int = 12  # KEEP TWELEE, NICE ARTIFACT


class TableColumn(str, Enum):
    POSITION = [
        "Position",
    ]
    CS_NAME = [
        "Name",
    ]
    FIRST_NAME = ["First", "First Name"]
    LAST_NAME = ["Last", "Last Name"]
    LENGTH = [
        "Day",
    ]
    WEEKDAY = ["Day of Week", "DoW", "D o W", "D of Week"]
    NOTE = ["Notes", "Notes to Student"]
    DATE = [
        "Date",
    ]

    def __eq__(self, val):
        if val != "":
            return val in self.__dict__["_value_"]
        else:
            return False

    def __hash__(self) -> int:
        return super().__hash__()


class BlockMapper(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.update(
            {
                SchoolBlock.A: "A",
                SchoolBlock.ADV: "ADV",
                SchoolBlock.B: "B",
                SchoolBlock.C: "C",
                SchoolBlock.D: "D",
                SchoolBlock.E: "E",
                SchoolBlock.F: "F",
                SchoolBlock.G: "G",
            }
        )


class ReverseBlockMapper(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.update(
            {
                "A": SchoolBlock.A,
                "ADV": SchoolBlock.ADV,
                "ADVISORY": SchoolBlock.ADV,
                "B": SchoolBlock.B,
                "C": SchoolBlock.C,
                "D": SchoolBlock.D,
                "E": SchoolBlock.E,
                "F": SchoolBlock.F,
                "G": SchoolBlock.G,
                "EXTRA": SchoolBlock.EXTRA,
            }
        )


#
# API ENUMS
#


class ErrorTypeMapper(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.update(
            {
                ErrorType.AUTH: "Authentication Error",
                ErrorType.DB: "Database Error",
                ErrorType.PAYLOAD: "Payload Error",
            }
        )


class ErrorType(Enum):
    AUTH = "Authentication Error"
    DB = "Database Error"
    PAYLOAD = "Payload Error"

    def __str__(self) -> str:
        mapper = ErrorTypeMapper()
        return mapper[self]


#
# STUDENT, TEACHER, CLASSTEACHERS(CUSTOM SET), ABSENTTEACHER, AND SCHEDULE OBJECTS
#


@dataclass
class SchoologyCreds:
    keys: dict
    secrets: dict


class RawUpdate(BaseModel):
    poster: str
    content: List[str]
    columns: int = None


#
# SESSION AND TOKEN OBJECTS
#
class ListenerStatus:

    # Represents if action has already been done or not
    state_path: str = "src/state.ini"

    absences: bool = False
    notifications: bool = False
    date: date

    def __init__(self, school: SchoolName, date: date = date.today()):
        self.school = school
        self.date = date
        self.absences, self.notifications = self.readState()

    def __repr__(self) -> str:
        return f"Statuses: \n\tAbsence: {self.absences}\n\tNotifications: {self.notifications}"

    def readState(self) -> Tuple[bool, bool]:
        absences: bool = False
        notifications: bool = False

        config = configparser.ConfigParser()
        config.read(ListenerStatus.state_path)

        if config[self.school.value]["absences"] == str(self.date):
            absences = True

        if config[self.school.value]["notifications"] == str(self.date):
            notifications = True

        return absences, notifications

    def updateState(self, absences: Optional[bool], notifications: Optional[bool]):

        config = configparser.ConfigParser()
        config.read(ListenerStatus.state_path)  # Create dict from existing state file

        if absences:  # Update dict state when True
            config[self.school.value]["absences"] = str(self.date)
            self.absences = True

        if notifications:  # Update dict state when True
            config[self.school.value]["notifications"] = str(self.date)
            self.notifications = True

        with open(
            ListenerStatus.state_path, "w"
        ) as config_file:  # Write new states to file
            config.write(config_file)

    @staticmethod
    def resetState():
        config = configparser.ConfigParser()
        config.read(ListenerStatus.state_path)

        config[self.school.value]["absences"] = str(
            date(year=2022, month=3, day=23)
        )  # Set to abSENT launch date (Default date)

        config[self.school.value]["notifications"] = str(
            date(year=2022, month=3, day=23)
        )  # Set to abSENT launch date (Default date)

        with open(ListenerStatus.state_path, "w") as config_file:
            config.write(config_file)

    @staticmethod
    def resetAll():
        for school in SchoolName:
            ListenerStatus.resetState()


class ColumnMap(Dict[TableColumn, Tuple[int, int]]):
    def __init__(self):
        super().__init__()
        self.update(
            {
                TableColumn.POSITION: (-1, -1),
                TableColumn.CS_NAME: (-1, -1),
                TableColumn.FIRST_NAME: (-1, -1),
                TableColumn.LAST_NAME: (-1, -1),
                TableColumn.LENGTH: (-1, -1),
                TableColumn.WEEKDAY: (-1, -1),
                TableColumn.NOTE: (-1, -1),
                TableColumn.DATE: (-1, -1),
                "CS_MAP": (-1, -1),
            }
        )


class Confidence(BaseModel):
    confidences: dict
    csMap: Union[Tuple, None]


class NotificationBuild(BaseModel):
    uid: str = None
    tid: str = None
    block: SchoolBlock = None
    date: date = None


class NotificationSend(NotificationBuild):
    fcm: str = None
    title: str = None
    body: str = None
    data: dict = None


class Lunch(BaseModel):
    lunch: LunchBlock = None
    startTime: time = None
    endTime: time = None


class Lunches(List[Lunch]):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class BlockWithTimes(BaseModel):
    block: SchoolBlock
    startTime: time
    endTime: time
    lunches: Lunches = None

    class Config:
        from_orm = True
        arbitrary_types_allowed = True


class ScheduleWithTimes(List[BlockWithTimes]):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __repr__(self) -> str:
        if len(self) == 0:
            return "No schedule"
        printOut = "\n"
        for block in self:
            printOut += f"\t{block.block}: {block.startTime.strftime('%I:%M')}-{block.endTime.strftime('%H:%M')}\n"
            if block.lunches is not None:
                for lunch in block.lunches:
                    printOut += f"\t\t{lunch.lunch}: {lunch.startTime.strftime('%I:%M')}-{lunch.endTime.strftime('%H:%M')}\n"
        return f"Schedule: {printOut}"

    def __str__(self) -> str:
        return self.__repr__()

    def blocks(self) -> List[SchoolBlock]:
        if self is None:
            return []
        return [block.block for block in self]

    @classmethod
    def __modify_schema__(cls, field_schema, field: Optional[ModelField]):  # type: ignore
        if field:
            field_schema["items"] = schema_of(BlockWithTimes)
            # field_schema['examples'] = [BlockWithTimes.schema_json()['properties']['examples']]
            # field_schema['examples'] = schema_of(BlockWithTimes)['examples']

    # @classmethod
    # def __get_validators__(cls):
    #     # one or more validators may be yielded which will be called in the
    #     # order to validate the input, each validator will receive as an input
    #     # the value returned from the previous validator
    #     yield cls.validate

    # @classmethod
    # def __modify_schema__(cls, field_schema):
    #     # __modify_schema__ should mutate the dict it receives in place,
    #     # the returned value will be ignored
    #     field_schema.update(
    #         # simplified regex here for brevity, see the wikipedia link above
    #         pattern='^[A-Z]{1,2}[0-9][A-Z0-9]? ?[0-9][A-Z]{2}$',
    #         # some example postcodes
    #         examples=['SP11 9DG', 'w1j7bu'],
    #     )

    # @classmethod
    # def validate(cls, v):
    #     if not isinstance(v, ScheduleWithTimes):
    #         raise TypeError('ScheduleWithTimes required')
    #     return v


class SchoolBlocksOnDayWithTimes(Dict[int, ScheduleWithTimes]):
    def __init__(self):
        super().__init__()
        self.update(
            {
                # 0 : [SchoolBlock.A, SchoolBlock.ADV, SchoolBlock.B, SchoolBlock.C, SchoolBlock.D, SchoolBlock.E],
                0: ScheduleWithTimes(
                    [
                        BlockWithTimes(
                            block=SchoolBlock.A,
                            startTime=time(hour=9, minute=0),
                            endTime=time(hour=10, minute=5),
                        ),
                        BlockWithTimes(
                            block=SchoolBlock.ADV,
                            startTime=time(hour=10, minute=10),
                            endTime=time(hour=10, minute=30),
                        ),
                        BlockWithTimes(
                            block=SchoolBlock.B,
                            startTime=time(hour=10, minute=35),
                            endTime=time(hour=11, minute=40),
                        ),
                        BlockWithTimes(
                            block=SchoolBlock.C,
                            startTime=time(hour=11, minute=45),
                            endTime=time(hour=13, minute=25),
                            lunches=Lunches(
                                [
                                    Lunch(
                                        lunch=LunchBlock.L1,
                                        startTime=time(hour=11, minute=45),
                                        endTime=time(hour=12, minute=15),
                                    ),
                                    Lunch(
                                        lunch=LunchBlock.L2,
                                        startTime=time(hour=12, minute=20),
                                        endTime=time(hour=12, minute=50),
                                    ),
                                    Lunch(
                                        lunch=LunchBlock.L3,
                                        startTime=time(hour=12, minute=55),
                                        endTime=time(hour=13, minute=25),
                                    ),
                                ]
                            ),
                        ),
                        BlockWithTimes(
                            block=SchoolBlock.D,
                            startTime=time(hour=13, minute=30),
                            endTime=time(hour=14, minute=35),
                        ),
                        BlockWithTimes(
                            block=SchoolBlock.E,
                            startTime=time(hour=14, minute=40),
                            endTime=time(hour=15, minute=45),
                        ),
                    ]
                ),
                1: ScheduleWithTimes(
                    [
                        BlockWithTimes(
                            block=SchoolBlock.A,
                            startTime=time(hour=9, minute=0),
                            endTime=time(hour=10, minute=15),
                        ),
                        BlockWithTimes(
                            block=SchoolBlock.B,
                            startTime=time(hour=10, minute=20),
                            endTime=time(hour=11, minute=35),
                        ),
                        BlockWithTimes(
                            block=SchoolBlock.F,
                            startTime=time(hour=11, minute=40),
                            endTime=time(hour=13, minute=20),
                            lunches=Lunches(
                                [
                                    Lunch(
                                        lunch=LunchBlock.L1,
                                        startTime=time(hour=11, minute=40),
                                        endTime=time(hour=12, minute=10),
                                    ),
                                    Lunch(
                                        lunch=LunchBlock.L2,
                                        startTime=time(hour=12, minute=15),
                                        endTime=time(hour=12, minute=45),
                                    ),
                                    Lunch(
                                        lunch=LunchBlock.L3,
                                        startTime=time(hour=12, minute=50),
                                        endTime=time(hour=13, minute=20),
                                    ),
                                ]
                            ),
                        ),
                        BlockWithTimes(
                            block=SchoolBlock.G,
                            startTime=time(hour=13, minute=25),
                            endTime=time(hour=14, minute=30),
                        ),
                        BlockWithTimes(
                            block=SchoolBlock.EXTRA,
                            startTime=time(hour=14, minute=35),
                            endTime=time(hour=15, minute=25),
                        ),
                    ]
                ),
                2: ScheduleWithTimes(
                    [
                        BlockWithTimes(
                            block=SchoolBlock.C,
                            startTime=time(hour=9, minute=0),
                            endTime=time(hour=10, minute=15),
                        ),
                        BlockWithTimes(
                            block=SchoolBlock.WIN,
                            startTime=time(hour=10, minute=20),
                            endTime=time(hour=11, minute=10),
                        ),
                        BlockWithTimes(
                            block=SchoolBlock.D,
                            startTime=time(hour=11, minute=15),
                            endTime=time(hour=1, minute=5),
                            lunches=Lunches(
                                [
                                    Lunch(
                                        lunch=LunchBlock.L1,
                                        startTime=time(hour=11, minute=15),
                                        endTime=time(hour=11, minute=45),
                                    ),
                                    Lunch(
                                        lunch=LunchBlock.L2,
                                        startTime=time(hour=11, minute=55),
                                        endTime=time(hour=12, minute=25),
                                    ),
                                    Lunch(
                                        lunch=LunchBlock.L3,
                                        startTime=time(hour=12, minute=35),
                                        endTime=time(hour=13, minute=5),
                                    ),
                                ]
                            ),
                        ),
                        BlockWithTimes(
                            block=SchoolBlock.E,
                            startTime=time(hour=13, minute=10),
                            endTime=time(hour=14, minute=25),
                        ),
                        BlockWithTimes(
                            block=SchoolBlock.F,
                            startTime=time(hour=14, minute=30),
                            endTime=time(hour=15, minute=45),
                        ),
                    ]
                ),
                3: ScheduleWithTimes(
                    [
                        BlockWithTimes(
                            block=SchoolBlock.A,
                            startTime=time(hour=9, minute=0),
                            endTime=time(hour=10, minute=15),
                        ),
                        BlockWithTimes(
                            block=SchoolBlock.B,
                            startTime=time(hour=10, minute=20),
                            endTime=time(hour=11, minute=35),
                        ),
                        BlockWithTimes(
                            block=SchoolBlock.G,
                            startTime=time(hour=11, minute=40),
                            endTime=time(hour=13, minute=30),
                            lunches=Lunches(
                                [
                                    Lunch(
                                        lunch=LunchBlock.L1,
                                        startTime=time(hour=11, minute=40),
                                        endTime=time(hour=12, minute=10),
                                    ),
                                    Lunch(
                                        lunch=LunchBlock.L2,
                                        startTime=time(hour=12, minute=20),
                                        endTime=time(hour=12, minute=50),
                                    ),
                                    Lunch(
                                        lunch=LunchBlock.L3,
                                        startTime=time(hour=13, minute=0),
                                        endTime=time(hour=13, minute=30),
                                    ),
                                ]
                            ),
                        ),
                        BlockWithTimes(
                            block=SchoolBlock.E,
                            startTime=time(hour=13, minute=35),
                            endTime=time(hour=14, minute=50),
                        ),
                        BlockWithTimes(
                            block=SchoolBlock.WIN,
                            startTime=time(hour=14, minute=55),
                            endTime=time(hour=15, minute=45),
                        ),
                    ]
                ),
                4: ScheduleWithTimes(
                    [
                        BlockWithTimes(
                            block=SchoolBlock.C,
                            startTime=time(hour=9, minute=0),
                            endTime=time(hour=10, minute=15),
                        ),
                        BlockWithTimes(
                            block=SchoolBlock.WIN,
                            startTime=time(hour=10, minute=20),
                            endTime=time(hour=11, minute=10),
                        ),
                        BlockWithTimes(
                            block=SchoolBlock.D,
                            startTime=time(hour=11, minute=15),
                            endTime=time(hour=13, minute=5),
                            lunches=Lunches(
                                [
                                    Lunch(
                                        lunch=LunchBlock.L1,
                                        startTime=time(hour=11, minute=15),
                                        endTime=time(hour=11, minute=45),
                                    ),
                                    Lunch(
                                        lunch=LunchBlock.L2,
                                        startTime=time(hour=11, minute=55),
                                        endTime=time(hour=12, minute=25),
                                    ),
                                    Lunch(
                                        lunch=LunchBlock.L3,
                                        startTime=time(hour=12, minute=35),
                                        endTime=time(hour=13, minute=5),
                                    ),
                                ]
                            ),
                        ),
                        BlockWithTimes(
                            block=SchoolBlock.F,
                            startTime=time(hour=13, minute=10),
                            endTime=time(hour=14, minute=25),
                        ),
                        BlockWithTimes(
                            block=SchoolBlock.G,
                            startTime=time(hour=14, minute=30),
                            endTime=time(hour=15, minute=45),
                        ),
                    ]
                ),
                5: ScheduleWithTimes(),
                6: ScheduleWithTimes(),
            }
        )

        def __repr__(self):
            return str(self.__dict__)
