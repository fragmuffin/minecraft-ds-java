import os
import re
import urllib.parse
import http.client
import json

from .core import Notifier, register, LogMessage


@register
class Slack(Notifier):
    def __init__(self, host, path):
        self.host = host
        self.path = path
    
    @classmethod
    def from_environ(cls):
        if all((
            (webhook_url := os.environ.get('SLACK_WEBHOOK_URL',  None)),
        )):
            url = urllib.parse.urlsplit(webhook_url)
            if url.scheme != 'https':
                raise ValueError("slack webohok must be https")
            return cls(host=f'{url.netloc}:443', path=url.path)

    def process(self, msg:LogMessage):
        # TODO: add server errors & stuff? (currently only loggs people joining)
        (key, _) = msg.type
        if any((
            key == 'player:join',
            key == 'player:advancement',
            key.startswith('player:death'),
        )):
            return self.send(message=msg.message)

    def send(self, message):
        conn = http.client.HTTPSConnection(self.host)
        conn.request(
            'POST',
            self.path,
            json.dumps({'text': message}),
            {'Content-type': 'application/json'}
        )
        conn.getresponse()
        return True  # TODO: handle error-cases

