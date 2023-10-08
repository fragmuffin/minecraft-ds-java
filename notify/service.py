
import os
import sys
sys.path.insert(0, os.path.join(os.path.split(__file__)[0], 'lib'))

import webhooks
import logs

DEFAULT_LOGFILE = '/var/logs/latest.log'


def main():
    import argparse
    parser = argparse.ArgumentParser("Parser PaperMC server logs & send join notifications off")
    parser.add_argument(
        '--logfile', default=DEFAULT_LOGFILE, metavar='LOG',
        help="PaperMC logfile (<server data>/logs/latest.log)",
    )
    args = parser.parse_args()
    
    hooks = list(webhooks.default_gen())    
    for msg in logs.log_iter(args.logfile, verbose=True):
        for hook in hooks:
            if hook.process(msg):
                print(f"sent webhook: {hook}")


if __name__ == '__main__':
    main()