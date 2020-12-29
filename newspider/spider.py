import os
import sys
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
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(fmt)
logger.addHandler(handler)
logger.setLevel(logging.INFO)


class SpiderBase:
    ROOT: str

    def __init__(self, mongo_uri):
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

    def __init__(self, mongo_uri):
        super().__init__(mongo_uri)
        logger.info('DantriSpider is created')

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
        title = None
        title_node = soup.select_one('.dt-news__title')

        if title_node:
            title = (title_node.get_text() or '').strip()

        if not title:
            raise ValueError('Title not found')
        return title

    def get_breadcrumb_from_soup(self, soup):
        nodes = soup.select('.dt-breadcrumb a')
        if nodes:
            return list(map(lambda x: x.get_text(), nodes))
        return []

    def get_tags_from_soup(self, soup):
        nodes = soup.select('.dt-news__tag-list .dt-news__tag a')
        if nodes:
            return list(map(lambda x: x.get_text(), nodes))
        return []

    def get_date_from_soup(self, soup):
        dt_node = soup.select_one('.dt-news__time')
        if dt_node:
            dt_text = dt_node.get_text()
            dt_text = dt_text.split(',')
            if len(dt_text) > 1:
                dt_text = dt_text[1].strip()
                return datetime.strptime(dt_text, '%d/%m/%Y - %H:%M')

    def get_content_from_soup(self, soup):
        content_node = soup.select_one('.dt-news__content')
        if content_node:
            return ''.join(str(x) for x in content_node.contents).strip()
        raise ValueError('Content not found')

    async def fetch_page(self, path: str) -> T.Dict[str, T.Any]:
        url = self.ROOT + path      #pylint: disable=E1101
        async with httpx.AsyncClient() as c:
            resp = await c.get(url)

            if resp.status_code == 200:
                soup = BeautifulSoup(resp.content, 'html.parser')

                title = self.get_title_from_soup(soup)
                return {
                    'title': title,
                    'slug': slugify(title),
                    'path': path,
                    'categories': self.get_breadcrumb_from_soup(soup),
                    'date': self.get_date_from_soup(soup),
                    'content': self.get_content_from_soup(soup),
                    'tags': self.get_tags_from_soup(soup),
                    'source': 'Dân trí',
                }
            raise ValueError('Fetch page failure')

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
                logger.error(exc)


class VnxpressSpider(SpiderBase):
    ROOT = 'https://vnexpress.net'

    def __init__(self, mongo_uri):
        logger.info('VnexpressSpider is created')
        super().__init__(mongo_uri)

    async def get_list_post(self) -> T.Dict[str, str]:
        class_item = '.item-news .title-news a'

        async with httpx.AsyncClient() as c:
            resp = await c.get(self.ROOT)       #pylint: disable=E1101

        if resp.status_code == 200:
            soup = BeautifulSoup(resp.content, 'html.parser')
            items = soup.select(class_item)

            for item in items:
                title = item.get('title')
                c = await self.db.posts.count_documents({'title': title})
                if c:
                    continue

                path = item.get('href')
                if 'video.vnexpress.net' in path:
                    continue

                yield path

    def get_title_from_soup(self, soup):
        title_node = soup.select_one('.title-detail')
        if title_node:
            return title_node.get_text().strip()
        raise ValueError('Title not found')

    def get_breadcrumb_from_soup(self, soup):
        nodes = soup.select('ul.breadcrumb li a')
        return list(map(lambda x: x.get('title'), nodes))

    def get_tags_from_soup(self, soup):
        return []

    def get_date_from_soup(self, soup):
        dt_node = soup.select_one('.header-content .date')
        if dt_node:
            dt_text = dt_node.get_text()
            dt_text = dt_text.split(',', 1)[1]
            dt_text = dt_text.split('(')[0].strip()
            if dt_text:
                return datetime.strptime(dt_text, '%d/%m/%Y, %H:%M')

    def get_content_from_soup(self, soup):
        content_node = soup.select_one('article.fck_detail')
        if content_node:
            data = ''.join(str(x) for x in content_node.contents).strip()
            data = data.replace('data-src', 'src')
            return data
        raise ValueError('Content not found')

    async def fetch_page(self, path: str) -> T.Dict[str, T.Any]:
        url = path      #pylint: disable=E1101
        async with httpx.AsyncClient() as c:
            resp = await c.get(url)

            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, 'html.parser')

                title = self.get_title_from_soup(soup)
                return {
                    'title': title,
                    'slug': slugify(title),
                    'path': path,
                    'categories': self.get_breadcrumb_from_soup(soup),
                    'date': self.get_date_from_soup(soup),
                    'content': self.get_content_from_soup(soup),
                    'tags': self.get_tags_from_soup(soup),
                    'source': 'VnExpress',
                }
            raise ValueError('Fetch page failure')

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
                logger.error(exc)


def create_spider(name, *args, **kwargs):
    return {
        'dantri': DantriSpider,
        'vnexpress': VnxpressSpider,
    }.get(name)(*args, **kwargs)
