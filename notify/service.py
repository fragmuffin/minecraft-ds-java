
import os
import sys
_this_dir = os.path.split(__file__)[0]
sys.path.insert(0, os.path.normpath(os.path.join(_this_dir, 'lib')))

import webhooks
import logs
import logging

log = logging.getLogger(__name__)

DEFAULT_LOGFILE = os.path.normpath(os.path.join(_this_dir, '..', 'data', 'logs', 'latest.log'))
AFFIRMATIVE = {'1', 'yes', 'on', 'true'}  # lower case


def main():
    # --- Parse CLI Arguments
    import argparse
    parser = argparse.ArgumentParser("Parser PaperMC server logs & send join notifications off")
    parser.add_argument(
        '--logfile', default=DEFAULT_LOGFILE, metavar='LOG',
        help="PaperMC logfile (<server data>/logs/latest.log)",
    )
    parser.add_argument(
        '--debug', dest='loglevel',
        action='store_const', const=logging.DEBUG,
        default=logging.DEBUG if os.environ.get('DEBUG', '').lower() in AFFIRMATIVE else logging.INFO,
        help="Log all the things",
    )
    args = parser.parse_args()
    
    # --- Logging (outward)
    logging.basicConfig(level=args.loglevel)
    
    # --- Process Logfile (follow)
    hooks = list(webhooks.default_gen())
    for msg in logs.LogMessage.from_file_gen(args.logfile):
        for hook in hooks:
            if hook.process(msg):
                log.info("sent webhook %r for message: %s", hook, msg)

if __name__ == '__main__':
    main()
