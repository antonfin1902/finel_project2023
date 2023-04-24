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

async def user_messages_db_call(sender,event):
    try:
        user= await User.filter(id=sender).prefetch_related("lest_messages")
        if len(user) == 0:
            return None
        user_lest_messgas=user[0].lest_messages
        return user_lest_messgas
    except Exception as e:
        await event.respond('Error loading buyer lestMessages from db please try again::', parse_mode='html' ,buttons=main_markup())
        print("Error loading buyer lestMessages from db please try again::",e)
        return None
    
    
#delete all the user messages thet stord in the db     
async def delet_all_messages(sender ,event):
    buyer =await user_messages_db_call(sender ,event)
    deleteList=[]
    if buyer is None:
        print("hamana-hamana")
        pass
    else:
        try:
            print("hamana-hamana2")
            async for message in buyer:
                if message == None:
                    break
                await bot.delete_messages(entity=sender, message_ids= [message.id])
                deleteList.append(message.id)
            
            for messageId in deleteList: 
                await UserMessages().filter(id=messageId).delete()
        except Exception as e:
            print(f"eror in deliting message ::{e}")