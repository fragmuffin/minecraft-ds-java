import re

_TEMPLATES = {
    # Lightly curated from : https://minecraft.fandom.com/wiki/Death_messages
    #   $ xclip -o | grep -P '^<player>' | xclip
    # Then will be search/replacing the following, to form regular expressions:
    #     <player>        -> (?P<player>[\w ]+)
    #     <player/mob>    -> (?P<other>[\w ]+)
    #     <item>          -> (?P<item>[\w ]+)
    #     while           -> whil(e|st)

    # --- Death Messages
    'player:death:cactus': [
        "<player> was pricked to death",
        "<player> walked into a cactus while trying to escape <player/mob>",
    ],
    'player:death:drowning': [
        "<player> drowned",
        "<player> drowned while trying to escape <player/mob>",
    ],
    'player:death:drying_out': [
        "<player> died from dehydration",
        "<player> died from dehydration while trying to escape <player/mob>",
    ],
    'player:death:explosions': [
        "<player> experienced kinetic energy",
        "<player> experienced kinetic energy while trying to escape <player/mob>",
        "<player> blew up",
        "<player> was blown up by <player/mob>",
        "<player> was blown up by <player/mob> using <item>",
        "<player> was killed by \[Intentional Game Design\]",
    ],
    'player:death:falling': [
        "<player> hit the ground too hard",
        "<player> hit the ground too hard while trying to escape <player/mob>",
        "<player> fell from a high place",
        "<player> fell off a ladder",
        "<player> fell off some vines",
        "<player> fell off some weeping vines",
        "<player> fell off some twisting vines",
        "<player> fell off scaffolding",
        "<player> fell while climbing",
        "<player> was doomed to fall",
        "<player> was doomed to fall by <player/mob>",
        "<player> was doomed to fall by <player/mob> using <item>",
        "<player> was impaled on a stalagmite",
        "<player> was impaled on a stalagmite while fighting <player/mob>",
    ],
    'player:death:falling_blocks': [
        "<player> was squashed by a falling anvil",
        "<player> was squashed by a falling block",
        "<player> was skewered by a falling stalactite",
    ],
    'player:death:fire': [
        "<player> went up in flames",
        "<player> walked into fire while fighting <player/mob>",
        "<player> burned to death",
        "<player> was burned to a crisp while fighting <player/mob>",
    ],
    'player:death:firework_rockets': [
        "<player> went off with a bang",
        "<player> went off with a bang due to a firework fired from <item> by <player/mob>",
    ],
    'player:death:lava': [
        "<player> tried to swim in lava",
        "<player> tried to swim in lava to escape <player/mob>",
    ],
    'player:death:lightning': [
        "<player> was struck by lightning",
        "<player> was struck by lightning while fighting <player/mob>",
    ],
    'player:death:magma_block': [
        "<player> discovered the floor was lava",
        "<player> walked into the danger zone due to <player/mob>",
    ],
    'player:death:magic': [
        "<player> was killed by magic",
        "<player> was killed by magic while trying to escape <player/mob>",
        "<player> was killed by <player/mob> using magic",
        "<player> was killed by <player/mob> using <item>",
    ],
    'player:death:powder_snow': [
        "<player> froze to death",
        "<player> was frozen to death by <player/mob>",
    ],
    'player:death:killed': [
        "<player> was slain by <player/mob>",
        "<player> was slain by <player/mob> using <item>",
        "<player> was stung to death",
        "<player> was stung to death by <player/mob> using <item>",
        "<player> was obliterated by a sonically-charged shriek",
        "<player> was obliterated by a sonically-charged shriek while trying to escape <player/mob> wielding <item>",
    ],
    'player:death:projectiles': [
        "<player> was shot by <player/mob>",
        "<player> was shot by <player/mob> using <item>",
        "<player> was pummeled by <player/mob>",
        "<player> was pummeled by <player/mob> using <item>",
        "<player> was fireballed by <player/mob>",
        "<player> was fireballed by <player/mob> using <item>",
        "<player> was shot by a skull from <player/mob>",
        "<player> was shot by a skull from <player/mob> using <item>",
    ],
    'player:death:starving': [
        "<player> starved to death",
        "<player> starved to death while fighting <player/mob>",
    ],
    'player:death:suffocation': [
        "<player> suffocated in a wall",
        "<player> suffocated in a wall while fighting <player/mob>",
        "<player> was squished too much",
        "<player> was squashed by <player/mob>",
        "<player> left the confines of this world",
        "<player> left the confines of this world while fighting <player/mob>",
    ],
    'player:death:sweet_berry_bushes': [
        "<player> was poked to death by a sweet berry bush",
        "<player> was poked to death by a sweet berry bush while trying to escape <player/mob>",
    ],
    'player:death:thorns': [
        "<player> was killed (while )?trying to hurt <player/mob>",
        "<player> was killed by <item> (while )?trying to hurt <player/mob>",
    ],
    'player:death:trident': [
        "<player> was impaled by <player/mob>",
        "<player> was impaled by <player/mob> with <item>",
    ],
    'player:death:void': [
        "<player> fell out of the world",
        "<player> didn't want to live in the same world as <player/mob>",
    ],
    'player:death:wither': [
        "<player> withered away",
        "<player> withered away while fighting <player/mob>",
    ],
    'player:death:generic': [
        "<player> died",
        "<player> died because of <player/mob>",
        "<player> was killed",
        "<player> didn't want to live as <player/mob>",
    ],
    'player:death:crash_prevention': [
        "<player> was killed by even more magic",
    ],

    # --- Join / Leave
    'player:join': [
        "<player> joined the game",
        r"<player>\[(?P<client>.*?)\] logged in with entity id (?P<id>\d+) at \(\[(?P<world>\w+)\]\s*(?P<x>-?\d+(\.\d+)?)\s*,\s*(?P<y>-?\d+(\.\d+)?)\s*,\s*(?P<z>-?\d+(\.\d+)?)\s*\)",
    ],
    'player:leave': [
        r"<player> lost connection: (?P<reason>.*?)",
        "<player> left the game",
    ],

    # --- Advancement
    'player:advancement': [
        r"<player> has made the advancement \[(?P<type>.*?)\]",
    ],
}


def _convert(template_map:dict):
    return {
        tag: [
            re.compile(r'^\s*' + template\
                .replace('<player>',    r'(?P<player>[\w ]+)')\
                .replace('<player/mob>',r'(?P<other>[\w ]+)')\
                .replace('<item>',      r'(?P<item>[\w ]+)')\
                .replace('while',       r'whil(e|st)') + r'\s*$'
            )
            for template in templates
        ]
        for (tag, templates) in template_map.items()
    }

REGEX_MAP = _convert(_TEMPLATES)
del _TEMPLATES  # no need to keep all those strings in memory


def detect(message:str) -> tuple[str, re.Match|None]:
    """
    Detect the 'type' of PaperMC server log message.
    
    :param message: server log message (excluding timestamp & owner)

    Example usage::

        >>> (key, match) = detect('Dude died')
        >>> key
        'player:death:generic'
        >>> match.groupdict()
        {'player': 'Dude'}
    
    Or, for more detail::

        >>> (key, match) = detect("FraggyMuffin[/172.25.0.1:39356] logged in with entity id 27 at ([world]9.5, 80.0, -2.5)")
        >>> key
        'player:join'
        >>> match.groupdict()
        {'player': 'FraggyMuffin', 'client': '/172.25.0.1:39356', 'id': '27', 'world': 'world', 'x': '9.5', 'y': '80.0', 'z': '-2.5'}

    Unrecognised log messages just return ``('unknown', None)``::

        >>> (key, match) = detect('derp')
        ('unknown', None)
    """
    for (key, regex_list) in REGEX_MAP.items():
        for regex in regex_list:
            if (match := regex.search(message)):
                return (key, match)
    return ('unknown', None)


if __name__ == '__main__':
    import unittest
    
    class TestLogMessages(unittest.TestCase):
        DATA = {  # format: {name: (type, input), ...} - taken directly from server logs
            'join1':    ('player:join',     "FraggyMuffin joined the game"),
            'join2':    ('player:join',     "FraggyMuffin[/172.25.0.1:39356] logged in with entity id 27 at ([world]9.5, 80.0, -2.5)"),
            'leave1':   ('player:leave',    "FraggyMuffin lost connection: Disconnected"),
            'leave2':   ('player:leave',    "FraggyMuffin left the game"),
            'advance':  ('player:advancement',      "FraggyMuffin has made the advancement [Monster Hunter]"),
            'death1':   ('player:death:falling',    "SomeDude fell from a high place"),
            'death2':   ('player:death:lava',       "SomeDude tried to swim in lava"),
            'other':    ('unknown',                 "blah blah"),
        }

        def test_detect(self):
            for (name, (e_key, message)) in self.DATA.items():
                with self.subTest(name=name):
                    (key, match) = detect(message)
                    self.assertEqual(key, e_key)
                    if key == 'unknown':
                        self.assertIsNone(match)
                    else:
                        self.assertIsInstance(match, re.Match)

    unittest.main()


