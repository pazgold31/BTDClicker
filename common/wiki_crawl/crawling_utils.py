import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent


def get_page_soup(url: str) -> BeautifulSoup:
    fake_ua = UserAgent()
    page = requests.get(url, headers={"User-Agent": fake_ua.chrome})
    return BeautifulSoup(page.content, "html.parser")
