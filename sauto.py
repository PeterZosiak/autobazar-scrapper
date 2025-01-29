import re
import time
import csv
import phonenumbers

from bs4 import BeautifulSoup
from validate_email import validate_email
from urllib.parse import urlsplit
from selenium import webdriver
from selenium.webdriver.common.by import By


sellers_links = []
options = webdriver.FirefoxOptions()
options.add_argument("--headless")
browser = webdriver.Firefox(options=options)


pattern_web = re.compile(
    r"^(?:http|ftp)s?://"
    r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|"
    r"localhost|"
    r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"
    r"(?::\d+)?"
    r"(?:/?|[/?]\S+)$",
    re.IGNORECASE,
)

browser.get("https://www.sauto.cz/")
browser.add_cookie({"name": "euconsent-v2", "value": "CQL_lsAQL_lsAD3ACQCSBaFsAP_gAEPgAATIJNQIwAFAAQAAqABkAEAAKAAZAA0ACSAEwAJwAWwAvwBhAGIAQEAggCEAEUAI4ATgAoQBxADuAIQAUgA04COgE2gKkAW4AvMBjID_AIDgRmAk0BecBIACoAIAAZAA0ACYAGIAPwAhABHACcAGaAO4AhABFgE2gKkAW4AvMAAA.YAAAAAAAAWAA", "domain": ".sauto.cz"})
browser.add_cookie({"name": "udid", "value": "Yf1VI-ppfX3vAoBT_8Ka8i-1us_IM7I6@1738125480631@1738125480631", "domain": ".sauto.cz"})

sellers = []

# TODO: Change range based on offers count / 20 (20 per page) 
for i in range(1, 72):
  print("Page: " + str(i))
  browser.get("https://www.sauto.cz/seznam-prodejcu/?page=" + str(i))
  html = browser.page_source
  page_soup = BeautifulSoup(html, features="html.parser")
  sellers_heads = page_soup.find_all("div", {"class": "c-premise-item"})

  for seller in sellers_heads:
    link = seller.find("a")["href"]
    sellers_links.append(link)
    print(link)


for seller_link in sellers_links:
  print("Seller: " + seller_link)
  page = browser.get(seller_link)
  time.sleep(1)
  html = browser.page_source
  seller_soup = BeautifulSoup(html, features="html.parser")
  
  try:
    browser.find_element(By.CSS_SELECTOR, "button.c-seller-card__show-phone-button").click()
    browser.find_element(By.CSS_SELECTOR, "button.c-seller-card__show-email-button").click()

    html = browser.page_source
    seller_soup = BeautifulSoup(html, features="html.parser")

    phones = []
    emails = []
    websites = []

    seller_name = seller_soup.find("div", {"class": "c-seller-contact-header__title"}).find("h1").text
    number_of_cars_text = seller_soup.find("div", {"class": "c-item-list__count"}).text
    number_of_cars = int(re.search(r'\d+', number_of_cars_text).group())
    address = seller_soup.find("div", {"class": "c-seller-card__locality-text c-seller-card__locality-text--in-seller-description"}).text

    email_links = seller_soup.find_all("a", {"class": "c-seller-card__emails-list--email"})
    for email_link in email_links:
        emails.append(email_link.text)

    phone_links = seller_soup.find_all("a", {"class": "c-seller-card__phones-list--number"})
    for phone_link in phone_links:
        phones.append(phone_link.text)

    website_links = seller_soup.find_all("a", {"class": "c-seller-card__web-link"})
    for website_link in website_links:
        websites.append(website_link["href"])

    sellers.append({
      "link": seller_link,
      "name": seller_name,
      "address": address,
      "number of cars": number_of_cars,
      "phone 1": phones[0] if len(phones) > 0 else "",
      "phone 2": phones[1] if len(phones) > 1 else "",
      "phone 3": phones[2] if len(phones) > 2 else "",
      "email 1": emails[0] if len(emails) > 0 else "",
      "email 2": emails[1] if len(emails) > 1 else "",
      "email 3": emails[2] if len(emails) > 2 else "",
      "website 1": websites[0] if len(websites) > 0 else ""})
  except:
    pass

  


print(sellers)
csv_file = open("sauto.csv", "w", encoding="utf-8", newline="")
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
    ]
)
for seller in sellers:
    writer.writerow(
        [
            seller["link"],
            seller["name"],
            seller["address"],
            seller["number of cars"],
            seller["phone 1"],
            seller["phone 2"],
            seller["phone 3"],
            seller["email 1"],
            seller["email 2"],
            seller["website 1"],
        ]
    )
browser.quit()
csv_file.close()
