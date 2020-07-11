# dotboy

A Python script to help with dot file management

### Dependencies:

GitPython

### Configuration:

Configuration is done in a json stored in '~/.config/dotboy/config.json'

An example configuration json is:

{
  "repo_path": "~/projects/dot-files",
  "paths": [
    {
      "installed_path": "~",
      "repo_path": "",
      "files_to_copy": [
        ".tmux.conf",
        ".zshrc",
        ".zprofile",
        ".zpreztorc"
      ]
    },
    {
      "installed_path": "~/.config",
      "repo_path": ".config",
      "files_to_copy": [
        "nvim/init.vim",
        "nvim/coc-settings.json"
      ],
      "dirs_to_copy": [
        "alacritty",
        "sway",
        "waybar",
        "i3",
        "polybar",
        "picom",
        "dotboy"
      ]
    },
    {
      "installed_path": "/efi/EFI/refind",
      "repo_path": "refind",
      "files_to_copy": [
        "refind.conf"
      ]
    }
  ]
}

repo_path is the path to the repository that you want to store the dot files in.

paths is a list of json objects, each corresponding to a path where dot files
are stored on the system. Each object in paths needs two variables with two
other optional variables.
"installed_path" is the path to the installed location of the dot_files.
"repo_path" is the path that you want the files stored within each host-folder
inside of the repo.
"files_to_copy" and "folders_to_copy" are both lists of files and folders,
respectively to/from the installed path and repo path.
