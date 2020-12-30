import asyncio
from datetime import datetime
import motor.motor_asyncio
from starlette import exceptions
from starlette.requests import Request
from starlette.responses import HTMLResponse
from starlette.templating import Jinja2Templates
from .storage import get_db, get_posts
from . import setting
from . import utils


templates = Jinja2Templates(directory=str(setting.TEMPLATES_DIR))


async def homepage(request: Request):
    template = 'homepage.html'
    context = {
        'request': request,
        'title': 'Homepage',
        'posts': await get_posts(fields=['title', 'date', 'source', 'url', 'slug']),
    }

    return templates.TemplateResponse(template, context)


async def post(request: Request):
    slug = request.path_params.get('slug')
    post = await get_posts({'slug': slug}, scalar=True)
    if not post:
        raise exceptions.HTTPException(404, 'Page not found')

    template = 'post.html'
    context = {
        'request': request,
        'post': post,
    }
    return templates.TemplateResponse(template, context)


async def search(request: Request):
    page_size = 10
    keyword = request.query_params.get('keyword')
    page = request.query_params.get('next_page')
    page = utils.safe_cast(page, int, 0)

    filters = {'$or': [{'title': {'$regex': keyword}}, {'slug': {'$regex': keyword.replace(' ', '-').lower()}}]}
    posts = await get_posts(filters, page, page_size)

    template = 'search.html'
    context = {
        'request': request,
        'posts': posts,
        'prev_page': page - 1,
        'page': page,
        'next_page': page + 1 if len(posts) == page_size else -1,
        'keyword': keyword,
    }
    return templates.TemplateResponse(template, context)


async def tags(request: Request):
    tag = request.query_params.get('tag')
    page = request.query_params.get('next_page')
    page = utils.safe_cast(page, int, 0)

    posts = await get_posts({'tags': tag}, page)

    template = 'tags.html'
    context = {
        'request': request,
        'tag': tag,
        'posts': posts,
        'prev_page': page - 1,
        'page': page,
        'next_page': page + 1 if len(posts) == 10 else -1,
    }
    return templates.TemplateResponse(template, context)


async def categories(request: Request):
    category = request.query_params.get('category')
    page = request.query_params.get('next_page')
    page = utils.safe_cast(page, int, 0)

    posts = await get_posts({'categories': category}, page)

    template = 'categories.html'
    context = {
        'request': request,
        'category': category,
        'posts': posts,
        'prev_page': page - 1,
        'page': page,
        'next_page': page + 1 if len(posts) == 10 else -1,
    }
    return templates.TemplateResponse(template, context)
