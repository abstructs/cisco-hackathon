import requests
import json

class Room:
    
    def __init__(self, webex):
        self.webex = webex
        self.api = webex.api + "rooms"
        self.rooms = {}
    
    def get(self):
        self.rooms = requests.get(self.api, headers=self.webex.build_header())
        self.rooms = json.dumps(self.rooms.json())
        self.rooms = json.loads(self.rooms)['items']