from telethon.tl.custom import Button

def main_markup():  
    markup = [
            [Button.inline("פרופיל אישי",'user_profile')],
            [Button.inline("חיפוש",'search')],
            [Button.inline("הוספת פוסט",'add_post')],
            [Button.inline("פוסטים לפי אזור",'choose_post_area')],
            [Button.inline("פוסטים שלי",'my_posts')],
            [Button.inline(" מחיקת פוסט",'delete_post_choice')],
            [Button.inline('שנה פוסט','change_post_choice')],
            [Button.inline("היסטורית הזמנות",'order_history')]         
        ]
    return markup

def admin_main_markup(): 
    m= main_markup()
    m.append([Button.inline(" אישור משתמשים חדשים",'registration_aproval_list')]) 
    return m

def change_post_option_markup(post_id):
    markup = [
            [Button.inline(" שנה את שם חברת הרכב",f'change_post_car_company:{post_id}')],
            [Button.inline("שנה את קטגורית הרכב",f'change_post_car_type:{post_id}')],
            [Button.inline("שנה את דגם הרכב",f'change_post_car_model:{post_id}')],
            [Button.inline("שנה את שנת היצור",f'change_post_car_production_year:{post_id}')],
            [Button.inline("שנה את נפח המנוע",f'change_post_Engine_capacity:{post_id}')],
            [Button.inline("שנה את כוחות הסוס",f'change_post_horsepower:{post_id}')],
            [Button.inline(" שנה את תמונת הפוסט",f'change_post_photo:{post_id}')],
            [Button.inline("שנה את תוכן הפוסט",f'change_post_txt_content:{post_id}')],
            [Button.inline("  שנה את קילומטרג״ הרכב",f'change_post_km:{post_id}')],
            [Button.inline("שנה את כתובת האיסוף",f'change_post_address:{post_id}')],
            [Button.inline(" שנה את מספר הטלפון ",f'change_post_phone_number:{post_id}')],
            [Button.inline(" שנה את מחיר הרכב ",f'change_post_cost:{post_id}')]     
        ]
    return markup

go_buck_to_main_markup = [Button.inline(" לחץ לחזרה לתפריט הראשי",'menu')]


go_buck_to_menu = [Button.inline(" לחץ לחזרה לתפריט הראשי",'menu')]
go_buck_to_menu_no_edit = [Button.inline(" לחץ לחזרה לתפריט הראשי",'menu:0:0:F')]

def order_history_option_buttons():  
    markup = [
            [Button.inline(" אישורי הזמנות",'order_history_request')],
            [Button.inline("כל ההזמנות",'order_history_answerd')]  ,
            go_buck_to_main_markup
        ]
    return markup