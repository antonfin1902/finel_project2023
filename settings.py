from telethon.sync import TelegramClient

TORTOISE_ORM = {
     "connections": {"default": 'sqlite://db_files/db.sqlite3'},
     "apps": {
         "models": {
             "models": ["tables", "aerich.models"],
             "default_connection": "default",
         },
     },
 }

TG_API_ID = 1910144
TG_API_HASH = "275a53e95d045f6d980c222640f36add"
bot_token = '5664640478:AAEQUDfGcCjpW2x_ZtTlpF93kCFFoL4Q2zs'


bot = TelegramClient(
    'bot', TG_API_ID, TG_API_HASH, base_logger='telegram').start(bot_token=bot_token)
POST_PER_PAGE = 4

BOT_USER_ID = 5664640478
admin_ids =[552647585]