import setuptools

from pyvid import __version__

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='pyvid',
    version=__version__,
    py_modules=['pyvid'],
    author='jdxt',
    author_email='jytrn@protonmail.com',
    description='Video conversion utility',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/0jdxt/pyvid',
    install_requires=['click', 'hurry.filesize', 'ffmpeg-python', 'click-spinner'],
    packages=setuptools.find_packages(),
    entry_points='[console_scripts]\npyvid=pyvid:main'
)
