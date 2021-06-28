import os
from dotenv import load_dotenv

class Config:
    BOT_TOKEN = None
    PUBG_TOKEN = None
    SEASONS_FILE = None
    SEASON_DATA_EXPIRE_DAYS = None
    TMP_AUDIO_FILE = None

    def __init__(self):
        load_dotenv()

        self.BOT_TOKEN = os.getenv('BOT_TOKEN')
        self.PUBG_TOKEN = os.getenv('PUBG_TOKEN')
        self.SEASONS_FILE = os.getenv('SEASONS_FILE','seasons.dat')
        self.SEASON_DATA_EXPIRE_DAYS = int(os.getenv('SEASON_DATA_EXPIRE_DAYS', 15))
        self.TMP_AUDIO_FILE = os.getenv('TMP_AUDIO_FILE', 'voice.mp3')