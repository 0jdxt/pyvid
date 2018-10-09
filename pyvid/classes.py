import itertools
import os
import re
from pathlib import Path
from typing import List, Tuple, Generator, Any

import click
from hurry.filesize import size


class Video:
    path: Path
    converted: int
    force: bool
    size: int
    conv_path: Path

    def __init__(self, path:Path, force:bool) -> None:
        self.path = path
        self.converted = 0
        self.force = force
        self.size = self.path.stat().st_size

        conv_name = self.path.with_suffix('.mp4').name
        self.conv_path = self.path.parent / 'converted' / conv_name

    def __repr__(self) -> str:
        return f'<Video {self.path.name} {size(self.size)}>'

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Video):
            return os.path.samestat(os.stat(self.path), os.stat(other.path))
        elif isinstance(other, Path):
            return os.path.samestat(os.stat(self.path), os.stat(other))
        raise NotImplementedError


class VideoPath(type(Path())):

    def __init__(self,
                folder:str, ext:str='',
                force:bool=False, rem:bool=False) -> None:
        if ext:
            self.exts = [ext[1:] if ext[0] == '.' else ext]
        else:
            self.exts = ['mp4', 'avi', 'mkv', 'mov', 'webm']
        self.force = force
        self.rem = rem

    def __iter__(self) -> Generator:
        if self.is_file():
            yield Video(self, self.force)
        else:
            for y in self.exts:
                for z in self.glob('*.' + y):
                    yield Video(z, self.force)


class Logger:
    """Logger for video conversion stats"""

    def __init__(self, fname:str, append:bool=False) -> None:
        """Store ref to fname and create fresh log unless append is True"""
        self.fname = fname
        if append:
            self.reset()

    def __repr__(self) -> str:
        return f'<Logger {self.fname}>'

    def log(self, entry:str, orig:int=0, conv:int=0) -> None:
        """Write entry to log file. If passed orig and conv, append to entry"""
        if orig:
            entry += f':{orig}:{conv}'

        with open(self.fname, 'a') as f:
            print(entry, file=f)

    def get(self, n: int) -> List[str]:
        """Return last n lines of log file."""
        with open(self.fname, 'r') as f:
            return f.readlines()[-n if n > 1 else -1:]

    def reset(self) -> None:
        """Delete log file from disk."""
        if os.path.exists(self.fname):
            os.remove(self.fname)

    def summarise(self, num: int) -> None:
        """Generate summary stats for conversions."""
        lines = '\n'.join(self.get(num))
        size_regex = re.compile(r':(?P<original>\d+):(?P<converted>\d+)$', re.M)

        tot_o = 0
        tot_c = 0
        for original, converted in size_regex.findall(lines):
            tot_o += int(original)
            tot_c += int(converted)

        try:
            rel_size = round(tot_c * 100 / tot_o)
        except ZeroDivisionError:
            click.echo('summary not written')
        else:
            self.log('-- Batch of last %d: %d%% of original size - %s -> %s' % (
                num, rel_size, size(tot_o), size(tot_c)
            ))
