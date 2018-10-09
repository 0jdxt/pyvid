from pathlib import Path

import pytest
from hurry.filesize import size

from pyvid.classes import Video


def test_video_class() -> None:
    pth = Path('files/Carne_job.mov')
    v_size = 20853615
    vid = Video(pth, True)

    assert vid == pth
    assert vid.size == v_size
    assert vid.force
    assert vid.converted == 0
    assert vid.conv_path == Path('files/converted/Carne_job.mp4')
    assert repr(vid) == f'<Video {pth.name} {size(v_size)}>'
    with pytest.raises(NotImplementedError):
        vid == 5
        vid == 'string'
