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

import json
import os
import socket
from time import sleep

SOCKET_NAME = "/tmp/canito.socket"
TMUX_SESSION = "canito"

class MPV:

    def __enter__(self):
        self.s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        return self

    def __exit__(self, *args):
        self.s.__exit__(*args)

    def connect_player(self):
        try:
            self.s.connect(SOCKET_NAME)
            return True
        except FileNotFoundError:
            return False
        except ConnectionRefusedError:
            return False

    def spawn_new_player(self):
        """
        Start a tmux session with mpv running and connect to the socket
        """
        tmux_invocation = [
            "tmux",
            "new-session",
            "-s" + TMUX_SESSION,
            "-d",
            "mpv",
            "--no-video",
            "--term-playing-msg='${media-title}'",
            "--idle",
            "--input-ipc-server=" + SOCKET_NAME,
        ]
        # start tmux with mpv and wait until ready
        os.spawnvp(os.P_WAIT, tmux_invocation[0], tmux_invocation)
        while not self.connect_player():
                sleep(0.1)

    def append_to_playlist(self, result):
        MPV_Message(self.s).loadfile(result.location, "append-play")

class MPV_Message:
    def __init__(self, s):
        self.s = s
    
    def __getattr__(self, command):
        def send(*param, request_id=None):
            cmd = MPV_Message._construct_command(self, command, *param, request_id=request_id)
            self.s.sendall(cmd.encode())
        return send

    @staticmethod
    def _construct_command(self, *args, request_id):
        message = {"command": args}
        if request_id:
            message["request_id"] = request_id
        return json.dumps(message) + "\n"
