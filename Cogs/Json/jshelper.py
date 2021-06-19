import json 
import os
from datetime import datetime, timedelta

def openf(self, name):
    path = os.getcwd() + f"{name}"
    with open(path, "r") as f:
        data = json.load(f)
    return data

def savef(self, name, data):
    path = os.getcwd() + f"{name}"
    with open(path, "w") as f:
        json.dump(data, f, indent=4, default=str)

def save_user(self, id, creds):
    data = self.openf("/Cogs/Json/cdb.json")
    data["members"][str(id)] = {
        "open": 0,
        "date": datetime.now(),
        "id": id,
    }
    self.savef("/Cogs/Json/cdb.json", data)

def makeopen(self, id):
    data = self.openf("/Cogs/Json/cdb.json")
    check = 0
    for member in data["members"]:
        if data["members"][member]["id"] == id:
            check = 1
            data["members"][member]["open"] = 1
            self.savef("/Cogs/Json/cdb.json", data)

def makeclose(self, id):
    data = self.openf("/Cogs/Json/cdb.json")
    check = 0
    for member in data["members"]:
        if data["members"][member]["id"] == id:
            check = 1
            data["members"][member]["open"] = 0
            self.savef("/Cogs/Json/cdb.json", data)

def checkopen(self, id):
    check = 0
    data = self.openf("/Cogs/Json/cdb.json")
    for member in data["members"]:
        if data["members"][member]["id"] == id:
            if data["members"][member]["open"] == 1:
                check = 1

    if check == 1:
        return True
    else:
        return False

def userexsist(self, id):
    data = self.openf("/Cogs/Json/cdb.json")
    check = 0
    for member in data["members"]:
        if data["members"][member]["id"] == id:
            check = 1

    if check != 1:
        self.save_user(id, 0)