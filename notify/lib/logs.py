# Handle minecraft logs
# (only tested for PaperMC v1.20)

import time
import re
import os
import datetime


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

    # Note: I'm going to ignore lines that don't start with [<timestamp>] for now

    REGEX_LINE = re.compile(r'''
        ^\[(?P<time_str>\d{2}:\d{2}:\d{2})\]\s* # time
        \[(?P<owner>.*?)\]:\s*                  # owner
        (?P<message>.*?)\s*$                    # message
    ''', re.VERBOSE)

    def __init__(self, date:datetime.date, time_str, owner, message):
        self.date = date
        self.time = datetime.time.fromisoformat(time_str)
        self.owner = owner
        self.message = message
    
    @classmethod
    def from_string(cls, date:datetime.date, line):
        if (match := cls.REGEX_LINE.search(line)):
            return cls(date=date, **match.groupdict())

    @property
    def datetime(self):
        return datetime.datetime.combine(self.date, self.time)

    def __str__(self):
        return f"[{self.datetime.isoformat()}] [{self.owner}] {self.message}"


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


RETRY_PERIOD = 0.05  # (unit: sec)

def log_iter(filename, verbose=False):
    event_iter = inotify_event_gen(filename)  # 'IN_DELETE'

    def file_gen():
        first = True
        while True:
            # wait for file to exist
            while not os.path.exists(filename):
                first = False  # if it doesn't initially exist, we'll want to see all content once it does
                time.sleep(RETRY_PERIOD)

            # Seek to end of file (first file only)
            ctime = os.path.getctime(filename)
            offset = os.path.getsize(filename) if first else 0
            first = False

            with open(filename, 'r') as handle:
                if verbose:
                    print(f'logfile opened: {filename!r}')
                if offset:
                    handle.seek(offset)
                yield (datetime.date.fromtimestamp(ctime), handle)

    def line_gen():
        for (date, logfile) in file_gen():
            file_exists = True
            while file_exists:
                if not (line := logfile.readline()):
                    while (event := next(event_iter)):
                        (_, e_types, _, _) = event
                        if 'IN_DELETE' in e_types:
                            file_exists = False
                            break
                    time.sleep(RETRY_PERIOD)
                    continue
                yield (date, line.rstrip())
    
    for (date, line) in line_gen():
        yield LogMessage.from_string(date, line)
