from pymongo import MongoClient
import os
import datetime
from bson import ObjectId

# Kết nối MongoDB
client = MongoClient(
    host=os.getenv('MONGO_HOST', 'mongo-comment-db'),
    port=int(os.getenv('MONGO_PORT', 27017)),
    username=os.getenv('MONGO_USER', 'root'),
    password=os.getenv('MONGO_PASSWORD', 'password'),
    authSource='admin'
)
db = client[os.getenv('MONGO_DB', 'comment_db')]
comments_collection = db['comments']

class Comment:
    def __init__(self, user_id, order_item_id, content, created_at=None, id=None):
        self.id = id
        self.user_id = user_id
        self.order_item_id = order_item_id
        self.content = content
        self.created_at = created_at or datetime.datetime.utcnow()

    @classmethod
    def create(cls, user_id, order_item_id, content):
        result = comments_collection.insert_one({
            'user_id': user_id,
            'order_item_id': order_item_id,
            'content': content,
            'created_at': datetime.datetime.utcnow()
        })
        return cls(user_id, order_item_id, content, datetime.datetime.utcnow(), str(result.inserted_id))

    @classmethod
    def all(cls):
        return [cls(**{**doc, 'id': str(doc['_id'])}) for doc in comments_collection.find()]

    @classmethod
    def filter(cls, **kwargs):
        return [cls(**{**doc, 'id': str(doc['_id'])}) for doc in comments_collection.find(kwargs)]

    @classmethod
    def get(cls, id):
        try:
            doc = comments_collection.find_one({'_id': ObjectId(id)})
            if doc:
                return cls(**{**doc, 'id': str(doc['_id'])})
            return None
        except:
            return None

    def save(self):
        comments_collection.update_one(
            {'_id': ObjectId(self.id)},
            {'$set': {'content': self.content}},
            upsert=False
        )

    def delete(self):
        comments_collection.delete_one({'_id': ObjectId(self.id)})