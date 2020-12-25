import asyncio
from .spider import create_spider
from . import setting

default_config = {
    'dantri': {
        'delay': 60 * 60 * 5,
    }
}

class Runner:
    def __init__(self, config=None):
        self.config = config or default_config

    def schedule_spider(self, spider, delay):
        loop = asyncio.get_event_loop()
        loop.create_task(spider.run())
        loop.call_later(delay, self.schedule_spider, spider, delay)

    async def run(self):
        for name, config in self.config.items():
            spider = create_spider(name, setting.MONGO_URI)
            self.schedule_spider(spider, config['delay'])
