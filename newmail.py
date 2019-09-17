#!/usr/bin/python3

import json
import mailbox
import os
import requests
import signal
import sys
import time

from datetime import datetime, timedelta

DEBUG = True
LOG_FILENAME = "debug.log"
MBOX = "/var/spool/mail/{}".format(os.getlogin())

PUSH_URL = "https://push.ubports.com/notify"
HEADERS = {"Content-Type" : "application/json"}

card = {
    "icon" : "notification",
    "body" : "",
    "summary" : "New mail",
    "popup" : True,
    "persist" : True
}

notification = {
    "card" : card,
    "vibrate" : True,
    "sound"   : True
    }

data = {
    "notification" : notification,
    }

params = {
    "appid" : "pushclient.christianpauly_pushclient",
    "token" : "YOUR_TOKEN",
    "expire_on" : "",
    "data" : data
}


client = None
logfile = None

def log(log_msg):
    if DEBUG:
        logfile.write(f'{str(log_msg)}\n')
        logfile.flush()
def signal_handler(sig, frame):
    log('Exiting with signal {sig}')
    if client and client.isLoggedIn():
        client.logout()
    if logfile:
        logfile.close()
    sys.exit(0)


def send_message(msg):
    dt = datetime.now() + timedelta(days=1)
    dt_str = dt.strftime("%Y-%m-%dT%H:%M:00.000Z")
    params["expire_on"] = dt_str
    params["data"]["notification"]["card"]["body"] = msg
    json_data = json.dumps(params)
    log(f'Data sent:\n {json_data}\n')
    r = requests.post(url=PUSH_URL, headers=HEADERS, data=json_data)
    log(r.json())

##################### MAIN #####################
if __name__ == "__main__":

    if DEBUG:
        print(f'Logging in: {LOG_FILENAME}')
        logfile = open(LOG_FILENAME, "a")

    signal.signal(signal.SIGINT, signal_handler)

    seenmsgs = []
    while True:
        m = mailbox.mbox(MBOX)
        newmsgs = []
        for number, msg in m.iteritems():
            flags = msg.get_flags()
            msgid = msg.get("message-id")
            if msgid in seenmsgs:
                continue
            author = msg.get("from")
            subject = msg.get("subject")
            seenmsgs.append(msgid)
            if not "R" in flags:
                print("adding one")
                newmsgs.append("from {0} about {1}".format(author, subject))
        if len(newmsgs) != 0:
            body = "New messages:\n" + str(newmsgs)
            print("Sending: {0}".format(body))
            send_message(body)
        time.sleep(15)
