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

import os
import sys

from ytsearch import Searcher
from mpvrpc import MPV, TMUX_SESSION

def main():
    user_search = ' '.join(sys.argv[1:])
    result = Searcher.search(user_search)

    if result is None:
        sys.exit("No result found.")

    with MPV() as m:
        player_connected = m.connect_player()
        if player_connected:
            m.append_to_playlist(result)
        else:
            m.spawn_new_player()
            m.append_to_playlist(result)

    replace_with_tmux()

def replace_with_tmux():
    """
    attach tmux and replace current process
    """
    tmux_invocation = [
        "tmux",
        "attach",
        "-t" + TMUX_SESSION
    ]
    os.execvp(tmux_invocation[0], tmux_invocation)

if __name__ == "__main__":
    main()
