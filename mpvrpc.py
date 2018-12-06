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

SOCKET_NAME = "/tmp/canito.socket"

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

    def spawn_new_player(self, mpv_file):
        """
        Replaces this process with an mpv process playing the given file.
        """
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
    
    def append_to_playlist(self, mpv_file):
        MPV_Message(self.s).loadfile(mpv_file, "append-play")

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