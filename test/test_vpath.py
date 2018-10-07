from pathlib import Path

import pytest

from pyvid.classes import VideoPath, Video


def test_file_vpath_file() -> None:
    fs = VideoPath('setup.cfg', ext='cfg')
    fi = Video(Path('setup.cfg'), force=False)

    for fname in fs:
        assert fname == fi
    assert fs.is_file()
    assert not fs.is_dir()


def test_file_vpath_folder() -> None:
    folder = 'files'
    p = Path(folder)
    fs = VideoPath(folder)

    files = [p/('Carne_job.' + x) for x in ['mp4', 'mov', 'webm']]

    for i, fname in enumerate(fs):
        assert fname == files[i]
    assert fs.is_dir()
    assert not fs.is_file()
