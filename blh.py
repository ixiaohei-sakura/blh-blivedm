from threading import Thread
import json
from typing import Any, Optional

try:
    from wsBlhLib.logger import Logger
except ImportError:
    pass


def readConfig(path: str) -> Optional[dict, list]:
    return json.loads(open(path, "r").read())


def writeConfig(path: str, data: Optional[dict, list]):
    open(path, "w").write(json.dumps(data, indent=3))


def writeKey(path: str, key: str, data: Any):
    buff = readConfig(path)
    buff = json.loads(buff)
    buff[key] = data
    writeConfig(path, buff)


config = {"DEBUG": False, "LOGGER_HEAD": "BLH", "CMD_PREFIX": "!!blh",
          "GITEE_ROOT": "https://gitee.com/ixiaohei-sakura/WebsocketBlh/raw/master",
          "GITHUB_ROOT": "https://raw.githubusercontent.com/ixiaohei-sakura/blh-blivedm/master/",
          "AUTO_UPDATE": True,
          }


class BlhControl(Thread):
    def __init__(self, server, logger: Logger, debug=False):
        super(BlhControl, self).__init__()
        self.name = "BlhMainThread"
        self.daemon = True
        self.server = server
        self.debug = debug
        self.logger = logger
        self.logger.setDebug(self.debug)
        self.roomLists = []
