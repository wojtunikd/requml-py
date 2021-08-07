import os
import bcrypt
import jwt
import datetime

from pymongo import MongoClient

cluster = MongoClient(os.getenv("MONGODB_CONNECTION"))
db = cluster["ReqUML"]
admins = db["admins"]


def getAdmin(email):
    return admins.find_one({"email": email})


def verifyPassword(adminPassword, passwordProvided):
    return bcrypt.checkpw(passwordProvided.encode("utf-8"), adminPassword.encode("utf-8"))


def generateJWT():
    return jwt.encode({"exp": datetime.datetime.utcnow() + datetime.timedelta(hours=3)}, os.getenv("JWT_SECRET"), algorithm="HS256")


def decodeJWT(token):
    return jwt.decode(token, os.getenv("JWT_SECRET"), algorithms=["HS256"])

