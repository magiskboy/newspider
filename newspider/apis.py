from starlette.requests import Request
from starlette.responses import JSONResponse
from .storage import get_db


async def get_post_links(request: Request):
    db = get_db()
    offset = request.query_params.get('offset')
    if offset:
        offset = int(offset)
    else:
        offset = 0

    limit = request.query_params.get('limit')
    if limit:
        limit = int(limit)
    else:
        limit = 10

    posts = []
    async for post in db.posts.find().sort('date').skip(offset).limit(limit):
        posts.append({
            'slug': post['slug'],
            'title': post['title'],
        })

    return JSONResponse(posts)
