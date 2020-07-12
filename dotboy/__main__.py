#!/usr/bin/env python

import datetime
import json
import os
import shutil
import socket
import sys
from pathlib import Path
from typing import List

import git

from .config import Config
from .path_info import PathInfo

# Set to True to enable 'no git' mode
# While True, all pulling/committing/pushing to the git repo (by the script)
#   is disabled
# Used for updated this script without committing changes everytime that the
#   script is run
NO_GIT = False

# Set to True while updating this script
# This variable won't let you run the script without passing a commit message
#   but still lets you push the changes it copies
# This can be useful for making sure that the code still works but with a
#   useful commit message about the changes
EDITING_SCRIPT = False


# Used to create the directory for the current HOST
HOSTNAME = 'host-' + socket.gethostname()


def load_config() -> Config:
    config_json_path = Path.home() / '.config/dotboy/config.json'
    if config_json_path.exists():
        with open(config_json_path) as config_json:
            config_json = config_json.read()
            config_json = json.loads(config_json)

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


def pull(origin: git.Remote):
    if not NO_GIT:
        origin.pull()


def push(origin: git.Remote):
    if not NO_GIT:
        origin.push()


def add(repo: git.Repo):
    if not NO_GIT:
        repo.git.add('-A')


def commit(repo: git.Repo, message: str = None):
    if not NO_GIT:
        if message != None:
            repo.index.commit(message)
        else:
            repo.index.commit('Update files for ' + HOSTNAME +
                              ' ' + str(datetime.datetime.now()))


def save(config: Config, message: str = None):
    '''
    Pulls any changes from the git repo.
    Deletes the directory in the repo for the current host then re-creates it.
    Copies all specified files to the directory for the host.
    Adds, commits, then pushes all the changes.

    If an argument is passed, it will replace the default commit message.
    '''

    no_remote = False

    # Set up the directory if it doesn't exist yet
    if not config.repo_path.exists():
        # If a url is in the config.json then we assume that the repo exists
        # somewhere
        # If there's no repo_url set, then we just initialize one and don't
        # push/pull anything (since there's not a remote yet)
        if len(config.repo_url) > 0:
            git.Repo.clone_from(config.repo_url, str(config.repo_path))
        else:
            no_remote = True
            git.Repo.init(config.repo_path)

    os.chdir(config.repo_path)
    repo = git.Repo(config.repo_path)


    # If the repo has a remote, origin will be set to it
    if not no_remote:
        try:
            origin = repo.remote()
        except ValueError:
            no_remote = True

    repo_hostname_path = config.repo_path / HOSTNAME

    # Pull the git repo before updating anything
    if not no_remote:
        pull(origin)

    # We remove the previous version so files that are no-longer there are removed
    if os.path.exists(HOSTNAME) and os.path.isdir(HOSTNAME):
        shutil.rmtree(HOSTNAME)
    repo_hostname_path.mkdir()

    # Copy files/dirs from their original locations into the repo
    for path in config.path_infos:
        installed_path = Path.expanduser(Path(path.path_pair[0]))
        repo_path = repo_hostname_path / path.path_pair[1]
        os.makedirs(repo_path, exist_ok=True)

        for dir_to_copy in path.dirs_to_copy:
            if (installed_path / dir_to_copy).exists():
                shutil.copytree(installed_path / dir_to_copy,
                                repo_path / dir_to_copy)

        for file_to_copy in path.files_to_copy:
            if '/' in file_to_copy:
                # We need to create any directories that don't exist already
                inner_dirs = file_to_copy[0:file_to_copy.rfind('/')]
                os.makedirs(repo_path / inner_dirs, exist_ok=True)
            if (installed_path / file_to_copy).exists():
                shutil.copy(installed_path / file_to_copy,
                            repo_path / file_to_copy)

    # Add, commit, and push any changes
    add(repo)
    if no_remote:
        diff = ''
    else:
        diff = repo.git.diff('HEAD~', repo_hostname_path).strip()
    if len(diff) > 0:
        if message != None:
            commit(repo, message)
        else:
            commit(repo)
        if not no_remote:
            push(origin)


def install(config: Config):
    '''
    Install dot-files from a specified host
    '''
    host_dir_paths = [x for x in config.repo_path.iterdir(
    ) if x.is_dir() and x.name.startswith('host')]
    host_dict = {}
    for i in range(0, len(host_dir_paths)):
        host_dict[i] = host_dir_paths[i]

    if len(host_dir_paths) > 0:
        print('You have no saved hosts so there is nothing to install\n'
              'Exiting now...')

    print('Select a host to install from:')
    for index, host in host_dict.items():
        host = host.name[host.name.find('-') + 1:]
        print(f'[{index}] - {host}')

    selected_host = int(input('\n'))
    if selected_host not in host_dict:
        print(f'{selected_host} is not a valid host option.\n'
              f'Exiting now...')

    selected_host_path = host_dict[selected_host]

    # Copy files/dirs from the repo to their installed locations
    for path in config.path_infos:
        installed_path = Path.expanduser(Path(path.path_pair[0]))
        repo_path = selected_host_path / path.path_pair[1]

        for dir_to_copy in path.dirs_to_copy:
            if (selected_host_path / dir_to_copy).exists():
                shutil.copytree(installed_path / dir_to_copy,
                                repo_path / dir_to_copy,
                                dirs_exist_ok=True)

        for file_to_copy in path.files_to_copy:
            if '/' in file_to_copy:
                # We need to create any directories that don't exist already
                inner_dirs = file_to_copy[0:file_to_copy.rfind('/')]
                os.makedirs(installed_path / inner_dirs, exist_ok=True)
            if (selected_host_path / file_to_copy).exists():
                shutil.copy(selected_host_path / file_to_copy,
                            installed_path / file_to_copy)


def main(argv):
    if NO_GIT:
        print('Running in NO_GIT mode')
        print('Any changes to dot files will not be commited or pushed to the '
              'git repo\n')
    elif EDITING_SCRIPT and len(argv) < 3:
        print('Please enter a commit message as an argument while using '
              'EDITING_SCRIPT mode')
        print('Exiting now...')
        return

    config = load_config()

    if len(argv) <= 1:
        save(config)
    elif argv[1] == 'save':
        if len(argv) > 2:
            save(config, argv[2])
        else:
            save(config)
    elif argv[1] == 'install':
        install(config)
    else:
        print(argv[1], ' is not a valid argument for dots.py')


if __name__ == '__main__':
    main(sys.argv)
