import re
import time

from bs4 import BeautifulSoup
from validate_email import validate_email
from urllib.parse import urlsplit
from selenium import webdriver

sellers_links = []
options = webdriver.ChromeOptions()
options.add_argument("--headless")
browser = webdriver.Chrome(options=options)

pattern_phone = r"^\+?\d{1,3}[\s-]?\d{3}[\s-]?\d{3}[\s-]?\d{3}$"
pattern_web = re.compile(
    r"^(?:http|ftp)s?://"  # Scheme
    r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|"  # Domain
    r"localhost|"  # Localhost
    r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # IP address
    r"(?::\d+)?"  # Port (optional)
    r"(?:/?|[/?]\S+)$",
    re.IGNORECASE,
)  # Path and query (optional)


for i in range(1, 2):
    browser.get("https://www.autobazar.eu/predajcovia-aut/?page=" + str(i))
    time.sleep(5)
    html = browser.page_source
    root_soup = BeautifulSoup(html, features="html.parser")

    sellers = root_soup.find_all("h3")
    for seller in sellers:
        sellers_links.append(seller.find("a")["href"])

# Testing
# print(sellers_links)
# sellers_links.append("https://aaaautosokolov.autobazar.eu/")
for seller_link in sellers_links:
    page = browser.get(seller_link)
    time.sleep(2)
    html = browser.page_source
    soup = BeautifulSoup(html, "html.parser")

    name = soup.find("h1")
    address = soup.find("address")

    contacts = soup.find_all(
        "a", {"class": "group flex items-center hover:cursor-pointer"}
    )

    if contacts is []:
        # TODO: find another way to get contacts
        contacts = "aaa"

    phones = []
    emails = []
    websites = []

    for contact in contacts:
        link = contact["href"]
        link = link.replace("mailto:", "").replace("tel:", "")

        if re.match(pattern_phone, link):
            phones.append(link)
        elif validate_email(link):
            emails.append(link)
        elif re.match(pattern_web, link):
            websites.append(link)

    number_of_cars = soup.find(
        "div",
        {
            "class": "flex items-center text-[14px] font-normal leading-[1.40] text-[rgba(235,235,245,.6)] underline"
        },
    )

    if number_of_cars is not None:
        cars = number_of_cars = (
            number_of_cars.text.replace(" ", "")
            .replace("\n", "")
            .replace("Inzerátov:", "")
        )
    else:
        cars = 0

    print(name.text)
    print(address.text)
    print(phones)
    print(emails)
    print(websites)
    print(cars)
