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
            "--idle",
            "--input-ipc-server=" + SOCKET_NAME,
        ]
        # start tmux with mpv and wait until ready
        os.spawnvp(os.P_WAIT, tmux_invocation[0], tmux_invocation)
        while not self.connect_player():
                sleep(0.1)

    def append_to_playlist(self, result):
        result_msg = self.prettify_result(result)
        MPV_Message(self.s).loadfile(result.location, "append-play", "term-playing-msg=\"{}\"".format(result_msg))
        MPV_Message(self.s).print_text("Added to playlist: {}".format(result_msg))

    def prettify_result(self, result):
        if result.artist is None:
            return "'{}'".format(result.name)
        return "'{}' by '{}'".format(result.name, result.artist)

class MPV_Message:
    def __init__(self, s):
        self.s = s
    
    def __getattr__(self, command):
        def recieve():
            # Warning: may steal reponses of another process
            # May throw up hands if the reponse is not a single result json
            response = bytearray()
            while response.find(b'\n') < 0:
                response.extend(self.s.recv(16))
            result_bytes, _, _ = response.partition(b'\n')
            result = json.loads(result_bytes)
            # swallow anything that is not a result
            if not "error" in result:
                return recieve()
            return result["error"] == 'success'
        def send(*param):
            command_hyphenated = command.replace('_', '-')
            cmd = MPV_Message._construct_command(self, command_hyphenated, *param, request_id=None)
            self.s.sendall(cmd.encode())
            return recieve()

        return send

    @staticmethod
    def _construct_command(self, *args, request_id):
        message = {"command": args}
        if request_id:
            message["request_id"] = request_id
        return json.dumps(message) + "\n"
