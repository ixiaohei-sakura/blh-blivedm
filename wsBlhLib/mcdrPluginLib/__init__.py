class HelpMessages:
    def __init__(self, cmd):
        self.cmd = cmd
        msg_1 = '''§e-------------WebSocketBlhClient--help-------------
        {0} cmds: §b命令交互列表
        {0}: §b显示help
        {0} help [页数 1-2]: §b显示help
        {0} add [自定义名称] [房间id]: §b向配置文件里添加一个blh启动项
        {0} rm [名称]: §b删除一个在配置中的房间
        {0} start [名称]: §b启动一个在配置文件中的房间
        {0} stop [名称]: §b停止一个房间
        {0} stop all: §b停止所有正在运行房间
        §e-------------------页1/2--------------------'''.format('§n§7' + self.cmd)

        msg_2 = '''§e-------------WebSocketBlhClient--help-------------
        {0} listRooms: §b列出所有在配置文件中的可用直播间
        {0} listRunning: §b列出所有正在运行的直播间名称
        {0} version: §b查看现在运行的BlhClient版本
        {0} updateMsg: §b查看现在运行的BlhClient更新消息
        {0} checkUpdate: §b检查版本更新
        {0} ud: §b强制更新(不管是不是最新版本)
        §e-------------------页2/2------------------------'''.format('§n§7' + self.cmd)

        self.help_messages = [msg_1, msg_2]
