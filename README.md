# dotboy

A Python script to help with dot file management.

I originally started this because I got tired of manually copying dot files into
my configuration repo any time I changed one and I didn't realize how many
existing solutions there were. 

Anyways, I kept working on it because it's a fun learning experience and I wanted 
to add specific features that I could use for myself and decided to share it with 
the world.

## Requirements:

`python>=3.8`

## Dependencies:

`GitPython` (handled by both pip and the aur packages)

## Installation:

On Arch, you can use the [python-dotboy](https://aur.archlinux.org/packages/python-dotboy/)
or [python-dotboy-git](https://aur.archlinux.org/packages/python-dotboy-git/) AUR packages.

Otherwise, you can install `DotBoy` with pip via `pip install dotboy`.

## Configuration:

Configuration is done in a json stored in '~/.config/dotboy/config.json'

An example configuration json is:
```
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
```

`repo_path` is the path to the repository that you want to store the dot files in or where the repository already exists. This field is required.

`paths` is a list of json objects, each corresponding to a path where dot files
are stored on the system. Each object in paths needs two fields with two
other optional variables.

  `installed_path` is the path to the installed location of the dot_files. This field is required for each element in paths.

  `repo_path` is the path that you want the files stored within each host-folder
  inside of the repo. This field is required for each element in paths.
  
  `files_to_copy` and `folders_to_copy` are both lists of files and folders,
  respectively to/from the installed path and repo path. These elements are optional, however the paths element will be useless without at least one.
