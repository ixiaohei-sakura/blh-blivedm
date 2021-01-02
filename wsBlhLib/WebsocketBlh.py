import time
import zlib
from wsBlhLib.network import NetworkingThread
from wsBlhLib.logger import Logger
from wsBlhLib.thread_rewrite import stop_thread
from wsBlhLib.messages import *
from wsBlhLib.packs import *
from threading import Thread


class BlhThread(Thread):
    _COMMAND_HANDLERS = {
        # 收到弹幕
        'DANMU_MSG': lambda client, command: client.on_receive_chat(
            ChatMessage.from_command(command['info'])
        ),
        # 有人送礼
        'SEND_GIFT': lambda client, command: client.on_receive_gift(
            GiftMessage.from_command(command['data'])
        ),
        # 有人上舰
        'GUARD_BUY': lambda client, command: client.on_buy_guard(
            GuardBuyMessage.from_command(command['data'])
        ),
        # 醒目留言
        'SUPER_CHAT_MESSAGE': lambda client, command: client.on_super_chat(
            SuperChatMessage.from_command(command['data'])
        ),
        # 删除醒目留言
        'SUPER_CHAT_MESSAGE_DELETE': lambda client, command: client.on_super_chat_delete(
            SuperChatDeleteMessage.from_command(command['data'])
        )
    }
    # 其他常见命令
    for cmd in (
            'INTERACT_WORD', 'ROOM_BANNER', 'ROOM_REAL_TIME_MESSAGE_UPDATE', 'NOTICE_MSG', 'COMBO_SEND',
            'COMBO_END', 'ENTRY_EFFECT', 'WELCOME_GUARD', 'WELCOME', 'ROOM_RANK', 'ACTIVITY_BANNER_UPDATE_V2',
            'PANEL', 'SUPER_CHAT_MESSAGE_JPN', 'USER_TOAST_MSG', 'ROOM_BLOCK_MSG', 'LIVE', 'PREPARING',
            'room_admin_entrance', 'ROOM_ADMINS', 'ROOM_CHANGE', 'ONLINE_RANK_V2', 'LIVE_INTERACTIVE_GAME',
            'WIDGET_BANNER', 'ONLINE_RANK_COUNT', 'ANCHOR_LOT_END', 'ANCHOR_LOT_AWARD', 'ANCHOR_LOT_START',
    ):
        _COMMAND_HANDLERS[cmd] = None
    del cmd

    def __init__(self, roomId, logger: Logger, inMCDR=False, mcdr_server=None):
        super(BlhThread, self).__init__()
        self.popularity = -1
        self.daemon = True
        self.run_flag = False
        self.name = "BlhThread %d" % roomId
        self.logger = logger
        self.room = LiveRoomObject(roomId, self.logger)
        self.networkingThread = NetworkingThread(self, self.logger, self._handle_message)
        self.inMCDR = inMCDR
        self.old_popularity = -1
        self.old_popularity_str = ""
        self.running = False
        self.stopped = True
        if inMCDR:
            self.MCDR_chat = MCDRChat(self.logger, mcdr_server)

    def start(self) -> None:
        self.run_flag = True
        self.room.updateData()
        self.logger.info("BlhThread 启动, 房间地址: {0}, 状态: {1}".format(self.room.roomUrl,
                                                             "直播中" if self.room.live_status else "未开播"))
        self.networkingThread.connect()
        super().start()

    def stop(self, force=False):
        if force and self.is_alive():
            stop_thread(self, SystemExit)
        else:
            self.run_flag = False
            self.networkingThread.close()

    def run(self):
        self.stopped = False
        self.running = True
        self.logger.debug("事件循环开始")
        self.networkingThread.send_pack(AuthPack(self.room))
        while self.run_flag:
            time.sleep(0.1)
        self.logger.info("事件循环结束")
        self.running = False
        self.stopped = True

    def getState(self):
        self.room.updateData()
        return "直播中" if self.room.live_status else "未开播"

    def _handle_message(self, data):
        offset = 0
        while offset < len(data):
            try:
                header = HeaderTuple(*HEADER_STRUCT.unpack_from(data, offset))
            except struct.error:
                break
            if header.operation == Operation.HEARTBEAT_REPLY:
                popularity = int.from_bytes(data[offset + HEADER_STRUCT.size:
                                                 offset + HEADER_STRUCT.size + 4],
                                            'big')
                self.on_receive_popularity(popularity)
            elif header.operation == Operation.SEND_MSG_REPLY:
                body = data[offset + HEADER_STRUCT.size: offset + header.pack_len]
                if header.ver == Operation.WS_BODY_PROTOCOL_VERSION_DEFLATE:
                    body = zlib.decompress(body)
                    self._handle_message(body)
                else:
                    try:
                        body = json.loads(body.decode('utf-8'))
                        self._handle_command(body)
                    except BaseException:
                        self.logger.error('body: %s', body)
                        raise

            elif header.operation == Operation.AUTH_REPLY:
                self.networkingThread.send_pack(Pack({}, Operation.HEARTBEAT))
            else:
                body = data[offset + HEADER_STRUCT.size: offset + header.pack_len]
                self.logger.warning('room %d 未知包类型：operation=%d %s%s', self.room.roomId,
                                    header.operation, header, body)
            offset += header.pack_len

    def _handle_command(self, command):
        if isinstance(command, list):
            for one_command in command:
                self._handle_command(one_command)
            return

        cmd = command.get('cmd', '')
        pos = cmd.find(':')
        if pos != -1:
            cmd = cmd[:pos]
        if cmd in self._COMMAND_HANDLERS:
            handler = self._COMMAND_HANDLERS[cmd]
            if handler is not None:
                handler(self, command)
        else:
            self.logger.warning('room %d 未知命令：cmd=%s %s', self.room.roomId, cmd, command)
            self._COMMAND_HANDLERS[cmd] = None

    def on_receive_chat(self, chat: ChatMessage):
        if self.inMCDR:
            self.MCDR_chat.on_receive_chat(chat)
        else:
            self.logger.info(f"\033[33m{'[房]' if chat.admin else ''}\033[0m"
                             f"\033[35m[Lv{chat.user_level}]\033[0m"
                             f"[{chat.uname}]: {chat.msg}")

    def on_super_chat(self, chat: SuperChatMessage):
        if self.inMCDR:
            self.MCDR_chat.on_super_chat(chat)
        else:
            self.logger.info(f"\033[35m[Lv{chat.user_level}]\033[0m"
                             f"[{chat.uname}]: {chat.message}")

    def on_super_chat_delete(self, chat: SuperChatDeleteMessage):
        if self.inMCDR:
            self.MCDR_chat.on_super_chat_delete(chat)
        else:
            pass

    def on_receive_gift(self, data: GiftMessage):
        if self.inMCDR:
            self.MCDR_chat.on_receive_gift(data)
        else:
            self.logger.info(f"[{data.uname}]: 送出 {data.gift_name}")

    def on_buy_guard(self, data: GuardBuyMessage):
        if self.inMCDR:
            self.MCDR_chat.on_buy_guard(data)
        else:
            pass

    def on_receive_popularity(self, popularity: int):
        if self.inMCDR:
            self.MCDR_chat.on_receive_popularity(popularity)
        else:
            self.popularity = popularity
            if self.old_popularity != popularity:
                self.old_popularity = popularity
                if self.popularity > 10000:
                    popularity_str = str(round(self.popularity / 10000, 1))
                    if self.old_popularity_str != popularity_str:
                        self.logger.info("人气值: " + popularity_str + "万")
                        self.old_popularity_str = popularity_str
                else:
                    self.logger.info("人气值: " + str(popularity))


class MCDRChat(object):
    def __init__(self, logger, server):
        self.logger = logger
        self.server = server
        self.old_popularity_str = -1
        self.old_popularity = -1
        self.popularity = -1
        self.last_super_message = None
        self.last_chat_message = None
        self.last_buy_guard = None
        self.last_gift = None

    def on_receive_chat(self, chat: ChatMessage):
        # self.logger.info(f"\033[33m{'[房]' if chat.admin else ''}\033[0m"
        #                  f"\033[35m[Lv{chat.user_level}]\033[0m"
        #                  f"\033[36m[{chat.uname}]\033[0m: {chat.msg}")
        pass

    def on_super_chat(self, chat: SuperChatMessage):
        # self.logger.info(f"\033[35m[Lv{chat.user_level}]\033[0m"
        #                  f"\033[36m[{chat.uname}]\033[0m: {chat.message}")
        pass

    def on_receive_gift(self, data: GiftMessage):
        # self.logger.info(f"\033[36m[{data.uname}]\033[0m: 送出 {data.gift_name}")
        pass

    def on_buy_guard(self, data: GuardBuyMessage):
        # self.logger.info(f"\033[36m[{data.username}]\033[0m: \033[31m上了"
        #                  f"{'舰长' if data.guard_level == 3 else '提督' if data.guard_level == 2 else '总督' if data.guard_level == 1 else ''}\033[0m")
        pass

    def on_super_chat_delete(self, chat: SuperChatDeleteMessage):
        pass

    def on_receive_popularity(self, popularity: int):
        # self.popularity = popularity
        # if self.old_popularity != popularity:
        #     self.old_popularity = popularity
        #     if self.popularity > 10000:
        #         popularity_str = str(round(self.popularity / 10000, 1))
        #         if self.old_popularity_str != popularity_str:
        #             self.logger.info("人气值: " + popularity_str + "万")
        #             self.old_popularity_str = popularity_str
        #     else:
        #         self.logger.info("人气值: " + str(popularity))
        pass


if __name__ == '__main__':
    room = 21422412
    head = "BLH"
    logger = Logger(head, str(room))
    logger.setDebug(True)
    blh = BlhThread(room, logger=logger, inMCDR=False)
    blh.start()
    try:
        blh.join()
    except KeyboardInterrupt:
        blh.stop()
        blh.join()
