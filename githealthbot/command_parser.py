import functools

class CommandParser(object):
    def __init__(self):
        self._commands = {}

    def register_command(self, name, handler):
        if name in self._commands:
            return False
        self._commands[name] = handler
        return True

    def run_command(self, event, person):
        text = event['text']
        firstSpace = text.find(' ')
        if firstSpace == -1:
            if text in self._commands:
                return self._commands[text](event, person, '')
            return False
        else:
            command = text[:firstSpace]
            arguments = text[firstSpace+1:]
            if command not in self._commands:
                return False
            return self._commands[command](event, person, arguments)
