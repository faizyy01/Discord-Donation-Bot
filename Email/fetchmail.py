from datetime import datetime, timedelta
import imaplib, email
import re
import Email.db as db
from smtplib import SMTP_SSL, SMTP_SSL_PORT
import json 
import os 
import Cogs.Json.jshelper as jshelper


def fetchmail():
    try:
        data = jshelper.openf("/settings.json")
        user = data["user"]
        password = data["password"]
        imap_url = data["imap_url"]
        #note = data["note"]
        mail = imaplib.IMAP4_SSL(imap_url)
        mail.login(user, password)
        mail.select('cash')
        type, data = mail.search(None, 'UNSEEN')
        mail_ids = data[0]
        id_list = mail_ids.split()
        for num in data[0].split():
            typ, data = mail.fetch(num, '(RFC822)')
            raw_email = data[0][1]
            raw_email_string = raw_email.decode('utf-8')
            email_message = email.message_from_string(raw_email_string)
            subject = str(email_message).split("Subject: ", 1)[1].split("\nTo:", 1)[0]
            mmm = str(email_message)
            if "cash@square.com" in mmm:
                try:
                    cash = re.search(r"\$([0-9]{1,3},([0-9]{3},)*[0-9]{3}|[0-9]+)(\.[0-9][0-9])?", subject).group(0)
                except AttributeError:
                    continue
                try:
                    code = re.search(r"1a001.\d\d\d\d", subject).group(0)
                except AttributeError:
                    continue
            else:
                try:
                    cash = re.search(r"\$([0-9]{1,3},([0-9]{3},)*[0-9]{3}|[0-9]+)(\.[0-9][0-9])?", subject).group(0)
                except AttributeError:
                    continue
                try:
                    code = re.search(r"1a001.\d\d\d\d", mmm).group(0)
                except AttributeError:
                    continue
            cash = cash.lstrip('$')
            code = code.replace('1a001-', '')
            db.save_user(str(code), str(cash))
        mail.close()
        mail.logout()
    except Exception as e:
        print(e)
