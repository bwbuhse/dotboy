from dataclasses import dataclass
from pathlib import Path
from typing import List

from path_info import PathInfo


@dataclass
class Config:
    ''' Class for holding information about dotman's configuration '''

    repo_path: Path
    repo_url: str
    path_infos: List[PathInfo]

