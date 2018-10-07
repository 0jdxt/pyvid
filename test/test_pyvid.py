from pathlib import Path

from pyvid.classes import Video


def test_video_class() -> None:
    pth = Path('files/Carne_job.mov')
    vid = Video(pth, True)

    assert vid == pth
    assert vid.size == 20853615
    assert vid.force
    assert vid.converted == 0
    assert vid.conv_path == Path('files/converted/Carne_job.mp4')
