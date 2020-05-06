import sys
from subprocess import PIPE, Popen, run
from threading  import Thread
from queue import Queue, Empty
import os
import time
from pathlib import Path
import urllib3
from utils.rtext import *
import json

Prefix = '!!blh'
datahead = '§cBlhControlThread§r/§e{0} §r'
cmd = '!!blh'
rooturl = 'https://gitee.com/ixiaohei-sakura/WebsocketBlh/raw/master'
debug = 'False'
stopName = ''
ON_POSIX = 'posix' in sys.builtin_module_names
popu = []
roomnames = []
stopflag = True
ud = False
isuding = 'True'

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
{0} 待补充: §b待补充
{0} 待补充: §b待补充
{0} 待补充: §b待补充
{0} 待补充: §b待补充
§e-------------------页3/3------------------------'''.format('§n§7' + cmd)

class Version(object):
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
    get_text(f'§7   {Prefix} setpyver', '§b设置python启动命令', f'{Prefix} setpyver', run=False),
    get_text(' §r§b设置启动命令\n'),
    get_text(f'§7   {Prefix} pip', '§b安装库文件', f'{Prefix} pip ', run=False),
    get_text(' §r§b安装库文件\n'),
    get_text(f'§7   {Prefix} killall', '§b强制停止', f'{Prefix} killall'),
    get_text(' §r§b强制停止blh\n'),
    get_text(f'§7   {Prefix} debug', '§b调试模式', f'{Prefix} debug'),
    get_text(' §r§b调试模式'),
)



def printHelp(server, player, msg):
    for line in msg.splitlines():
        if line != '\n' and line != '\r' and line != '':
            server.tell(player, line)



def enqueue_output(out, queue):
    for line in iter(out.readline, b''):
        queue.put(line)
    out.close()



def load(key):
    with open('plugins/blh/config.conf', 'r') as f:
        for line in f.readlines():
            tmp = line.split('=')
            if tmp[0] == key:
                tmp = str(tmp[1])
                tmp = tmp.replace('\n', '')
                tmp = tmp.replace('\r', '')
                return tmp

def write(key, roomid):
    f = open('plugins/blh/config.conf', 'r')
    buff = f.read()
    if key in buff:
        return False
    f = open('plugins/blh/config.conf', 'a')
    f.write('{0}={1}\r'.format(key, roomid))
    return True

def remove(key):
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

def loadpyver():
    f = open('plugins/blh/pyver', 'r')
    Pystartcmd = f.read().split('=')
    Pystartcmd = Pystartcmd[1]
    Pystartcmd = Pystartcmd.replace('\r', '')
    Pystartcmd = Pystartcmd.replace('\n', '')
    class returnObj(object):
        def __init__(self, Pystartcmd):
            self.cmd = Pystartcmd
    return returnObj(Pystartcmd)


def blh(server, info, args):
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



def dm_logger(server, data, name = "defalt"):
    global popu
    try:
        data = str(data, encoding='utf-8')
    except:
        pass
    buff = data.replace('\n', '')
    buff = buff.replace('\r', '')

    if '当前人气值' in buff:
        args = buff.split('|')
        server.say('§b[§cBLH§r§b][§c{0}§b] §e{1}: §a{2}'.format(name, args[0], args[1]))
    elif '赠送' in buff:
        args = buff.split('|')
        server.say('§b[§cBLH§r§b][§c{0}§b] §c{1}x{2}§r: §e{3}币x{4}'.format(name, args[0], args[1], args[2], args[3]))
    elif '购买' in buff:
        args = buff.split(' ')
        server.say('§b[§cBLH§r§b][§c{0}§b] §c{1}§r:{2}'.format(name, args[0], args[1]))
    elif '醒目留言' in buff:
        args = buff.split('|')
        server.say('§b[§cBLH§r§b][§c{0}§b] §e{1} §c{2}§r: {3}'.format(name, args[0], args[1], args[2]))
    elif '|' in buff:
        args = buff.split('|')
        server.say('§b[§cBLH§r§b][§c{0}§b] §c{1}§r:{2}'.format(name, args[0], args[1]))
    else:
        server.say('§b[§cBLH§r§b]§r ' + buff)

def dm_logger_tell(server, buff, player = '@a'):
    server.tell(player, '§b[§cBLH§r§b]§r ' + buff)


def test_blh_isrunning(server, player, name):
    global stopflag, roomnames
    try:
        roomnames.index(name)
    except ValueError:
        roomnames.append(name)
        return False
    else:
        dm_logger_tell(server, '§cBlhControlThread§r/§4§l{0}§r §athis blh:{1} is running'.format('Warn', name), player)
        return True

def test_file(server, player):
    global debug
    if debug == 'True':
        server.say(f'var player: {player}')
        server.say(f'var debug: {debug}')
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

def check_update(server, player):
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

def download_update(server, player):
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

def update(server, player):
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
        isuding = True
        JsonData = [{"text":"更▇新","color":"dark_green","clickEvent":{"action":"run_command","value":"!!blh startud"},"hoverEvent":{"action":"show_text","value":"启动更新"}},{"text":"      "},{"text":"取▇消","color":"dark_red","clickEvent":{"action":"run_command","value":"!!blh cud"},"hoverEvent":{"action":"show_text","value":"取消更新"}}]
        JsonData = json.dumps(JsonData)
        server.execute(f'tellraw {player} {JsonData}')
    elif data.status == 2:
        dm_logger_tell(server, '版本最新, 不需要更新!', player)
        dm_logger_tell(server, '强制更新请输入 !!blh ud', player)
    elif data.status == 3:
        dm_logger_tell(server, '未知错误! 检查控制台.', player)



def on_server_stop(server):
    global stopflag, popu, roomnames
    roomnames = []
    stopflag = False
    try:
        os.system('ps aux|grep "{0} demo.py"|grep -v grep|cut -c 9-15|xargs kill -15'.format(loadpyver().cmd))
    except:
        pass

def on_mcdr_stop(server):
    global stopflag, popu, roomnames
    roomnames = []
    stopflag = False
    try:
        os.system('ps aux|grep "{0} demo.py"|grep -v grep|cut -c 9-15|xargs kill -15'.format(loadpyver().cmd))
    except:
        pass

def on_unload(server):
    global stopflag, popu, roomnames
    roomnames = []
    stopflag = False
    try:
        os.system('ps aux|grep "{0} demo.py"|grep -v grep|cut -c 9-15|xargs kill -15'.format(loadpyver().cmd))
    except:
        pass

def on_load(server, old):
    global stopflag, popu, roomnames, debug
    server.add_help_message('!!blh', 'BiliBili弹幕姬')
    test_file(server, '@a')
    os.system('chmod 777 plugins/BlhClient.py')
    os.system('chmod 777 plugins/blh/*')
    os.system('chmod 777 plugins/blh')
    
    if old.ud == True:
        dm_logger(server, 'blh已经更新到最新版本!')
        f = open('plugins/blh/ver', 'r')
        ver = f.read()
        dm_logger(server, '版本: v{0}.0.0'.format(ver))
        dm_logger(server, 'blh已经是最新版本!')
        url = rooturl + '/msg'
        http = urllib3.PoolManager()
        res = http.request('GET', url)
        server.say(str(res.data, encoding='utf-8').replace('\r', ''))
    else:
        update(server, '@a')

    try:
        f = open('plugins/blh/ver', 'r')
    except:
        time.sleep(1.5)
        dm_logger(server, datahead.format('info') + '检测到第一次启动, 准备初始化')
        time.sleep(1.5)
        test_file(server, '@a')
        check_update(server, '@a')
    else:
        if f.read() == '0':
            time.sleep(1.5)
            dm_logger(server, '检测到第一次启动, 准备初始化')
            time.sleep(1.5)
            test_file(server, '@a')
            update(server, '@a')

    debug = open('plugins/blh/debugMode', 'r').read()
    dm_logger(server, '重载成功')



def on_info(server, info):
    global stopflag, popu, roomnames, stopName, isuding, debug
    if info.content.startswith('!!blh'):
        startargs = info.content.split(' ')
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
        elif len(startargs) == 2 and startargs[1] == 'reload':
            dm_logger_tell(server, '正在停止所有房间')
            if roomnames != []:
                stopflag = False
                stopflag = True
                dm_logger(server, '已取消订阅{0}房间'.format('所有'))
                roomnames = []
            server.load_plugin("BlhClient.py")
        elif len(startargs) == 2 and startargs[1] == 'checkud':
            check_update(server, info.player)
        elif len(startargs) == 2 and startargs[1] == 'v':
            f = open('plugins/blh/ver', 'r')
            ver = f.read()
            dm_logger(server, '当前版本: v{0}.0.0'.format(ver))
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
        elif len(startargs) == 3 and startargs[1] == 'pop':
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
        elif len(startargs) == 2 and startargs[1] == 'listrun':
            for line in roomnames:
                dm_logger(server, line)
        elif len(startargs) == 2 and startargs[1] == 'cmds':
            server.tell(info.player, easycmds)
        elif len(startargs) == 3 and startargs[1] == 'setpyver':
            f = open('plugins/blh/pyver', 'w')
            f.write('python=' + startargs[2] + '\r')
            dm_logger_tell(server, '写入成功!', info.player)
        elif len(startargs) == 2 and startargs[1] == 'killall':
            try:
                os.system('ps aux|grep "{0} demo.py"|grep -v grep|cut -c 9-15|xargs kill -15'.format(loadpyver().cmd))
            except:
                pass
            dm_logger_tell(server, '已经杀死所有demo.py进程')
        elif len(startargs) == 2 and startargs[1] == 'ud':
            download_update(server, info.player)
        elif len(startargs) == 2 and startargs[1] == 'startud' and isuding == True:
            isuding = False
            dm_logger_tell(server, '开始更新', info.player)
            download_update(server, info.player)
        elif len(startargs) == 2 and startargs[1] == 'cud' and isuding == True:
            dm_logger_tell(server, '已取消', info.player)
        elif len(startargs) ==2:
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
        elif len(startargs) == 3 and startargs[1] == 'pip':
            dm_logger(server, '正在安装库...')
            try:
                os.system(f'{startargs[2]} install asyncio')
            except:
                dm_logger(server, '安装失败!')
            else:
                dm_logger(server, '安装成功!')
        else:
            dm_logger_tell(server, datahead.format('Warn') + '参数错误, 请!!blh help查看帮助')
