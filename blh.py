from queue import Queue
from threading import Thread
from typing import Any
from logging import Logger
import json
import os

try:
    from utils.rtext import RText, RColor, RAction, RStyle, RTextList
    from plugins.wsBlhLib.WebsocketBlh import BlhThread
    from plugins.wsBlhLib.mcdrPluginLib import *
except ImportError:
    pass

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


def get_text(text, mous='', cickrun='', color=RColor.white, run=True):
    if mous != '':
        if cickrun != '':
            if run:
                stxt = RText(text, color=color).set_hover_text(
                    mous).set_click_event(RAction.run_command, cickrun)
            else:
                stxt = RText(text, color=color).set_hover_text(
                    mous).set_click_event(RAction.suggest_command, cickrun)
        else:
            stxt = RText(text, color=color,
                         styles=RStyle.italic).set_hover_text(mous)
    else:
        if cickrun == '':
            stxt = RText(text, color=color)
        else:
            if run:
                stxt = RText(text, color=color).set_click_event(
                    RAction.run_command, cickrun)
            else:
                stxt = RText(text, color=color).set_click_event(
                    RAction.suggest_command, cickrun)
    return stxt


class HelpMessages:
    def __init__(self, Prefix):
        self.easycmds = RTextList(
            get_text('§e------------§bBlh帮助§e------------\n   '),
            get_text(f'§7{Prefix} add [名称] [房间号]', '§b添加一个房间', f'{Prefix} add ', run=False),
            get_text(' §r§b添加房间\n   '),
            get_text(f'§7{Prefix} rm [名称]', '§b删除房间', f'{Prefix} rm ', run=False),
            get_text(' §r§b删除房间\n   '),
            get_text(f'§7{Prefix} start [名称]', '§b启动一个在配置文件里的房间', f'{Prefix} start ', run=False),
            get_text(' §r§b订阅房间\n   '),
            get_text(f'§7{Prefix} stop [名称]', '§b停止一个正在运行的房间', f'{Prefix} stop ', run=False),
            get_text(' §r§b取消订阅\n   '),
            get_text(f'§7{Prefix} list', '§b列出房间', f'{Prefix} list'),
            get_text(' §r§b列出所有\n   '),
            get_text(f'§7{Prefix} stopall', '§b停止所有房间', f'{Prefix} stopall'),
            get_text(' §r§b停止所有\n   '),
            get_text(f'§7{Prefix} startall', '§b启动所有开播的房间', f'{Prefix} startall'),
            get_text(' §r§b启动所有\n   '),
            get_text(f'§7{Prefix} listrun', '§b列出正在运行的房间', f'{Prefix} listrun'),
            get_text(' §r§b列出房间\n'),
            get_text(f'§7   {Prefix} reload', '§b重载插件', f'{Prefix} reload'),
            get_text(' §r§b重载插件'),
        )


class BlhControl(Thread):
    def __init__(self, server, logger: Logger):
        super(BlhControl, self).__init__()
        self.server = server
        self.logger = logger
        self.name = "BlhMainThread"
        self.daemon = True
        self.run_flag = False
        self.config = {}
        self.rooms = {}
        self.roomThreads = {}
        self.infoQueue = Queue(100)
        self.reloadThreads()
        self.reloadConfig()
        self.helpMsg = HelpMessages(self.config["CMD_PREFIX"])
        self.logger.info("Blh 初始化完毕")

    def reloadSelfPlugin(self):
        self.stopAll()
        self.stop()
        self.server.load_plugin(os.path.basename(__file__))

    def reloadThreads(self):
        self.reloadConfig()
        for room, roomId in self.config["ROOMS"].items():
            try:
                state = self.roomThreads[room].stopped
                if state:
                    self.roomThreads[room] = BlhThread(roomId, self.logger, True, self.server,
                                                       head=self.config["LOGGER_HEAD"])
            except KeyError:
                self.roomThreads[room] = BlhThread(roomId, self.logger, True, self.server,
                                                   head=self.config["LOGGER_HEAD"])

    def reloadConfig(self):
        self.config = readConfig(config_file)
        for name, roomId in self.config["ROOMS"].items():
            self.rooms[name] = roomId

    def serverSay(self, message, info=None, tell=False, reply=False):
        if info is None:
            self.server.say("§6[§2{}§6]§r".format(self.config["LOGGER_HEAD"]) + message)
        elif tell:
            self.server.tell(info.player, "§6[§2{}§6]§r".format(self.config["LOGGER_HEAD"]) + message)
        elif reply:
            self.server.reply(info, "§6[§2{}§6]§r".format(self.config["LOGGER_HEAD"]) + message)

    def parse_cmd(self, info):
        cmd = info.content.split(' ')[1:len(info.content.split(' '))]
        if len(cmd) == 0:
            if info.is_player:
                self.server.tell(info.player, self.helpMsg.easycmds.to_json_object())
        elif len(cmd) == 1:
            if cmd[0] == "stopall":
                self.serverSay("停止了所有正在运行的房间", info=info, reply=True)
                self.stopAll()
            if cmd[0] == "startall":
                self.serverSay("启动了所有已开播的房间", info=info, reply=True)
                self.startAll()
            if cmd[0] == "listrun":
                self.serverSay("有以下房间正在运行: ", info=info, reply=True)
                for name, thread in self.roomThreads.items():
                    if thread.run_flag:
                        self.server.say("   -{}".format(name), info=info, reply=True)
            if cmd[0] == "reload":
                self.serverSay("正在重载...")
                self.reloadSelfPlugin()
            if cmd[0] == "list":
                self.serverSay("配置文件中有以下房间:", info=info, reply=True)
                for name, roomId in self.config["ROOMS"].items():
                    self.serverSay(f"    -{name}: {roomId}, "
                                   f"状态: {self.roomThreads[name].getState()}",
                                   info=info, reply=True)
        elif len(cmd) == 2:
            if cmd[0] == "rm":
                self.serverSay(self.remove(cmd[1]), info=info, reply=True)
            if cmd[0] == "start":
                if cmd[1] == "all":
                    self.serverSay("启动了所有已开播的房间", info=info, reply=True)
                    self.startAll()
                    return
                self.serverSay("房间 {} 正在启动".format(cmd[1]), info=info, reply=True)
                self.startSingleRoomThread(cmd[1])
            if cmd[0] == "stop":
                if cmd[1] == "all":
                    self.serverSay("停止了所有正在运行的房间", info=info, reply=True)
                    self.stopAll()
                    return
                self.serverSay("房间 {} 正在停止".format(cmd[1]), info=info, reply=True)
                self.stopSingleThread(cmd[1])
        elif len(cmd) == 3:
            if cmd[0] == "add":
                self.serverSay(self.add(cmd[1], cmd[2]), info=info, reply=True)

    def addInfo(self, cmd):
        self.infoQueue.put(cmd)

    def add(self, name: str, roomId: int):
        for key in self.rooms.keys():
            if key == name:
                return "[§4失败, 原因§r]: §e房间已存在"
        roomId = int(roomId)
        d = readConfig(config_file)
        self.rooms[name] = roomId
        d["ROOMS"] = self.rooms
        writeConfig(config_file, d)
        self.reloadThreads()
        return "§2房间 {}: {} 添加成功".format(name, roomId)

    def remove(self, name: str):
        try:
            del self.rooms[name]
            self.roomThreads[name].stop()
            del self.roomThreads[name]
        except AttributeError:
            return "[§4失败, 原因§r]: §e房间不存在"
        writeKey(config_file, "ROOMS", self.rooms)
        return "§2房间 {} 删除成功".format(name)

    def startSingleRoomThread(self, name):
        self.reloadThreads()
        if not self.roomThreads[name].run_flag:
            self.roomThreads[name].start()

    def stopSingleThread(self, name):
        self.reloadThreads()
        if self.roomThreads[name].run_flag:
            self.roomThreads[name].stop()

    def startAll(self):
        self.reloadThreads()
        for thread in self.roomThreads.values():
            if thread.room.live_status:
                thread.start()

    def stopAll(self):
        for thread in self.roomThreads.values():
            if thread.run_flag:
                thread.stop()
        self.reloadThreads()

    def start(self) -> None:
        self.run_flag = True
        super(BlhControl, self).start()

    def stop(self):
        self.stopAll()
        self.run_flag = False

    def run(self) -> None:
        while self.run_flag:
            if len(self.infoQueue.queue) > 0:
                self.parse_cmd(self.infoQueue.get())


blhMain = None
blhMain: BlhControl


def reloadBlhMainThread(server):
    global blhMain
    if blhMain is not None:
        blhMain.stop()
    blhMain = BlhControl(server, server.logger)
    blhMain.start()


def on_load(server, old):
    global config
    config = readConfig(config_file)
    if hasattr(old, "blhMain"):
        if old.blhMain is not None:
            old.blhMain.stop()
    reloadBlhMainThread(server)


def on_unload(server):
    global blhMain
    if blhMain is not None:
        blhMain.stop()
        blhMain.join()


def on_mcdr_stop(server):
    global blhMain
    if blhMain is not None:
        blhMain.stop()
        blhMain.join()


def on_info(server, info):
    global blhMain, config
    config = readConfig(config_file)
    if info.content.startswith(config["CMD_PREFIX"]):
        if blhMain is not None:
            blhMain.addInfo(info)
