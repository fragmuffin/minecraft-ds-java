
import os
import sys
_this_dir = os.path.split(__file__)[0]
sys.path.insert(0, os.path.normpath(os.path.join(_this_dir, 'lib')))

import webhooks
import logs

DEFAULT_LOGFILE = os.path.normpath(os.path.join(_this_dir, '..', 'data', 'logs', 'latest.log'))


def main():
    # --- Parse CLI Arguments
    import argparse
    parser = argparse.ArgumentParser("Parser PaperMC server logs & send join notifications off")
    parser.add_argument(
        '--logfile', default=DEFAULT_LOGFILE, metavar='LOG',
        help="PaperMC logfile (<server data>/logs/latest.log)",
    )
    args = parser.parse_args()
    
    # --- Process Logfile (follow)
    hooks = list(webhooks.default_gen())
    for msg in logs.LogMessage.from_file_gen(args.logfile, verbose=True):
        for hook in hooks:
            if hook.process(msg):
                print(f"sent webhook: {hook}")


if __name__ == '__main__':
    main()