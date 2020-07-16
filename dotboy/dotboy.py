import os
import shutil
import sys
from typing import List
from pathlib import Path

import git

from .config import Config
from .path_info import PathInfo


class DotBoy():
    ''' The core of the DotBoy script. '''

    def __init__(self, config: Config, hostname: str, git_enabled: bool, verbose: bool):
        self.config = config
        self.hostname = hostname
        self.git_enabled = git_enabled
        self.verbose = verbose

    def _pull(self, origin: git.Remote):
        if self.git_enabled:
            if self.verbose:
                print('Pulling dot file repository')
            origin.pull()

    def _push(self, origin: git.Remote):
        if self.git_enabled:
            if self.verbose:
                print('Pushing dot file repository')
            origin.push()

    def _add(self, repo: git.Repo):
        if self.git_enabled:
            if self.verbose:
                print('Adding changed files to staging area')
            repo.git.add('-A')

    def _commit(self, repo: git.Repo, message: str):
        if self.git_enabled:
            if self.verbose:
                print('Pushing changes to the dot file repository')
            repo.index.commit(message)

    def save(self, config: Config, message: str = None):
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
                if self.verbose:
                    print('Cloning dot file repository')
                git.Repo.clone_from(config.repo_url, str(config.repo_path))
            else:
                if self.verbose:
                    print('Initializing a new git repository')
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

        repo_hostname_path = config.repo_path / self.hostname

        # Pull the git repo before updating anything
        if not no_remote:
            self._pull(origin)

        # We remove the previous version so files that are no-longer there are removed
        if os.path.exists(self.hostname) and os.path.isdir(self.hostname):
            if self.verbose:
                print(f"Deleting old version of {self.hostname}'s dot files")
            shutil.rmtree(self.hostname)
        repo_hostname_path.mkdir()

        if self.verbose:
            print('Copying dot files into the repository')

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
        changed_files = []
        if not no_remote:
            changed_files = [item.a_path for item in repo.index.diff(None)]
        if len(changed_files) > 0:
            message += '\n\nFiles: '
            for file in changed_files:
                message += f'\n  * {file}'
            self._add(repo)
            self._commit(repo, message)
            if not no_remote:
                self._push(origin)

    def install(self, config: Config, host: str = None):
        '''
        Install dot-files from a specified host
        '''
        if self.verbose:
            print('Looking for hosts in the dot file repository')
        host_dir_paths = [x for x in config.repo_path.iterdir(
        ) if x.is_dir() and x.name.startswith('host')]
        host_dict = {}
        for i in range(0, len(host_dir_paths)):
            host_dict[i] = host_dir_paths[i]
        selected_host_path = ''

        if not len(host_dir_paths) > 0:
            print('You have no saved hosts so there is nothing to install\n'
                  'Exiting now...')
            exit(1)

        hosts = [host.name[host.name.find('-') + 1:] for index, host in
                 host_dict.items()]

        if host != None:
            if host in hosts:
                selected_host_path = host_dict[hosts.index(host)]
            else:
                print(f"Host {host} is not available to install from (it's not saved "
                      "in the repo right now).\nExiting now...")
                exit(1)
        else:
            print('Select a host to install from:')
            for i in range(0, len(hosts)):
                print(f'[{i}] - {hosts[i]}')

            selected_host = int(input('\n'))
            if selected_host not in host_dict:
                print(f'{selected_host} is not a valid host option.\n'
                      'Exiting now...')
                exit(1)

            selected_host_path = host_dict[selected_host]

        # We don't need to do this if we have self.git_enabled enabled
        if not self.git_enabled:
            return

        if self.verbose:
            print('Copying dot files from the repository into their installed'
                  ' locations')

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
