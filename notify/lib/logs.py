# Handle minecraft logs
# (only tested for PaperMC v1.20)

import time
import re
import os
import datetime


def inotify_event_gen(filename):
    import os.path
    filename = os.path.normpath(filename)
    (path, fname) = os.path.split(filename if os.path.isabs(filename) else f'./{filename}')

    from inotify.adapters import Inotify
    notifier = Inotify(block_duration_s=0)
    notifier.add_watch(path)

    for event in notifier.event_gen(timeout_s=None, yield_nones=True):
        if event is None:
            yield None
            continue
        (_, _, e_path, e_filename) = event
        if (e_path, e_filename) == (path, fname):
            yield event


class LogMessage:
    # Message Examples:
    # [06:25:20] [Server thread/INFO]: Preparing start region for dimension minecraft:the_end
    # [06:25:20] [Server thread/INFO]: Time elapsed: 33 ms
    # [06:25:20] [Server thread/INFO]: [CoreProtect] Enabling CoreProtect v22.1
    # [06:25:22] [Server thread/INFO]: [CoreProtect] CoreProtect has been successfully enabled! 
    # [06:25:22] [Server thread/INFO]: [CoreProtect] Using SQLite for data storage.
    # [06:25:22] [Server thread/INFO]: --------------------
    # [06:25:23] [Craft Scheduler Thread - 3 - Essentials/INFO]: [Essentials] Fetching version information...
    # [06:25:23] [Server thread/INFO]: Done (3.904s)! For help, type "help"
    # [12:15:23] [Server thread/INFO]: FraggyMuffin joined the game
    # [12:15:23] [Server thread/INFO]: FraggyMuffin[/172.25.0.1:39356] logged in with entity id 27 at ([world]9.5, 80.0, -2.5)
    # [12:17:11] [Server thread/INFO]: FraggyMuffin lost connection: Disconnected
    # [12:17:11] [Server thread/INFO]: FraggyMuffin left the game
    # [12:15:08] [Server thread/WARN]: [!] The timings profiler has been enabled but has been scheduled for removal from Paper in the future.
    #     We recommend installing the spark profiler as a replacement: https://spark.lucko.me/
    #     For more information please visit: https://github.com/PaperMC/Paper/issues/8948
    # [12:17:11] [Server thread/INFO]: FraggyMuffin has made the advancement [Monster Hunter]
    # [02:13:12] [Server thread/INFO]: SomeDude fell from a high place
    # [02:23:19] [Server thread/INFO]: SomeDude tried to swim in lava

    # Note: I'm going to ignore lines that don't start with [<timestamp>] for now

    REGEX_LINE = re.compile(r'''^\s*
        \[(?P<time_str>\d{2}:\d{2}:\d{2})\]\s*  # time (no date)
        \[(?P<owner>.*?)\]:\s*                  # owner
        (?P<message>.*?)\s*                     # message
    $''', re.VERBOSE)
    RETRY_PERIOD = 0.05  # (unit: sec)

    def __init__(self, date:datetime.date, time_str, owner, message):
        self.date = date
        self.time = datetime.time.fromisoformat(time_str)
        self.owner = owner
        self.message = message

        self._type = None
    
    @classmethod
    def from_string(cls, line, date:datetime.date=datetime.date.today()):
        if (match := cls.REGEX_LINE.search(line)):
            return cls(date=date, **match.groupdict())

    @property
    def datetime(self):
        return datetime.datetime.combine(self.date, self.time)

    def __str__(self):
        return f"[{self.datetime.isoformat()}] [{self.owner}] {self.message}"

    @classmethod
    def from_file_gen(cls, filename, verbose=False):
        event_iter = inotify_event_gen(filename)  # 'IN_DELETE'
        date = None  # will be set per file from file_gen()

        def file_gen():
            first = True
            while True:
                # wait for file to exist
                while not os.path.exists(filename):
                    first = False  # if it doesn't initially exist, we'll want to see all content once it does
                    time.sleep(cls.RETRY_PERIOD)

                # Set date - to set timestamp for all log entries
                nonlocal date
                date = datetime.date.fromtimestamp(os.path.getctime(filename))

                # Seek to end of file (first file only)
                offset = os.path.getsize(filename) if first else 0
                first = False

                with open(filename, 'r') as handle:
                    if verbose:
                        print(f'logfile opened: {filename!r}')
                    if offset:
                        handle.seek(offset)
                    yield handle

        def line_gen():
            for logfile in file_gen():
                file_exists = True
                while file_exists:
                    if not (line := logfile.readline()):
                        while (event := next(event_iter)):
                            (_, e_types, _, _) = event
                            if 'IN_DELETE' in e_types:
                                file_exists = False
                                break
                        time.sleep(cls.RETRY_PERIOD)
                        continue
                    yield line.rstrip()
        
        for line in line_gen():
            if (logentry := cls.from_string(line=line, date=date)):
                yield logentry

    IDENTITY_MAP = {  # fmt: {<key>: <regex>, ...}
        # Joining / Leaving
        'joined': re.compile(r'^\s*(?P<name>[\w ]+?) joined the game\s*$'),
        'logged_in': re.compile(r'''^\s*
            (?P<name>[\w ]+?)\[.*?\]\s*     # Username (TODO: from IP)
            logged in with entity id (?P<id>\d+) at\s*  # entity ID
            \(\[(?P<world>\w+)\]\s*         # World name
                (?P<x>\d+(\.\d+)?)\s*,\s*   # coord: x
                (?P<y>\d+(\.\d+)?)\s*,\s*   # coord: y
                (?P<z>\d+(\.\d+)?)\s*,?\s*  # coord: z
            \)
        \s*$''', re.VERBOSE),
        'disconnected': re.compile(r'^\s*(?P<name>[\w ]+?) lost connection: (?P<reason>.*?)\s*$'),
        'left': re.compile(r'^\s*(?P<name>[\w ]+?) left the game\s*$'),

        # Events
        'advancement': re.compile(r'^\s*(?P<name>[\w ]+?)\s*has made the advancement \[(?P<type>.*)\]\s*$'),

        # Deaths : https://minecraft.fandom.com/wiki/Death_messages
        'drowned': re.compile(r'^\s*(?P<name>[\w ]+?)\s*drowned\s*$'),
        'slain': re.compile(r'^\s*(?P<name>[\w ]+?)\s*was slain by\s*(?P<other>.*?)(\s+using (?P<weapon>.*?))?\s*$'),,
        'lava': re.compile(r'^\s*(?P<name>[\w ]+?)\s*tried to swim in lava\s*$'),
        'fell': re.compile(r'^\s*(?P<name>[\w ]+?)\s*fell from a high place\s*$'),
        'stung': re.compile(r'^\s*(?P<name>[\w ]+?)\s*was stung to death(by\s*(?P<other>.*?)(\s+using (?P<weapon>.*?))?)?\s*$'),
        'shriek': re.compile(r'^\s*(?P<name>[\w ]+?)\s*was obliterated.*$'),
        'shot': re.compile(r'^\s*(?P<name>[\w ]+?)\s*was shot by\s*(?P<other>.*?)(\s+using (?P<weapon>.*?))?\s*$'),
        
        '_template': re.compile(r'^\s*(?P<name>[\w ]+?)\s*\s*$'),  # template

        # there are a lot... perhaps rethink this method

    }

    @property
    def type(self):
        """Identify a log message as a particular type"""
        if self._type is None:
            for (tag, regex) in self.IDENTITY_MAP.items():
                if (match := regex.search(self.message)):
                    self._type = tag
                    break
                    # note: match not used; so (?P<names>) are lost, useful?
            else:
                self._type = 'UNKNOWN'
        return self._type


if __name__ == '__main__':
    import unittest
    
    class TestLogMessages(unittest.TestCase):
        def assertLogType(self, text, exp_type):
            today = datetime.date.today()
            obj = LogMessage.from_string(text, date=today)
            self.assertEqual(obj.type, exp_type)
        
        def test_joined(self):
            self.assertLogType(
                "[12:15:23] [Server thread/INFO]: FraggyMuffin joined the game",                
                'joined'
            )
    
        def test_logged_in(self):
            self.assertLogType(
                "[12:15:23] [Server thread/INFO]: FraggyMuffin[/172.25.0.1:39356] logged in with entity id 27 at ([world]9.5, 80.0, -2.5)",
                'logged_in'
            )
        def test_disconnected(self):
            self.assertLogType(
                "[12:17:11] [Server thread/INFO]: FraggyMuffin lost connection: Disconnected",
                'disconnected'
            )
        
        def test_left(self):
            self.assertLogType(
                "[12:17:11] [Server thread/INFO]: FraggyMuffin left the game",
                'left'
            )
        
        def test_advancement(self):
            self.assertLogType(
                "[12:17:11] [Server thread/INFO]: FraggyMuffin has made the advancement [Monster Hunter]",
                'advancement'
            )
        
        def test_drowned(self):
            self.assertLogType(
                "[02:13:12] [Server thread/INFO]: Dude drowned",
                'drowned'
            )
        
        def test_slain(self):
            self.assertLogType(
                "[02:13:12] [Server thread/INFO]: Dude was slain by AnotherDude",
                'slain'
            )
        
        def test_lava(self):
            self.assertLogType(
                "[02:23:19] [Server thread/INFO]: SomeDude tried to swim in lava",
                'lava'
            )
        
        def test_fell(self):
            self.assertLogType(
                "[02:13:12] [Server thread/INFO]: SomeDude fell from a high place",
                'fell'
            )
        


    unittest.main()
