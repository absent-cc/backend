from datetime import date, timedelta
from typing import List

# Inclusive date range generator
def dateRangeGen(start: date, end: date) -> List[date]:
    dates = []
    curr = start
    while curr <= end:
        dates.append(curr)
        curr += timedelta(days=1)
    return dates

# if __name__ == "__main__":
#     print(dateRangeGen(date(2020, 1, 1), date(2020, 1, 10)))