#!/usr/bin/env python
import os
import pwd
from jinja2 import Template

def random_words(*args, delimiter:str='') -> str:
    import wonderwords
    randomword = wonderwords.RandomWord()
    return delimiter.join(
        randomword.word(include_parts_of_speech=[p]).capitalize()
        for p in args
    )

def random_name():
    return random_words('verb', 'noun', delimiter=' ')

def random_seed():
    return random_words('adjective', 'noun')

def random_password():
    from random import randbytes
    from binascii import b2a_base64
    return '.'.join((
        random_words('verb', 'adjective', 'noun'),
        b2a_base64(randbytes(3)).decode()[:4],
    ))


def ask(question, default, default_text=None):
    """
    Ask question, get answer.
    """
    print(f'{question} [default: {default_text}]')
    answer = input('   > ').strip()
    if answer:
        return answer
    answer = default() if callable(default) else default
    print(f'   - {answer}')
    return answer


def generate_settings_env(templates, output, random, **_):
    """
    Genreate settings environment file
    """
    filename = ('settings.env', '.jinja2')
    filename_in = os.path.join(templates, ''.join(filename))
    filename_out = os.path.join(output, filename[0])

    if os.path.exists(filename_out):
        replace = input(f"Output file already exists: {filename_out!r}, do you want to replace it? [yN]")
        if not replace.lower().startswith('y'):
            print('[aborting...]')
            return
    
    # Ask Questions
    questions = {  # format: {<variable>: *args, ... }
        'SERVER_NAME': ("Name of server when viewed by a client", random_name, '<random>'),
        'SEED': ("Map seed", random_seed, "<random>"),
        'MODE': ("Game mode (creative, survival, etc)", 'creative', 'creative'),
        'RCON_PASSWORD': ("Password for external RCON", random_password, '<random>'),
    }
    answers = {}
    for (name, (question, default, default_text)) in questions.items():
        if random:
            answers[name] = default() if callable(default) else default
        else:
            answers[name] = ask(f'{name}: {question}', default, default_text)

    # Render to File
    with open(filename_in, 'r') as file_in, open(filename_out, 'w') as file_out:
        print(f"Writing: {filename_out!r}")
        file_out.write(Template(file_in.read()).render(
            UID=pwd.getpwnam(os.environ['USER']).pw_uid,
            GID=pwd.getpwnam(os.environ['USER']).pw_gid,
            **answers,
        ))


def generate_tasks_cron(templates, output, **_):
    """
    Genreate tasks cron file
    """
    filename = ('tasks.cron', '.jinja2')
    filename_in = os.path.join(templates, ''.join(filename))
    filename_out = os.path.join(output, filename[0])

    if os.path.exists(filename_out):
        replace = input(f"Output file already exists: {filename_out!r}, do you want to replace it? [yN]")
        if not replace.lower().startswith('y'):
            print('[aborting...]')
            return

    # Render to File
    with open(filename_in, 'r') as file_in, open(filename_out, 'w') as file_out:
        print(f"Writing: {filename_out!r}")
        file_out.write(Template(file_in.read()).render(**os.environ))


if __name__ == '__main__':
    import argparse

    DEFAULT_TEMPLATES = os.path.relpath(os.path.join(os.path.dirname(__file__), 'templates'), os.getcwd())
    DEFAULT_OUTPUT = os.path.relpath(os.path.join(os.path.dirname(__file__), '..'), os.getcwd())

    parser = argparse.ArgumentParser(
        description="Set minecraft server's initial environment",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    group = parser.add_argument_group('File Paths')
    group.add_argument(
        '--templates', '-t', default=DEFAULT_TEMPLATES,
        help="Folder containing templates",
    )
    group.add_argument(
        '--output', '-o', default=DEFAULT_OUTPUT,
        help="Folder to write outputs to",
    )

    parser.add_argument(
        '--random', '-r', action='store_true', default=False,
        help="If set, ask no questions, set all random answers.",
    )

    args = parser.parse_args()
    try:
        generate_settings_env(**vars(args))
        generate_tasks_cron(**vars(args))
    except KeyboardInterrupt:
        print("\n[cancelled]")

