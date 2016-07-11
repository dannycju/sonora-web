from mongoengine import *
from bson.objectid import ObjectId

class Profile(DynamicDocument):
    name = StringField(required=True)
    email = EmailField(unique=True, required=True)
    password = StringField(required=True)
    description = StringField(default="")
    topics = DynamicField(default=[])
    date_created = DateTimeField(default=timezone.now())
    date_updated = DateTimeField(default=timezone.now())
    is_deleted = BooleanField(default=False)
    meta = {"collection": "profiles"}
