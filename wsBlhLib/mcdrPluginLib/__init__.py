from wsBlhLib.mcdrPluginLib.rtext import RText, RColor, RAction, RStyle, RTextList


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
            get_text(f'§7{Prefix} list', '§b列出所有房间间', f'{Prefix} list'),
            get_text(' §r§b列出所有\n   '),
            get_text(f'§7{Prefix} stopall', '§b停止所有房间', f'{Prefix} stopall'),
            get_text(' §r§b停止所有\n   '),
            get_text(f'§7{Prefix} startall', '§b启动所有开播的房间', f'{Prefix} startall'),
            get_text(' §r§b启动所有\n   '),
            get_text(f'§7{Prefix} listrun', '§b列出正在运行的房间', f'{Prefix} listrun'),
            get_text(' §r§b列出房间\n'),
        )


class ProgressBar(object):

    def __init__(self, title,
                 count=0.0,
                 run_status=None,
                 fin_status=None,
                 total=100.0,
                 unit='', sep='/',
                 chunk_size=1.0):
        super(ProgressBar, self).__init__()
        self.info = "【%s】%s %.2f %s %s %.2f %s"
        self.title = title
        self.total = total
        self.count = count
        self.chunk_size = chunk_size
        self.status = run_status or ""
        self.fin_status = fin_status or " " * len(self.status)
        self.unit = unit
        self.seq = sep

    def __get_info(self):
        # 【名称】状态 进度 单位 分割线 总数 单位
        _info = self.info % (self.title, self.status,
                             self.count/self.chunk_size, self.unit, self.seq, self.total/self.chunk_size, self.unit)
        return _info

    def refresh(self, count=1, status=None):
        self.count += count
        # if status is not None:
        self.status = status or self.status
        end_str = "\r"
        if self.count >= self.total:
            end_str = '\n'
            self.status = status or self.fin_status
        print(self.__get_info(), end=end_str)


_config = {"LOGGER_HEAD": "BLH", "CMD_PREFIX": "!!blh",
            "GITEE_ROOT": "https://gitee.com/ixiaohei-sakura/WebsocketBlh/raw/master/",
            "GITHUB_ROOT": "https://raw.githubusercontent.com/ixiaohei-sakura/blh-blivedm/master/",
            "AUTO_UPDATE": True, "ROOMS": {}
            }