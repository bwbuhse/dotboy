#!/usr/bin/env python

import argparse
import datetime
import json
import socket
from pathlib import Path

from .config import Config
from .path_info import PathInfo
from .dotboy import DotBoy


def load_config(config_json_path=Path.home() / '.config/dotboy/config.json') -> Config:
    ''' Load dotboy's config.json (if it exists) '''
    if config_json_path.exists():
        with open(config_json_path) as config_json:
            config_json = config_json.read()
            config_json = json.loads(config_json)
    else:
        print(f"{str(config_json_path)} doesn't exist.\nExiting now...")
        exit(1)

    paths: List[PathInfo] = []
    for path in config_json['paths']:
        path_pair = path['installed_path'], path['repo_path']
        files_to_copy = path.get('files_to_copy', [])
        dirs_to_copy = path.get('dirs_to_copy', [])
        paths.append(PathInfo(path_pair, files_to_copy, dirs_to_copy))

    repo_path = Path.home() / '.dotboy'
    if 'repo_path' in config_json.keys():
        repo_path = Path.expanduser(Path(config_json['repo_path']))

    repo_url = ''
    if 'repo_url' in config_json.keys():
        repo_url = config_json['repo_url']

    return Config(repo_path, repo_url, paths)


def main():
    hostname = 'host-' + socket.gethostname()

    # Set-up and parse arguments to dotboy
    default_message = f'Update files for {hostname} at ' \
        f'{str(datetime.datetime.now())}'
    parser = argparse.ArgumentParser(prog='python -m dotboy',
                                     description='Manage your dot files easily')
    action = parser.add_mutually_exclusive_group()
    action.add_argument('-s', '--save', nargs='?', type=str,
                        const=default_message, metavar='MESSAGE',
                        help='Save your dot files with an '
                        'optional commit message. The default message just '
                        'specifies the time at which the changes were made. '
                        'This is the default option if neither save nor install'
                        'are specified.')
    action.add_argument('-i', '--install', nargs='?', type=str, const='',
                        metavar='HOST', help='Install dot files from your '
                        'chosen host. If a host is not specified, dotboy will '
                        'ask you to choose a host from all options.')
    parser.add_argument('-c', '--config', type=str, help='Specify a config.json'
                        ' for dotboy to use.')
    parser.add_argument('-G', '--no-git', help="Disable git. Files will still be copied but"
                        " any git actions in the repository won't happen.",
                        action='store_false')
    parser.add_argument('-v', '--verbose', help="Enable verbose output.",
                        action='store_true')

    args = parser.parse_args()

    if args.config == None:
        config = load_config()
    else:
        config = load_config(Path(args.config))

    db = DotBoy(config, hostname, args.no_git, args.verbose)

    if args.install != None:
        if len(args.install) > 0:
            db.install(config, args.install)
        else:
            db.install(config)
    else:
        if args.save == None:
            db.save(config, default_message)
        else:
            db.save(config, args.save)


if __name__ == '__main__':
    main()
