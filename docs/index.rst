Welcome to pyvid's documentation!
=================================

.. toctree::
    :titlesonly:

Pyvid is a package that shrinks video files using defaults on ffmpeg to get high quality and low file size. Works best on 1080p videos.

Dependencies
^^^^^^^^^^^^

- `install <https://www.ffmpeg.org/download.html>`_
  ffmpeg with libx264 or libx265 support and make sure the executable is in $PATH

Installation
^^^^^^^^^^^^

Install as global executable::

    $ pip install --user pyvid

check installation::

    $ pyvid --version
    pyvid, version 0.1.1


Usage
^^^^^

The most basic usage is as follows::

    $ pyvid PATH

where PATH is a file or directory. If PATH is a directory, it will look for video files. Converted videos are placed in a `converted/` subfolder.

The following::

    $ pyvid files -e ext1,ext2

will convert all `.ext1` and `.ext2` files in directory `files/` to output directory `files/converted/`.

.. click:: pyvid:main
    :prog: pyvid
    :show-nested:

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
