from collections import namedtuple
from enum import IntEnum
import struct


HEADER_STRUCT = struct.Struct('>I2H2I')


class Operation(IntEnum):
    HANDSHAKE = 0
    HANDSHAKE_REPLY = 1
    HEARTBEAT = 2
    HEARTBEAT_REPLY = 3
    SEND_MSG = 4
    SEND_MSG_REPLY = 5
    DISCONNECT_REPLY = 6
    AUTH = 7
    AUTH_REPLY = 8
    RAW = 9
    PROTO_READY = 10
    PROTO_FINISH = 11
    CHANGE_ROOM = 12
    CHANGE_ROOM_REPLY = 13
    REGISTER = 14
    REGISTER_REPLY = 15
    UNREGISTER = 16
    UNREGISTER_REPLY = 17
    WS_BODY_PROTOCOL_VERSION_NORMAL = 0
    WS_BODY_PROTOCOL_VERSION_INT = 1  # 用于心跳包
    WS_BODY_PROTOCOL_VERSION_DEFLATE = 2

HeaderTuple = namedtuple('HeaderTuple', ('pack_len', 'raw_header_size', 'ver', 'operation', 'seq_id'))


class URLs:
    roomDataUrl = "https://api.live.bilibili.com/room/v1/Room/room_init"
    apiUrl = "wss://broadcastlv.chat.bilibili.com:2245/sub"
