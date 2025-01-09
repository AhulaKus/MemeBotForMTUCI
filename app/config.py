from pathlib import Path


APP_ROOT = Path(__file__).parent

RESOURCES_PATH = APP_ROOT / 'resources'
FONTS_PATH = RESOURCES_PATH / 'fonts'
IMAGES_PATH = RESOURCES_PATH / 'images'
MEMES_PATH = RESOURCES_PATH / 'memes'

DB_PATH = APP_ROOT.parent / 'database.db'
