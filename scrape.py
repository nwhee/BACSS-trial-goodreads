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
list_of_reviews = []

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
            send_request(row[0], row[1], row[2])
    write_to_csv()

def send_request(book_id, title, author):
    """
    Sends get requests to Goodreads to find the link for the given book and extract book review data

    Args:
        book_id (int): The id of the current book
        title (str): The title of the current book
        author (str): The author of the current book
    """

    # Rate-limiting delay
    time.sleep(1)

    # debug: checks if there is a comma in author and splits it if it does
    # came from the case where the translator and author were listed
    if "," in author:
        temp_author = author.split(",")
        author = temp_author[1]

    payload = {"q": (title, author)}
    # get request to mimic searching for the title + author
    r = requests.get("https://www.goodreads.com/search?utf8=✓", params = payload, headers = HEADERS)

    # Parses the text using Beautiful Soup
    doc = BeautifulSoup(r.text, "html.parser")
    book_tags = doc.find_all("a", class_ = "bookTitle")
    book_authors = doc.find_all("a", class_ = "authorName")
    for book_tag, book_author in zip(book_tags,book_authors):
        # temp_title = book_tag.span.text
        # stay_title = book_tag.span.text
        # temp_author = book_author.span.text

        # debug: dealing with Goodreads titles containing extra information, such as series
        # if "(" in temp_title:
        #     split_temp_title = temp_title.split("(")
        #     temp_title = split_temp_title[0]
        # if "[" in temp_title:
        #     split_temp_title = temp_title.split("[")
        #     temp_title = split_temp_title[0]
        # if ":" in temp_title:
        #     split_temp_title = temp_title.split(":")
        #     temp_title = split_temp_title[0]
        # if SequenceMatcher(None, stay_title, title).ratio() > 0.70 or SequenceMatcher(None, temp_title, title).ratio() > 0.70:
        # # if SequenceMatcher(None, temp_title, title).ratio() > 0.40:
        #     flipped_author = flip_author(author)
        #     if SequenceMatcher(None, temp_author, author).ratio() > 0.80 or SequenceMatcher(None, temp_author, flipped_author).ratio() > 0.80:
        #         book_url = book_tag["href"]
        #         break

        # extracting the link for the book's page
        book_url = book_tag["href"]
        break 

    time.sleep(1)
    book_r = requests.get(f"{goodreads_url}{book_url}")
    book_doc = BeautifulSoup(book_r.text, "html.parser")
    book_title = book_doc.find("h1", class_ = "Text Text__title1").text
    book_author = book_doc.find("span", class_ = "ContributorLink__name").text

    # flipped_author = flip_author(author)
    # assert(SequenceMatcher(None, book_title, title).ratio() > 0.60)
    # assert(SequenceMatcher(None, book_author, author).ratio() > 0.80 or SequenceMatcher(None, book_author, flipped_author).ratio() > 0.80)

    review_tags = book_doc.find_all("article", class_ = "ReviewCard")
    for review in review_tags:
        review_text = review.find("span", class_ = "Formatted")
        try:
            review_rating = review.find("span", class_ = "RatingStars RatingStars__small")["aria-label"][7]
        except:
            review_rating = 3
        reviewer_id = review.find("div", class_ = "ReviewerProfile__name").a["href"]
        review_date = review.find("span", class_ = "Text Text__body3").a.text
        try:
            social = review.find("div", class_ = "SocialFooter__statsContainer").find_all("span", class_ = "Button__labelItem")
            review_upvotes = social[0].text.split(" ")[0]
            review_comments = social[1].text.split(" ")[0]
        except:
            review_upvotes = 0
            review_comments = 0

        review_dict = {
            "book_id": book_id,
            "author": author,
            "review_text": review_text,
            "review_rating": review_rating,
            "reviewer_id": reviewer_id,
            "review_upvotes": review_upvotes,
            "review_date": review_date,
            "review_comments": review_comments,
        }

        list_of_reviews.append(review_dict)


def write_to_csv():
    """
    Writes the list of review dicts to a csv file
    """

    csv_filename = "reviews_output.csv"
    fieldnames = ["book_id",
            "author",
            "review_text",
            "review_rating",
            "reviewer_id",
            "review_upvotes",
            "review_date",
            "review_comments"]
    
    with open(csv_filename, mode = "w", newline = "") as f:
        writer = csv.DictWriter(f, fieldnames = fieldnames)
        writer.writeheader()
        writer.writerows(list_of_reviews)

def flip_author(author) -> str: 
    """
    Changes the given string by moving the first word to the end

    Args:
        author (str): The given string to be flipped
    """
    
    names = author.split(" ")
    temp_name = names[0]
    names.pop(0)
    names.append(temp_name)
    # flipped_name = " ".join(names[::-1])
    flipped_name = " ".join(names)
    return flipped_name


read_csv()