# canito

A cli music streaming tool.

Canito is very brittle, will likely not work as expected yet, and subject to change.

## Usage

Run `./canito.py name of the song`.
The tool searches for that song on Youtube, trying to find uploads made by Youtube itself.
It then spawns an instance of mpv to play the found song, or – if already running – adds it to the playlist.

## Dependencies

Canito is written in Python 3.
You need to have both [mpv](https://mpv.io) and [youtube-dl](https://rg3.github.io/youtube-dl/) in your path.
Youtube-dl needs to be installed as a python library.