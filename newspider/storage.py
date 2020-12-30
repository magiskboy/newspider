import asyncio
from datetime import datetime
import motor.motor_asyncio
from . import setting


def post_to_dict(post, fields=None):
    if fields is None:
        return {
            'title': post['title'],
            'content': post['content'],
            'date': post['date'].strftime('%c'),
            'tags': post['tags'],
            'slug': post['slug'],
            'categories': post['categories'],
            'source': post['source'],
            'url': post['url'],
        }
    ret = {k: post[k] for k in fields}
    if 'date' in ret:
        ret['date'] = ret['date'].strftime('%c')
    return ret


def get_db():
    mongo_client = motor.motor_asyncio.AsyncIOMotorClient(
        setting.MONGO_URI,
        io_loop=asyncio.get_event_loop(),
    )

    db = mongo_client['newspider']

    return db


async def get_posts(filters=None, page=0, page_size=10, fields=None, scalar=False):
    offset = page * page_size
    db = get_db()
    if scalar:
        post = await db.posts.find_one(filters) if filters else db.posts.find_one()
        return post_to_dict(post, fields)

    query = db.posts.find(filters) if filters else db.posts.find()
    query = query.sort('date', -1).skip(offset).limit(page_size)

    posts = []
    async for post in query:
        posts.append(post_to_dict(post, fields))

    return posts
