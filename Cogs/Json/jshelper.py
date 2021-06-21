import json 
import os
from datetime import datetime, timedelta

def openf(name):
    path = os.getcwd() + f"{name}"
    with open(path, "r") as f:
        data = json.load(f)
    return data

def savef(name, data):
    path = os.getcwd() + f"{name}"
    with open(path, "w") as f:
        json.dump(data, f, indent=4, default=str)

def save_user(id, creds):
    data = openf("/Cogs/Json/cdb.json")
    data["members"][str(id)] = {
        "open": 0,
        "date": datetime.now(),
        "id": id,
    }
    savef("/Cogs/Json/cdb.json", data)

def makeopen(id):
    data = openf("/Cogs/Json/cdb.json")
    check = 0
    for member in data["members"]:
        if data["members"][member]["id"] == id:
            check = 1
            data["members"][member]["open"] = 1
            savef("/Cogs/Json/cdb.json", data)

def makeclose(id):
    data = openf("/Cogs/Json/cdb.json")
    check = 0
    for member in data["members"]:
        if data["members"][member]["id"] == id:
            check = 1
            data["members"][member]["open"] = 0
            savef("/Cogs/Json/cdb.json", data)

def checkopen(id):
    check = 0
    data = openf("/Cogs/Json/cdb.json")
    for member in data["members"]:
        if data["members"][member]["id"] == id:
            if data["members"][member]["open"] == 1:
                check = 1

    if check == 1:
        return True
    else:
        return False

def userexsist(id):
    data = openf("/Cogs/Json/cdb.json")
    check = 0
    for member in data["members"]:
        if data["members"][member]["id"] == id:
            check = 1

    if check != 1:
        save_user(id, 0)

def prestart():
    try:
        token = str(os.environ['token'])
        user = str(os.environ['user'])
        password = str(os.environ['pass'])
        imap_url = str(os.environ['imap_url'])
        data = openf("/config/config.json")
        data["token"] = token
        data["user"] = user
        data["password"] = password
        data["imap_url"] = imap_url
        savef("/config/config.json", data)
        return True
    except Exception as e:
        print(e)
        return False