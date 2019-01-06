#!/usr/bin/env python
# -*- encoding: utf-8
"""pyvid package. converts files in path to smaller mp4 files."""
from typing import List, Tuple, Generator, Any
from pathlib import Path
import os
import re
import shutil
import subprocess
import sys

import ffmpeg
import click
import click_spinner as spin
from hurry.filesize import size
from tqdm import tqdm

__version__ = "0.0.9"


class VideoPath(os.PathLike):
    __slots__ = ("path", "exts", "force", "rem")

    def __init__(
        self, path: str, ext: str = "", force: bool = False, rem: bool = False
    ) -> None:
        self.path = Path(path)
        if ext:
            self.exts = [x[1:] if x[0] == "." else x for x in ext.split(",")]
        else:
            self.exts = ["mp4", "avi", "mkv", "mov", "webm"]
        self.force = force
        self.rem = rem
        if self.path.is_file():
            self.videos = [Video(self.path, self.force)]
        else:
            self.videos = [
                Video(z, self.force)
                for y in self.exts
                for z in self.path.glob("*." + y)
            ]

    def __iter__(self):
        return iter(self.videos)

    def __fspath__(self):
        return str(self.path)

    __repr__ = __fspath__


class Video:
    __slots__ = ("path", "converted", "force", "conv_path")

    def __init__(self, path: Path, force: bool) -> None:
        self.path = path
        self.converted = 0
        self.force = force

        conv_name = self.path.with_suffix(".mp4").name
        self.conv_path = self.path.parent / "converted" / conv_name

    @property
    def size(self):
        return self.path.stat().st_size

    def __repr__(self) -> str:
        return f"<Video {self.path.name} {size(self.size)}>"

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Video):
            return os.path.samestat(os.stat(self.path), os.stat(other.path))
        elif isinstance(other, Path):
            return os.path.samestat(os.stat(self.path), os.stat(other))
        return NotImplemented


class Logger:
    """Logger for video conversion stats"""

    __slots__ = "fname"

    def __init__(self, fname: str, append: bool = False) -> None:
        """Store ref to fname and create fresh log unless append is True"""
        self.fname = fname
        if append:
            self.reset()

    def __repr__(self) -> str:
        return f"<Logger {self.fname}>"

    def log(self, entry: str, orig: int = 0, conv: int = 0) -> None:
        """Write entry to log file. If passed orig and conv, append to entry"""
        if orig:
            entry += f":{orig}:{conv}"

        with open(self.fname, "a") as f:
            print(entry, file=f)

    def get(self, n: int) -> List[str]:
        """Return last n lines of log file."""
        with open(self.fname, "r") as f:
            return f.readlines()[-n if n > 1 else -1 :]

    def reset(self) -> None:
        """Delete log file from disk."""
        if os.path.exists(self.fname):
            os.remove(self.fname)

    def summarise(self, num: int) -> None:
        """Generate summary stats for conversions."""
        lines = "\n".join(self.get(num))
        size_regex = re.compile(r":(\d+):(\d+)$", re.M)

        tot_o = 0
        tot_c = 0
        for original, converted in size_regex.findall(lines):
            tot_o += int(original)
            tot_c += int(converted)

        try:
            rel_size = round(tot_c * 100 / tot_o)
        except ZeroDivisionError:
            click.echo("summary not written")
        else:
            self.log(
                "-- Batch of last %d: %d%% of original size - %s -> %s"
                % (num, rel_size, size(tot_o), size(tot_c))
            )


def convert_files(vids: VideoPath, logger: Logger) -> None:
    """Convert file in VideoPath object."""
    top = vids if vids.path.is_dir() else vids.path.parent
    n_proc = 0

    n_vids = len(vids.videos)
    i = 1

    # click.echo(f"output directory: {vids.conv_path}")

    if vids.force:
        click.echo(f"\n{n_vids} files found:")
        click.echo(vids.videos)
        click.echo(f"convert {n_vids} files? (y)es/(n)o: [n] ", nl=False)

        ans = click.getchar()
        click.echo(ans)
        if ans != "y":
            sys.exit()

    for vid in vids:
        if not vids.force:
            click.echo()

        if n_proc == 0:
            logger.log(f"CONVERTING FILES IN {top}")

        success, code = convert_video(vid, i, n_vids)

        i += 1
        if not success:
            if code:
                break
            continue

        logger.log(vid.path.name, vid.size, vid.converted)
        n_proc += 1

        if vids.rem:
            os.remove(vid.path)

    if n_proc:
        logger.summarise(n_proc)
        max_lines = 3
        click.echo()
        if n_proc > max_lines:
            click.echo("...")
        n_lines = max_lines if n_proc > max_lines else n_proc + 1
        click.echo("".join(logger.get(n_lines)))
        if n_proc > max_lines:
            click.echo(f"see {logger.fname} for more details")
    else:
        logger.reset()
        click.echo(f"NO VIDEO FILES CONVERTED IN {top}")


def convert_video(vid: Video, idx: int, nvid: int) -> Tuple[bool, int]:
    """Use fmmpeg to convert Video object."""

    if not vid.force:
        prompt = (
            click.style(str(vid.path), fg="yellow")
            + " -> "
            + click.style(str(vid.conv_path.parent / vid.conv_path.name), fg="green")
            + "\ncontinue? (y)es/(n)o/(c)ancel all: [n] "
        )

        click.echo(prompt, nl=False)

    opt = "y" if vid.force else click.getchar()
    if not vid.force:
        click.echo(opt)

    if opt == "y":
        os.makedirs(vid.conv_path.parent, exist_ok=True)

        stream = ffmpeg.input(str(vid.path))
        stream = ffmpeg.output(
            stream,
            str(vid.conv_path),
            vcodec="libx265",
            crf=18,
            acodec="copy",
            preset="veryfast",
        )

        click.echo(f"[{idx}/{nvid}] converting {vid.path}...", nl=False)

        with spin.spinner():
            try:
                err, out = ffmpeg.run(stream, quiet=True, overwrite_output=True)
            except KeyboardInterrupt:
                click.echo("\baborted")
                os.remove(vid.conv_path)
                vid.conv_path.parent.rmdir()
                return False, 0

        click.echo("done")
        vid.converted = vid.conv_path.stat().st_size
        return True, 0

    return False, int(opt == "c")


@click.command()
@click.argument("path", type=click.Path(exists=True))
@click.option("-e", "--ext", help="File extension to look for")
@click.option("-y", "--force", is_flag=True, help="Disable per video prompt")
@click.option("-d", "--rem", is_flag=True, help="Delete source video file(s)")
@click.version_option()
def main(path: str, ext: str, force: bool, rem: bool) -> None:
    """Convert video(s) in specified path."""
    if ext:
        click.echo(f"extensions: {ext}")
    else:
        click.echo(f"looking for videos in {path}")

    click.echo("Checking ffmpeg support...", nl=False)
    if not shutil.which("ffmpeg"):
        click.echo("\nERROR: ffmpeg is either not installed or not in PATH")
        sys.exit()

    click.echo("found")

    codec = False
    codecs = subprocess.run(
        ["ffmpeg", "-codecs"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
    ).stdout.splitlines()
    for line in codecs:
        # check the codec exists and can encode
        if b"264" in line and b"E" in line[:3]:
            codec = True
            break

    if not codec:
        click.echo(
            "ERROR: ffmpeg installation does not support H.264 encoding (libx264)"
        )
        sys.exit()

    logger = Logger("stats.txt")
    vp = VideoPath(path, ext=ext, force=force, rem=rem)
    convert_files(vp, logger)


if __name__ == "__main__":
    main()
