from calendar import c
from distutils.command.install_egg_info import to_filename
from enum import unique
from unittest.util import _MAX_LENGTH
from tortoise.models import Model
from tortoise import fields
from tortoise.contrib.postgres.fields import ArrayField

class User(Model):
    id = fields.BigIntField(pk=True)
    first_name = fields.CharField(max_length=80, default = "None", unique= False)
    last_name = fields.CharField(max_length=80, default = "None", unique= False)
    email = fields.CharField(max_length=80, default = "None", unique= False)
    phone_number = fields.CharField(max_length=80, default = "None", unique= False)
    photo_dir = fields.TextField( null = True)
    seller_payment_grade = fields.IntField(default = 0)
    seller_availability_grade = fields.IntField(default = 0)
    seller_cleaning_grade = fields.IntField(default = 0)
    sellerre_liability_grade = fields.IntField(default = 0)
    buyer_payment_grade = fields.IntField(default = 0)
    buyer_availability_grade = fields.IntField(default = 0)
    buyer_cleaning_grade = fields.IntField(default = 0)
    buyer_reliability_grade = fields.IntField(default = 0)
    posts_as_owner: fields.ReverseRelation["Post"]
    posts_as_renter: fields.ReverseRelation["CarOrder"]
    lest_messages: fields.ReverseRelation["UserMessages"]
    request_as_sender: fields.ReverseRelation["PostRequest"]
    request_as_reciever: fields.ReverseRelation["PostRequest"]
    flow = fields.TextField(null=True)
    is_admin = fields.BooleanField(default=False)
    registration_step = fields.BooleanField(default=False)
    
class UserMessages(Model):
    id = fields.IntField(pk=True)
    user: fields.ForeignKeyRelation["User"] = fields.ForeignKeyField(
        "models.User", related_name="lest_messages" , to_field = "id"
    )
    
class Post(Model):
    id = fields.BigIntField(pk=True)
    #car_company = fields.CharField(max_length=50, null=True)
    car_company = fields.TextField(null=True)
    car_type = fields.CharField(max_length=50, null=True)
    car_name = fields.CharField(max_length=50, null=True)
    car_model = fields.CharField(max_length=50, null=True)
    car_type = fields.CharField(max_length=50, null=True)
    car_production_year = fields.CharField(max_length=20, null=True)
    Engine_capacity = fields.CharField(max_length=20, null=True)
    horsepower = fields.CharField(max_length=20, null=True)
    photo_path = fields.TextField( null = True)
    from_date= fields.DatetimeField(auto_now_add=True) 
    to_date= fields.DatetimeField(auto_now_add=True) 
    txt_content= fields.CharField(max_length=200, null = True, unique= False)
    km = fields.IntField(default = 0)
    area = fields.CharField(max_length=20, null = True, unique= False)
    address = fields.CharField(max_length=40, null = True, unique= False)
    phone_number = fields.IntField(null = True, unique= False)
    date_and_time = fields.DatetimeField(auto_now_add=True)
    owner: fields.ForeignKeyRelation["User"] = fields.ForeignKeyField(
        "models.User", related_name="posts_as_owner" , to_field = "id"
    )
    order: fields.ReverseRelation["CarOrder"]
    cost = fields.IntField(null=True)
    is_order = fields.BooleanField(default=False)
    post_requests : fields.ReverseRelation["PostRequest"]
    data_is_full = fields.BooleanField(default=False,description="say if the user finish registration of the post")
    
class CarOrder(Model):
    post_id = fields.BigIntField(pk=True)# taks the id of the post
    renter: fields.ForeignKeyRelation["User"] = fields.ForeignKeyField(
        "models.User", related_name="posts_as_renter" , to_field = "id"
    )
    
class PostRequest(Model):
    request_id = fields.BigIntField(pk=True)
    #post_id = fields.BigIntField(null=False)# taks the id of the post
    request_sender: fields.ForeignKeyRelation["User"] = fields.ForeignKeyField(
        "models.User", related_name="request_as_sender" , to_field = "id"
    )
    request_reciever: fields.ForeignKeyRelation["User"] = fields.ForeignKeyField(
        "models.User", related_name="request_as_reciever" , to_field = "id"
    )
    post: fields.ForeignKeyRelation["Post"] = fields.ForeignKeyField(
        "models.Post", related_name="post_requests" , to_field = "id"
    )
    amswer = fields.CharField(max_length=15, null=True , default=None)
    request_text = fields.CharField(max_length=80, null=True)
    step_grade = fields.CharField(max_length=10, null=True , default=None)
    date= fields.DatetimeField(auto_now_add=True) 