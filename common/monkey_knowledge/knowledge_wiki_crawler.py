from typing import Dict, Tuple
from urllib.parse import urljoin

import bs4
from PIL import Image

from common.user_files import get_knowledge_images_dir
from common.wiki_crawl.crawling_utils import get_page_soup, read_image
from common.wiki_crawl.wiki_consts import BASE_WIKI_URL

KNOWLEDGE_PAGE_URL = urljoin(BASE_WIKI_URL, r"wiki/Monkey_Knowledge_(BTD6)")
KNOWLEDGE_IMAGE_SIZE = (122, 122)


def crawl_table(table_body: bs4.Tag) -> Dict[str, str]:
    output = {}
    rows = table_body.find_all('tr')
    for row in rows[1:]:  # Skip the headlines
        cols = row.find_all('td')
        knowledge_name = cols[0].text.strip()
        knowledge_picture_url = cols[0].next.attrs["href"]
        output[knowledge_name] = knowledge_picture_url

    return output


def read_images(urls_dict: Dict[str, str]) -> Dict[str, Image.Image]:
    return {key: read_image(url) for key, url in urls_dict.items()}


def crawl_knowledge_pictures() -> Dict[str, Dict[str, Image.Image]]:
    urls_dict = {}
    soup = get_page_soup(url=KNOWLEDGE_PAGE_URL)
    tables = soup.find_all("table", class_="article-table")
    for table in tables:
        table_title = table.find_previous("h3").find(class_="mw-headline").text
        urls_dict[table_title] = crawl_table(table_body=table)

    return {k: read_images(urls_dict=v) for k, v in urls_dict.items()}


def resize_image(image: Image.Image, new_size: Tuple[int, int] = KNOWLEDGE_IMAGE_SIZE):
    image.thumbnail(size=new_size, resample=Image.LANCZOS)


def save_knowledge_pictures(total_dict: Dict[str, Dict[str, Image.Image]]):
    for category, pictures_dict in total_dict.items():
        for knowledge_name, picture in pictures_dict.items():
            output_path = (get_knowledge_images_dir(subdirectory=category) / knowledge_name).with_suffix(".png")
            resize_image(image=picture)
            picture.save(output_path, format="png")


def download_knowledge_pictures():
    save_knowledge_pictures(total_dict=crawl_knowledge_pictures())
