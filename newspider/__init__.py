from starlette.applications import Starlette
from starlette.middleware.cors import CORSMiddleware
from . import urls, setting


def create_app():
    app = Starlette(routes=urls.routes, debug=setting.DEBUG)
    app.add_route('/', urls.routes)

    app.add_middleware(CORSMiddleware, allow_origins=['*'])

    return app
