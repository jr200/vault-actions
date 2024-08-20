import logging

from .app import run
from .util import initialise_logging, load_config, parse_args

def main(args):
    print("running main...", __name__)
    initialise_logging(args.CONFIG_LOG)
    config = load_config(args.CONFIG_FILES)

    if run(config):
        exit(0)
    
    exit(-1)


if __name__ == '__main__':
    args = parse_args()
    main(args)