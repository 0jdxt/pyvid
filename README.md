# pyvid 0.0.9

[![PyPI version](https://badge.fury.io/py/pyvid.svg)](https://badge.fury.io/py/pyvid)
[![Build Status](https://travis-ci.org/0jdxt/pyvid.svg?branch=master)](https://travis-ci.org/0jdxt/pyvid)
[![Documentation Status](https://readthedocs.org/projects/pyvid/badge/?version=latest)](https://pyvid.readthedocs.io/en/latest/?badge=latest)
[![Coverage Status](https://coveralls.io/repos/github/0jdxt/pyvid/badge.svg?branch=master)](https://coveralls.io/github/0jdxt/pyvid?branch=master)

## Dependencies

- [install](https://www.ffmpeg.org/download.html)
  ffmpeg with H.264 encoding (libx264 support) and make sure the executable is in PATH

## Installation

Install as global executable

```
pip install --user pyvid
```

## Usage

The following

```
pyvid files -e avi
```

will convert all `.avi` files in directory `files/` to output directory `files/converted/`

Uses defaults on ffmpeg executable to get high quality and low file size.

```
Usage: pyvid [OPTIONS] PATH

  Convert video(s) in specified path.

Options:
  -e, --ext TEXT  File extension to look for
  -y, --force     Disable convert prompt
  -d, --rem       Delete source video file(s)
  --version       Show the version and exit.
  --help          Show this message and exit.
```
