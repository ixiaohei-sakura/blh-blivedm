from utils.rtext import RText, RAction, RStyle, RColor, RTextList
from subprocess import PIPE, Popen, run
from threading  import Thread, Timer
from queue import Queue, Empty
from pathlib import Path

import sys
import json
import os
import time
import urllib3
import socket

# Strs
Prefix = '!!blh'
cmd = '!!blh'
rooturl = 'https://gitee.com/ixiaohei-sakura/WebsocketBlh/raw/master'
debug = 'False'
stopName = ''
isuding = 'True'
datahead = '§cBlhControlThread§r/§e{0} §r'
ON_POSIX = 'posix' in sys.builtin_module_names

# Nones
update_timer = None

# Bools
stopflag = True
udstopflag = True
ud = False

# Lists
popu = []
roomnames = []

# Sockets
num_online_client = 0
ADDRESS = ('127.0.0.1', 8812)
stop_all_thread = False
g_socket_server = None
start_socket = None
thread = None
g_conn_pool = []
online_client = []
thread_pool = []

# Helpmsgs
helpmsg = '''§e-------------WebSocketBlhClient--help-------------
{0} cmds: §b命令交互列表(ClickEvent)
{0}: §b显示help
{0} help [页数(可选,默认1)]: §b显示help
{0} add [自定义名称] [房间id]: §b向配置文件里添加一个blh启动项
{0} rm [名称]: §b删除config.conf
{0} start [名称]: §b启动一个在配置文件blhClient
{0} stop [名称]: §b停止一个正在运行的blhClient
{0} stop all: §b停止所有正在运行的blhClient
§e-------------------页3/1--------------------'''.format('§n§7' + cmd)

helpmsg_2 = '''§e-------------WebSocketBlhClient--help-------------
{0} pop [名称]: §b关闭/开启 一个已经启动的blh的人气
{0} list: §b列出所有在配置文件中的可用直播间
{0} listrun: §b列出所有正在运行的直播间名称
{0} v: §b查看现在运行的BlhClient版本
{0} vmsg: §b查看现在运行的BlhClient更新消息
{0} reload: §b重载此插件的内容(一般用不到)
{0} checkud: §b检查版本更新
{0} ud: §b强制更新(不管是不是最新版本)
§e-------------------页3/2------------------------'''.format('§n§7' + cmd)

helpmsg_3 = '''§e-------------WebSocketBlhClient--help-------------
{0} pip [您的pip安装命令]: §b安装BlhClient所需要的库文件
{0} setpyver [您的python命令]: §b设置py命令, 如: python3
{0} killall: §b杀死所有可能的僵尸子进程
{0} debug: §b开启/关闭 调试模式
{0} sendsocmsg: §b向Socket客户端发送消息
{0} stopth: §b停止所有SocketServer
{0} restartSoc: §b重启SocketServer
{0} listSoc: §b列出在线的客户端
§e-------------------页3/3------------------------'''.format('§n§7' + cmd) 

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


easycmds = RTextList(
    get_text('§e------------§bBlhClient§e------------\n   '),
    get_text(f'§7{Prefix} add [名称] [roomid]', '§b添加一个房间', f'{Prefix} add ', run=False),
    get_text(' §r§b添加房间\n   '),
    get_text(f'§7{Prefix} rm [名称]', '§b用名称删除房间', f'{Prefix} rm ',run=False),
    get_text(' §r§b删除房间\n   '),
    get_text(f'§7{Prefix} start [名称]', '§b启动一个在配置文件里的blh', f'{Prefix} start ', run=False),
    get_text(' §r§b订阅房间\n   '),
    get_text(f'§7{Prefix} stop [名称]', '§b停止一个正在运行的blh', f'{Prefix} stop ',run=False),
    get_text(' §r§b取消订阅\n   '),
    get_text(f'§7{Prefix} stop all', '§b停止所有', f'{Prefix} stop all'),
    get_text(' §r§b停止所有\n   '),
    get_text(f'§7{Prefix} pop [名称]', '§b开/关 一个正在运行的blh人气显示', f'{Prefix} pop ', run=False),
    get_text(' §r§b人气开关\n'),
    get_text(f'§7   {Prefix} listrun','§b列出正在运行的直播间', f'{Prefix} listrun'),
    get_text(' §r§b列表\n'),
    get_text(f'§7   {Prefix} v', '§b查看现在运行的BlhClient版本', f'{Prefix} v'),
    get_text(' §r§b版本查看\n'),
    get_text(f'§7   {Prefix} vmsg', '§b查看现在运行的BlhClient更新消息', f'{Prefix} vmsg'),
    get_text(' §r§b版本信息查看\n'),
    get_text(f'§7   {Prefix} reload', '§b重载blh', f'{Prefix} reload'),
    get_text(' §r§b重载blh\n'),
    get_text(f'§7   {Prefix} checkud', '§b检查版本更新', f'{Prefix} checkud'),
    get_text(' §r§b更新blh\n'),
    get_text(f'§7   {Prefix} ud', '§b强制更新', f'{Prefix} ud'),
    get_text(' §r§b强制更新blh\n'),
    get_text(f'§7   {Prefix} setpyver', '§b设置python启动命令', f'{Prefix} setpyver ', run=False),
    get_text(' §r§b设置启动命令\n'),
    get_text(f'§7   {Prefix} pip', '§b安装库文件', f'{Prefix} pip ', run=False),
    get_text(' §r§b安装库文件\n'),
    get_text(f'§7   {Prefix} killall', '§b强制停止', f'{Prefix} killall'),
    get_text(' §r§b强制停止blh\n'),
    get_text(f'§7   {Prefix} debug', '§b调试模式', f'{Prefix} debug'),
    get_text(' §r§b调试模式\n'),
)



def printHelp(server: classmethod, player: str, msg: str) -> None:
    """
    def printHelp(server, player, msg) -> None
    :输出一个Helpmsg
    :output a Helpmsg
    """
    for line in msg.splitlines():
        if line != '\n' and line != '\r' and line != '':
            server.tell(player, line)
    return None


# init funcs
def enqueue_output(out, queue) -> None:
    """
    你用不着
    :这是多线程取数据用的
    """
    for line in iter(out.readline, b''):
        queue.put(line)
    out.close()

def load(key: str) -> str:
    """
    加载key -> value from config
    """
    with open('plugins/blh/config.conf', 'r') as f:
        for line in f.readlines():
            tmp = line.split('=')
            if tmp[0] == key:
                tmp = str(tmp[1])
                tmp = tmp.replace('\n', '')
                tmp = tmp.replace('\r', '')
                return tmp

def write(key: str, roomid: str) -> bool:
    """
    写配置文件
    """
    f = open('plugins/blh/config.conf', 'r')
    buff = f.read()
    if key in buff:
        return False
    f = open('plugins/blh/config.conf', 'a')
    f.write('{0}={1}\r'.format(key, roomid))
    return True

def remove(key: str) -> bool:
    """
    删除配置项
    """
    try:
        tmpbuff = []
        data = key + '=' + load(key) + '\n'
        f = open('plugins/blh/config.conf', 'r')
        for line in f.readlines():
            if line != data:
                tmpbuff.append(line)
        print(tmpbuff)
        f_ = open('plugins/blh/config.conf', 'w')
        for line in tmpbuff:
            f_.write(line)
        return True
    except:
        return False

def loadpyver() -> classmethod:
    """
    加载python版本
    """
    f = open('plugins/blh/pyver', 'r')
    Pystartcmd = f.read().split('=')
    Pystartcmd = Pystartcmd[1]
    Pystartcmd = Pystartcmd.replace('\r', '')
    Pystartcmd = Pystartcmd.replace('\n', '')
    class returnObj(object):
        def __init__(self, Pystartcmd):
            self.cmd = Pystartcmd
    return returnObj(Pystartcmd)


# blh start func
def blh(server: classmethod, info: classmethod, args: list) -> None:
    """
    BlhMainFunction
    :Blh主逻辑
    """
    global stopflag, stopName, debug
    roomid = load(args[2])
    if roomid is None:
        dm_logger_tell(server, '§cBlhControlThread§r/§e{0}§r §a key not found'.format('info'), info.player)
        return
    if test_blh_isrunning(server, info.player, args[2]) is True:
        return
    if debug == 'False':
        test_file(server, 'None')
    elif debug == 'True':
        test_file(server, info.player)
    selfname = args[2]
    stopflag = True
    f = open('plugins/blh/pyver', 'r')
    Pystartcmd = f.read().split('=')
    if len(Pystartcmd) != 2:
        dm_logger(server, datahead.format('Err') + '§e没有python启动命令!')
        dm_logger(server, datahead.format('info') + '§e输入 !!blh setpyver [版本] 来设置')
        dm_logger(server, datahead.format('info') + '§e示例: !!blh setpyver python3')
        return
    Pystartcmd = Pystartcmd[1]
    Pystartcmd = Pystartcmd.replace('\r', '')
    Pystartcmd = Pystartcmd.replace('\n', '')
    p = Popen('{0} demo.py {1} True'.format(Pystartcmd, roomid), stdout = PIPE, shell = True, bufsize = 1, close_fds = ON_POSIX, cwd = 'plugins/blh')
    dm_logger(server, '§cBlhControlThread§r/§e{0}§r §a blh is running at pid {1}'.format('info', str(p.pid)))
    q = Queue()
    t = Thread(target=enqueue_output, args=(p.stdout, q))
    t.daemon = True
    t.start()
    dm_logger(server, datahead.format('info') + '已订阅{0}的直播间'.format(selfname))
    while stopflag and p.poll() is None:
            if selfname == stopName:
                roomnames.remove(selfname)
                tmp = p.pid
                p.kill()
                os.system('kill {0}'.format(str(tmp)))
                t._delete()
                stopName = ''
                return
            try:
                roomnames.index(selfname)
            except ValueError:
                break
            try:
                line = q.get_nowait()
            except Empty:  
                pass
            else:
                try:
                    popu.index(selfname)
                except ValueError:
                    dm_logger(server, line, selfname)
                else:
                    if bytes('当前人气值|', encoding='utf-8') not in line:
                        dm_logger(server, line, selfname)


# blh logger func
def dm_logger(server: classmethod, data, name = "defalt") -> bool:
    """
    游戏中logger
    :以全局广播的方式广播数据
    """
    global popu, g_conn_pool
    try:
        data = str(data, encoding='utf-8')
    except:
        pass
    buff = data.replace('\n', '')
    buff = buff.replace('\r', '')
    try:
        if '当前人气值' in buff:
            args = buff.split('|')
            server.say('§b[§cBLH§r§b][§c{0}§b] §e{1}: §a{2}'.format(name, args[0], args[1]))
            for i in range(len(g_conn_pool)):
                g_conn_pool[i].sendall(bytes('§b[§cBLH§r§b][§c{0}§b] §e{1}: §a{2}'.format(name, args[0], args[1]), encoding='UTF-8'))
        elif '赠送' in buff:
            args = buff.split('|')
            server.say('§b[§cBLH§r§b][§c{0}§b] §c{1}x{2}§r: §e{3}币x{4}'.format(name, args[0], args[1], args[2], args[3]))
            for i in range(len(g_conn_pool)):
                g_conn_pool[i].sendall(bytes('§b[§cBLH§r§b][§c{0}§b] §c{1}x{2}§r: §e{3}币x{4}'.format(name, args[0], args[1], args[2], args[3]), encoding='UTF-8'))
        elif '购买' in buff:
            args = buff.split(' ')
            server.say('§b[§cBLH§r§b][§c{0}§b] §c{1}§r:{2}'.format(name, args[0], args[1]))
            for i in range(len(g_conn_pool)):
                g_conn_pool[i].sendall(bytes('§b[§cBLH§r§b][§c{0}§b] §c{1}§r:{2}'.format(name, args[0], args[1]), encoding='UTF-8'))
        elif '醒目留言' in buff:
            args = buff.split('|')
            server.say('§b[§cBLH§r§b][§c{0}§b] §e{1} §c{2}§r: {3}'.format(name, args[0], args[1], args[2]))
            for i in range(len(g_conn_pool)):
                g_conn_pool[i].sendall(bytes('§b[§cBLH§r§b][§c{0}§b] §e{1} §c{2}§r: {3}'.format(name, args[0], args[1], args[2]), encoding='UTF-8'))
        elif '|' in buff:
            args = buff.split('|')
            server.say('§b[§cBLH§r§b][§c{0}§b] §c{1}§r:{2}'.format(name, args[0], args[1]))
            for i in range(len(g_conn_pool)):
                g_conn_pool[i].sendall(bytes('§b[§cBLH§r§b][§c{0}§b] §c{1}§r:{2}'.format(name, args[0], args[1]), encoding='UTF-8'))
        else:
            server.say('§b[§cBLH§r§b]§r ' + buff)
            for i in range(len(g_conn_pool)):
                g_conn_pool[i].sendall(bytes('§b[§cBLH§r§b]§r ' + buff, encoding='UTF-8'))
            server.logger.info('§b[§cBLH§r§b]§r ' + buff)
    except:
        return False
    else:
        return True
    return None

def dm_logger_tell(server: classmethod, buff: str, player = '@a') -> bool:
    """
    在player为一个指定值如info.player时,向玩家player显示buff中的内容
    """
    try:
        server.tell(player, '§b[§cBLH§r§b]§r ' + buff)
        if player == '@a':
            server.logger.info('§b[§cBLH§r§b]§r ' + buff)
    except:return False
    else:return True
    return None


# Blh tests
def test_blh_isrunning(server: classmethod, player: str, name: str) -> bool:
    """
    检测这个blh有没有正在运行
    """
    global stopflag, roomnames
    try:
        roomnames.index(name)
    except ValueError:
        roomnames.append(name)
        return False
    else:
        dm_logger_tell(server, '§cBlhControlThread§r/§4§l{0}§r §athis blh:{1} is running'.format('Warn', name), player)
        return True

def test_file(server: classmethod, player: str) -> None:
    """
    检查Blh必须文件完整性
    """
    global debug
    if debug == 'True':
        server.say('{0}var player: {1}'.format(datahead.format('debug'), player))
        server.say('{0}var debug: {1}'.format(datahead.format('debug'), debug))
    if debug == 'False':
        player_ = 'None'
    elif debug == 'True':
        player_ = player
    if debug == 'True':
        server.say('{0}var player_: {1}'.format(datahead.format('debug'), player_))
    filedir = Path('plugins/blh')
    filedemo = Path('plugins/blh/demo.py')
    fileblhdm = Path('plugins/blh/blivedm.py')
    fileconf = Path('plugins/blh/config.conf')
    filever = Path('plugins/blh/ver')
    filepyver = Path('plugins/blh/pyver')
    fileDebug = Path('plugins/blh/debugMode')

    dm_logger_tell(server, '§cBlhControlThread§r/§e{0}§r §a 正在检查Blhlibs完整性: {1}'.format('load', 'blh.dir'), player_)
    if filedir.is_dir() is not True:
        try:
            dm_logger_tell(server, '§cBlhControlThread§r/§e{0}§r §a 未找到文件: {1}'.format('load', 'blh.dir'), player_)
            dm_logger_tell(server, '§cBlhControlThread§r/§e{0}§r §a 正在新建文件夹: {1}'.format('load', 'blh.dir'), player_)
            os.mkdir('plugins/blh')
        except:
            pass

    dm_logger_tell(server, '§cBlhControlThread§r/§e{0}§r §a 正在检查conf完整性: {1}'.format('load', 'version'), player_)
    if fileconf.is_file() is not True:
        try:
            dm_logger_tell(server, '§cBlhControlThread§r/§e{0}§r §a 未找到文件: {1}'.format('load', 'config.conf'), player_)
            dm_logger_tell(server, '§cBlhControlThread§r/§e{0}§r §a 正在新建文件: {1}'.format('load', 'config.conf'), player_)
            os.mknod('plugins/blh/config.conf')
        except:
            pass

    dm_logger_tell(server, '§cBlhControlThread§r/§e{0}§r §a 正在检查版本文件完整性: {1}'.format('load', 'config.conf'), player_)
    if filever.is_file() is not True:
        try:
            dm_logger_tell(server, '§cBlhControlThread§r/§e{0}§r §a 未找到文件: {1}'.format('load', '版本文件'), player_)
            dm_logger_tell(server, '§cBlhControlThread§r/§e{0}§r §a 正在新建文件: {1}'.format('load', '版本文件'), player_)
            os.mknod('plugins/blh/ver')
            f = open('plugins/blh/ver', 'w')
            f.write('python')
        except:
            pass

    dm_logger_tell(server, '§cBlhControlThread§r/§e{0}§r §a 正在检查Debug文件完整性: {1}'.format('load', 'Debug'), player_)
    if fileDebug.is_file() is not True:
        try:
            dm_logger_tell(server, '§cBlhControlThread§r/§e{0}§r §a 未找到文件: {1}'.format('load', 'Debug文件'), player_)
            dm_logger_tell(server, '§cBlhControlThread§r/§e{0}§r §a 正在新建文件: {1}'.format('load', 'Debug文件'), player_)
            os.mknod('plugins/blh/debugMode')
            f = open('plugins/blh/debugMode', 'w')
            f.write('False')
        except:
            pass

    dm_logger_tell(server, '§cBlhControlThread§r/§e{0}§r §a 正在检查python启动命令: {1}'.format('load', 'python'), player_)
    if filepyver.is_file() is not True:
        try:
            dm_logger_tell(server, '§cBlhControlThread§r/§e{0}§r §a 未找到文件: {1}'.format('load', '启动命令配置'), player_)
            dm_logger_tell(server, '§cBlhControlThread§r/§e{0}§r §a 正在新建文件: {1}'.format('load', '启动命令配置'), player_)
            os.mknod('plugins/blh/pyver')
            f = open('plugins/blh/ver', 'w')
            f.write('0')
        except:
            pass

    dm_logger_tell(server, '§cBlhControlThread§r/§e{0}§r §a 正在检查Blhlibs完整性: {1}'.format('load', 'demo.py'), player_)
    if filedemo.is_file() is not True:
        try:
            dm_logger_tell(server, '§cBlhControlThread§r/§e{0}§r §a 未找到文件: {1}'.format('load', 'demo.py'), player_)
            dm_logger_tell(server, '§cBlhControlThread§r/§e{0}§r §a 正在下载文件: {1}'.format('load', 'demo.py'), player_)
            urldemopy = rooturl + '/demo.py'
            http = urllib3.PoolManager()
            res = http.request('GET', urldemopy)
            with open('plugins/blh/demo.py', 'wb') as f:
                f.write(str(res.data, encoding='utf-8'))
        except:
            pass

    dm_logger_tell(server, '§cBlhControlThread§r/§e{0}§r §a 正在检查Blhlibs完整性: {1}'.format('load', 'blivedm.py'), player_)
    if fileblhdm.is_file() is not True:
        try:
            dm_logger_tell(server, '§cBlhControlThread§r/§e{0}§r §a 未找到文件: {1}'.format('load', 'blivedm.py'), player_)
            dm_logger_tell(server, '§cBlhControlThread§r/§e{0}§r §a 正在下载文件: {1}'.format('load', 'blivedm.py'), player_)
            urlblivedm = rooturl + '/blivedm.py'
            http = urllib3.PoolManager()
            res = http.request('GET', urlblivedm)
            with open('plugins/blh/blivedm.py', 'wb') as f:
                f.write(str(res.data, encoding='utf-8'))
        except:
            pass



# Version funcs
class Version(object):
    """
    版本返回值
    """
    def __init__(self, nowversion, version, status, init):
        if version.find('alpha') or version.find('beta'):
            self.isalpha = True
        else: self.isalpha = False
        self.version = version
        self.nowver = nowversion
        self.status = status
        url = rooturl + '/au'
        http = urllib3.PoolManager()
        res = http.request('GET', url)
        self.au = str(res.data, encoding='utf-8').replace('\r', '')

def check_update_timer(server: classmethod) -> bool:
    """
    检查更新定时器函数,用作多线程thread.timer
    """
    url = rooturl + '/ver'
    http = urllib3.PoolManager()
    res = http.request('GET', url)

    ver = open('plugins/blh/ver', 'r')
    ver.read()
    ver_res = str(res.data, encoding='UTF-8')
    if ver != ver_res:
        update(server, '@a')
        try:
            update_timer = None
        except:pass
        return

    if udstopflag == False:
        try:
            update_timer.cancel()
            update_timer = None
        except:pass
        return

    try:
        update_timer = Timer(300, check_update_timer, [server])
        update_timer.setDaemon(True)
        update_timer.start()
    except:return False
    else:return True
    return None

def check_update(server: classmethod, player: str) -> classmethod:
    """
    手动检查更新或定时器检查更新时调用的函数, 只是 用于检查更新
    """
    global roomnames, stopflag
    dm_logger(server, '检查更新中,请耐心等待.期间请勿重载插件!')

    url = rooturl + '/ver'
    http = urllib3.PoolManager()
    res = http.request('GET', url)

    f = open('plugins/blh/ver', 'r')
    ver = f.read()

    if str(ver) == str(0):
        return Version(ver, str(res.data, encoding='utf-8'), 0, True)
    elif str(ver) != str(res.data, encoding='utf-8'):
        return Version(ver, str(res.data, encoding='utf-8'), 1, False)
    elif str(ver) == str(res.data, encoding='utf-8'):
        return Version(ver, str(res.data, encoding='utf-8'), 2, False)
    else: return Version(ver, str(res.data, encoding='utf-8'), 3, False)

def download_update(server: classmethod, player: str) -> bool:
        """
        下载更新, 插件没有权限自主下载更新, 需要玩家手动确认.
        """
        global roomnames, stopflag
        try:
            time.sleep(1.5)
            dm_logger(server, datahead.format('info') + '停止所有房间')
            roomnames = []
            stopflag = False
            dm_logger(server, '等待3秒之后将开始更新.期间请勿重载插件!')
            time.sleep(3)
            dm_logger_tell(server, '更新: demo.py')
            url = rooturl + '/demo.py'
            http = urllib3.PoolManager()
            res = http.request('GET', url)
            os.remove('plugins/blh/demo.py')
            f = open('plugins/blh/demo.py', 'w')
            f.write(str(res.data, encoding='utf-8'))
            dm_logger_tell(server, '更新: blivedm.py')
            url = rooturl + '/blivedm.py'
            http = urllib3.PoolManager()
            res = http.request('GET', url)
            os.remove('plugins/blh/blivedm.py')
            f = open('plugins/blh/blivedm.py', 'w')
            f.write(str(res.data, encoding='utf-8'))
            dm_logger_tell(server, '更新版本文件')
            url = rooturl + '/ver'
            http = urllib3.PoolManager()
            res = http.request('GET', url)
            os.remove('plugins/blh/ver')
            f = open('plugins/blh/ver', 'w')
            f.write(str(res.data, encoding='utf-8'))
            dm_logger_tell(server, '更新Blh主程序, Blh即将退出!')
            url = rooturl + '/BlhClient.py'
            http = urllib3.PoolManager()
            res = http.request('GET', url)
            os.remove('plugins/BlhClient.py')
            f = open('plugins/BlhClient.py', 'w')
            f.write(str(res.data, encoding='utf-8'))
            dm_logger(server, datahead.format('info') + '即将重载!')
            global ud
            ud = True
            server.load_plugin('BlhClient.py')
        except:
            dm_logger(server, datahead.format('Err') + '检测更新: 失败(请检查网络)')
            return False

def update(server: classmethod, player: str) -> classmethod:
    """
    检测Blh第一次启动或告知玩家新版本可用时调用的函数, 没有权限自动更新.
    """
    global isuding
    data = check_update(server, player)
    if data.status == 0:
        dm_logger_tell(server, datahead.format('info') + '检测到第一次启动, 准备初始化', player)
        download_update(server, player)
    elif data.status == 1:
        dm_logger_tell(server, '有新版本!', player)
        server.tell(player, f'   作者: {data.au}')
        time.sleep(0.1)
        server.tell(player, f'   版本: {data.version}')
        time.sleep(0.1)
        server.tell(player, f'   现在版本: {data.nowver}')
        time.sleep(0.1)
        server.tell(player, f'   是否为测试版本: {data.isalpha}')
        time.sleep(0.1)
        isuding = True
        JsonData = [{"text":"更▇新","color":"dark_green","clickEvent":{"action":"run_command","value":"!!blh startud"},"hoverEvent":{"action":"show_text","value":"启动更新"}},{"text":"      "},{"text":"取▇消","color":"dark_red","clickEvent":{"action":"run_command","value":"!!blh cud"},"hoverEvent":{"action":"show_text","value":"取消更新"}}]
        JsonData = json.dumps(JsonData)
        server.execute(f'tellraw {player} {JsonData}')
        return True
    elif data.status == 2:
        dm_logger_tell(server, '版本最新, 不需要更新!', player)
        dm_logger_tell(server, '强制更新请输入 !!blh ud', player)
        return False
    elif data.status == 3:
        dm_logger_tell(server, '未知错误! 检查控制台.', player)
        return None



# init socket funcs
def init_socket(server: classmethod, player='@a', debug=False) -> bool:
    """
    初始化socket连接池,线程等资源
    """
    global g_socket_server
    for i_ in range(200):
        i = i_ + 1
        try:
            g_socket_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # 创建 socket 对象
            g_socket_server.bind(ADDRESS)
            g_socket_server.listen(5)  # 最大等待数（有很多人理解为最大连接数，其实是错误的
        except:
            if debug == True:
                dm_logger_tell(server, '第 {0} 次尝试未成功, 于500ms后尝试.'.format(str(i)), player)
            server.logger.info('第 {0} 次尝试未成功, 于500ms后尝试.'.format(str(i)))
            time.sleep(0.5)
        else:
            dm_logger_tell(server, '第 {0} 次尝试成功!, 启动服务端中...'.format(str(i)), player)
            server.logger.info('第 {0} 次尝试成功!, 启动服务端中...'.format(str(i)))
            dm_logger_tell(server, "Socket服务端已启动，等待客户端连接...", player)
            server.logger.info("Socket服务端已启动，等待客户端连接...")
            return True
    return False

# 连接处理
def accept_client(server: classmethod) -> bool:
    """
    用于处理刚刚介入的连接,并加入连接池.
    """
    global g_socket_server
    while True:
        try:                                                                # 循环等待连接接入
            client, _ = g_socket_server.accept()                            # 阻塞，等待客户端连接
            g_conn_pool.append(client)                                      # 添加连接到进程池
            thread = Thread(target=message_handle, args=[server, client])   # 给每个客户端创建一个独立的线程进行管理
            thread_pool.append(thread)                                      # 启动线程
            thread_pool[thread_pool.index(thread)].setDaemon(True)
            thread_pool[thread_pool.index(thread)].start()
        except:pass
    return False

# 消息处理
def message_handle(server: classmethod, client: socket):
    """
    socketBlh的消息处理.
    """
    global num_online_client                                  # 全局变量
    client_id = ''                                            # 客户端id
    client.sendall("连接服务器成功!".encode(encoding='utf8'))   # 发送消息
    while True:                                               # main loop
        buff = str(client.recv(1024), encoding='UTF-8')
        if '[id]:' in buff:
            tmp = buff.split(':')
            client_id = str(tmp[1])
            dm_logger(server, f'客户端上线! 客户端id: {client_id}\n')
            online_client.append(client_id)
            num_online_client += 1
            time.sleep(0.5)
            dm_logger(server, f'目前在线数量: {num_online_client}\n')
        elif len(buff) == 0:
            try:
                g_conn_pool.remove(client)
                online_client.remove(client_id)
                client.close()
            except:pass
            dm_logger(server, '有一个客户端下线了! 客户端id: {0}\n'.format(client_id))
            num_online_client -= 1
            break
        else:dm_logger(server, "客户端消息: {0}\n".format(buff))

def Socket_server_init(server: classmethod, player='@a', debug=False) -> bool:
    """
    初始化SocketServer
    """
    global thread
    if init_socket(server, player, debug) == True:
        thread = Thread(target=accept_client, args=[server])
        thread.setDaemon(True)
        thread.start()
        return True
    else:return False
    return None

def stop_socket_thread() -> bool:
    """
    停止所有socket
    """
    global stop_all_thread, thread_pool, g_conn_pool, start_socket, online_client, thread
    stop_all_thread = True
    if stop_all_thread == True:
        for i in range(len(g_conn_pool)):
            g_conn_pool[i].sendall(bytes('stop_and_exit', encoding='UTF-8'))
        for i in range(len(g_conn_pool)):
            try:
                g_conn_pool[i].shutdown(2)
                g_conn_pool[i].close()
            except:pass
        g_conn_pool = []

        for i in range(len(thread_pool)):
            try:thread_pool[i].join(0.0)
            except:pass

        try:
            g_socket_server.shutdown(2)
            g_socket_server.close()
        except:pass

        try:
            thread_pool = []
            online_client = []
        except:pass

        try:
            start_socket.join(0.0)
            update_timer.join(0.0)
            thread.join(0.0)
        except:pass
        return True



def on_server_stop(server: classmethod):
    global stopflag, popu, roomnames, update_timer, udstopflag, stop_all_thread
    udstopflag = False
    update_timer.cancel()
    roomnames = []
    stopflag = False
    stop_socket_thread()
    try:
        os.system('ps aux|grep "{0} demo.py"|grep -v grep|cut -c 9-15|xargs kill -15'.format(loadpyver().cmd))
    except:
        pass

def on_mcdr_stop(server: classmethod):
    global stopflag, popu, roomnames, update_timer, stop_all_thread
    update_timer.cancel()
    roomnames = []
    stopflag = False
    stop_socket_thread()
    try:
        os.system('ps aux|grep "{0} demo.py"|grep -v grep|cut -c 9-15|xargs kill -15'.format(loadpyver().cmd))
    except:
        pass

def on_unload(server: classmethod):
    global stopflag, popu, roomnames, update_timer, udstopflag, stop_all_thread
    udstopflag = False
    roomnames = []
    stopflag = False
    stop_socket_thread()
    update_timer.cancel()
    try:
        os.system('ps aux|grep "{0} demo.py"|grep -v grep|cut -c 9-15|xargs kill -15'.format(loadpyver().cmd))
    except:
        pass

def on_load(server: classmethod, old: classmethod):
    global stopflag, popu, roomnames, debug, update_timer, g_conn_pool, stop_all_thread, start_socket
    stop_all_thread = False
    update_timer = Timer(300, check_update_timer, [server])
    update_timer.setDaemon(True)
    update_timer.start()
    server.add_help_message('!!blh', 'BiliBili弹幕姬')
    test_file(server, '@a')
    os.system('chmod 777 plugins/BlhClient.py')
    os.system('chmod 777 plugins/blh/*')
    os.system('chmod 777 plugins/blh')
    
    try:
        if old.ud == True:
            dm_logger(server, 'blh已经更新到最新版本!')
            f = open('plugins/blh/ver', 'r')
            ver = f.read()
            dm_logger(server, '版本: {0}'.format(ver))
            dm_logger(server, 'blh已经是最新版本!')
            url = rooturl + '/msg'
            http = urllib3.PoolManager()
            res = http.request('GET', url)
            server.say(str(res.data, encoding='utf-8').replace('\r', ''))
            time.sleep(3)
            dm_logger(server, '如果您没有安装过asyncio, 请输入:')
            dm_logger(server, '!!blh pip [pip命令], 或查看help')
            debug = open('plugins/blh/debugMode', 'r').read()
            return
        else:
            update(server, '@a')
    except:pass

    try:
        f = open('plugins/blh/ver', 'r')
    except:
        time.sleep(1.5)
        dm_logger(server, datahead.format('info') + '检测到第一次启动, 准备初始化')
        time.sleep(1.5)
        test_file(server, '@a')
        download_update(server, '@a')
    else:
        if f.read() == '0':
            time.sleep(1.5)
            dm_logger(server, '检测到第一次启动, 准备初始化')
            time.sleep(1.5)
            test_file(server, '@a')
            download_update(server, '@a')

    debug = open('plugins/blh/debugMode', 'r').read()
    start_socket = Thread(target=Socket_server_init, args=[server, '@a', bool(debug)])
    start_socket.setDaemon(True)
    start_socket.start()
    time.sleep(0.5)
    dm_logger(server, '重载成功')



def on_info(server: classmethod, info: classmethod):
    global stopflag, popu, roomnames, stopName, isuding, debug
    if info.content.startswith('!!blh'):
        startargs = info.content.split(' ')
        # helpmsgs
        if len(startargs) == 1:
            printHelp(server, info.player, helpmsg)
        elif len(startargs) == 2 and startargs[1] == 'help':
            printHelp(server, info.player, helpmsg)
        elif len(startargs) == 3 and startargs[1] == 'help':
            if startargs[2] == '1':
                printHelp(server, info.player, helpmsg)
            elif startargs[2] == '2':
                printHelp(server, info.player, helpmsg_2)
            elif startargs[2] == '3':
                printHelp(server, info.player, helpmsg_3)
            else:
                printHelp(server, info.player, helpmsg)
        
        # 房间配置操作
        elif len(startargs) == 4 and startargs[1] == 'add':
            test_file(server, info.player)
            if write(startargs[2], startargs[3]) is not False:
                dm_logger_tell(server, '§cBlhControlThread§r/§e{0}§r §a 写入成功!'.format('info'), info.player)
            else:
                dm_logger_tell(server, '§cBlhControlThread§r/§e{0}§r §a 写入失败:,原因: 已经存在!'.format('info'), info.player)
        elif len(startargs) == 3 and startargs[1] == 'rm':
            if remove(startargs[2]) is not False:
                dm_logger_tell(server, '§cBlhControlThread§r/§e{0}§r §a 删除成功!'.format('info'), info.player)
            else:
                dm_logger_tell(server, '§cBlhControlThread§r/§e{0}§r §4 删除失败!'.format('info'), info.player)
        elif len(startargs) == 2 and startargs[1] == 'list':
            dm_logger_tell(server, '直播间列表:')
            with open('plugins/blh/config.conf', 'r') as f:
                for line in f.readlines():
                    tmp = line.split('=')
                    tmp[0] = tmp[0].replace('\n', '')
                    tmp[1] = tmp[1].replace('\n', '')
                    dm_logger_tell(server, '名称:{0} 房号:{1}'.format(tmp[0], tmp[1]))

        # Blh 开启/关闭
        elif len(startargs) == 3 and startargs[1] == 'start':
            blh(server, info, startargs)
        elif len(startargs) == 3 and startargs[1] == 'stop':
            if startargs[2] == 'all':
                if roomnames != []:
                    stopflag = False
                    stopflag = True
                    dm_logger(server, '已取消订阅全部房间,名称:')
                    for line in roomnames:
                        dm_logger(server, line)
                    roomnames = []
                else:
                    dm_logger(server, datahead.format('Warn') + '没有房间可以被取消订阅')
            elif startargs[2] != 'all':
                try:
                    roomnames.index(startargs[2])
                except ValueError:
                    dm_logger(server, '没有名叫: {0}的直播间'.format(startargs[2]))
                    return
                else:
                    stopName = startargs[2]
                    dm_logger(server, '已取消订阅{0}的直播间'.format(startargs[2]))
            else:
                dm_logger(server, '参数错误!')

        # 重载Blh
        elif len(startargs) == 2 and startargs[1] == 'reload':
            dm_logger(server, '正在关闭Socket连接')
            if stop_socket_thread() == True:
                dm_logger(server, '断开成功!')
                dm_logger_tell(server, '正在停止所有房间')
                if roomnames != []:
                    stopflag = False
                    stopflag = True
                    dm_logger(server, '已取消订阅{0}房间'.format('所有'))
                    roomnames = []
                server.load_plugin("BlhClient.py")
            else:
                dm_logger(server, '未知错误，检查控制台')

        # 当前版本显示
        elif len(startargs) == 2 and startargs[1] == 'v':
            f = open('plugins/blh/ver', 'r')
            ver = f.read()
            dm_logger(server, '当前版本: {0}'.format(ver))

        # 新版消息显示
        elif len(startargs) == 2 and startargs[1] == 'vmsg':
            url = rooturl + '/msg'
            http = urllib3.PoolManager()
            res = http.request('GET', url)
            server.say(str(res.data, encoding='utf-8').replace('\r', ''))
        elif len(startargs) == 3 and startargs[1] == 'vmsg':
            if startargs[2] == '1':
                url = rooturl + '/msg'
                http = urllib3.PoolManager()
                res = http.request('GET', url)
                server.say(str(res.data, encoding='utf-8').replace('\r', ''))
            elif startargs[2] == '2':
                url = rooturl + '/msg2'
                http = urllib3.PoolManager()
                res = http.request('GET', url)
                server.say(str(res.data, encoding='utf-8').replace('\r', ''))

        # 开/关 人气
        elif len(startargs) == 3 and startargs[1] == 'pop':
            if startargs[2] == 'all':
                popu = roomnames
                dm_logger_tell(server, '所有房间的人气显示已关闭', info.player)
            try:
                roomnames.index(startargs[2])
            except ValueError:
                dm_logger_tell(server, datahead.format('Warn') + ' 没有房间名称为: {0}'.format(startargs[2]), info.player)
                return
            else:
                try:
                    popu.index(startargs[2])
                except ValueError:
                    popu.append(startargs[2])
                    dm_logger_tell(server, datahead.format('info') + ' 关闭了房间{0}的人气显示'.format(startargs[2]), info.player)
                else:
                    popu.remove(startargs[2])
                    dm_logger_tell(server, datahead.format('info') + ' 打开了房间{0}的人气显示'.format(startargs[2]), info.player)

        # 显示正在运行的Blh
        elif len(startargs) == 2 and startargs[1] == 'listrun':
            for line in roomnames:
                dm_logger(server, line)

        # ClickEvent cmds
        elif len(startargs) == 2 and startargs[1] == 'cmds':
            server.tell(info.player, easycmds)

        # 设置python启动命令
        elif len(startargs) == 3 and startargs[1] == 'setpyver':
            f = open('plugins/blh/pyver', 'w')
            f.write('python=' + startargs[2] + '\r')
            dm_logger_tell(server, '写入成功!', info.player)
        
        # 杀死所有子进程
        elif len(startargs) == 2 and startargs[1] == 'killall':
            try:
                os.system('ps aux|grep "{0} demo.py"|grep -v grep|cut -c 9-15|xargs kill -15'.format(loadpyver().cmd))
            except:
                pass
            dm_logger_tell(server, '已经杀死所有demo.py进程')

        # 手动检查更新
        elif len(startargs) == 2 and startargs[1] == 'checkud':
            update(server, info.player)

        # 强制更新
        elif len(startargs) == 2 and startargs[1] == 'ud':
            download_update(server, info.player)

        # 自动更新反馈
        elif len(startargs) == 2 and startargs[1] == 'startud' and isuding == True:
            isuding = False
            dm_logger_tell(server, '开始更新', info.player)
            download_update(server, info.player)
        elif len(startargs) == 2 and startargs[1] == 'cud' and isuding == True:
            dm_logger_tell(server, '已取消', info.player)

        # debug模式
        elif len(startargs) ==2 and startargs[1] == 'debug':
            if debug == 'False':
                f = open('plugins/blh/debugMode', 'w')
                f.write('True')
                f.close()
                f = open('plugins/blh/debugMode', 'r')
                debug = f.read()
                dm_logger_tell(server, f'调试模式: {debug}', info.player)
                f.close()
            elif debug == 'True':
                f = open('plugins/blh/debugMode', 'w')
                f.write('False')
                f.close()
                f = open('plugins/blh/debugMode', 'r')
                debug = f.read()
                dm_logger_tell(server, f'调试模式: {debug}', info.player)
                f.close()

        # 库安装
        elif len(startargs) == 3 and startargs[1] == 'pip':
            dm_logger(server, '正在安装库...')
            try:
                piptmp = Popen(f'{startargs[2]} list', stdout=PIPE, stderr=PIPE, shell=True)
                tmpbuff = str(piptmp.stdout.read(), encoding='utf-8')
                piptmp.kill()
                if tmpbuff.find('asyncio') and tmpbuff.find('already'):
                    dm_logger_tell(server, '此库已经被安装过了, 无需再次安装!')
                    return
                os.system(f'{startargs[2]} install asyncio')
            except Exception as exception:
                dm_logger(server, '安装失败!详情信息查看控制台或debug')
                if debug == 'True':
                    dm_logger_tell(server, datahead.format('debug')+f'原因: {exception}', info.player)
            else:
                dm_logger(server, '安装成功!')

        # socket cmds
        elif len(startargs) == 3 and startargs[1] == 'sendsocmsg' and debug == True:
            for i in range(len(g_conn_pool)):
                g_conn_pool[i].sendall(bytes(startargs[2], encoding='UTF-8'))

        elif len(startargs) == 2 and startargs[1] == 'stopth' and debug == True:
            stop_socket_thread()

        elif len(startargs) == 2 and startargs[1] == 'listSoc':
            if len(online_client) == 0:
                dm_logger_tell(server, '没有在线的客户端!', info.player)
                return
            for value in online_client:
                dm_logger_tell(server, value, info.player)

        elif len(startargs) == 2 and startargs[1] == 'restartSoc':
            stop_socket_thread()
            dm_logger_tell(server, '已停止, 3秒后启动')
            time.sleep(3)
            dm_logger_tell(server, '正在启动...')
            Socket_server_init(server, 'None')

        elif len(startargs) == 2 and startargs[1] == 'stopClient':
            for i in range(len(g_conn_pool)):
                g_conn_pool[i].sendall(bytes('stop_and_exit', encoding='UTF-8'))
            dm_logger_tell(server, '已经向所有客户端发送.', info.player)


        # 参数错误提示
        else:
            dm_logger_tell(server, datahead.format('Warn') + '参数错误, 请!!blh help查看帮助')
