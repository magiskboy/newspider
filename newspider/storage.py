import asyncio
import motor.motor_asyncio
from . import setting


def get_db():
    mongo_client = motor.motor_asyncio.AsyncIOMotorClient(
        setting.MONGO_URI,
        io_loop=asyncio.get_event_loop(),
    )

    db = mongo_client['newspider']

    return db

