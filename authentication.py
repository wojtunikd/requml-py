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
    expiryDate = (datetime.datetime.now() + datetime.timedelta(hours=3)).strftime("%Y-%m-%d %H:%M:%S")
    return jwt.encode({"expiry": expiryDate}, str(os.getenv("JWT_SECRET")), algorithm="HS256")


def decodeAndVerifyJWT(token):
    try:
        decodedToken = jwt.decode(token, os.getenv("JWT_SECRET"), algorithms=["HS256"])
    except Exception as error:
        print(error)
        raise Exception("Error while decoding the JSON web token")

    print(decodedToken)

    expiryDateTime = datetime.datetime.strptime(decodedToken["expiry"], "%Y-%m-%d %H:%M:%S")
    now = datetime.datetime.now()

    if expiryDateTime > now:
        return True
    else:
        raise Exception("The token provided is expired. Please log in again.")
