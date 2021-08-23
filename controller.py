import json
import os
import random
import string

from bson.objectid import ObjectId
from bson.errors import InvalidId

from pymongo import MongoClient


def connectMongoAndGetCollection():
    cluster = MongoClient(os.getenv("MONGODB_CONNECTION"))
    db = cluster["ReqUML"]
    return db["requests"]


requests = connectMongoAndGetCollection()


def getNewParameter():
    # Inspired by https://pynative.com/python-generate-random-string/
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for i in range(12))


def getAndVerifyUniqueUCParameter():
    param = getNewParameter()
    duplicate = requests.find_one({"ucParam": param})

    if duplicate is not None:
        unique = False

        while not unique:
            param = getNewParameter()
            duplicate = requests.find_one({"ucParam": param})
            if duplicate is None:
                unique = True

    return param


def getAndVerifyUniqueClassParameter():
    param = getNewParameter()
    duplicate = requests.find_one({"ucParam": param})

    if duplicate is not None:
        unique = False

        while not unique:
            param = getNewParameter()
            duplicate = requests.find_one({"ucParam": param})
            if duplicate is None:
                unique = True

    return param


def getOrder(orderId):
    try:
        return requests.find_one({"_id": ObjectId(orderId)})
    except InvalidId:
        return None


def updateActorUseCases(orderId, useCases):
    ucParam = getAndVerifyUniqueUCParameter()
    requests.update_one({"_id": ObjectId(orderId)}, {"$set": {"actorsWithUseCases": json.dumps(useCases), "ucParam": ucParam}})
    return {"useCasesParam": ucParam}


def updateClasses(orderId, classes):
    classParam = getAndVerifyUniqueClassParameter()
    requests.update_one({"_id": ObjectId(orderId)}, {"$set": {"classes": json.dumps(classes), "classParam": classParam}})
    return {"classParam": classParam}


def markOrderComplete(orderId):
    requests.update_one({"_id": ObjectId(orderId)}, {"$set": {"completed": True}})
    return


def getOrderUseCases(orderId):
    order = requests.find_one({"_id": ObjectId(orderId)})
    orderUseCases = None

    try:
        orderUseCases = order["actorsWithUseCases"]
    except KeyError:
        print("No order use cases yet.")

    return list(orderUseCases)


def getAllOrders():
    orders = requests.find()
    return list(orders)


def deleteAnOrder(orderId):
    try:
        return requests.delete_one({"_id": ObjectId(orderId)})
    except InvalidId:
        return None


def deleteAllOrders():
    return requests.delete_many({})
