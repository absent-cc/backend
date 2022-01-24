WEEKDAY_TITLE = ["DoW", "Day of Week"]
WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday", "MON", "TUES", "WEDS", "THURS", "FRI", "SAT", "SUN"]

TIME_TITLE = ["Day"]
TIMES = ["All Day", "Partial Day AM", "Partial Day PM", "Partial Day", "Partial AM", "Partial PM"]

LAST_NAME_TITLE = ["Last Name", "Last"]

FIRST_NAME_TITLE = ["First Name", "First"]

CS_NAME_TITLE = ["Name"]

NOTES_TITLE = ["Notes", "Notes to Student"]
NOTES_KEYWORDS = ["cancelled", "canceled", "block", "schoology", "classes", "as usual"]

POSITION_TITLE = ["Position"]
POSITION_KEYWORDS = ["Teacher", "Counselor"]

DATE_TITLE = ["Date"]

def is_date(str):
    slash_split = str.split("/")
    if len(slash_split) != 3:
        return False

    for segment in slash_split:
        if not segment.isnumeric():
            return False

    return True

def fuzzy_split(name):
    lower_name = name.lower()
    no_hyphen = lower_name.replace("-", " ")
    split = no_hyphen.split(" ")
    return split

def is_fuzzy_match(first, second):
    split_first = fuzzy_split(first)
    split_second = fuzzy_split(second)
    
    # # First names must match
    # if split_first[0] != split_second[0]:
    #     return False
    
    # iterate through shorter list
    for subname in min(split_first, split_second):
        # every element of the shorter one must be in the longer one
        if subname not in max(split_first, split_second):
            return False
    
    return True

# the thing about 
def is_first_name(name, teacher_table):
    for [first, _] in teacher_table:
        if not is_fuzzy_match(name, first):
            return False
    
    return True

def is_last_name(name, teacher_table):
    for [_, last] in teacher_table:
        if not is_fuzzy_match(name, last):
            return False
    
    return True


def column_detector(column, teacher_table):
    confidence = {
        "first_name": 0,
        "last_name": 0,
        "cs_name": 0,
        "weekday": 0,
        "date": 0,
        "notes": 0,
        "time": 0,
        "position": 0,
    }
    # keep track of which row it finds the title in
    title_row = -1

    for i, item in enumerate(column):
        found = True

        # it is most common to find the title in the first column, that's pretty strong
        points = i == 0 if 1.5 else 1.0

        if item in FIRST_NAME_TITLE:
            confidence["first_name"] += points
        elif item in LAST_NAME_TITLE:
            confidence["last_name"] += points
        elif item in CS_NAME_TITLE:
            confidence["cs_name"] += points
        elif item in TIME_TITLE:
            confidence["time"] += points
        elif item in DATE_TITLE:
            confidence["date"] += points
        elif item in NOTES_TITLE:
            confidence["notes"] += points
        elif item in POSITION_TITLE:
            confidence["position"] += points
        else:
            found = False
        
        if found:
            # remove title from the column
            title_row = i
            del column[title_row]
            break

    # the column detector will now check the first up to five items of the column to see what formats they match
    max_check_length = 10
    item_checker_length = min(max_check_length + 1, len(column)) - 1

    # if all items match, then that's pretty good
    item_points = 2.0 / item_checker_length

    for i in range(1, item_checker_length + 1): # Get the next five items
        item = column[i]

        # add confidence points if matching info is found

        if item in TIMES:
            confidence["time"] += item_points

        if item in WEEKDAYS:
            confidence["weekday"] += item_points

        for kw in NOTES_KEYWORDS:
            if kw in column[i]:
                confidence["notes"] += item_points
        
        # notes and only notes are empty sometimes
        if len(item) == 0:
            confidence["notes"] += item_points

        for kw in POSITION_KEYWORDS:
            if kw in column[i]:
                confidence["position"] += item_points

        if is_date(item):
            confidence["date"] += item_points
        
        if is_first_name(item, teacher_table):
            confidence["first_name"] += item_points

        if is_last_name(item, teacher_table):
            confidence["last_name"] += item_points
        
        # check for comma separated name
        split_by_comma = item.split(",")
        
        # there will only be one comma
        if len(split_by_comma) == 2:
            # having a comma gives half credit
            confidence["cs_name"] += item_points / 2.0

            # the second item past the comma should be one word long first name
            stripped_second = split_by_comma[1].strip()
            if len(stripped_second.split(" ")) == 1:
                confidence["cs_name"] += item_points

    # these are very high confidence values
    if confidence["date"] >= 1.5:
        confidence["date"] = 100.0

    if confidence["weekday"] >= 1.5:
        confidence["weekday"] = 100.0


    return confidence, title_row


def table_analysis(table):
    # Build confidence map
    confidence_map = []
    for col in table:
        confidence_map.append(column_detector(col))
    
    available_cols = list(range(len(table))) # get list of all not yet parsed cols

    # starting ruling out columns with confidence > 1

    # date parsing is probably most strong
    highest_date = [1.0, -1]
    for index, confidence in enumerate(confidence_map):
        if confidence["date"] >= highest_date[0]:
            highest_date[1] = index
    try:
        available_cols.remove(highest_date[1])
    except ValueError:
        print("No date column found")

    # weekday parsing is pretty good
    highest_dow = [1.0, -1]
    for index, confidence in enumerate(confidence_map):
        if confidence["weekday"] >= highest_dow[0]:
            highest_dow[1] = index
    try:
        available_cols.remove(highest_dow[1])
    except ValueError:
        print("No DoW column found")

    
