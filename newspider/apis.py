from starlette.requests import Request
from starlette.responses import JSONResponse
from .storage import get_posts
from . import utils


async def get_post_links(request: Request):
    page = request.query_params.get('page')
    page = utils.safe_cast(page, int, 0)

    page_size = request.query_params.get('page_size')
    page_size = utils.safe_cast(page_size, int, 10)

    posts = await get_posts(None, page, page_size, fields=['title', 'slug', 'source', 'url', 'date'])
    return JSONResponse(posts)
