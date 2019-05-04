import requests
import json
from dateutil import parser

class Message:
    
    def __init__(self, webex):
        self.webex = webex
        self.api = webex.api + "messages"

    def get(self, messageId):
        # params = {"roomId": room['id']}
        # if room['type'] == "group":
        #    params['mentionedPeople'] = "me"
        message = requests.get(self.api + "/" + messageId, headers=self.webex.build_header())
        return message.json()

    def send(self, room, text):
        data = {"roomId": room, "text": text}
        requests.post(self.api, data=data, headers=self.webex.build_header())
