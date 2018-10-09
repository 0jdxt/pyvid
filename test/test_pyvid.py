from pathlib import Path

import pytest
from hurry.filesize import size
from click.testing import CliRunner

from pyvid import main
from pyvid.classes import Video


def test_video_class() -> None:
    pth = Path("files/Carne_job.mov")
    v_size = 20_853_615
    vid = Video(pth, True)

    assert vid == pth
    assert vid.size == v_size
    assert vid.force
    assert vid.converted == 0
    assert vid.conv_path == Path("files/converted/Carne_job.mp4")
    assert repr(vid) == f"<Video {pth.name} {size(v_size)}>"


def test_cli_file_in() -> None:
    with open("files/Carne_job.mp4", "rb") as f:
        orig_vid = f.read()

    runner = CliRunner()
    with runner.isolated_filesystem():
        with open("Carne_job.mp4", "wb") as f:
            f.write(orig_vid)

        res = runner.invoke(main, "Carne_job.mp4 -y".split())
        assert res.exit_code == 0
        assert "Carne_job.mp4:9878103:9117977" in res.output
