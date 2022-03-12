from bs4 import BeautifulSoup
import requests

BASE_URL = "https://schoology.newton.k12.ma.us/school/40673949/faculty"

cookies = 
page = requests.get(BASE_URL)

print(page.text)