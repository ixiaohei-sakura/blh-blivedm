from .constants import *
from .liveRoom import LiveRoomObject
import json


class Pack(object):
    def __init__(self, data, operation):
        self.body = json.dumps(data).encode('utf-8')
        self.header = HEADER_STRUCT.pack(
            HEADER_STRUCT.size + len(self.body),
            HEADER_STRUCT.size,
            1,
            operation,
            1
        )
        self.data = self.header + self.body

    def getData(self):
        return self.data


class AuthPack(Pack):
    def __init__(self, room: LiveRoomObject):
        self.data = {"uid": 0, "roomid": room.roomId, "protover": 1, "platform": "web", "clientver": "1.4.0"}
        super(AuthPack, self).__init__(self.data, Operation.AUTH)
