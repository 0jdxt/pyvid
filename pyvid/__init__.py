import os
from typing import List, Tuple

import ffmpeg
import click
import click_spinner as spin

from pyvid.classes import Logger, Video, VideoPath


__version__ = '0.1.0'

@click.command()
@click.argument('folder', type=click.Path(exists=True))
@click.option('-e', '--ext', help='File extension to look for')
# @click.option('-a', '--all', help='Convert all matching files')
@click.option('-y', '--force', is_flag=True, help='Disable convert prompt')
@click.option('-d', '--rem', is_flag=True, help='Delete source video file(s)')
@click.version_option()
def main(folder:str, ext:str, force:bool, rem:bool) -> None:
    if ext:
        click.echo(f'extension: {ext}')

    logger = Logger('stats.txt')

    vp = VideoPath(folder, ext=ext, force=force, rem=rem)
    convert_files(vp, logger)


def convert_files(vids: VideoPath, logger: Logger) -> None:
    top = vids if vids.is_dir() else vids.parent
    n_proc = 0

    for vid in vids:
        click.echo()
        if n_proc == 0:
            logger.log(f'CONVERTING FILES IN {top}')

        success, code = convert_video(vid)

        if not success:
            if code:
                break
            continue

        logger.log(vid.path.name, vid.size, vid.converted)
        n_proc += 1

        if vids.rem:
            os.remove(vid)

    if n_proc:
        logger.summarise(n_proc)
        max_lines = 3
        click.echo()
        if n_proc > max_lines:
            click.echo('...')
        n_lines = max_lines if n_proc > max_lines else n_proc + 1
        click.echo(''.join(logger.get(n_lines)))
        if n_proc > max_lines:
            click.echo(f'see {logger.fname} for more details')
    else:
        logger.reset()
        click.echo(f'NO VIDEO FILES CONVERTED IN {top}')


def convert_video(vid: Video) -> Tuple[bool, int]:
        prompt = click.style(str(vid.path), fg='yellow')
        prompt += ' -> '
        prompt += click.style(str(vid.conv_path.parent), fg='green') + '\\'
        prompt += click.style(vid.conv_path.name, fg='yellow') + '\n'
        prompt += 'continue? (y)es/(n)o/(c)ancel all'
        click.echo(prompt)

        opt = 'y' if vid.force else click.getchar()
        if opt == 'y':
            os.makedirs(vid.conv_path.parent, exist_ok=True)

            stream = ffmpeg.input(str(vid.path))
            stream = ffmpeg.output(
                stream,
                str(vid.conv_path),
                vcodec='libx264',
                crf=20,
                acodec='copy',
                preset='veryfast')

            click.echo(f'converting {vid.path}...', nl=False)
            try:
                with spin.spinner():
                    err, out = ffmpeg.run(stream, quiet=True, overwrite_output=True)
            except KeyboardInterrupt:
                click.echo('aborted')
                os.remove(vid.conv_path)
                vid.conv_path.parent.rmdir()
                return False, 0
            except FileNotFoundError:
                raise OSError('ffmpeg is either not installed or not in PATH')

            click.echo('done')
            vid.converted = vid.conv_path.stat().st_size
            return True, 0

        if opt == 'c':
            return False, 1
        # default [n]
        return False, 0
