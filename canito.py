#!/usr/bin/env python3

# Copyright 2018 goppacode (Michael Rosenthal)
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

import socket
import sys
import os

from ytsearch import Searcher

SOCKET_NAME = "/tmp/canito.socket"

def main():
    user_search = ' '.join(sys.argv[1:])
    url = Searcher.search(user_search)

    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
        player_connected = connect_player(s)
        if player_connected:
            print("Adding {} to the playlist.".format(user_search))
            append_to_playlist(s, url)
        else:
            spawn_new_player(url)

def append_to_playlist(s, mpv_file):
    mpv_command = 'loadfile "{}" append-play\n'.format(mpv_file)
    s.sendall(mpv_command.encode())

def spawn_new_player(mpv_file):
    mpv_invocation = [
        "mpv",
        mpv_file,
        "--no-video",
        "--term-playing-msg='${media-title}'",
        "--keep-open=yes",
        "--input-ipc-server={}".format(SOCKET_NAME)
    ]
    # start mpv and replace this current process
    os.execvp(mpv_invocation[0], mpv_invocation)

def connect_player(s):
    try:
        s.connect(SOCKET_NAME)
        return True
    except FileNotFoundError:
        return False
    except ConnectionRefusedError:
        return False

if __name__ == "__main__":
    main()