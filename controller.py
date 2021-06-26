from pymongo import MongoClient
from bson.objectid import ObjectId
import os

cluster = MongoClient(os.getenv("MONGODB_CONNECTION"))
db = cluster["ReqUML"]
requests = db["requests"]


def getOrder(orderId):
    return requests.find_one({"_id": ObjectId(orderId)})
