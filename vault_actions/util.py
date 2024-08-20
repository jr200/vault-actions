import argparse
import logging
import logging.config
import os
from importlib.resources import files
import sys
from typing import Dict, Any, List
import yaml

def load_config(filenames: List[str]) -> Dict[str, Any]:
    merged_config = {}

    for filename in filenames:
        print(f"loading config: {filename}")
        with open(filename, 'r') as file:
            config = yaml.safe_load(file)
            config = _expand_env_vars(config)
            merged_config = _merge_dicts(merged_config, config)

    return merged_config

def _expand_env_vars(value: Any) -> Any:
    if isinstance(value, str):
        return os.path.expandvars(value)
    elif isinstance(value, dict):
        return {k: _expand_env_vars(v) for k, v in value.items()}
    elif isinstance(value, list):
        return [_expand_env_vars(v) for v in value]
    else:
        return value

def _merge_dicts(a: Dict[str, Any], b: Dict[str, Any]) -> Dict[str, Any]:
    """
    Recursively merges dictionary `b` into dictionary `a`.
    If there are overlapping keys and both values are dictionaries, it merges them recursively.
    Otherwise, `b`'s value overwrites `a`'s value.
    """
    for key in b:
        if key in a and isinstance(a[key], dict) and isinstance(b[key], dict):
            a[key] = _merge_dicts(a[key], b[key])
        else:
            a[key] = b[key]
    return a

def parse_args() -> argparse.Namespace:
    argv = sys.argv[1:]
    parser = argparse.ArgumentParser(add_help=True)

    parser.add_argument(
        '-f', '--config',
        help='Path to config file(s)',
        default=None,
        nargs='*',
        dest='CONFIG_FILES'
    )

    parser.add_argument(
        '-l', '--log-config',
        help='Path to logger config',
        default=str(files(__package__).joinpath("logging.yaml")),
        action='store',
        dest='CONFIG_LOG'
    )

    args = parser.parse_args(argv)

    if not args.CONFIG_FILES:
        args.CONFIG_FILES = [str(files(__package__).joinpath("config.yaml"))]

    return args


def initialise_logging(config_file: str) -> None:
    config = load_config([config_file])
    if 'logging' in config:
        logging.config.dictConfig(config['logging'])
    else:
        logging.basicConfig(level=logging.INFO)
    
    def handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        logger = logging.getLogger("UNCAUGHT_EXCEPTION")
        logger.fatal('', exc_info=(exc_type, exc_value, exc_traceback))

    sys.excepthook = handle_exception
