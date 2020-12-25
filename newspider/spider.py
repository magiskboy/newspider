import os
import typing as T
import logging
from pprint import pprint
from datetime import datetime
import asyncio
import httpx
from slugify import slugify
from bs4 import BeautifulSoup
import motor.motor_asyncio


logger = logging.getLogger('newspider.spider')
fmt = logging.Formatter('[%(asctime)-15s] %(message)s')
handler = logging.StreamHandler()
handler.setFormatter(fmt)
logger.addHandler(handler)
logger.setLevel(logging.INFO)


class SpiderBase:
    ROOT: str

    def __init__(self, mongo_uri):
        logger.info('DantriSpider is created')
        self.page_success = 0
        self.mongo_client = motor.motor_asyncio.AsyncIOMotorClient(
            mongo_uri,
            io_loop=asyncio.get_event_loop(),
        )

        self.db = self.mongo_client['newspider']

    async def get_list_post(self) -> T.Dict[str, str]:
        raise NotImplementedError

    async def fetch_page(self, path: str) -> T.Dict[str, T.Any]:
        raise NotImplementedError

    async def run(self):
        raise NotImplementedError

    def get_title_from_soup(self, soup) -> str:
        raise NotImplementedError

    def get_tags_from_soup(self, soup) -> T.List[str]:
        raise NotImplementedError

    def get_breadcrumb_from_soup(self, soup) -> T.List[str]:
        raise NotImplementedError

    def get_date_from_soup(self, soup) -> datetime:
        raise NotImplementedError

    def get_content_from_soup(self, soup) -> str:
        raise NotImplementedError

    async def save_to_storage(self, page):
        await self.db.posts.insert_one(page)


class DantriSpider(SpiderBase):
    ROOT = 'https://dantri.com.vn'

    async def get_list_post(self) -> str:
        class_item = '.news-item__title'

        async with httpx.AsyncClient() as c:
            resp = await c.get(self.ROOT)       #pylint: disable=E1101

        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, 'html.parser')
            items = soup.select(class_item)

            for item in items:
                title = item.get_text().strip()
                c = await self.db.posts.count_documents({'title': title})
                if c:
                    continue

                a = item.findChildren('a', recursive=False)
                if len(a) == 0:
                    continue

                path = a[0].get('href')

                yield path

    def get_title_from_soup(self, soup):
        title_node = soup.select_one('.dt-news__title')
        return title_node.get_text().strip()

    def get_breadcrumb_from_soup(self, soup):
        nodes = soup.select_one('.dt-breadcrumb').findChildren('a', recursive=True)
        return list(map(lambda x: x.get_text(), nodes))

    def get_tags_from_soup(self, soup):
        nodes = soup.select_one('.dt-news__tag-list').findChildren('a', recursive=True)
        return list(map(lambda x: x.get_text(), nodes))

    def get_date_from_soup(self, soup):
        dt_node = soup.select_one('.dt-news__time')
        dt_text = dt_node.get_text()
        dt_text = dt_text.split(',')
        if len(dt_text) > 1:
            dt_text = dt_text[1].strip()
            return datetime.strptime(dt_text, '%d/%m/%Y - %H:%M')

    def get_content_from_soup(self, soup):
        content_node = soup.select_one('.dt-news__content')
        return ''.join(str(x) for x in content_node.contents).strip()

    async def fetch_page(self, path: str) -> T.Dict[str, T.Any]:
        page = {}
        url = self.ROOT + path      #pylint: disable=E1101
        async with httpx.AsyncClient() as c:
            resp = await c.get(url)

            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, 'html.parser')

                title = self.get_title_from_soup(soup)
                page = {
                    'title': title,
                    'slug': slugify(title),
                    'path': path,
                    'categories': self.get_breadcrumb_from_soup(soup),
                    'date': self.get_date_from_soup(soup),
                    'content': self.get_content_from_soup(soup),
                    'tags': self.get_tags_from_soup(soup),
                }
            return page

    async def fetch_and_save(self, path: str):
        page = await self.fetch_page(path)
        await self.save_to_storage(page)

    async def run(self):
        fs = []
        async for path in self.get_list_post():
            f = asyncio.create_task(self.fetch_and_save(path))
            fs.append(f)

        await asyncio.wait(fs)
        self.page_success = 0
        for f in fs:
            exc = f.exception()
            if exc is None:
                self.page_success += 1
            else:
                logger.error(exc.msg)


def create_spider(name, *args, **kwargs):
    return {
        'dantri': DantriSpider(*args, **kwargs),
    }.get(name)
