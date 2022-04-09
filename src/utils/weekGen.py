from calendar import week
import datetime
from typing import List

def weekDayGenerator(year: int, weekNumber: int):
    data: List[datetime.date] = []
    for weekday in range (1, 6):
        date = datetime.datetime.strptime(f'{year}-W{weekNumber}' + f'-{weekday}', "%Y-W%W-%w") # %W is week number, %w is weekday
        data.append(date.date()) # Cast to date

    return data

for i in weekDayGenerator(2022, 13):
    print(i)
