#!/usr/bin/env python3
"""pyvid package. converts files in path to smaller mp4 files."""
from typing import List, Tuple, Any, Iterator
from pathlib import Path
import os
import re
from shutil import which
import subprocess
import sys

import ffmpeg
import click
import click_spinner as spin
from hurry.filesize import size

__version__ = "0.1.2"


class Logger:
    """Logger for video conversion stats"""

    __slots__ = "_fname"

    def __init__(self, fname: str, append: bool = False) -> None:
        """Store ref to fname and create fresh log unless append is True"""
        self._fname = fname
        if not append:
            self.reset()

    def __repr__(self) -> str:
        return self._fname

    def log(self, entry: str, orig: int = 0, conv: int = 0) -> None:
        """Write entry to log file. If passed orig and conv, append to entry"""
        if orig:
            entry += f":{orig}:{conv}"

        with open(self._fname, "a") as f:
            print(entry, file=f)

    def get(self, n: int) -> List[str]:
        """Return last n lines of log file."""
        with open(self._fname, "r") as f:
            return f.readlines()[-n if n > 1 else -1 :]

    def reset(self) -> None:
        """Delete log file from disk."""
        if os.path.exists(self._fname):
            os.remove(self._fname)

    def summarise(self, num: int) -> None:
        """Generate summary stats for conversions."""
        lines = "\n".join(self.get(num))
        size_regex = re.compile(r":(\d+):(\d+)$", re.M)

        tot_o = tot_c = 0
        for original, converted in size_regex.findall(lines):
            tot_o += int(original)
            tot_c += int(converted)

        if tot_o:
            rel_size = round(tot_c * 100 / tot_o)
            self.log("-- Batch of %d: %d%% of original size %sB -> %sB" % (num, rel_size, size(tot_o), size(tot_c)))
        else:
            click.echo("summary not written")


class Video:
    __slots__ = ("path", "converted", "force", "conv_path")

    def __init__(self, path: Path, force: bool) -> None:
        self.path = path
        self.converted = 0
        self.force = force

        conv_name = self.path.name
        self.conv_path = self.path.parent / "converted" / conv_name

    @property
    def size(self) -> int:
        return self.path.stat().st_size

    def __repr__(self) -> str:
        return f"<{self.path.name} {size(self.size)}B>"

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Video):
            return os.path.samestat(os.stat(self.path), os.stat(other.path))
        if isinstance(other, Path):
            return os.path.samestat(os.stat(self.path), os.stat(other))
        return NotImplemented

    def __gt__(self, other: Any) -> bool:
        if isinstance(other, Video):
            return str(self) > str(other)
        return NotImplemented


class VideoPath(os.PathLike):
    __slots__ = ("path", "codec", "exts", "force", "rem")

    def __init__(self, path: str, codec: str, ext: str, force: bool = False, rem: bool = False) -> None:

        self.path = Path(path)
        self.codec = codec
        self.force = force
        self.rem = rem
        self.exts = [x.replace(".", "") for x in ext.split(",") if x]

        self.videos = sorted(
            [Video(self.path, self.force)]
            if self.path.is_file()
            else [Video(z, self.force) for y in self.exts for z in self.path.glob("*." + y)]
        )

    def __iter__(self) -> Iterator[Video]:
        return iter(self.videos)

    def __fspath__(self) -> str:
        return str(self.path)

    __repr__ = __fspath__


def convert_files(vids: VideoPath, logger: Logger, dbl_force: bool) -> None:
    """Convert file in VideoPath object."""
    # top = vids if vids.path.is_dir() else vids.path.parent
    n_proc = 0

    n_vids = len(vids.videos)
    counter = 1

    # click.echo(f"output directory: {vids.conv_path}")

    if vids.path.is_dir():
        top = vids.path
        click.echo(f"\n{n_vids} file(s) found:")
        for vid in vids:
            click.secho(str(vid), fg="yellow")
    else:
        top = vids.path.parent

    if vids.force and not dbl_force and not click.confirm(f"convert {n_vids} files?"):
        sys.exit()

    logger.log(f"CONVERTING FILES IN {top}")
    for vid in vids:
        if not vids.force:
            click.echo()

        try:
            success = convert_video(vids.codec, vid, counter, n_vids)
        except KeyboardInterrupt:
            print("KI")
            success = False

        counter += 1
        if not success:
            continue

        logger.log(vid.path.name, vid.size, vid.converted)
        n_proc += 1

        if vids.rem:
            click.echo(f"removing {vid.path}")
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
            click.echo(f"see {logger} for more details")
    else:
        logger.reset()
        click.echo(f"\nNO VIDEO FILES CONVERTED IN {top}")


def convert_video(codec: str, vid: Video, counter: int, nvid: int) -> bool:
    """Use ffmpeg to convert Video object."""

    prompt = (
        click.style(str(vid.path), fg="yellow")
        + " -> "
        + click.style(str(vid.conv_path.parent / vid.conv_path.name), fg="green")
        + "\ncontinue?"
    )

    if vid.force or click.confirm(prompt):
        os.makedirs(vid.conv_path.parent, exist_ok=True)

        stream = ffmpeg.input(str(vid.path))
        stream = ffmpeg.output(stream, str(vid.conv_path), vcodec=codec, crf=24, acodec="copy", preset="veryfast")

        click.echo(f"[{counter}/{nvid}] converting {vid.path}...", nl=False)

        with spin.spinner():
            try:
                err, out = ffmpeg.run(stream, overwrite_output=True, quiet=True)
            except KeyboardInterrupt:
                # check for dbl force and offer quit
                click.echo("\baborted")
                os.remove(vid.conv_path)
                vid.conv_path.parent.rmdir()  # only removes if empty
                # add quit option afer ctrl-c
                return False
            except ffmpeg.Error as e:
                click.echo("\bffmpeg error:")
                click.echo("-" * 10)
                click.echo(b"\n".join(e.stderr.splitlines()[-5:]))
                click.echo("-" * 10)
                return False

        click.echo(click.style("done", fg="green"))
        vid.converted = vid.conv_path.stat().st_size
        return True

    return False


def get_codec() -> str:
    codecs = subprocess.run(["ffmpeg", "-codecs"], stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout

    i = 0
    for line in codecs.splitlines():
        # check the codecs exist and have the encoding ability
        if not i and b"264" in line and b"E" in line[:3]:
            i = 1
        elif b"265" in line and b"E" in line[:3]:
            i = 2
            break

    return ["", "libx264", "libx265"][i]


def get_exts() -> str:
    fformats = subprocess.run(["ffmpeg", "-demuxers"], stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout
    exts: List[str] = []
    for line in fformats.splitlines()[4:]:
        parts = line.decode().split()
        exts.extend(parts[1].split(","))
    return ",".join(exts)


@click.command()
@click.argument("path", default=".", type=click.Path(exists=True))
@click.option("-e", "--ext", default=get_exts(), help="Comma seperated list of file extension(s) to look for")
@click.option(
    "-y", "--force", count=True, help="A single count disables per-video prompts. A count of 2 disables all prompts."
)
@click.option("-d", "--rem", is_flag=True, help="Delete source video files")
@click.version_option()
def main(path: str, ext: str, force: int, rem: bool) -> None:
    """Convert video(s) in specified path."""

    # look for ffmpeg
    click.echo("Checking ffmpeg support...", nl=False)
    if not which("ffmpeg"):
        click.echo("\nERROR: ffmpeg is either not installed or not in PATH")
        sys.exit()
    click.echo("ok")

    codec = get_codec()
    if not codec:
        click.echo("ERROR: ffmpeg installation supports neither H.264 nor H.265 encoding")
        sys.exit()

    click.echo("codec: ", nl=False)
    click.secho(codec, fg="green")
    click.echo(f"looking for videos at '{path}'")

    vp = VideoPath(path, codec, ext=ext, force=bool(force), rem=rem)

    # start conversion
    logger = Logger("stats.txt")
    convert_files(vp, logger, force > 1)

    if not force > 1:
        if click.confirm("view log?"):
            click.edit(filename=str(logger))

    click.echo()


if __name__ == "__main__":
    main()
