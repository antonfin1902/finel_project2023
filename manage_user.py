
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
            full = await bot(GetFullUserRequest(self.sender))
            print("pini--------------------pppppppppppppppppppppp88888888888888")
            print(f"the ful is{full}")
            if full.users[0].username is None or str(full.users[0].username) =="None":
                await bot.send_file( self.sender , "photoDir/system1photo.jpeg",caption = "כדי ששוכרים או משכירים יוכלו לגשת אליך נא להוסיף username בטלגרם" )
            #system1photo.jpeg
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
        await self.restart_flow()
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
    async def message_sender(self,message,markup=None ,edit =None):
        m=None
        if markup is None and edit == None:
            m = await self.event.respond(message)
        elif markup is None and edit :
            m = await self.event.edit(message)
        
        elif edit :
            m = await self.event.edit( message ,buttons = markup)
        else:
            m = await self.event.respond( message ,buttons = markup)    
        return m
        
    async def private_message(self):
        print(f"theflow is:{self.user_db.flow}")
        if self.user_db.flow is None:
           self.user_db.flow = "editoe" 
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
                
            await self.message_sender("שם חברת הרכב שונה בהצלחה",markup = main_markup())
            
        elif "change_post_car_type" in self.user_db.flow :
            params = self.user_db.flow .split(":")
            await Post().filter(id = int(params[1])).update(car_type= self.text)
            self.user_db.flow= None
            await self.user_db.save()
            markup=main_markup()
            if self.is_admin:
                markup=admin_main_markup()
            await self.message_sender("קטגוריית הרכב שונתה בהצלחה",markup=main_markup())
            
    
        
        elif "change_post_car_model" in self.user_db.flow :
            params = self.user_db.flow .split(":")
            await Post().filter(id = int(params[1])).update(car_model= self.text)
            self.user_db.flow= None
            await self.user_db.save()
            markup=main_markup()
            if self.is_admin:
                markup=admin_main_markup()
            await self.message_sender("דגם הרכב שונה בהצלחה",markup=main_markup())
        
        elif "change_post_car_production_year" in self.user_db.flow :
            params = self.user_db.flow .split(":")
            await Post().filter(id = int(params[1])).update(car_production_year= self.text)
            self.user_db.flow= None
            await self.user_db.save()
            markup=main_markup()
            if self.is_admin:
                markup=admin_main_markup()
            await self.message_sender("שנת היצור שונתה בהצלחה",markup=main_markup())
            
        elif "change_post_Engine_capacity" in self.user_db.flow :
            params = self.user_db.flow .split(":")
            await Post().filter(id = int(params[1])).update(Engine_capacity= self.text)
            self.user_db.flow= None
            await self.user_db.save()
            markup=main_markup()
            if self.is_admin:
                markup=admin_main_markup()
            await self.message_sender("נפח המנוע שונה בהצלחה",markup=main_markup())
            
        elif "change_post_horsepower" in self.user_db.flow :
            params = self.user_db.flow .split(":")
            await Post().filter(id = int(params[1])).update(horsepower= self.text)
            self.user_db.flow= None
            await self.user_db.save()
            markup=main_markup()
            if self.is_admin:
                markup=admin_main_markup()
            await self.message_sender("כוחות הסוס שונו בהצלחה",markup=main_markup())
        #צריך לסדר את שינוי התמונה    
        elif "change_post_photo" in self.user_db.flow :
            params = self.user_db.flow .split(":")
            await Post().filter(id = int(params[1])).update(horsepower= self.text)
            self.user_db.flow= None
            await self.user_db.save()
            markup=main_markup()
            if self.is_admin:
                markup=admin_main_markup()
            await self.message_sender("כוחות הסוס שונו בהצלחה",markup=main_markup())
            
        elif "change_post_txt_content" in self.user_db.flow :
            params = self.user_db.flow .split(":")
            await Post().filter(id = int(params[1])).update(txt_content= self.text)
            self.user_db.flow= None
            await self.user_db.save()
            markup=main_markup()
            if self.is_admin:
                markup=admin_main_markup()
            await self.message_sender("תוכן הפוסט שונה בהצלחה",markup=main_markup())

        elif "change_post_km" in self.user_db.flow :
            params = self.user_db.flow .split(":")
            await Post().filter(id = int(params[1])).update(km= self.text)
            self.user_db.flow= None
            await self.user_db.save()
            markup=main_markup()
            if self.is_admin:
                markup=admin_main_markup()
            await self.message_sender("הקילוג״ הרכב שונה בהצלחה",markup=main_markup())
        
        elif 'search_filter' in self.user_db.flow:
            params = self.user_db.flow.split(":")
            await self.search_filter(params[1],self.text)    
        
        elif "add_text_to_post_request" in self.user_db.flow :
            params = self.user_db.flow.split(":") 
            await PostRequest.filter(request_id = params[1]).update(request_text = self.text)
            await self.message_sender("סיבת הסירוב נשמרה בהצלחה",markup=main_markup())
                
        else:
            self.user_db.flow = None
            await self.user_db.save()
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

    """User_format= "שם : {} {} \n אימייל: {} \n מספר טלפון: {} \n דירוגים שלי: \n דירוגים שלי כמשכיר  \n זמינות:{} ניקיון: {} אמינות: {} 
        User_format1= "שם : {} {} \n אימייל: {} \n מספר טלפון: {} \n עדיין לא דירגו אותך """
    async def user_profile(self):
        #calculate avrage garde for seller..need to conver as function 
        try:
            # seller_rate_list=[self.user_db.seller_payment_grade,self.user_db.seller_availability_grade,self.user_db.seller_cleaning_grade,self.user_db.sellerre_liability_grade]
            # avg_seller_rate=int(map(sum,seller_rate_list))/len(seller_rate_list)
            print(f"the fuking grage is {self.user_db.seller_availability_grade}")
            grade_amunt = len(await PostRequest.filter(request_reciever_id = self.sender, step_grade = "F").all())
            if  grade_amunt !=0: 
                user_text= User_format.format(self.user_db.first_name,self.user_db.last_name,self.user_db.email,self.user_db.phone_number,self.user_db.seller_availability_grade,self.user_db.seller_cleaning_grade,self.user_db.sellerre_liability_grade)
            else:
                user_text= User_format1.format(self.user_db.first_name,self.user_db.last_name,self.user_db.email,self.user_db.phone_number)
            #user_text+= f"\n דירוג בתור משכיר \n אמינות{self.user_db.sellerre_liability_grade} ניקיון{self.user_db.seller_cleaning_grade} זמינות{self.user_db.seller_availability_grade}"
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
                await self.message_sender("נא להוסיף את סוג הרכב ")
            except Exception as e:
                print(f"eror in add_post flow=none :{e}")
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
                    flow = "car_photo"
                    #await self.message_sender("נא לשלוח טקסט סתמי עד 10 תוים להתחלת תהליך קליתת התמונה")  
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
                        await self.message_sender("נא להוסיף את דגם הרכב ")  
                        
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
                await self.message_sender("נא להוסיף תוכן הפוסט ואת תאריכי הזמינות של הרכב לדוגמא: 22.3-28.3")
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
     
        all_posts = await Post.filter(is_order = False).all()
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
            #.filter(is_order = False)
        posts = await Post.filter(area = area ,is_order = False ).all()
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
        posts = await Post.filter(is_order = False).all()
        posts_info_list = []
        posts_info = ""
        for post in posts:
            if str(post.car_company) not in  posts_info_list:
                posts_info += "," + str(post.car_company)
                posts_info_list.append(str(post.car_company))
               
        await self.event.edit("שמות החברות הקיימות במערכת הן :" + posts_info + "\n" + "אנא שלח את שם חברת הרכב")
        #await self.message_sender("שמות החברות הקיימות במערכת הן :" + posts_info + "\n" + "אנא שלח את שם חברת הרכב")
        filter = 'company'
        print("ssdii")
        self.user_db.flow = f"search_filter:{filter}"
        await self.user_db.save()

    async def search_by_car_name(self):
        posts = await Post.filter(is_order = False).all()
        posts_info_list = []
        posts_info = ""
        for post in posts:
            if str(post.car_name) not in  posts_info_list:
                posts_info += "," + str(post.car_name)
                posts_info_list.append(str(post.car_name))
        # posts_info = ""
        # for post in posts:
        #     posts_info += "," + str(post.car_name)
            
        await self.event.edit("שמות הרכבים הקיימים במערכת הן :" + posts_info + "\n" + "אנא שלח את שם הרכב")
        #await self.message_sender("אנא שלח את שם הרכב")
        filter = 'name'
        self.user_db.flow = f"search_filter:{filter}"
        await self.user_db.save()

    async def search_by_car_type(self):
        posts = await Post.filter(is_order = False).all()
        posts_info_list = []
        posts_info = ""
        for post in posts:
            if str(post.car_type) not in  posts_info_list:
                posts_info += "," + str(post.car_type)
                posts_info_list.append(str(post.car_type))
        # posts_info = ""
        # for post in posts:
        #     posts_info += "," + str(post.car_type)
            
        await self.event.edit("שמות סוגי הרכבים הקיימים במערכת הן :" + posts_info + "\n" + "אנא שלח את סוג רכב ")
        #await self.message_sender("אנא שלח את סוג רכב ")
        filter = 'type'
        self.user_db.flow = f"search_filter:{filter}"
        await self.user_db.save()

    async def search_by_car_model(self):
        posts = await Post.filter(is_order = False).all()
        posts_info_list = []
        posts_info = ""
        for post in posts:
            if str(post.car_model) not in  posts_info_list:
                posts_info += "," + str(post.car_model)
                posts_info_list.append(str(post.car_model))
        # posts_info = ""
        # for post in posts:
        #     posts_info += "," + str(post.car_model)
            
        await self.event.edit("שמות סוגי הדגמים הקיימים במערכת הן :" + posts_info + "\n" + "אנא שלח את דגם הרכב")
        #await self.message_sender("אנא שלח את דגם הרכב")
        filter = 'model'
        self.user_db.flow = f"search_filter:{filter}"
        await self.user_db.save()

    async def search_by_car_production_year(self):
        posts = await Post.filter(is_order = False).all()
        posts_info_list = []
        posts_info = ""
        for post in posts:
            if str(post.car_production_year) not in  posts_info_list:
                posts_info += "," + str(post.car_production_year)
                posts_info_list.append(str(post.car_production_year))
        # posts_info = ""
        # for post in posts:
        #     posts_info += "," + str(post.car_production_year)
            
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
            posts = await Post.filter(car_company = query ,is_order = False).all()
        if filter_type == 'name':
            posts = await Post.filter(car_name = query ,is_order = False).all()
        if filter_type == 'type':
            posts = await Post.filter(car_type = query ,is_order = False).all()
        if filter_type == 'model':
            posts = await Post.filter(car_model = query ,is_order = False).all()
        if filter_type == 'year':
            posts = await Post.filter(car_production_year = query ,is_order = False).all()

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
                    post_text = Post_format_additional.format(user_link,post.phone_number,post.txt_content,str(post.date_and_time)[:10],post.address)
                    grade_amunt = len(await PostRequest.filter(request_reciever_id = post.owner.id, step_grade = "F").all())
                    if grade_amunt != 0:
                        post_text += f"\nדירוג המשכיר ::\n כמות דירוגים :{grade_amunt}\n אמינות:{post.owner.sellerre_liability_grade}🎖 \n זמינות :{post.owner.seller_availability_grade} 🎖\n ניקיון {post.owner.seller_cleaning_grade} 🎖"
                    else:
                        post_text += "\n למשכיר זה אין עוד דירוגים"
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
        await self.event.edit("אנא בחר" , buttons = order_history_byuer_or_seller)
    
    async def order_history_option_owner(self):
        await self.event.edit("אנא בחר" , buttons = order_history_option_buttons())
    
    async def order_history_option_renter(self):
        await self.event.edit("אנא בחר" , buttons = order_history_option_buttons_renter())
    
    #order_history_byuer_or_seller = [Button.inline("בקשות בתור משכיר",'order_history_option_owner'), Button.inline("בקשות בתור שוכר",'order_history_option_renter') ]       
    async def order_history_request(self,all = None , renter = None):
        print(f"i get hear::{renter}")
        if all == "none":
            all = None
        try:
            if renter == None :
                if all:
                    post_requests = await PostRequest().filter(request_reciever_id = self.sender).prefetch_related("post","request_sender").all()  
                else:
                    post_requests = await PostRequest().filter(amswer = None , request_reciever_id = self.sender).prefetch_related("post","request_sender").all()
            else:
                if all:
                    post_requests = await PostRequest().filter(request_sender_id = self.sender).prefetch_related("post","request_reciever").all()  
                else:
                    post_requests = await PostRequest().filter(amswer = None , request_sender_id = self.sender).prefetch_related("post","request_reciever").all()
                
            
            print(f"post_requests len {len(post_requests)}")
            if len(post_requests) == 0:
                await self.event.edit("אין לך בקשות חדשות " , buttons = go_buck_to_menu)
            else:
                m =await self.event.edit("ttt")
                await bot.delete_messages(entity=self.sender, message_ids= [m.id])
                if renter:
                    for post_request in post_requests:
                        reciever = post_request.request_reciever
                        post = post_request.post
                        full = await bot(GetFullUserRequest(post_request.request_reciever.id))
                        #print(full)       
                        #print(full.users[0].username)
                        user_link = "@" + str(full.users[0].username)
                        if all:
                            post_text = Post_format_additional.format(user_link,post.phone_number,post.txt_content,str(post_request.date)[:16],post.address)
                            if not post_request.amswer:
                                answer = "סטטוס : מחכה לאישור"
                            elif post_request.amswer == "YES":
                                answer = "סטטוס : מאושר"
                            else:
                                answer = "סטטוס : סורב"
                            post_text = post_text + "\n" + answer
                            m=await bot.send_file( self.sender , post.photo_path ,caption = post_text )
                            await self.save_all_lest_messag([m.id])
                        else:   
                            #buttons = [[Button.inline(" אישור הבקשה",f'answer_post_Request:{post.id}:{post_request.request_id}:YES')],[Button.inline(" סירוב הבקשה",f'answer_post_Request:{post.id}:{post_request.request_id}:NO')]]
                            #print(f"mmmmmmmmmmmmm {buttons}")
                            post_text = Post_format_additional.format(user_link,post.phone_number,post.txt_content,str(post_request.date)[:16],post.address)
                            m=await bot.send_file( self.sender , post.photo_path ,caption = post_text )
                            await self.save_all_lest_messag([m.id])
                    await self.message_sender("לחזרה " , go_buck_to_menu)

                else:
                    for post_request in post_requests:
                        requester = post_request.request_sender
                        post = post_request.post
                        full = await bot(GetFullUserRequest(post_request.request_sender.id))
                        #print(full)       
                        #print(full.users[0].username)
                        user_link = "@" + str(full.users[0].username)
                        if all:
                            post_text = Post_format_additional.format(user_link,requester.phone_number,post.txt_content,str(post_request.date)[:16],post.address)
                            if not post_request.amswer:
                                answer = "סטטוס : מחכה לאישור"
                            elif post_request.amswer == "YES":
                                answer = "סטטוס : מאושר"
                            else:
                                answer = "סטטוס : סורב"
                            post_text = post_text + "\n" + answer
                            m=await bot.send_file( self.sender , post.photo_path ,caption = post_text )
                            await self.save_all_lest_messag([m.id])
                        else:   
                            buttons = [[Button.inline(" אישור הבקשה",f'answer_post_Request:{post.id}:{post_request.request_id}:YES')],[Button.inline(" סירוב הבקשה",f'answer_post_Request:{post.id}:{post_request.request_id}:NO')],go_buck_to_menu]
                            print(f"mmmmmmmmmmmmm {buttons}")
                            post_text = Post_format_additional.format(user_link,requester.phone_number,post.txt_content,str(post_request.date)[:16],post.address)
                            post_text+="\n סטטוס: ממתין ל אישור"
                            m=await bot.send_file( self.sender , post.photo_path ,caption = post_text ,buttons = buttons)
                            await self.save_all_lest_messag([m.id])
                        
                        print(f"post content {post.id} sender {requester.first_name}")
                    if all:
                        await self.message_sender("לחזרה " , go_buck_to_menu)
                
        
                #await self.message_sender("אנא בחר" ,  go_buck_to_menu)
        except Exception as e:
            print(f" eror in order_history_request :: {e}")
        
    async def answer_post_Request(self,post_id,post_requests_id , answer):
        print(f"the answer is :{answer}")
        try:
            if answer == "YES":
                await PostRequest.filter(request_id = post_requests_id).update(amswer = "YES")
                await Post.filter(id = post_id).update(is_order = True)
                ather_posts = await PostRequest.filter(post_id = post_id).all()
                for post_request in ather_posts:
                    if int(post_requests_id) != post_request.request_id:
                        await PostRequest.filter(request_id = post_request.request_id).update(amswer = "NO" , request_text = "הבקשה נדחתה בגלל שהשוכר השכיר כבר את הרכב") 
                await self.message_sender("הבקשה של הרכב שלך אושרה ונשלחה עדכון למשכיר \n מוזמן ליצור קשר עם שולח הבקשה ולדרך דרך כפתור כל ההזמנות " , go_buck_to_menu)
            else:
                await PostRequest.filter(request_id = post_requests_id).update(amswer = "NO")
                await self.message_sender(" נא לשלוח בהודעת טקסט את סיבת הסירוב \n במקרה שאתה לא מעוניין לתת סיבה חזור לטפריט הראשי" ,go_buck_to_menu)
                self.user_db.flow= f"add_text_to_post_request:{post_requests_id}"
                await self.user_db.save()
        except Exception as e:
            print(f"poblem in answer_post_Request :: {e}")
    
    
    async def order_history_approved_post_requests(self,as_renter = None):
        try:
            if as_renter:
                post_requests = await PostRequest().filter(amswer = "YES" ,request_sender_id = self.sender).prefetch_related("post","request_reciever").all()
            else:
                post_requests = await PostRequest().filter(amswer = "YES" ,request_reciever_id = self.sender).prefetch_related("post","request_sender").all()  
                
            print(f"post_requests len {len(post_requests)}")
            if len(post_requests) == 0:
                await self.event.edit("אין לך בקשות חדשות " , buttons = go_buck_to_menu)
            else:
                m =await self.event.edit("ttt")
                await bot.delete_messages(entity=self.sender, message_ids= [m.id])
                for post_request in post_requests:
                    if as_renter:
                        other_side = post_request.request_reciever
                    else:
                        other_side = post_request.request_sender
                    post = post_request.post
                    full = await bot(GetFullUserRequest(other_side.id))
                    user_link = "@" + str(full.users[0].username)
                    #grade(self,requst_id ,id_of_ho_you_grader ,step = "0",befor_grade=None, as_renter ="T" ):
                    
                        
                    post_text = Post_format_additional.format(user_link,other_side.phone_number,post.txt_content,str(post_request.date)[:16],post.address)
                    print(f"the date is :: {str(post_request.date)[:14]}")
                    answer = "סטטוס : מאושר"
                    post_text = post_text + "\n" + answer
                    if as_renter and post_request.step_grade!='F':
                        button = [Button.inline(" דירוג ",f'grade:{post_request.request_id}:{other_side.id}:{"0"}:1:T')]
                        m=await bot.send_file( self.sender , post.photo_path ,caption = post_text ,buttons= button)  
                    elif as_renter: 
                         m=await bot.send_file( self.sender , post.photo_path ,caption = post_text )
                    else:
                        m=await bot.send_file( self.sender , post.photo_path ,caption = post_text )
                        
                    await self.save_all_lest_messag([m.id])
                await self.message_sender("לחזרה " , go_buck_to_menu)

        except Exception as e:
            print(f"porblem if :: order_history_approved_post_requests ::{e}")
    
    async def order_history_refus_post_requests(self,as_renter = None):
        try:
            if as_renter:
                post_requests = await PostRequest().filter(amswer = "NO" ,request_sender_id = self.sender).prefetch_related("post","request_reciever").all()
            else:
                post_requests = await PostRequest().filter(amswer = "NO" ,request_reciever_id = self.sender).prefetch_related("post","request_sender").all()  
                
            print(f"post_requests len {len(post_requests)}")
            if len(post_requests) == 0:
                await self.event.edit("אין לך בקשות חדשות " , buttons = go_buck_to_menu)
            else:
                m =await self.event.edit("ttt")
                await bot.delete_messages(entity=self.sender, message_ids= [m.id])
                for post_request in post_requests:
                    if as_renter:
                        other_side = post_request.request_reciever
                    else:
                        other_side = post_request.request_sender
                    post = post_request.post
                    full = await bot(GetFullUserRequest(other_side.id))
                    user_link = "@" + str(full.users[0].username)
                    post_text = Post_format_additional.format(user_link,other_side.phone_number,post.txt_content,str(post_request.date)[:16],post.address)
                    answer = "סטטוס : סורב" +f"\n סיבת סירוב :: {post_request.request_text}"
                    post_text = post_text + "\n" + answer
                    m=await bot.send_file( self.sender , post.photo_path ,caption = post_text )
                    await self.save_all_lest_messag([m.id])
                    
                await self.message_sender("לחזרה " , go_buck_to_menu)
        except Exception as e:
            print(f"porblem if :: order_history_refus_post_requests ::{e}")
            
    async def grade(self,requst_id ,id_of_ho_you_grader ,step = "0",befor_grade=None, as_renter ="T" ):
        try:
            if as_renter:
                
                if step == "0":
                    buttons = [[Button.inline(" 1 🎖 ",f'grade:{requst_id}:{id_of_ho_you_grader}:{"1"}:1:T')],[Button.inline(" 2 🎖 ",f'grade:{requst_id}:{id_of_ho_you_grader}:{"1"}:2:T')],[Button.inline(" 3 🎖 ",f'grade:{requst_id}:{id_of_ho_you_grader}:{"1"}:3:T')]]
                    await self.message_sender("נא לדרג את זמינות המשכיר ",buttons)
                elif step =="1":
                    requst = await PostRequest.filter(request_id = requst_id).first().prefetch_related("request_reciever")
                    requst.step_grade = "0"
                    await requst.save()
                    renter = requst.request_reciever
                    grade_amunt = len(await PostRequest.filter(request_reciever_id = renter.id , step_grade = "F").all())
                    renter.seller_availability_grade = int(renter.seller_availability_grade)*(grade_amunt/(grade_amunt+1))+int(befor_grade)*(1/(grade_amunt+1))
                    print(f"the new grade is ::{renter.seller_availability_grade}")
                    await renter.save()
                    buttons = [[Button.inline(" 1 🎖 ",f'grade:{requst_id}:{id_of_ho_you_grader}:2:1:T')],[Button.inline(" 2 🎖 ",f'grade:{requst_id}:{id_of_ho_you_grader}:2:2:T')],[Button.inline(" 3 🎖 ",f'grade:{requst_id}:{id_of_ho_you_grader}:2:3:T')]]
                    await self.message_sender("נא לדרג את ניקיון המשכיר ",buttons,"t")
                elif step =="2":
                    requst = await PostRequest.filter(request_id = requst_id).first().prefetch_related("request_reciever")
                    requst.step_grade = "1"
                    await requst.save()
                    renter = requst.request_reciever
                    grade_amunt = len(await PostRequest.filter(request_reciever_id = renter.id , step_grade = "F").all())
                    renter.seller_cleaning_grade = int(renter.seller_cleaning_grade)*(grade_amunt/(grade_amunt+1))+int(befor_grade)*(1/(grade_amunt+1))
                    await renter.save()
                    buttons = [[Button.inline(" 1 🎖 ",f'grade:{requst_id}:{id_of_ho_you_grader}:3:1:T')],[Button.inline(" 2 🎖 ",f'grade:{requst_id}:{id_of_ho_you_grader}:3:2:T')],[Button.inline(" 3 🎖 ",f'grade:{requst_id}:{id_of_ho_you_grader}:3:3:T')]]
                    await self.message_sender("נא לדרג את אמינות המשכיר ",buttons,"t")
                elif step =="3":
                    requst = await PostRequest.filter(request_id = requst_id).first().prefetch_related("request_reciever")
                    requst.step_grade = "F"
                    await requst.save()
                    renter = requst.request_reciever
                    grade_amunt = len(await PostRequest.filter(request_reciever_id = renter.id , step_grade = "F").all())
                    renter.sellerre_liability_grade = int(renter.sellerre_liability_grade)*(grade_amunt/(grade_amunt+1))+int(befor_grade)*(1/(grade_amunt+1))
                    await renter.save()
                    #buttons = [[Button.inline(" 1 🎖 ",f'grade:{requst_id}:{id_of_ho_you_grader}:3:1:T')],[Button.inline(" 2 🎖 ",f'grade:{requst_id}:{id_of_ho_you_grader}:3:2:T')],[Button.inline(" 2 🎖 ",f'grade:{requst_id}:{id_of_ho_you_grader}:3:3:T')]]
                    await self.message_sender("תודה שדירגתה את המשכיר",go_buck_to_menu,"t")
                    
            else:
                if step == "0":
                    self.message_sender("נא לדרג את דירוג השוכר  ")
        except Exception as e:
            print(f"problem in grade :: {e}")
            
        
        
         
    """seller_payment_grade = fields.IntField(default = 0)
    seller_availability_grade = fields.IntField(default = 0)
    seller_cleaning_grade = fields.IntField(default = 0)
    sellerre_liability_grade = fields.IntField(default = 0)
    buyer_payment_grade = fields.IntField(default = 0)
    buyer_availability_grade = fields.IntField(default = 0)
    buyer_cleaning_grade = fields.IntField(default = 0)
    buyer_reliability_grade = fields.IntField(default = 0)"""   
#------------------ admin options

    async def sum_of_users(self):
        
        users =await User.all()
        text = "-----------------------------------------------------------------\n"
        for user in users:
            
            if user.is_admin:
                text += f"שם:{user.last_name} | שם משפחה:{user.last_name} | מספר טלפון:{user.phone_number} | admin\n"
            else:
                text += f"שם:{user.last_name} | שם משפחה:{user.last_name} | מספר טלפון:{user.phone_number} | user\n"    
            text +="-----------------------------------------------------------------\n"
        text += f"סך הכול מספר משתמשים במערכת::{len(users)}"
        await self.message_sender(text,go_buck_to_menu,"TRUE")
        
    async def sum_of_posts(self):
        posts = await Post.all()
        
        await self.message_sender(f"כמות הפוסטים במערכת :: {len(posts)}",go_buck_to_menu,"TRUE")
        