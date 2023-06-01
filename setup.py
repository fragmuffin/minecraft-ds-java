#!/usr/bin/env python
import os
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


def setup(args):
    if os.path.exists(args.output):
        replace = input(f"Output file already exists: {args.output!r}, do you want to replace it? [Yn]")
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
        if args.random:
            answers[name] = default() if callable(default) else default
        else:
            answers[name] = ask(f'{name}: {question}', default, default_text)

    # Render to File
    with open(args.template, 'r') as file_in, open(args.output, 'w') as file_out:
        file_out.write(Template(file_in.read()).render(**answers))


if __name__ == '__main__':
    import argparse

    DEFAULT_TEMPLATE = 'settings.env.jinja2'
    DEFAULT_OUTPUT = 'settings.env'

    parser = argparse.ArgumentParser(
        description="Set minecraft server's initial environment",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    group = parser.add_argument_group('Files')
    group.add_argument(
        '--template', '-t', default=DEFAULT_TEMPLATE,
        help="Template environment file",
    )
    group.add_argument(
        '--output', '-o', default=DEFAULT_OUTPUT,
        help="Output environment file.",
    )

    parser.add_argument(
        '--random', '-r', action='store_true', default=False,
        help="If set, ask no questions, set all random answers.",
    )

    args = parser.parse_args()
    try:
        setup(args)
    except KeyboardInterrupt:
        print("\n[cancelled]")

