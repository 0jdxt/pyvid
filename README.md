# pyvid 0.1.2

[![PyPI version](https://badge.fury.io/py/pyvid.svg)](https://badge.fury.io/py/pyvid)
[![Build Status](https://travis-ci.org/0jdxt/pyvid.svg?branch=master)](https://travis-ci.org/0jdxt/pyvid)
[![Documentation Status](https://readthedocs.org/projects/pyvid/badge/?version=latest)](https://pyvid.readthedocs.io/en/latest/?badge=latest)
[![Coverage Status](https://coveralls.io/repos/github/0jdxt/pyvid/badge.svg?branch=master)](https://coveralls.io/github/0jdxt/pyvid?branch=master)


Pyvid is a package that shrinks video files using defaults on ffmpeg to get high quality and low file size. Works best on 1080p videos.

## Dependencies

- [install](https://www.ffmpeg.org/download.html)
  ffmpeg with libx264 or libx265 support and make sure the executable can be found with the `$PATH` environment variable.

## Installation

Install as global executable

```
pip install --user pyvid
```

## Usage

The most basic usage is as follows:

```
pyvid PATH
```

where `PATH` is a file or directory. If `PATH` is a directory, it will look for video files. Converted videos are placed in a `converted/` subfolder.

The following

```
pyvid files -e ext1,ext2
```

will convert all `.ext1` and `.ext2` files in directory `files/` to output directory `files/converted/`.

```
Usage: pyvid [OPTIONS] PATH

  Convert video(s) in specified path.

Options:
  -e, --ext TEXT  Comma seperated list of file extension(s) to look for
  -y, --force     A single count disables per-video prompts. A count of 2
                  disables all prompts.
  -d, --rem       Delete source video files
  --version       Show the version and exit.
  --help          Show this message and exit.
```
