import os
from pathlib import Path
from starlette.config import Config

config = Config()

DEBUG = config('DEBUG', cast=bool, default=False)

BASE_DIR = Path(__file__).parent

TEMPLATES_DIR = BASE_DIR / 'templates'
STATIC_DIR = BASE_DIR / 'static'

MONGO_URI = config('MONGO_URI', default='mongodb://localhost:27017')
