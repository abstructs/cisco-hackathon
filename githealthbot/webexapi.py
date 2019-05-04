import datetime
from dateutil import parser
from githealthbot.message import Message
from githealthbot.logger import Logger
from githealthbot.command_parser import CommandParser
from githealthbot import botconfig, learning_model
import re
import requests

class WebexAPI:

    def _health_method(self, event, person, args):
        try:
            roomId = event['roomId']
            user, repo = args.strip().split()
            result = learning_model.health(user, repo)
            msg = ''
            if result == False:
                msg = 'No repository was found'
            else:
                msg = 'The git HealthScore of the repository {} by {} scored {}%'.format(repo, user, abs(result))
            self.Message.send(roomId, msg)
        except Exception as ex:
            self.Message.send(roomId, 'An error occured, please try again later')
        return True

    def _dump_method(self, event, person, args):
        roomId = event['roomId']
        user, repo = args.strip().split()
        result = learning_model.dump(user, repo)
        self.Message.send(roomId, str(result))
        return True

    def _help_method(self, event, person, args):
        message = """
GitHealth Help:
    health <username> <reponame> - Gets the HealthScore of the specified repository
    dump <username> <reponame>   - Dumps information about the specified repository
    help                         - Displays this prompt
"""
        self.Message.send(event['roomId'], message)
        return True

    def __init__(self):
        self.cmd_parser = CommandParser()
        self.cmd_parser.register_command('help', self._help_method)
        # self.cmd_parser.register_command('teams', self._team_health_method)
        self.cmd_parser.register_command('health', self._health_method)
        self.cmd_parser.register_command('dump', self._dump_method)

        self.api = "https://api.ciscospark.com/v1/"
        self.bearer_token = botconfig.ACCESS_TOKEN
        self.bot_id = botconfig.BOT_ID
        self.bot_person = botconfig.MY_ID
        self.Message = Message(self)

    def build_header(self):
        return {'Authorization': self.bearer_token}

    def get_person(self, personId):
        url = '{}people/{}'.format(self.api, personId)
        result = requests.get(url, headers=self.build_header())
        return result.json()

    def parse_event(self, event):
        REGEX_PATTERN = '(.*)<spark-mention.*>.*<\/spark-mention>(.*)'
        messageId = event['id']
        personId = event['personId']
        if personId == self.bot_person:
            return
        message = self.Message.get(messageId)
        roomType = message['roomType']
        if roomType != 'direct':
            html = message['html']
            if html.startswith('<p>'):
                html = html[3:]
            if html.endswith('</p>'):
                html = html[:-4]
            message['text'] = ''.join(re.match(REGEX_PATTERN, html).groups()).strip()
        person = self.get_person(message['personId'])

        if not self.cmd_parser.run_command(message, person):
            self.Message.send(message['roomId'], '"{}" is an unrecognized command'.format(message['text']))

    def update(self):
        self.Room.get()
        for room in self.Room.rooms:
            if self.Message.get(room):
                Logger.log("ROOM", room['title'])
                for message in self.Message.messages:
                    Logger.log("MESSAGE", message['text'])
                    self.Message.send(room, "I kind of work!")
        self.last_update = datetime.datetime.utcnow()
