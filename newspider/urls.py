from starlette.routing import Route, Mount
from starlette.staticfiles import StaticFiles
from . import views, setting, apis


view_routing = [
    Route('/', endpoint=views.homepage),
    Route('/posts/{slug:str}', views.post),
]


api_routing = [
    Route('/post_links', apis.get_post_links),
]


static = StaticFiles(directory=str(setting.STATIC_DIR))


routes = [
    Mount('/api', routes=api_routing, name='api'),
    Mount('/static', static, name='static'),
    Mount('/', routes=view_routing, name='web'),
]
