from pathlib import Path
import re

import pytest
from hurry.filesize import size
from click.testing import CliRunner

from pyvid import main, Video


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


def get_file() -> bytes:
    with open("files/Carne_job.mp4", "rb") as f:
        return f.read()


def test_rem_opt() -> None:
    runner = CliRunner()
    test_file = get_file()
    with runner.isolated_filesystem():
        with open("video.mp4", "wb") as f:
            f.write(test_file)
        # print(list(Path().glob("*")))
        res = runner.invoke(main, "video.mp4 --rem -y".split())
        assert res.exit_code == 0
        assert not Path("video.mp4").exists()


# TODO: hypothesis
def test_cli_file_in() -> None:
    runner = CliRunner()
    test_file = get_file()
    with runner.isolated_filesystem():
        with open("Carne_job.mp4", "wb") as f:
            f.write(test_file)

        res = runner.invoke(main, "Carne_job.mp4 -y".split())
        assert res.exit_code == 0

        with open("stats.txt", "r") as log:
            text = log.read()
        assert re.search(r"^Carne_job.mp4:9878103:\d+$", text, re.M)


prompt_c_reg = re.compile(r"^NO VIDEO FILES CONVERTED", re.M)


def test_prompt_cancel_all() -> None:
    runner = CliRunner()
    res = runner.invoke(main, "files", input="c")
    assert res.exit_code == 0
    assert prompt_c_reg.search(res.output)


def test_prompt_cancel() -> None:
    runner = CliRunner()
    res = runner.invoke(main, "files", input="nnn")
    assert res.exit_code == 0
    assert prompt_c_reg.search(res.output)
