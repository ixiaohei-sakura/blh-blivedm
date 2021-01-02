from .constants import *
import requests
import json


class LiveRoomObject(object):
    class RoomNotExist(Exception):
        pass

    class Error(Exception):
        pass

    def __init__(self, roomId, logger):
        self.roomId = roomId
        self.logger = logger
        self.roomUrl = "https://live.bilibili.com/" + str(roomId)
        self.roomDataUrl = URLs.roomDataUrl + "?id=" + str(roomId)
        self.roomWsUrl = URLs.apiUrl

        self.shortId = roomId
        self.members = [attr for attr in dir(self) if not callable(getattr(self, attr)) and not attr.startswith("__")]
        self.uid = -1
        self.liveRoomCode = -1
        self.msg = ""
        self.need_p2p = False
        self.is_hidden = False
        self.is_locked = False
        self.is_portrait = False
        self.encrypted = False
        self.pwd_verified = False
        self.non_existent = False
        self.live_status = False
        self.special_type = False
        self.hidden_till = None
        self.lock_till = None
        self.live_time = None
        self.live_start_time = None
        self.error = None
        self.error_code = None
        self.updateData()

    def updateData(self):
        try:
            result = requests.get(self.roomDataUrl)
        except Exception as exc:
            self.error = exc
            return self.error
        if result.status_code == 200:
            if json.loads(str(result.content, encoding='utf-8'))["msg"] == "房间不存在":
                self.error_code = json.loads(str(result.content, encoding='utf-8'))["code"]
                self.error = self.RoomNotExist(json.loads(str(result.content, encoding='utf-8'))["msg"])
                self.non_existent = True
                return self.error
            elif json.loads(str(result.content, encoding='utf-8'))["msg"] != "ok":
                self.error_code = json.loads(str(result.content, encoding='utf-8'))["code"]
                self.error = self.Error(json.loads(str(result.content, encoding='utf-8'))["msg"])
            result = json.loads(str(result.content, encoding="utf-8"))
            self.need_p2p = False if result["data"]["need_p2p"] == 0 else True
            self.is_hidden = False if result["data"]["is_hidden"] == 0 else True
            self.is_locked = False if result["data"]["is_locked"] == 0 else True
            self.is_portrait = False if result["data"]["is_portrait"] == 0 else True
            self.encrypted = False if result["data"]["encrypted"] == 0 else True
            self.pwd_verified = False if result["data"]["pwd_verified"] == 0 else True
            self.live_status = False if result["data"]["live_status"] == 0 else True
            self.special_type = False if result["data"]["special_type"] == 0 else True
            self.hidden_till = result["data"]["hidden_till"]
            self.lock_till = result["data"]["lock_till"]
            self.live_time = result["data"]["live_time"]
            self.shortId = result["data"]["short_id"]
            self.uid = result["data"]["uid"]
            self.live_start_time = self.live_time
            self.logger.info("房间信息成功更新")
        else:
            self.error_code = result.status_code
