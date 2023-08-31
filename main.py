import asyncio
from telethon import events
import init_db as database
from telethon.sync import TelegramClient
from os import path
from tables import *
import sys
from settings import bot
from buttons import *
from manage_user import *
import utils as uti

initDbFlag=False

@bot.on(events.NewMessage)
async def message1(event):
    print("_-------------------------------------------------------------0-----")
    #print(event)
    sender = await event.get_sender()
    sender = sender.id
    print(event)
    await uti.delet_all_messages(sender ,event)
    if event.message.message == "/start":
        
        helper = await UserEventHelper(event,sender,event.from_id).manage.init_()
    else:
        
        help =  UserEventHelper(event,sender,event.from_id)

        #await help.runner("delet_all_messages")
        await help.runner('message')
    

@bot.on(events.CallbackQuery)
async def callback(event):
    print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    sender = await event.get_sender()
    sender = sender.id
    print(f"88888{sender}")
    help =  UserEventHelper(event,sender)
    await uti.delet_all_messages(sender ,event)
    await help.runner('callback_query')
    



class UserEventHelper:

    def __init__(self, event,sender,from_id=None):

        self.manage = Manage_User(event,sender,from_id)
        return None

    async def runner(self, func):
        try:

            check = await self.manage.init_()
            if check != None:
                await getattr(self.manage, func)()
        except Exception as e:
            print(f"from user event helper:{e} ")
            
async def main():
    print("trying to create database")
    await database.init()
    print("database is created")
    await asyncio.gather(bot.run_until_disconnected())


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    while True:
        try:
            loop.run_until_complete(main())
        except KeyboardInterrupt:
            exit()
        except Exception:
            print("problem whit main")

async def check_user(sender):
    user =await User.filter(id = sender)
    return user

async def user_registration(event,sender):
    user =await User(id = sender , flow = "user_registration_first_name").save()
    await UserEventHelper(event,sender).manage.message_sender("ברוך הבא לtelecar בוט השכרת הרכב הטוב ביותר. מה שנשאר זה רק להרשם\n נא לשלוח הודעת טקסט עם שמך")
    
    # call messaes of the user
