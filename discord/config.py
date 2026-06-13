import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
ADMIN_ROLE = os.getenv("ADMIN_ROLE", "debt-collector")
ID_SERVER = int(os.getenv("ID_SERVER", "1101872962312876032"))
ID_CHANNEL_NOTIFICATION = int(os.getenv("ID_CHANNEL_NOTIFICATION", "1101872962312876032"))
ID_CHANNEL_REPORT = int(os.getenv("ID_CHANNEL_REPORT", "1101872962312876032"))