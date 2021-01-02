from websocket import WebSocket, ABNF
from websocket._exceptions import WebSocketConnectionClosedException
from threading import Thread
from queue import Queue
from time import sleep
from .thread_rewrite import stop_thread
from .packs import *
import ssl
ssl._create_default_https_context = ssl._create_unverified_context


class CallBackThread(Thread):
    def __init__(self, room, logger):
        super(CallBackThread, self).__init__()
        self.name = f"{room.roomId}-CallBackThread"
        self.daemon = True
        self.run_flag = False
        self.callBackQueue = Queue(100)
        self.logger = logger

    def start(self) -> None:
        self.run_flag = True
        super().start()

    def stop(self, force=False):
        if force:
            self.callBackQueue = Queue(100)
            stop_thread(self, SystemExit)
            self.run_flag = False
        else:
            self.callBackQueue = Queue(100)
            self.run_flag = False

    def run(self) -> None:
        self.logger.info("回调任务线程启动")
        while self.run_flag:
            if len(self.callBackQueue.queue) > 0:
                self.callBackQueue.get()()
        self.logger.info("回调任务线程停止")
        return None

    def addTask(self, func):
        self.callBackQueue.put(func)


class NetworkingThread(Thread):
    def __init__(self, parent, logger, callBack):
        super(NetworkingThread, self).__init__()
        self.room = parent.room
        self.parent = parent
        self.logger = logger
        self.cb = callBack
        self.daemon = True
        self.name = "{}-NetworkingThread".format(self.room.roomId)
        self.connection = WebSocket(sslopt={"cert_reqs": ssl.CERT_NONE})
        self.callBackThread = CallBackThread(self.room, self.logger)
        self.heartBeatThread = Thread(target=self.heartBeat, daemon=True, name=f"{self.room.roomId}-HeartBeat")
        self.binaryDataQueue = Queue(100)
        self.dataQueue = Queue(100)
        self.run_flag = True

    def stop(self):
        self.run_flag = False

    def connect(self, just_check=False):
        if just_check:
            if not self.connection.connected:
                self.logger.info("ws掉线, 正在重连")
                self.connection = WebSocket(sslopt={"cert_reqs": ssl.CERT_NONE})
                self.connection.connect(self.room.roomWsUrl)
                if self.connection.connected:
                    self.logger.info("ws连接创建, 已连接")
        elif not self.connection.connected:
            self.connection.connect(self.room.roomWsUrl)
            if self.connection.connected:
                self.logger.info("ws连接创建, 已连接")
            self.run_flag = True
            self.start()

    def close(self):
        if self.is_alive() and self.run_flag:
            self.run_flag = False
            self.callBackThread.stop()
            self.join(10)
            self.connection.shutdown()
            self.logger.info("ws连接关闭")

    def send_byte(self, data):
        self.binaryDataQueue.put(data, False)

    def send_pack(self, pack):
        self.binaryDataQueue.put(pack.getData(), False)

    def send(self, data):
        self.dataQueue.put(data, False)

    def heartBeat(self, sec=25):
        per = sec * 2
        self.logger.info("心跳循环开始")
        while self.run_flag:
            for i in range(0, per+1):
                if not self.run_flag:
                    break
                sleep(0.5)
            self.logger.debug("心跳包已发送")
            self.send_pack(Pack({}, Operation.HEARTBEAT))
        self.logger.info("心跳循环结束")
        return None

    def call_back_func(self):
        while True:
            try:
                buff = self.connection.recv()
                self.cb(buff)
                break
            except WebSocketConnectionClosedException:
                self.connect(True)
                continue

    def run(self) -> None:
        self.logger.info("网络线程启动")
        self.heartBeatThread.start()
        self.callBackThread.start()
        while self.run_flag:
            self.connect(True)
            if len(self.dataQueue.queue) > 0:
                buff = self.dataQueue.get()
                self.logger.debug(buff)
                self.connection.send(buff, ABNF.OPCODE_TEXT)
            if len(self.binaryDataQueue.queue) > 0:
                buff = self.binaryDataQueue.get()
                self.logger.debug(buff)
                self.connection.send(buff, ABNF.OPCODE_BINARY)
            self.callBackThread.addTask(self.call_back_func)
        self.logger.info("网络线程已停止")
        return None
