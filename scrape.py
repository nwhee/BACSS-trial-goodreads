import csv
import requests
import time
from bs4 import BeautifulSoup
from difflib import SequenceMatcher

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64)...",
    "Accept-Language": "en-US, en;q=0.5",
}

goodreads_url = "https://www.goodreads.com"

def read_csv():
    """
    Reads the given goodreads_list.csv file
    """

    with open("goodreads_list.csv") as f:
        reader = csv.reader(f)
        for row in reader:
            # skipping the first row
            if "Book ID" in row:
                continue
            send_request(row[1], row[2])
            break

def send_request(title, author):
    time.sleep(2)
    payload = {"q": (title, author)}
    r = requests.get("https://www.goodreads.com/search?utf8=✓", params = payload, headers = HEADERS)

    doc = BeautifulSoup(r.text, "html.parser")
    book_tag = doc.find("a", class_ = "bookTitle")
    book_url = book_tag["href"]

    time.sleep(2)
    book_r = requests.get(f"{goodreads_url}{book_url}")
    book_doc = BeautifulSoup(book_r.text, "html.parser")
    book_title = book_doc.find("h1", class_ = "Text Text__title1").text
    book_author = book_doc.find("span", class_ = "ContributorLink__name").text
    assert(SequenceMatcher(None, book_title, title).ratio() > 0.80)
    assert(SequenceMatcher(None, book_author, author).ratio() > 0.80)

    review_tags = book_doc.find_all("article", class_ = "ReviewCard")
    
    # print(len(review_tags))


read_csv()