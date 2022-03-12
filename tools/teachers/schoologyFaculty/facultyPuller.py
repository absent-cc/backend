from bs4 import BeautifulSoup
import requests
from requests.structures import CaseInsensitiveDict

BASE_URL = "https://schoology.newton.k12.ma.us/school/40673949/faculty"

cookies = {
    "SESS57ef7b3f45b691c5d2133f3db8eadd7e": "cb78361e423892687e22796433dc4f75"
    }

def pullPage(n: int):
    addOnQuery = f"?page={n}"
    fullURL = BASE_URL + addOnQuery
    page = requests.get(fullURL, cookies=cookies)
    
    soup = BeautifulSoup(page.content, "html.parser")
    raw_HTML_teachers = soup.findAll(class_="faculty-name")
    for entry in raw_HTML_teachers:
        getNameFromHTMLEntry(entry)

def getNameFromHTMLEntry(entry) -> (str, str): # First Last
    a_tag = entry.find("a")
    split1 = str(a_tag).split(">")[1]
    split2 = split1.split("<")[0]

    nameSpaceSplit = split2.split(" ")
    first = nameSpaceSplit[0]
    last = nameSpaceSplit[1]

    print(first, last) 
    return first, last

