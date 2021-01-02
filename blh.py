from queue import Queue
from threading import Thread
from typing import Any
from logging import Logger
try:
    from plugins.wsBlhLib.mcdrPluginLib import HelpMessages
    from plugins.wsBlhLib.WebsocketBlh import BlhThread
except ImportError:
    try:
        from .wsBlhLib.mcdrPluginLib import HelpMessages
        from .wsBlhLib.WebsocketBlh import BlhThread
    except ImportError:
        try:
            from wsBlhLib.mcdrPluginLib import HelpMessages
            from wsBlhLib.WebsocketBlh import BlhThread
        except ImportError:
            pass
import json
plugin_dir = "./plugins/"
config_dir = "./plugins/wsBlhLib/configs/"
lib_dir = "./plugins/wsBlhLib/"
config_file = config_dir + "config.json"
config = {}


def readConfig(path: str):
    return json.loads(open(path, "r").read())


def writeConfig(path: str, data):
    open(path, "w").write(json.dumps(data, indent=3))


def getKey(path: str, key: str):
    return readConfig(path)[key]


def writeKey(path: str, key: str, data: Any):
    buff = readConfig(path)
    buff[key] = data
    writeConfig(path, buff)


class BlhControl(Thread):
    def __init__(self, server, logger: Logger):
        super(BlhControl, self).__init__()
        self.name = "BlhMainThread"
        self.daemon = True
        self.infoQueue = Queue(100)
        self.server = server
        self.logger = logger
        self.rooms = {}
        self.roomThreads = {}
        self.run_flag = False
        self.helpMsg = HelpMessages(config["CMD_PREFIX"])
        for room, roomId in config["ROOMS"].items():
            self.roomThreads[room] = BlhThread(roomId, self.logger, True, self.server, head=config["LOGGER_HEAD"])

    def serverSay(self, message):
        self.server.say("§6[§2{}§6]§r".format(config["LOGGER_HEAD"]) + message)

    def parse_cmd(self, info):
        cmd = info.content.split(' ')[1:len(info.content.split(' '))]
        if len(cmd) == 0:
            if info.is_player:
                self.server.tell(info.player, self.helpMsg.easycmds.to_json_object())
        elif len(cmd) == 1:
            if cmd[0] == "stopall":
                self.stopAll()
                self.serverSay("停止了所有正在运行的房间")
            if cmd[0] == "startall":
                self.startAll()
                self.serverSay("启动了所有已开播的房间")
            if cmd[0] == "listrun":
                self.serverSay("有以下房间正在运行: ")
                for name, thread in self.roomThreads.items():
                    if thread.run_flag:
                        self.server.say("   -{}".format(name))
            if cmd[0] == "list":
                self.serverSay("配置文件中有以下房间:")
                for name, room in config["ROOMS"].items():
                    self.server.say(f"   -{name}: {room}")
        elif len(cmd) == 2:
            if cmd[0] == "rm":
                self.remove(cmd[1])
                self.serverSay("房间 {} 删除完毕".format(cmd[1]))
            if cmd[0] == "start":
                self.serverSay("房间 {} 正在启动".format(cmd[1]))
                self.startSingleRoomThread(cmd[1])
            if cmd[0] == "stop":
                self.serverSay("房间 {} 正在停止".format(cmd[1]))
                self.stopSingleThread(cmd[1])
        elif len(cmd) == 3:
            if cmd[0] == "add":
                self.add(cmd[1], cmd[2])
                self.serverSay("房间 {0}-{1} 添加完毕".format(cmd[1], cmd[2]))

    def addInfo(self, cmd):
        self.infoQueue.put(cmd)

    def add(self, name: str, roomId: int):
        for key in self.rooms.keys():
            if key == name:
                return "房间已存在"
        roomId = int(roomId)
        d = readConfig(config_file)
        self.rooms[name] = roomId
        self.roomThreads[name] = BlhThread(roomId, self.logger, True, self.server, head=config["LOGGER_HEAD"])
        d["ROOMS"] = self.rooms
        writeConfig(config_file, d)
        return "完成"

    def remove(self, name: str):
        try:
            del self.rooms[name]
            self.roomThreads[name].stop()
            del self.roomThreads[name]
        except AttributeError:
            return "房间不存在"
        writeKey(config_file, "ROOMS", self.rooms)
        return "完成"

    def startSingleRoomThread(self, name):
        if not self.roomThreads[name].run_flag:
            self.roomThreads[name].start()

    def stopSingleThread(self, name):
        if self.roomThreads[name].run_flag:
            self.roomThreads[name].stop()

    def startAll(self):
        for thread in self.roomThreads.values():
            if thread.room.live_status:
                thread.start()

    def stopAll(self):
        for thread in self.roomThreads.values():
            if thread.run_flag:
                thread.stop()

    def start(self) -> None:
        self.run_flag = True
        super(BlhControl, self).start()

    def stop(self):
        self.run_flag = False

    def run(self) -> None:
        while self.run_flag:
            if len(self.infoQueue.queue) > 0:
                self.parse_cmd(self.infoQueue.get())


blhMain: BlhControl


def on_load(server, old):
    if hasattr(old, "blhMain"):
        old.blhMain.stopAll()
        old.blhMain.stop()
    global config, blhMain
    config = readConfig(config_file)
    blhMain = BlhControl(server, server.logger)
    blhMain.start()


def on_unload(server):
    global blhMain
    blhMain.stop()
    blhMain.join()


def on_mcdr_stop(server):
    global blhMain
    blhMain.stop()
    blhMain.join()


def on_info(server, info):
    global blhMain
    if info.content.startswith(config["CMD_PREFIX"]):
        blhMain.addInfo(info)
