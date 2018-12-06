# canito

A cli music streaming tool.

Canito is very brittle, will likely not work as expected yet, and subject to change.

## Usage

Run `./canito.py name of the song`.
The tool searches for that song on Youtube, trying to find uploads made by Youtube itself.
It then starts a tmux session with mpv playing the file, or – if already running – adds it to the playlist.

## Dependencies

Canito is written in Python 3. You need the [youtube-dl][1] python library
and [mpv][2], [youtube-dl][1] and [tmux][3] in your path.

[1]: https://rg3.github.io/youtube-dl/
[2]: https://mpv.io
[3]: https://tmux.github.io/
