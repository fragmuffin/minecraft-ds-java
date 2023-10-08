import os
import re
import http.client
import urllib.parse

from .core import Notifier, register, LogMessage


@register
class Pushover(Notifier):
    API_URL = 'api.pushover.net:443'
    REGEX_JOINED = re.compile(r'^(?P<user>\S+) joined the game$')

    def __init__(self, user_key, app_token):
        self.user_key = user_key
        self.app_token = app_token

    @classmethod
    def from_environ(cls):
        if all((
            (user_key  := os.environ.get('PUSHOVER_USER_KEY',  None)),
            (app_token := os.environ.get('PUSHOVER_APP_TOKEN', None)),
        )):
            return cls(user_key=user_key, app_token=app_token)
    
    def process(self, msg:LogMessage):
        # TODO: add server errors & stuff? (currently only loggs people joining)
        if (match := self.REGEX_JOINED.search(msg.message)):
            return self.send(
                title=match.group('user'),
                message=msg.message,
            )
    
    def send(self, title, message):
        conn = http.client.HTTPSConnection(self.API_URL)
        content = {
            'token': self.app_token,
            'user': self.user_key,
            'title': title,
            'message': message,
        }
        conn.request(
            'POST',
            '/1/messages.json',
            urllib.parse.urlencode(content),
            {'Content-type': 'application/x-www-form-urlencoded'}
        )
        conn.getresponse()
        return True  # TODO: handle error-cases
