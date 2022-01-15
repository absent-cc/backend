from fastapi import HTTPException
from dataStructs import *

class HelperFunctions:
    def __init__(self):
        pass

    def raiseError(self, code, error, type: ErrorType):
        raise HTTPException(
            status_code=code,
            detail=f"{str(type)} - {error}"
        )   
    
    def returnStatus(self, message: str):
        return {'detail': message}

    # def scheduleToSchema(self, schedule: Schedule):
    #     schema = ScheduleSchema()
    #     if schedule == None:
    #         return None
    #     for block in schedule:
    #         teachers = schedule[block]
    #         teacherList = list()
    #         if teachers == None:
    #             continue
    #         for teacher in teachers:
    #             teacherList.append(Teacher(first=teacher.first, last=teacher.last, school=teacher.school, tid=teacher.tid))
    #         setattr(schema, BlockMapper()[block], teacherList)
    #     return schema
                
    # def schemaToSchedule(self, student, schedule: ScheduleSchema):
    #     if schedule == None:
    #         return None
    #     dictSchedule = dict(schedule)
    #     scheduleObject = Schedule()
    #     for block in dictSchedule:
    #         enumblock = ReverseBlockMapper()[block]
    #         teachers = ClassTeachers()
    #         if isinstance(dictSchedule[block], ResponseStatus):
    #             print(block)
    #             pass
    #         elif dictSchedule[block] != None:
    #             for teacher in dictSchedule[block]:
    #                 try:
    #                     #castedTeacher = Teacher(teacher[0], teacher[1], student.school)
    #                     teachers.add(Teacher(first=teacher.first, last=teacher.last, school=teacher.school))
    #                 except BaseException as error:
    #                     self.raiseError(422, error, ErrorType.PAYLOAD)
    #             if teachers != ClassTeachers():
    #                 scheduleObject[enumblock] = teachers
    #     return scheduleObject