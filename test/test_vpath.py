from pathlib import Path

from pyvid import VideoPath, Video


def test_file_vpath_file() -> None:
    fs = VideoPath("setup.cfg", codec="libx265", ext="cfg")
    fi = Video(Path("setup.cfg"), force=False)

    for fname in fs:
        assert fname == fi
    assert fs.path.is_file()


def test_file_vpath_folder() -> None:
    folder = "files"
    p = Path(folder)
    fs = VideoPath(folder, codec="libx265", ext="")

    vids = [p / ("Carne_job." + x) for x in ["mp4", "mov", "webm"]]

    for i, vid in enumerate(fs):
        assert vid == vids[i]
    assert fs.path.is_dir()
    assert not fs.path.is_file()
