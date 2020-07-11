from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class PathInfo:
    '''
    Class for holding a path pair from installed to repo path and also holds
    information about which files and directories belong to the path
    '''
    path_pair: Tuple[str, str]
    files_to_copy: List[str]
    dirs_to_copy: List[str]
