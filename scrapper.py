import re
import time
import csv
import phonenumbers

from bs4 import BeautifulSoup
from validate_email import validate_email
from urllib.parse import urlsplit
from selenium import webdriver


sellers_links = []
options = webdriver.ChromeOptions()
options.add_argument("--headless")
browser = webdriver.Chrome(options=options)

pattern_web = re.compile(
    r"^(?:http|ftp)s?://"
    r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|"
    r"localhost|"
    r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"
    r"(?::\d+)?"
    r"(?:/?|[/?]\S+)$",
    re.IGNORECASE,
)


browser.get("https://www.autobazar.eu/predajcovia-aut/")
time.sleep(2)
html = browser.page_source
root_soup = BeautifulSoup(html, features="html.parser")

last_page_number = root_soup.find_all(
    "a",
    {
        "class": "my-0 mr-0 ml-2 inline-block h-[40px] w-auto min-w-[40px] rounded-lg bg-none p-0 text-center text-[14px] font-semibold leading-10 text-white transition-all duration-[0.2s] ease-in-out disabled:cursor-not-allowed disabled:bg-none disabled:text-white/60 disabled:hover:bg-inherit cursor-pointer hover:bg-[#0a84ff] hover:text-white"
    },
)[1].text

print("Last page number: " + last_page_number)

sellers_page_url = "https://www.autobazar.eu/predajcovia-aut/?page="
for i in range(1, 2):
    browser.get(sellers_page_url + str(i))
    print("Page: " + sellers_page_url + str(i))

    time.sleep(2)
    html = browser.page_source
    page_soup = BeautifulSoup(html, features="html.parser")

    sellers_heads = page_soup.find_all("h3")
    for seller in sellers_heads:
        sellers_links.append(seller.find("a")["href"])


sellers = []
# Testing
# sellers_links.append("https://autopolaksro33333333.autobazar.eu")
for seller_link in sellers_links:
    page = browser.get(seller_link)
    print("Seller: " + seller_link)
    time.sleep(2)
    html = browser.page_source
    soup = BeautifulSoup(html, "html.parser")

    name = soup.find("h1").text.strip().replace("\n", "") if soup.find("h1") else ""
    address = (
        soup.find("address").text.replace("\n", "") if soup.find("address") else ""
    )

    contacts = []
    contacts = soup.find_all(
        "a", {"class": "group flex items-center hover:cursor-pointer"}
    )

    if len(contacts) == 0:
        # TODO: find another way to get contacts
        contact_list = soup.find("ul", {"class": "p-contacts"})
        if contact_list is not None:
            contacts = contact_list.find_all("a")

    phones = []
    emails = []
    websites = []

    for contact in contacts:
        link = contact["href"]
        link = link.replace("mailto:", "").replace("tel:", "")

        is_phone_number = False
        try:
            my_number = phonenumbers.parse(link, "SK")
            is_phone_number = phonenumbers.is_valid_number(my_number)
        except phonenumbers.NumberParseException:
            pass

        if is_phone_number:
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

    if number_of_cars is None:
        stats_list = soup.find("ul", {"class": "p-stats"})
        if stats_list is not None:
            number_of_cars = stats_list.find("span", {"class": "p-link"})

    if number_of_cars is not None:
        cars = number_of_cars = (
            number_of_cars.text.replace(" ", "")
            .replace("\n", "")
            .replace("Inzerátov:", "")
            if number_of_cars
            else ""
        )
    else:
        cars = 0

    print(name)
    print(address)
    print(phones)
    print(emails)
    print(websites)
    print(cars)
    sellers.append(
        {
            "link": seller_link,
            "name": name,
            "address": address,
            "cars": cars,
            "phone 1": phones[0] if len(phones) > 0 else "",
            "phone 2": phones[1] if len(phones) > 1 else "",
            "phone 3": phones[2] if len(phones) > 2 else "",
            "email 1": emails[0] if len(emails) > 0 else "",
            "email 2": emails[1] if len(emails) > 1 else "",
            "website 1": websites[0] if len(websites) > 0 else "",
            "website 2": websites[1] if len(websites) > 1 else "",
        }
    )


csv_file = open("autobazareu.csv", "w", encoding="utf-8", newline="")
writer = csv.writer(csv_file)
writer.writerow(
    [
        "Link",
        "Name",
        "Address",
        "Cars",
        "Phone 1",
        "Phone 2",
        "Phone 3",
        "Email 1",
        "Email 2",
        "Website 1",
        "Website 2",
    ]
)
for seller in sellers:
    writer.writerow(
        [
            seller["link"],
            seller["name"],
            seller["address"],
            seller["cars"],
            seller["phone 1"],
            seller["phone 2"],
            seller["phone 3"],
            seller["email 1"],
            seller["email 2"],
            seller["website 1"],
            seller["website 2"],
        ]
    )
csv_file.close()
