import random
import pymongo

from settings import DBuser, DBpass, DBurl
from datetime import datetime

client = pymongo.MongoClient(f"mongodb+srv://{DBuser}:{DBpass}@{DBurl}")
db = client['ohsea']
registered = db['registered_users']
verification = db['pending_verifications']
edu_emails = db['edu_emails']


async def addVerification(user: dict):
    # generate random auth codes
    auth_code = None
    while True:
        auth_code = random.randint(100000, 999999)

        # break out if auth code isn't taken
        if not await authCodeTaken(auth_code):
            break

    # set auth code
    user['auth_code'] = auth_code
    # set timestamp
    user['created'] = datetime.now()
    # add to database
    verification.insert_one(user)


async def emailTaken(email: str):
    # search databases for that email
    search1 = verification.find_one({"email": email})
    search2 = registered.find_one({"email": email})
    # return bool if it was found or not
    return search1 is not None or search2 is not None


async def authCodeTaken(auth_code: int):
    # search database for that auth token
    search = verification.find_one({"auth_code": auth_code})
    # return bool if it was found or not
    return search is not None


async def idTaken(id: int):
    # search database for that id
    search = registered.find_one({"_id": id})
    # return bool if it was found or not
    return search is not None


async def verify(id, auth_code):
    # search database for that user from auth token
    user = verification.find_one({"auth_code": auth_code})
    # remove from verification database
    verification.delete_one(user)
    # remove auth code field
    user.pop('auth_code')
    # update timestamp
    user['created'] = datetime.now()
    # update _id to discord id
    user['_id'] = id
    # add to registered database
    registered.insert_one(user)


async def isEDUEmail(email: str, address=False):
    # split address from email if not an address
    if not address:
        email = email.split('@')[1]
    # search the database for that email address
    search = edu_emails.find_one({'address': email})
    return search is not None


async def addEDUEmail(address: str):
    edu_emails.insert_one({'address': address})