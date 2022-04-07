import csv
from typing import List, Tuple

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://schoology.newton.k12.ma.us/school/15424565/faculty"

# South: https://schoology.newton.k12.ma.us/school/40673949/faculty
# North: https://schoology.newton.k12.ma.us/school/15424565/faculty

cookies = {
    "SESS57ef7b3f45b691c5d2133f3db8eadd7e": "REPLACE ME WITH COOKIE!"  # Replace with cookies
}


def pullPage(n: int):
    addOnQuery = f"?page={n}"
    fullURL = BASE_URL + addOnQuery
    page = requests.get(fullURL, cookies=cookies)

    soup = BeautifulSoup(page.content, "html.parser")
    raw_HTML_teachers = soup.findAll(class_="faculty-name")

    names: List[Tuple[str, str]] = []

    for entry in raw_HTML_teachers:
        name = getNameFromHTMLEntry(entry)
        names.append(name)

    return names


def getNameFromHTMLEntry(entry) -> Tuple[str, str]:  # First Last
    a_tag = entry.find("a")
    split1 = str(a_tag).split(">")[1]
    split2 = split1.split("<")[0]

    nameSpaceSplit = split2.split(" ", maxsplit=1)
    first = nameSpaceSplit[0]
    last = nameSpaceSplit[1]

    return first, last


def writeToCSV(names: List[Tuple[str, str]]):
    with open("tools/teachers/schoologyFaculty/NNHS_faculty.csv", "w") as f:
        csv_file = csv.writer(f)
        csv_file.writerow(["First", "Last"])
        for name in names:
            csv_file.writerow([name[0], name[1]])


def run():
    names: List[Tuple[str, str]] = []
    for i in range(0, 25):
        page_names = pullPage(i)
        for name in page_names:
            names.append(name)
    writeToCSV(names)


run()
