import asyncio
import motor.motor_asyncio
from starlette import exceptions
from starlette.requests import Request
from starlette.responses import HTMLResponse
from starlette.templating import Jinja2Templates
from .storage import get_db
from . import setting


templates = Jinja2Templates(directory=str(setting.TEMPLATES_DIR))


async def homepage(request: Request):
    limit = 10
    template = 'homepage.html'
    context = {
        'request': request,
        'title': 'Homepage',
    }

    db = get_db()

    posts = []
    async for post in db.posts.find().sort('date').limit(limit):
        posts.append(post)
    context['posts'] = posts

    return templates.TemplateResponse(template, context)


async def post(request: Request):
    template = 'post.html'
    context = {
        'request': request,
    }

    slug = request.path_params.get('slug')
    db = get_db()
    post = await db.posts.find_one({'slug': slug})
    if not post:
        raise exceptions.HTTPException(404, 'Page not found')

    context.update({
        'post': post,
        'title': post['title'],
    })

    return templates.TemplateResponse(template, context)
