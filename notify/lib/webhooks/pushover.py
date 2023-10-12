import os
import re
import http.client
import urllib.parse

from .core import Notifier, register, LogMessage


@register
class Pushover(Notifier):
    API_URL = 'api.pushover.net:443'

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
        (key, match) = msg.type
        if key == 'player:join':
            return self.send(
                title=match.group('player'),
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
