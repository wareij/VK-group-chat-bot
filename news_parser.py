import requests
from bs4 import BeautifulSoup
import time

class News():
    date_now = time.strftime("%d.%m.%Y")
    base_url = "https://63.ru"
    post = ""
    n = 0

    full_url = f"{base_url}/search/?keywords=covid&sort=date&dateFrom={date_now}&dateTo={date_now}"
    response = requests.get(full_url)

    soup = BeautifulSoup(response.content, "lxml")
    teme = soup.find_all("h2", class_="GNjj")
    for title in teme:
        n += 1
        href = title.find("a", {"data-test" :"archive-record-header"}).get("href")
        post_url = base_url + href
        post += (str(n) + ". " + title.text + " :\n" + post_url + "\n")
