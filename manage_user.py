
from ast import Break
from logging import exception
import os
from typing import Final
from telethon import types
import telethon
from random import choices
import time
import asyncio
from telethon.tl.functions.users import GetFullUserRequest
from telethon import events
from telethon.sync import TelegramClient
from telethon.tl.custom import Button
from tables import *
from buttons import *
from telethon.tl.functions.messages import SearchRequest
from telethon.tl.types import InputMessagesFilterEmpty
from text import *
from tortoise.expressions import Q
from settings import *
from text_formats import *
from telethon.tl.functions.users import GetFullUserRequest

class Manage_User():

    def __init__(self, event,sender,from_id =None):
        print("1")
        self.event = event

        print(f"------{sender}")
    #    sender = sender.id
        #self.sender = await event.get_sender().id
        self.sender = sender
        self.chat_id = event.chat_id
        self.user_db = None
        self.post_in_work = None
        self.from_id = from_id
        self.is_admin = False
        
        try:
            print(f"text::::::::::{type(self.event.text)}")
            self.text = self.event.text
        except AttributeError:
            self.text = None
#        self.entities = event.message.entities
        return None
    async def init_(self):
        #print(f"media{self.event.new_photo()}")
        if self.from_id !=None or self.sender==BOT_USER_ID  :
            return None
        try:
            user =await User.filter(id = self.sender).first()
            print(f"ppppppppppppppp{self.sender}")
            print(f"::::{user}")
            if user == None:
                user_photo_folder_path = str(os.getcwd())+'/photoDir/'+str(self.sender)+'/'
                print(user_photo_folder_path)
                try:
                    os.mkdir(user_photo_folder_path)
                except Exception:
                    print("this dir all ready take")
                self.user_db = User(id = self.sender , flow = "user_registration_first_name",photo_dir=user_photo_folder_path)
                await self.user_db.save()
                print(type(self.user_db))
                await self.message_sender("ברוך הבא לtelecar בוט השכרת הרכב הטוב ביותר. מה שנשאר זה רק להרשם\n נא לשלוח הודעת טקסט עם שמך")
                
                return True
                
            else:
                if user.is_admin == True:
                    self.is_admin = True
                self.user_db=user
                return True
                
        except AttributeError as e:
            print(f"problem whit init_{e}")
            return None
        
#אישור משתמשים חדשים 
    async def registration_aproval_list(self):
        m =await self.event.edit("ttt")
        await bot.delete_messages(entity=self.sender, message_ids= [m.id])
        not_aproval_list = await User.filter(registration_step = False).all()
        if len(not_aproval_list) == 0:
            await self.message_sender("אין עדיין מועמדים",go_buck_to_menu)
        
        else:
            message_list = []
            for candidate in not_aproval_list:
                m= await self.message_sender(candidate_form.format(candidate.first_name , candidate.last_name , candidate.email  , candidate.phone_number), [Button.inline(" לאישור",f'registration_aprov:{candidate.id}:A'), Button.inline(" לסירוב",f'registration_aprov:{candidate.id}:"D')])
                message_list.append(m.id)
            
            await self.save_all_lest_messag(message_list)
            await self.message_sender("לחזרה לתפריט" , go_buck_to_menu)
            
    async def registration_aprov(self,user_id ,delete_or_aprov):
        if delete_or_aprov == "A":
            user = await User.filter(id = user_id).update(registration_step = True)
            print(user)
            print(type(user))
            await bot.send_message(int(user_id ), message="ההרשמה בוצע בהצלחה ברוך הבא ל telecar",buttons=main_markup())
            await self.event.edit("האישור בוצע בהצלחה", buttons=go_buck_to_menu)
        else:
            user = await User.filter(id = user_id).first()
            await bot.send_message(int(user_id ) , message="המנהל לא אישר את הוספתכם למערכת")
            await User.filter(id = user_id).delete()
            await self.event.edit("  הסירוב בוצע בהצלחה", buttons=go_buck_to_menu)
            
        
    async def restart_flow(self):
        self.user_db.flow = None
        await self.user_db.save()
        
    async def menu(self, message =None, markup = None, edit = True):
        if markup == '0' and edit == 'F':
            markup = None
            edit = False
        if message is None or message == '0':
            message = "ברוך הבא ל telecar"
        
        if markup == None:
            markup = main_markup()
            if self.is_admin:
               markup = admin_main_markup() 
            if edit == True:
                await self.event.edit(message,buttons = markup)
            else:
                await self.event.respond(message,buttons = markup)
        else:
            if edit == True:
                await self.event.edit(message , buttons = markup)
            else:
                await self.event.respond(message , buttons = markup)
        
    async def message(self):
        #print(f"pppppp{self.sender}")
        print(12)
        if self.event.message.is_private:
            print(13)
            await self.private_message()
            return
#send the message and buttons and save in db (after callback this message will be deleted )
    async def message_sender(self,message,markup=None ,edit =False):
        m=None
        if markup is None and edit == False:
            m = await self.event.respond(message)
        elif markup is None and edit == True:
            m = await self.event.edit(message)
        
        elif edit == True:
            m = await self.event.edit( message ,buttons = markup)
        else:
            m = await self.event.respond( message ,buttons = markup)    
        return m
        
    async def private_message(self):
        if self.user_db.flow == "user_registration_first_name":
            print(f"text++++++++++++++++++{self.text}")
            self.user_db.first_name = self.text
            self.user_db.flow= "user_registration_last_name"
            await self.user_db.save()
            await self.message_sender("מצויין עכשיו נא לשלוח את שם המשפחה בהודעת טקסט")
            print(self.text)
            
        elif self.user_db.flow == "user_registration_last_name":
            self.user_db.last_name = self.text
            self.user_db.flow= "user_registration_email"
            await self.user_db.save()
            await self.message_sender("מצויין עכשיו נא לשלוח את שם האימייל בהודעת טקסט")
            
        elif self.user_db.flow == "user_registration_email":
            self.user_db.email = self.text
            self.user_db.flow= "user_registration_phone_number"
            await self.user_db.save()
            await self.message_sender("מצויין עכשיו נא לשלוח את מספר הטלפון בהודעת טקסט")
            
        elif self.user_db.flow == "user_registration_phone_number":
            self.user_db.phone_number = self.text
            self.user_db.flow= None
            await self.user_db.save()
            user = await User().filter(id = self.sender).first()
            #print(f"types 1 :{type(user.id)} 2{type(admin_ids[0])}")
            #print(admin_main_markup())
            if user.id in admin_ids:
                user.is_admin = True
                user.registration_step = True
                self.is_admin = True
                await user.save()
                await self.message_sender("ההרשמה הסתיימה בהצלחה!! \n  ברוך הבא לtelecar",markup=admin_main_markup())
                
            else:
                
                await self.message_sender("ההרשמה הסתיימה בהצלחה!! \n  ברוך הבא לtelecar" + "\n" +"עכשיו נשאר רק לאשר אותך עלידי המנהלים שלנו בדקות הקרובות ישלח לך אישור")
            
        elif "add_post" in self.user_db.flow:
            step=self.user_db.flow.split(":")
            await self.add_post(step[1])
            
        elif "change_post_car_company" in self.user_db.flow :
            params = self.user_db.flow .split(":")
            await Post().filter(id = int(params[1])).update(car_company= self.text)
            self.user_db.flow= None
            await self.user_db.save()
            markup=main_markup()
            if self.is_admin:
                markup=admin_main_markup()
                
            await self.message_sender("שם חברת הרכב שונה בהצלחה",markup = markup)
            
        elif "change_post_car_type" in self.user_db.flow :
            params = self.user_db.flow .split(":")
            await Post().filter(id = int(params[1])).update(car_type= self.text)
            self.user_db.flow= None
            await self.user_db.save()
            markup=main_markup()
            if self.is_admin:
                markup=admin_main_markup()
            await self.message_sender("קטגוריית הרכב שונתה בהצלחה",markup=markup)
            
    
        
        elif "change_post_car_model" in self.user_db.flow :
            params = self.user_db.flow .split(":")
            await Post().filter(id = int(params[1])).update(car_model= self.text)
            self.user_db.flow= None
            await self.user_db.save()
            markup=main_markup()
            if self.is_admin:
                markup=admin_main_markup()
            await self.message_sender("דגם הרכב שונה בהצלחה",markup=markup)
        
        elif "change_post_car_production_year" in self.user_db.flow :
            params = self.user_db.flow .split(":")
            await Post().filter(id = int(params[1])).update(car_production_year= self.text)
            self.user_db.flow= None
            await self.user_db.save()
            markup=main_markup()
            if self.is_admin:
                markup=admin_main_markup()
            await self.message_sender("שנת היצור שונתה בהצלחה",markup=markup)
            
        elif "change_post_Engine_capacity" in self.user_db.flow :
            params = self.user_db.flow .split(":")
            await Post().filter(id = int(params[1])).update(Engine_capacity= self.text)
            self.user_db.flow= None
            await self.user_db.save()
            markup=main_markup()
            if self.is_admin:
                markup=admin_main_markup()
            await self.message_sender("נפח המנוע שונה בהצלחה",markup=markup)
            
        elif "change_post_horsepower" in self.user_db.flow :
            params = self.user_db.flow .split(":")
            await Post().filter(id = int(params[1])).update(horsepower= self.text)
            self.user_db.flow= None
            await self.user_db.save()
            markup=main_markup()
            if self.is_admin:
                markup=admin_main_markup()
            await self.message_sender("כוחות הסוס שונו בהצלחה",markup=markup)
        #צריך לסדר את שינוי התמונה    
        elif "change_post_photo" in self.user_db.flow :
            params = self.user_db.flow .split(":")
            await Post().filter(id = int(params[1])).update(horsepower= self.text)
            self.user_db.flow= None
            await self.user_db.save()
            markup=main_markup()
            if self.is_admin:
                markup=admin_main_markup()
            await self.message_sender("כוחות הסוס שונו בהצלחה",markup=markup)
            
        elif "change_post_txt_content" in self.user_db.flow :
            params = self.user_db.flow .split(":")
            await Post().filter(id = int(params[1])).update(txt_content= self.text)
            self.user_db.flow= None
            await self.user_db.save()
            markup=main_markup()
            if self.is_admin:
                markup=admin_main_markup()
            await self.message_sender("תוכן הפוסט שונה בהצלחה",markup=markup)

        elif "change_post_km" in self.user_db.flow :
            params = self.user_db.flow .split(":")
            await Post().filter(id = int(params[1])).update(km= self.text)
            self.user_db.flow= None
            await self.user_db.save()
            markup=main_markup()
            if self.is_admin:
                markup=admin_main_markup()
            await self.message_sender("הקילוג״ הרכב שונה בהצלחה",markup=markup)
        
        elif 'search_filter' in self.user_db.flow:
            params = self.user_db.flow.split(":")
            await self.search_filter(params[1],self.text)    
               
        else:
            markup=main_markup()
            if self.is_admin:
                markup=admin_main_markup()
            await self.message_sender("הודעתך נקלטה אך המערכת לא מחכה להודעות \n אנא בחר",markup)

    #save list of message ids in the db     
    async def save_all_lest_messag(self,m_ids):
        try:
            for m_id in m_ids:
                newMessage = UserMessages(id = m_id , user_id = self.sender )
                await newMessage.save()
        except Exception as e:
            markup=main_markup()
            if self.is_admin:
                markup=admin_main_markup()
            await self.event.respond('Error loading func save_all_lest_messag please try again::', parse_mode='html' ,buttons=markup)
            print("'Error loading func save_all_lest_messag please try again::",e)


    async def user_profile(self):
        #calculate avrage garde for seller..need to conver as function 
        try:
            # seller_rate_list=[self.user_db.seller_payment_grade,self.user_db.seller_availability_grade,self.user_db.seller_cleaning_grade,self.user_db.sellerre_liability_grade]
            # avg_seller_rate=int(map(sum,seller_rate_list))/len(seller_rate_list)

            user_text= User_format.format(self.user_db.first_name,self.user_db.last_name,self.user_db.email,self.user_db.phone_number,144,self.user_db.buyer_payment_grade,self.user_db.buyer_availability_grade,self.user_db.buyer_cleaning_grade,self.user_db.buyer_reliability_grade)
            print(f"user_text::{user_text}")
            await self.event.edit(user_text,buttons= go_buck_to_menu)

            print(f"##########sha1234{self.user_db.first_name}")
        except Exception as e:
            print(e)
        #await self.message_sender(text)
    async def my_posts(self,page=0):
        if type(page)is int:
            m =await self.event.edit("ttt")
            await bot.delete_messages(entity=self.sender, message_ids= [m.id])
        if type(page) is str:
            page = int(page)
        print("yyy")
        next_flag=True
        prev_flag=True
        posts = await Post().filter(Q(Q(owner_id=self.sender), Q(data_is_full=True), join_type="AND")).all()
        print(len(posts))
        if len(posts) == 0:
            self.message_sender("אין לך עדיין פוסטים אבל אתה מוזמן להוסיף פוסט עלידי לחיצה על הוספת פוסט")
        print("lllltttt")
        if page == 0:
            prev_flag=False
        first_post_index = page * POST_PER_PAGE
        try:
            if len(posts)>first_post_index+POST_PER_PAGE:
                print("kaka1")
                page_post = posts[first_post_index:first_post_index+POST_PER_PAGE]
                
            else:
                print("kaka2")
                page_post = posts[first_post_index:]
                next_flag=False
        except Exception as e:
            print(e)
        print("lllltttt-------")
        try:
            for post in page_post:
                print(f"ssssssss:{post.car_company}")
                post_text = Post_format.format(post.car_company,post.car_model,post.car_type,post.car_production_year,post.Engine_capacity,post.horsepower,str(post.from_date)[:10],str(post.to_date)[:10],post.txt_content,post.km,post.cost)
                print(f"post text::{post_text}")
                if post.photo_path==None:
                    await self.message_sender(post_text)
                else:
                    m=await bot.send_file( self.sender , post.photo_path ,caption = post_text )
                    await self.save_all_lest_messag([m.id])
        except Exception as e:
            print(f"problem in my posts{e}")
            
        next_page_button =[Button.inline(" >>",f'my_posts:{page+1}')]
        prev_page_button =[Button.inline(" <<",f'my_posts:{page-1}')]
        move_page_markup=[]
        
        move_page_markup=[]
        if prev_flag and next_flag:
            move_page_markup.append(prev_page_button)
            move_page_markup.append(next_page_button)
        
        elif prev_flag:
            move_page_markup.append(prev_page_button)
            
        elif next_flag:
            move_page_markup.append(next_page_button)
        print(move_page_markup)
        
        move_page_markup.append(go_buck_to_menu_no_edit)
        print(move_page_markup)
        m=await self.event.respond(f"מספר דף:{page}", buttons=move_page_markup)
        await self.save_all_lest_messag([m.id])
       
        

    """async def add_post(self,flow = None):
        print(f"thhe flow in add function:::{flow}")
        if flow is None:
            try:
                
                self.post_in_work = await Post(owner_id=self.sender).save()
                print("xx")
                self.user_db.flow= "add_post:car_company"
                await self.user_db.save()
                await self.event.edit("נא להוסיף את שם חברת הרכב . לדוגמא יונדאי,פורד וכדומה")
            except Exception as e:
                print(f"eror in add_post flow=none :{e}")
        
        elif flow == "car_company":
            try:
                print(f"TEXT IN ADD FUNCTION car_company{self.text}")
                self.post_in_work = await Post().filter(Q(Q(owner_id=self.sender), Q(data_is_full=False), join_type="AND")).first()
                self.post_in_work.car_company = self.text
                await self.post_in_work.save()
                self.user_db.flow= "add_post:car_type"
                await self.user_db.save()
                #print(f"post id??????:::{self.post_in_work.id}")
                await self.message_sender("נא להוסיף את שם הדגם של הרכב ")
            except Exception as e:
                print(f"eror in add_post flow=none :{e}")

        elif flow == "car_type" or flow == "car_photo":
            print(f"TEXT IN ADD FUNCTION car_type{self.text}")
            self.post_in_work = await Post().filter(Q(Q(owner_id=self.sender), Q(data_is_full=False), join_type="AND")).first()
            if flow == "car_type":
                try:
                    print(f"check car compeny{self.post_in_work.car_company}")
                    self.post_in_work.car_type = self.text
                    await self.post_in_work.save()
                    self.user_db.flow= "add_post:car_photo"
                    await self.user_db.save()
                    await self.message_sender("נא להוסיף את סוג הרכב ")  
                except Exception as e:
                    print(f"eror in add_post flow=car_type :{e}")
                    
            
                
            if  "car_photo" in flow:
                print("hear")
                flag =True
                try:
                    async with bot.conversation(await self.event.get_chat(), exclusive=True) as conv:
                        m=await conv.send_message("אנא שלך תמונה של המנה::", parse_mode='html')
                        await self.save_all_lest_messag([m.id])
                        imageMessage = await conv.get_response()
                        conv.cancel()
                        try:
                            if imageMessage.media:
                                self.post_in_work.photo_path = self.user_db.photo_dir+str(self.post_in_work.id)+".jpg"
                                await self.post_in_work.save()
                                await bot.download_media(imageMessage,file=self.post_in_work.photo_path)
                                await self.message_sender("התמונה הוכנסה בהצלחה")

                            else:
                                await self.message_sender("משהו השתבש ")
                                flag=False
                        except Exception as e:
                            flag=False
                            
                        
                    if flag:
                        self.user_db.flow= "add_post:car_model"
                        await self.user_db.save()
                        await self.message_sender("נא להוסיף את סוג הרכב ")  
                        
                    else:
                        await self.message_sender('משהו השתבש בהכנסת תמונה נסה שוב')
                        await self.post_in_work.save()
                        self.user_db.flow= "add_post:car_photo"
                        await self.user_db.save()
                except Exception as e:
                    print(e)
                
            
           
        # elif flow == "car_name":
        #     self.post_in_work.car_type = self.text
        #     await self.post_in_work.save()
        #     self.user_db.flow= "add_post:car_company"
        #     await self.user_db.save()
        #     await self.message_sender("נא להוסיף את שם חברת הרכב . לדוגמא יונדאי,פורד וכדומה")
        
        elif flow == "car_model":
            try:
                self.post_in_work = await Post().filter(Q(Q(owner_id=self.sender), Q(data_is_full=False), join_type="AND")).first()
                print(f"check car_type{self.post_in_work.car_type}id{self.post_in_work.id}")
                self.post_in_work.car_model = self.text
                await self.post_in_work.save()
                self.user_db.flow= "add_post:car_production_year"
                await self.user_db.save()
                await self.message_sender("נא להוסיף את שם הדגם של הרכב")
            except Exception as e:
                print(f"eror in add_post flow=car_model :{e}")
            
        
        elif flow == "car_production_year":
            try:
                self.post_in_work = await Post().filter(Q(Q(owner_id=self.sender), Q(data_is_full=False), join_type="AND")).first()
                print(f"check car_model{self.post_in_work.car_model}id{self.post_in_work.id}")
                self.post_in_work.car_production_year = self.text
                await self.post_in_work.save()
                self.user_db.flow= "add_post:Engine_capacity"
                await self.user_db.save()
                await self.message_sender("נא להוסיף את הנפח המנוע בליטרים")
            except Exception as e:
                print(f"eror in add_post flow=car_production_year :{e}")
                self.post_in_work = await Post().filter(Q(Q(owner_id=self.sender), Q(data_is_full=False), join_type="AND")).first()
                self.post_in_work.car_production_year = self.text
                await self.post_in_work.save()
                self.user_db.flow= "add_post:Engine_capacity"
                await self.user_db.save()
                await self.message_sender("נא להוסיף את הנפח המנוע בליטרים")
            
        elif flow == "Engine_capacity":
            try:
                self.post_in_work = await Post().filter(Q(Q(owner_id=self.sender), Q(data_is_full=False), join_type="AND")).first()
                print(f"check car_production_year{self.post_in_work.car_production_year}id{self.post_in_work.id}")
                self.post_in_work.Engine_capacity = self.text
                await self.post_in_work.save()
                self.user_db.flow= "add_post:horsepower"
                await self.user_db.save()
                await self.message_sender("נא להוסיף את כוחות הסוס של הרכב ")
            except Exception as e:
                print(f"eror in add_post flow=Engine_capacity :{e}")
            
            
        elif flow == "horsepower":
            try:
                self.post_in_work = await Post().filter(Q(Q(owner_id=self.sender), Q(data_is_full=False), join_type="AND")).first()
                print(f"check Engine_capacity{self.post_in_work.Engine_capacity}id{self.post_in_work.id}")
                self.post_in_work.horsepower = self.text
                await self.post_in_work.save()
                self.user_db.flow= "add_post:txt_content"
                await self.user_db.save()
                await self.message_sender("נא להוסיף תוכן הפוסט")
            except Exception as e:
                print(f"eror in add_post flow=horsepower :{e}")
            
            
        elif flow == "txt_content":
            try:
                self.post_in_work = await Post().filter(Q(Q(owner_id=self.sender), Q(data_is_full=False), join_type="AND")).first()
                print(f"check horsepower{self.post_in_work.horsepower}id{self.post_in_work.id}")
                self.post_in_work.txt_content = self.text
                await self.post_in_work.save()
                self.user_db.flow= "add_post:km"
                await self.user_db.save()
                await self.message_sender("נא להוסיף את הקילומטרז של הרכב")
            except Exception as e:
                print(f"eror in add_post flow=txt_content :{e}")
                
            
        elif flow == "km":
            try:
                self.post_in_work = await Post().filter(Q(Q(owner_id=self.sender), Q(data_is_full=False), join_type="AND")).first()
                print(f"check txt_content{self.post_in_work.txt_content}id{self.post_in_work.id}")
                self.post_in_work.km = self.text
                await self.post_in_work.save()
                
                self.user_db.flow= "add_post:address"
                await self.user_db.save()
                await self.message_sender("נא להוסיף כתובת לאיסוף")
            except Exception as e:
                print(f"eror in add_post flow=km :{e}")
            
            
        elif flow == "address":
            try:
                self.post_in_work = await Post().filter(Q(Q(owner_id=self.sender), Q(data_is_full=False), join_type="AND")).first()
                self.post_in_work.address = self.text
                await self.post_in_work.save()
                self.user_db.flow= "add_post:phone_number"
                await self.user_db.save()
                await self.message_sender("נא להוסיף את מספר הטלפון")    
            except Exception as e:
                print(f"eror in add_post flow=address :{e}")
            
            
        elif flow == "phone_number":
            try:
                self.post_in_work = await Post().filter(Q(Q(owner_id=self.sender), Q(data_is_full=False), join_type="AND")).first()
                self.post_in_work.phone_number = self.text
                await self.post_in_work.save()
                self.user_db.flow= "add_post:area"
                await self.user_db.save()
                await self.message_sender("נא להוסיף אתה אזור האיסוף של הרכב")    
            except Exception as e:
                print(f"eror in add_post flow = area :{e}")
            
        elif flow == "area":
            try:
                self.post_in_work = await Post().filter(Q(Q(owner_id=self.sender), Q(data_is_full=False), join_type="AND")).first()
                self.post_in_work.area = self.text
                await self.post_in_work.save()
                self.user_db.flow= "add_post:cost"
                await self.user_db.save()
                await self.message_sender("נא להוסיף אתה מחיר השכרת רכב פר יום")    
            except Exception as e:
                print(f"eror in add_post flow=phone_number :{e}")
            
        elif flow == "cost":
            try:
                self.post_in_work = await Post().filter(Q(Q(owner_id=self.sender), Q(data_is_full=False), join_type="AND")).first()
                self.post_in_work.cost = self.text
                self.post_in_work.data_is_full = True
                await self.post_in_work.save()
                print(f"from add post in flow cost:{self.post_in_work.cost} type{self.post_in_work.car_company}")
                self.user_db.flow= None
                await self.user_db.save()
                await self.message_sender("הפוסט שלך פורסם בהצלחה ניתן יהיה לראות אותו בפוסטים שלי",markup=main_markup())   
            except Exception as e:
                print(f"eror in add_post flow=cost :{e}")
                self.post_in_work.cost= None
                self.post_in_work.data_is_full = False
                self.post_in_work.save()
                self.user_db.flow= "add_post:cost"
                self.user_db.save()
                await self.message_sender("משהו השתבש בהכנסת המכיר אנא נסו שוב")"""
    
    async def add_post(self,flow = None):
        print(f"thhe flow in add function:::{flow}")
        if flow is None:
            try:
                
                self.post_in_work = await Post(owner_id=self.sender).save()
                print("xx starting adding new post!!!")
                self.user_db.flow= "add_post:car_company"
                await self.user_db.save()
                await self.event.edit("נא להוסיף את שם חברת יצרן הרכב . לדוגמא יונדאי,פורד, טסלה וכדומה")
            except Exception as e:
                print(f"eror in add_post flow=none :{e}")
                await self.message_sender("!משהו השתבש בהכנסת חברת הרכב אנא נסו שוב")
        elif flow == "car_company":
            try:
                print(f"TEXT IN ADD FUNCTION car_company{self.text}")
                self.post_in_work = await Post().filter(Q(Q(owner_id=self.sender), Q(data_is_full=False), join_type="AND")).first()
                self.post_in_work.car_company = self.text
                await self.post_in_work.save()
                self.user_db.flow= "add_post:car_type"
                await self.user_db.save()
                #print(f"post id??????:::{self.post_in_work.id}")
                await self.message_sender("נא להוסיף את שם הדגם של הרכב ")
            except Exception as e:
                print(f"eror in add_post flow=none :{e}")
                # self.post_in_work.car_company = None
                # await self.post_in_work.save()
                self.user_db.flow= "add_post:car_company"
                await self.message_sender("משהו השתבש בהכנסת יצרן הרכב אנא נסו שוב")


        elif flow == "car_type" or flow == "car_photo":
            print(f"TEXT IN ADD FUNCTION car_type{self.text}")
            self.post_in_work = await Post().filter(Q(Q(owner_id=self.sender), Q(data_is_full=False), join_type="AND")).first()
            if flow == "car_type":
                try:
                    print(f"check car compeny{self.post_in_work.car_company}")
                    self.post_in_work.car_type = self.text
                    await self.post_in_work.save()
                    self.user_db.flow= "add_post:car_photo"
                    await self.user_db.save()
                    await self.message_sender("נא להוסיף את סוג הרכב ")  
                except Exception as e:
                    print(f"eror in add_post flow=car_type :{e}")
                    
            
                
            if  "car_photo" in flow:
                print("hear")
                flag =True
                try:
                    async with bot.conversation(await self.event.get_chat(), exclusive=True) as conv:
                        m=await conv.send_message("אנא שלך תמונה של הרכב::", parse_mode='html')
                        await self.save_all_lest_messag([m.id])
                        imageMessage = await conv.get_response()
                        conv.cancel()
                        try:
                            if imageMessage.media:
                                self.post_in_work.photo_path = self.user_db.photo_dir+str(self.post_in_work.id)+".jpg"
                                await self.post_in_work.save()
                                await bot.download_media(imageMessage,file=self.post_in_work.photo_path)
                                await self.message_sender("התמונה הוכנסה בהצלחה")

                            else:
                                await self.message_sender("משהו השתבש ")
                                flag=False
                        except Exception as e:
                            flag=False
                            
                        
                    if flag:
                        self.user_db.flow= "add_post:car_model"
                        await self.user_db.save()
                        await self.message_sender("נא להוסיף את סוג הרכב ")  
                        
                    else:
                        await self.message_sender('משהו השתבש בהכנסת תמונה נסה שוב')
                        await self.post_in_work.save()
                        self.user_db.flow= "add_post:car_photo"
                        await self.user_db.save()
                except Exception as e:
                    print(e)
                
            
           
        # elif flow == "car_name":
        #     self.post_in_work.car_type = self.text
        #     await self.post_in_work.save()
        #     self.user_db.flow= "add_post:car_company"
        #     await self.user_db.save()
        #     await self.message_sender("נא להוסיף את שם חברת הרכב . לדוגמא יונדאי,פורד וכדומה")
        
        elif flow == "car_model":
            try:
                self.post_in_work = await Post().filter(Q(Q(owner_id=self.sender), Q(data_is_full=False), join_type="AND")).first()
                print(f"check car_type{self.post_in_work.car_type}id{self.post_in_work.id}")
                self.post_in_work.car_model = self.text
                await self.post_in_work.save()
                self.user_db.flow= "add_post:car_production_year"
                await self.user_db.save()
                await self.message_sender("נא לשלוח את שנת היצור של הרכב")
            except Exception as e:
                print(f"eror in add_post flow=car_model :{e}")
                # self.post_in_work.car_model = None
                # await self.post_in_work.save()
                self.user_db.flow= "add_post:car_model"
                await self.user_db.save()
                await self.message_sender("משהו השתבש בהכנסת שם הדגם, אנא נסו שוב")

            
        
        elif flow == "car_production_year":
            try:
                self.post_in_work = await Post().filter(Q(Q(owner_id=self.sender), Q(data_is_full=False), join_type="AND")).first()
                print(f"check car_model{self.post_in_work.car_model}id{self.post_in_work.id}")
                self.post_in_work.car_production_year = self.text
                await self.post_in_work.save()
                self.user_db.flow= "add_post:Engine_capacity"
                await self.user_db.save()
                await self.message_sender("נא להוסיף את הנפח המנוע בליטרים")
            except Exception as e:
                print(f"eror in add_post flow=car_production_year :{e}")
                self.post_in_work = await Post().filter(Q(Q(owner_id=self.sender), Q(data_is_full=False), join_type="AND")).first()
                # self.post_in_work.car_production_year = None
                # await self.post_in_work.save()
                self.user_db.flow= "add_post:car_production_year"
                await self.user_db.save()
                await self.message_sender("משהו השתבש בהכנסת שנת היצור של הרכב, אנא נסו שוב")

            
        elif flow == "Engine_capacity":
            try:
                self.post_in_work = await Post().filter(Q(Q(owner_id=self.sender), Q(data_is_full=False), join_type="AND")).first()
                print(f"check car_production_year{self.post_in_work.car_production_year}id{self.post_in_work.id}")
                self.post_in_work.Engine_capacity = self.text
                await self.post_in_work.save()
                self.user_db.flow= "add_post:horsepower"
                await self.user_db.save()
                await self.message_sender("נא להוסיף את כוחות הסוס של הרכב ")
            except Exception as e:
                print(f"eror in add_post flow=Engine_capacity :{e}")
                # self.post_in_work.Engine_capacity = None
               #  await self.post_in_work.save()
                self.user_db.flow= "add_post:Engine_capacity"
                await self.user_db.save()
                await self.message_sender("משהו השתבש בהכנסת מספר הנפח המנוע אנא נסו שוב")

            
            
        elif flow == "horsepower":
            try:
                self.post_in_work = await Post().filter(Q(Q(owner_id=self.sender), Q(data_is_full=False), join_type="AND")).first()
                print(f"check Engine_capacity{self.post_in_work.Engine_capacity}id{self.post_in_work.id}")
                self.post_in_work.horsepower = self.text
                await self.post_in_work.save()
                self.user_db.flow= "add_post:txt_content"
                await self.user_db.save()
                await self.message_sender("נא להוסיף תוכן הפוסט")
            except Exception as e:
                print(f"eror in add_post flow=horsepower :{e}")
                # self.post_in_work.horsepower = None
               #  await self.post_in_work.save()
                self.user_db.flow= "add_post:horsepower"
                await self.user_db.save()
                await self.message_sender("משהו השתבש בהכנסת מספר כוחות סוס אנא נסו שוב")

            
            
        elif flow == "txt_content":
            try:
                self.post_in_work = await Post().filter(Q(Q(owner_id=self.sender), Q(data_is_full=False), join_type="AND")).first()
                print(f"check horsepower{self.post_in_work.horsepower}id{self.post_in_work.id}")
                self.post_in_work.txt_content = self.text
                await self.post_in_work.save()
                self.user_db.flow= "add_post:km"
                await self.user_db.save()
                await self.message_sender("נא להוסיף את הקילומטרז של הרכב")
            except Exception as e:
                print(f"eror in add_post flow=txt_content :{e}")
                # self.post_in_work.txt_content = None
                # await self.post_in_work.save()
                self.user_db.flow= "add_post:txt_content"
                await self.user_db.save()
                await self.message_sender("משהו השתבש בהכתיבת הטקסט, אנא נסו שוב")

                
            
        elif flow == "km":
            try:
                self.post_in_work = await Post().filter(Q(Q(owner_id=self.sender), Q(data_is_full=False), join_type="AND")).first()
                print(f"check txt_content{self.post_in_work.txt_content}id{self.post_in_work.id}")
                self.post_in_work.km = self.text
                await self.post_in_work.save()
                
                self.user_db.flow= "add_post:address"
                await self.user_db.save()
                await self.message_sender("נא להוסיף כתובת לאיסוף")
            except Exception as e:
                print(f"eror in add_post flow=km :{e}")
                # self.post_in_work.km = None
                # await self.post_in_work.save()
                
                self.user_db.flow= "add_post:km"
                await self.user_db.save()
                await self.message_sender("משהו השתבש בהכנסת מספר הקילומטרים אנא נסו שוב")

            
        elif flow == "address":
            try:
                self.post_in_work = await Post().filter(Q(Q(owner_id=self.sender), Q(data_is_full=False), join_type="AND")).first()
                self.post_in_work.address = self.text
                await self.post_in_work.save()
                self.user_db.flow= "add_post:phone_number"
                await self.user_db.save()
                await self.message_sender("נא להוסיף את מספר הטלפון")    
            except Exception as e:
                print(f"eror in add_post flow=address :{e}")
               # self.post_in_work.address = None
                # await self.post_in_work.save()
                self.user_db.flow= "add_post:address"
                await self.user_db.save()
                await self.message_sender("משהו השתבש בהכנסת מספר הכתובת אנא נסו שוב")

            
            
        elif flow == "phone_number":
            try:
                self.post_in_work = await Post().filter(Q(Q(owner_id=self.sender), Q(data_is_full=False), join_type="AND")).first()
                self.post_in_work.phone_number = self.text
                await self.post_in_work.save()
                self.user_db.flow= "add_post:area"
                await self.user_db.save()
                await self.message_sender("נא להוסיף אתה אזור האיסוף של הרכב")    
            except Exception as e:
                print(f"eror in add_post flow = area :{e}")

                # self.post_in_work.phone_number = None
                # await self.post_in_work.save()

                self.user_db.flow= "add_post:phone_number"
                self.user_db.save()
                await self.message_sender("משהו השתבש בהכנסת מספר הטלפון אנא נסו שוב")

            
        elif flow == "area":
            try:
                self.post_in_work = await Post().filter(Q(Q(owner_id=self.sender), Q(data_is_full=False), join_type="AND")).first()
                self.post_in_work.area = self.text
                await self.post_in_work.save()
                self.user_db.flow= "add_post:cost"
                await self.user_db.save()
                await self.message_sender("נא להוסיף אתה מחיר השכרת רכב פר יום")    
            except Exception as e:
                print(f"eror in add_post flow=phone_number :{e}")
                # self.post_in_work.area= None
                # await self.post_in_work.save()
                
                self.user_db.flow= "add_post:area"

                self.user_db.save()
                await self.message_sender("משהו השתבש בהכנסת האזור אנא נסו שוב")
            
        elif flow == "cost":
            try:
                self.post_in_work = await Post().filter(Q(Q(owner_id=self.sender), Q(data_is_full=False), join_type="AND")).first()
                self.post_in_work.cost = self.text
                self.post_in_work.data_is_full = True
                await self.post_in_work.save()
                print(f"from add post in flow cost:{self.post_in_work.cost} type{self.post_in_work.car_company}")
                self.user_db.flow= None
                await self.user_db.save()
                markup=main_markup()
                if self.is_admin:
                    markup=admin_main_markup()
                await self.message_sender("הפוסט שלך פורסם בהצלחה ניתן יהיה לראות אותו בפוסטים שלי",markup = markup)   
            except Exception as e:
                print(f"eror in add_post flow=cost :{e}")
                self.post_in_work.cost= None
                self.post_in_work.data_is_full = False
                self.post_in_work.save()
                self.user_db.flow= "add_post:cost"
                self.user_db.save()
                await self.message_sender("משהו השתבש בהכנסת המחיר אנא נסו שוב")
                    
                
    async def main_window(self):
        markup=main_markup()
        if self.is_admin:
            markup=admin_main_markup()
        await self.message_sender("אנא בחר ",markup)
        
    async def callback_query(self):
        try:
            data = self.event.data.decode("utf-8").split(':')
            if len(data) > 1:
                await getattr(self, data[0])(*data[1:])
            else:
                await getattr(self, data[0])()
        except Exception as e:
            print(f"problem whit callback query{e}" )
            
        print(f"2222222222{data}")
        
    async def delete_post_choice(self,page=0):
        try:
            if type(page) is str:
                page = int(page)
            print("yyy")
            next_flag=True
            prev_flag=True
            posts = await Post().filter(Q(Q(owner_id=self.sender), Q(data_is_full=True), join_type="AND")).all()
            print(len(posts))
            if len(posts) == 0:
                self.event.edit("אין לך עדיין פוסטים אבל אתה מוזמן להוסיף פוסט עלידי לחיצה על הוספת פוסט")
            print("lllltttt")
            if page == 0:
                prev_flag=False
            first_post_index = page * POST_PER_PAGE
            if len(posts)>first_post_index+POST_PER_PAGE:
                page_post = posts[first_post_index:first_post_index+POST_PER_PAGE]
                
                
            else:
                page_post = posts[first_post_index:]
                next_flag=False
            print("lllltttt-------")
            markup = []
            try:
                for post in page_post:
                    print(f"{post.date_and_time}")
                    markup.append([Button.inline(f"{post.date_and_time}",f'delete_post:{post.id}')])
                
            except Exception as e:
                print(f"problem in my posts{e}")
            print(markup)
            print("----------")
            #markup.append(go_buck_to_menu) 
            print(markup)
            print("----------")  
            #await self.message_sender("נא לבחור איזה פוסט למחוק",markup)
            
            next_page_button =Button.inline(" >>",f'delete_post_choice:{page+1}')
            prev_page_button =Button.inline(" <<",f'delete_post_choice:{page-1}')
            move_page_markup=[]
            if prev_flag and next_flag:
                move_page_markup.append(prev_page_button)
                move_page_markup.append(next_page_button)
                #move_page_markup.append(go_buck_to_main_markup[0])
            elif prev_flag:
                move_page_markup.append(prev_page_button)
                #move_page_markup.append(go_buck_to_main_markup[0])
                
            elif next_flag:
                move_page_markup.append(next_page_button)
                #move_page_markup.append(go_buck_to_main_markup[0])

            
            markup.append(go_buck_to_main_markup)
            markup.append(move_page_markup)
            print(markup)
            await self.message_sender(f"מספר דף:{page}" + "\nנא לבחור איזה פוסט למחוק",markup , True)
        except Exception as e:
            print(f"delete error{e}")
        
    async def delete_post(self,post_id):
        try:
            await Post.filter(id = post_id).delete()
            await self.message_sender(f"פוסט מספר::{post_id} נמחק בהצלחה",go_buck_to_main_markup)
        except Exception as e:
            print(f"problem delete_post_choice{e}")
            
#------------------------------------------------------------------------ CHANGE POST FUNCTIONS
           
    async def change_post_choice(self,page=0):
        if type(page) is str:
            page = int(page)
        print("yyy")
        next_flag=True
        prev_flag=True
        posts = await Post().filter(Q(Q(owner_id=self.sender), Q(data_is_full=True), join_type="AND")).all()
        print(len(posts))
        if len(posts) == 0:
            await self.message_sender(message = "אין לך עדיין פוסטים אבל אתה מוזמן להוסיף פוסט עלידי לחיצה על הוספת פוסט" , edit = True)
        print("lllltttt")
        if page == 0:
            prev_flag=False
        first_post_index = page * POST_PER_PAGE
        if len(posts)>first_post_index+POST_PER_PAGE:
            page_post = posts[first_post_index:first_post_index+POST_PER_PAGE]
            
            
        else:
            page_post = posts[first_post_index:]
            next_flag=False
        print("lllltttt-------")
        markup = []
        try:
            for post in page_post:
                print(f"{post.date_and_time}")
                markup.append([Button.inline(f"{post.date_and_time}",f'change_post:{post.id}')])
               
        except Exception as e:
            print(f"change_post_choice{e}")
            
        await self.message_sender("נא לבחור איזה פוסט תרצה לשנות",markup,True)
    
        next_page_button =[Button.inline(" >>",f'change_post_choice:{page+1}')]
        prev_page_button =[Button.inline(" <<",f'change_post_choice:{page-1}')]
        move_page_markup=[]
        if prev_flag and next_flag:
            move_page_markup.append([prev_page_button,next_flag])
            move_page_markup.append([go_buck_to_main_markup])
        elif prev_flag:
            move_page_markup.append(prev_page_button)
            move_page_markup.append(go_buck_to_main_markup)
            
        elif next_flag:
            move_page_markup.append(next_page_button)
            move_page_markup.append(go_buck_to_main_markup)
        else:
            move_page_markup.append(go_buck_to_main_markup)
        
        await self.message_sender(f"מספר דף:{page}",move_page_markup)
            
        
    #change post attributs function
    async def change_post(self,post_id):
        await self.message_sender("נא לבחור איזה פרט תרצה לשנות",change_post_option_markup(post_id),True)   
    async def change_post_car_company(self,post_id):
        self.user_db.flow=f"change_post_car_company:{post_id}"
        await self.user_db.save()
        await self.message_sender(message = "נא לשלוח בהודעת טקסט את שם החברה החדש של הרכב",edit = True)
    
    async def change_post_car_type(self,post_id):
        self.user_db.flow=f"change_post_car_type:{post_id}"
        await self.user_db.save()
        await self.message_sender(message = "נא לשלוח בהודעת טקסט את הקוטגריה החדשה שהרכב משוייך אליה ",edit = True)
        
    async def change_post_car_model(self,post_id):
        self.user_db.flow=f"change_post_car_model:{post_id}"
        await self.user_db.save()
        await self.message_sender(message = " נא לשלוח בהודעת טקסט את הדגם החדש של הרכב ",edit = True)
        
    async def change_post_car_production_year(self,post_id):
        self.user_db.flow=f"change_post_car_production_year:{post_id}"
        await self.user_db.save()
        await self.message_sender(message = "נא לשלוח בהודעת טקסט את שנת היצור ",edit = True)
        
    async def change_post_Engine_capacity(self,post_id):
        self.user_db.flow=f"change_post_Engine_capacity:{post_id}"
        await self.user_db.save()
        await self.message_sender(message = "נא לשלוח בהודעת טקסט את נפח המנוע ",edit = True)
        
    async def change_post_horsepower(self,post_id):
        self.user_db.flow=f"change_post_horsepower:{post_id}"
        await self.user_db.save()
        await self.message_sender(message = "נא לשלוח בהודעת טקסט את כוח הסוס של הרכב ",edit = True)
        
    async def change_post_photo(self,post_id):
        self.user_db.flow=f"change_post_photo:{post_id}"
        await self.user_db.save()
        await self.message_sender(message = "נא לשלוח את התמונה החדשה ",edit = True)
        
    async def change_post_txt_content(self,post_id):
        self.user_db.flow=f"change_post_txt_content:{post_id}"
        await self.user_db.save()
        await self.message_sender(message = "נא לשלוח בהודעת טקסט את תוכן הטקסט ",edit = True)
        
    async def change_post_km(self,post_id):
        self.user_db.flow=f"change_post_km:{post_id}"
        await self.user_db.save()
        await self.message_sender(message = "נא לשלוח בהודעת טקסט קלומטרז״ החדש ",edit = True)
        
    async def change_post_address(self,post_id):
        self.user_db.flow=f"change_post_address:{post_id}"
        await self.user_db.save()
        await self.message_sender(message = "נא לשלוח בהודעת טקסט את הכתובת החדשה ",edit = True)
        
    async def change_post_phone_number(self,post_id):
        self.user_db.flow=f"change_post_phone_number:{post_id}"
        await self.user_db.save()
        await self.message_sender(message = " נא לשלוח בהודעת טקסט מספר הטלפון החדש ",edit = True)
        
    async def change_post_cost(self,post_id):
        self.user_db.flow=f"change_post_cost:{post_id}"
        await self.user_db.save()
        await self.message_sender(message = "נא לשלוח בהודעת טקסט את המחיר החדש ",edit = True)

# ------------------------------------------------------------------------ post by area
    
    async def choose_post_area(self):
        
        all_posts = await Post.filter().all()
        print(f"{all_posts}+++++++++)))))")
        area_list=[]
        for post in all_posts:
            print("::::::")
            if post.area not in area_list:
                area_list.append(post.area)
        print(area_list)        
        markup = []
        for area in area_list:
            markup.append([Button.inline(f"{area}",f'area_paging:{area}')])
        print("mama")
        markup.append(go_buck_to_menu)
        print(markup)
        m = await self.message_sender("נא לבחור את אזור הפוסטים",markup , True)
        await self.save_all_lest_messag([m.id])
        
    async def area_paging(self,area,page = 0):
        
        if type(page)is str:
            page = int(page)
            
        posts = await Post.filter(area = area ).all()
        prev_flag = True
        next_flag = True
        print(len(posts))
        if len(posts) == 0:
            await self.message_sender("לא נמצאו פוסטים",[go_buck_to_main_markup])
        else:
            if page == 0:
                prev_flag=False
            first_post_index = page * POST_PER_PAGE
            if len(posts)>first_post_index+POST_PER_PAGE:
                page_post = posts[first_post_index:first_post_index+POST_PER_PAGE]

            else:
                page_post = posts[first_post_index:]
                next_flag=False
            try:
                for post in page_post:
                    print(f"ssssssss:{post.car_company}")
                    post_text = Post_format.format(post.car_company,post.car_model,post.car_type,post.car_production_year,post.Engine_capacity,post.horsepower,str(post.from_date)[:10],str(post.to_date)[:10],post.txt_content,post.km,post.cost)
                    print(f"post text::{post_text}")
                    if post.photo_path==None:
                        await self.message_sender(post_text,go_buck_to_main_markup)
                    else:
                        print("pipi")
                        m=await bot.send_file( self.sender , post.photo_path ,caption = post_text, buttons = [Button.inline(" לפרטים",f'additional_info_screen:{post.id}:{None}:{None}:{page}:{area}')])
                        await self.save_all_lest_messag([m.id])
            except Exception as e:
                print(f"problem in my posts{e}")

            next_page_button =Button.inline(" >>",f'area_paging:{area}:{page+1}')
            prev_page_button =Button.inline(" <<",f'area_paging:{area}:{page-1}')
            move_page_markup=[]
            if prev_flag and next_flag:
                move_page_markup.append(prev_page_button)
                move_page_markup.append(next_page_button)
            elif prev_flag:
                move_page_markup.append(prev_page_button)
                #move_page_markup.append(go_buck_to_main_markup)

            elif next_flag:
                move_page_markup.append(next_page_button)
                #move_page_markup.append(go_buck_to_main_markup)
            
            #move_page_markup.append(go_buck_to_main_markup)
            markup = []
            markup.append(move_page_markup)
            markup.append(go_buck_to_menu_no_edit)
            print(markup)
            m = await self.message_sender(f"מספר דף:{page}",markup)
            await self.save_all_lest_messag([m.id])
    
    async def test_area(self,id):    
        await self.message_sender("הכול בסדר",go_buck_to_main_markup)
    
   #----elad------------
    async def search(self):
        m= [[Button.inline("חפש לפי שם חברת הרכב",'search_by_car_company')],
            [Button.inline("חפש לפי שם הרכב",'search_by_car_name')],
            [Button.inline(" חפש לפי סוג רכב ",'search_by_car_type')],
            [Button.inline(" חפש לפי דגם רכב ",'search_by_car_model')],
            [Button.inline(" חפש לפי שנת יצור ",'search_by_car_production_year')],
            ]
        await self.event.edit("אנא בחר פרמטר לחיפוש הרכב" , buttons = m)
        #await self.message_sender("choose an option",m)

    #------------ Search filters-----------------------
    async def search_by_car_company(self):
        posts = await Post.all()
        posts_info = ""
        for post in posts:
            posts_info += "," + str(post.car_company)
            
        await self.event.edit("שמות החברות הקיימות במערכת הן :" + posts_info + "\n" + "אנא שלח את שם חברת הרכב")
        #await self.message_sender("שמות החברות הקיימות במערכת הן :" + posts_info + "\n" + "אנא שלח את שם חברת הרכב")
        filter = 'company'
        print("ssdii")
        self.user_db.flow = f"search_filter:{filter}"
        await self.user_db.save()

    async def search_by_car_name(self):
        posts = await Post.all()
        posts_info = ""
        for post in posts:
            posts_info += "," + str(post.car_name)
            
        await self.event.edit("שמות הרכבים הקיימים במערכת הן :" + posts_info + "\n" + "אנא שלח את שם הרכב")
        #await self.message_sender("אנא שלח את שם הרכב")
        filter = 'name'
        self.user_db.flow = f"search_filter:{filter}"
        await self.user_db.save()

    async def search_by_car_type(self):
        posts = await Post.all()
        posts_info = ""
        for post in posts:
            posts_info += "," + str(post.car_type)
            
        await self.event.edit("שמות סוגי הרכבים הקיימים במערכת הן :" + posts_info + "\n" + "אנא שלח את סוג רכב ")
        #await self.message_sender("אנא שלח את סוג רכב ")
        filter = 'type'
        self.user_db.flow = f"search_filter:{filter}"
        await self.user_db.save()

    async def search_by_car_model(self):
        posts = await Post.all()
        posts_info = ""
        for post in posts:
            posts_info += "," + str(post.car_model)
            
        await self.event.edit("שמות סוגי הדגמים הקיימים במערכת הן :" + posts_info + "\n" + "אנא שלח את דגם הרכב")
        #await self.message_sender("אנא שלח את דגם הרכב")
        filter = 'model'
        self.user_db.flow = f"search_filter:{filter}"
        await self.user_db.save()

    async def search_by_car_production_year(self):
        posts = await Post.all()
        posts_info = ""
        for post in posts:
            posts_info += "," + str(post.car_production_year)
            
        await self.event.edit("הנות יצור הרכבים הקיימים במערכת הן:" + posts_info + "\n" + "אנא שלח את שנת יצור הרכב")
        #await self.message_sender("אנא שלח את שנת יצור הרכב")
        filter = 'year'
        self.user_db.flow = f"search_filter:{filter}"
        await self.user_db.save()
    #---------------------------------------------------------------


    async def search_filter(self ,filter_type,query, page = 0 ):
        if type(page) is str:
            page = int(page)
        print(f"kakakaka{filter_type}")
        print(f"kakakaka{type(filter_type)}")
        print(f"jsodajf{query}")
        next_flag=True
        prev_flag=True

        if filter_type == 'company':
            posts = await Post.filter(car_company = query).all()
        if filter_type == 'name':
            posts = await Post.filter(car_name = query).all()
        if filter_type == 'type':
            posts = await Post.filter(car_type = query).all()
        if filter_type == 'model':
            posts = await Post.filter(car_model = query).all()
        if filter_type == 'year':
            posts = await Post.filter(car_production_year = query).all()

        print(len(posts))
        if len(posts) == 0:
            await self.message_sender("לא נמצאו פוסטים",[go_buck_to_main_markup])
        else:
            if page == 0:
                prev_flag=False
            first_post_index = page * POST_PER_PAGE
            if len(posts)>first_post_index+POST_PER_PAGE:
                page_post = posts[first_post_index:first_post_index+POST_PER_PAGE]

            else:
                page_post = posts[first_post_index:]
                next_flag=False
            try:
                for post in page_post:
                    print(f"ssssssss:{post.car_company}")
                    post_text = Post_format.format(post.car_company,post.car_model,post.car_type,post.car_production_year,post.Engine_capacity,post.horsepower,str(post.from_date)[:10],str(post.to_date)[:10],post.txt_content,post.km,post.cost)
                    print(f"post text::{post_text}")
                    if post.photo_path==None:
                        await self.message_sender(post_text,go_buck_to_main_markup)
                    else:
                        print("pipi")
                        m=await bot.send_file( self.sender , post.photo_path ,caption = post_text , buttons= [Button.inline(" לפרטים",f'additional_info_screen:{post.id}:{filter_type}:{query}:{page}')])
                        await self.save_all_lest_messag([m.id])
                       # await self.message_sender('לפרטים נוספים',[Button.inline(" פרטים",f'additional_info_screen:{post.id}:{filter_type}:{query}:{page}')])
            except Exception as e:
                print(f"problem in my posts{e}")

            next_page_button =Button.inline(" >>",f'search_filter:{filter_type}:{query}:{page+1}')
            prev_page_button =Button.inline(" <<",f'search_filter:{filter_type}:{query}:{page-1}')
            move_page_markup=[]
            if prev_flag and next_flag:
                move_page_markup.append(prev_page_button)
                move_page_markup.append(next_page_button)
            elif prev_flag:
                move_page_markup.append(prev_page_button)
                #move_page_markup.append(go_buck_to_main_markup)

            elif next_flag:
                move_page_markup.append(next_page_button)
                #move_page_markup.append(go_buck_to_main_markup)
            
            #move_page_markup.append(go_buck_to_main_markup)
            markup = []
            markup.append(move_page_markup)
            markup.append(go_buck_to_menu_no_edit)
            print(markup)
            m = await self.message_sender(f"מספר דף:{page}",markup)
            await self.save_all_lest_messag([m.id])
            
    async def additional_info_screen(self,post_id,filter,query,page ,area = None):
            try:
                # prefetch_related("owner")
                
                post1 = await Post().filter(id = post_id).all()
                for post in post1:
                    await post.fetch_related('owner')
                    full = await bot(GetFullUserRequest(post.owner.id))
                    #print(full)       
                    #print(full.users[0].username)
                    user_link = "@" + str(full.users[0].username)
                    post_text = Post_format_additional.format(user_link,post.phone_number,post.txt_content,str(post.date_and_time),post.address)
                    if not area:
                        beck_button=[Button.inline(" חזור",f'search_filter:{filter}:{query}:{page}')]
                    else:
                        beck_button = [Button.inline(" חזור",f'area_paging:{area}:{page}')]
                    buttons = [[Button.inline(" לשליחת בקשה",f'send_post_Request:{post_id}')],beck_button]
                    m=await bot.send_file( self.sender , post.photo_path ,caption = post_text , buttons = buttons)
                    #m =await self.message_sender(post_text,beck_button)
                    await self.save_all_lest_messag([m.id])
            except Exception as e:
                print(f"problem in my posts{e}")
                
                
    async def send_post_Request(self,post_id):
        try:
            post = await Post().filter(id = post_id).prefetch_related("owner").first()
            request = await PostRequest(post_id = post_id , request_sender_id = self.sender , request_reciever_id = post.owner.id).save()
            await self.message_sender(f" הפוסט נשלח לאישור בהצלחה",go_buck_to_menu)
            #test = await PostRequest.filter(post_id = post_id ).first()
            # test = await User.filter(id = post.owner.id).prefetch_related("request_as_reciever").first()
            # test = test.request_as_reciever
            # for i in test:
            #     print(f"test request id is {i.request_id}")
            
            
        except Exception as e:
            print(f"problem in send_post_Request :: {e}")
        
        

    
    async def order_history(self):
        await self.event.edit("אנא בחר" , buttons = order_history_option_buttons())
        
    async def order_history_request(self):
        try:
            post_requests = await PostRequest().filter(amswer = None , request_reciever_id = self.sender).prefetch_related("post","request_sender").all()
            
            print(f"post_requests len {len(post_requests)}")
            if len(post_requests) == 0:
                await self.event.edit("אין לך בקשות חדשות " , buttons = go_buck_to_menu)
            else:
                m =await self.event.edit("ttt")
                await bot.delete_messages(entity=self.sender, message_ids= [m.id])
                for post_request in post_requests:
                    requester = post_request.request_sender
                    post = post_request.post
                    full = await bot(GetFullUserRequest(post_request.request_sender.id))
                    #print(full)       
                    #print(full.users[0].username)
                    user_link = "@" + str(full.users[0].username)
                    post_text = Post_format_additional.format(user_link,post.phone_number,post.txt_content,str(post.date_and_time),post.address)
                    m=await bot.send_file( self.sender , post.photo_path ,caption = post_text )
                    await self.save_all_lest_messag([m.id])
                    
                    print(f"post content {post.id} sender {requester.first_name}")
                    
                await self.message_sender("אנא בחר" ,  go_buck_to_menu)
        except Exception as e:
            print(f" eror in order_history_request :: {e}")
        
    
    
    async def order_history_answerd(self):
        return    
            
    """[Button.inline(" אישורי הזמנות",'order_history_request')],
            [Button.inline("כל ההזמנות",'order_history_answerd')]  ,"""