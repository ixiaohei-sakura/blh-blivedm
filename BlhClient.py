import sys
from subprocess import PIPE, Popen, run
from threading  import Thread
from queue import Queue, Empty
import os
import time
from pathlib import Path
import urllib3
from utils.stext import *

Prefix = '!!blh'
datahead = '§cBlhControlThread§r/§e{0} §r'
cmd = '!!blh'
rooturl = 'bs.s1.blackserver.cn:8900'
stopName = ''
ON_POSIX = 'posix' in sys.builtin_module_names
popu = []
roomnames = []
stopflag = True
ud = False

helpmsg = '''§e-------------WebSocketBlhClient--help-------------
{0} cmds: §b命令交互列表(ClickEvent)
{0}: §b显示help
{0} help [页数(可选,默认1)]: §b显示help
{0} add [自定义名称] [房间id]: §b向配置文件里添加一个blh启动项
{0} rm [名称]: §b删除config.conf
{0} start [名称]: §b启动一个在配置文件blhClient
{0} stop [名称]: §b停止一个正在运行的blhClient
{0} stop all: §b停止所有正在运行的blhClient
§e-------------------页2/1--------------------'''.format('§n§7' + cmd)

helpmsg_2 = '''§e-------------WebSocketBlhClient--help-------------
{0} pop [名称]: §b关闭/开启 一个已经启动的blh的人气
{0} list: §b列出所有在配置文件中的可用直播间
{0} listrun: §b列出所有正在运行的直播间名称
{0} v: §b查看现在运行的BlhClient版本
{0} vmsg: §b查看现在运行的BlhClient更新消息
{0} reload: §b重载此插件的内容(一般用不到)
{0} checkud: §b检查版本更新
§e-------------------页2/2------------------------'''.format('§n§7' + cmd)

def get_text(t1, t2='', t3='', color=SColor.white, run=True):
    if t2 != '':
        if t3 != '':
            if run:
                stxt = SText(t1, color=color).set_hover_text(
                    t2).set_click_event(SAction.run_command, t3)
            else:
                stxt = SText(t1, color=color).set_hover_text(
                    t2).set_click_event(SAction.suggest_command, t3)
        else:
            stxt = SText(t1, color=color,
                         styles=SStyle.italic).set_hover_text(t2)
    else:
        if t3 != '':
            stxt = SText(t1, color=color)
        else:
            if run:
                stxt = SText(t1, color=color).set_click_event(
                    SAction.run_command, t3)
            else:
                stxt = SText(t1, color=color).set_click_event(
                    SAction.suggest_command, t3)
    return stxt


easycmds = STextList(
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
    get_text(f'§7   {Prefix} checkud', '§b检查版本更新', f'{Prefix} reload'),
    get_text(' §r§b更新blh'),
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



def blh(server, info, args):
    global stopflag, stopName
    roomid = load(args[2])
    if roomid is None:
        dm_logger_tell(server, '§cBlhControlThread§r/§e{0}§r §a key not found'.format('info'), info.player)
        return
    if test_blh_isrunning(server, info.player, args[2]) is True:
        return
    test_file(server, info.player)
    selfname = args[2]
    stopflag = True
    p = Popen('python3 demo.py {0} True'.format(roomid), stdout = PIPE, shell = True, bufsize = 1, close_fds = ON_POSIX, cwd = 'plugins/blh')
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
    filedir = Path('plugins/blh')
    filedemo = Path('plugins/blh/demo.py')
    fileblhdm = Path('plugins/blh/blivedm.py')
    fileconf = Path('plugins/blh/config.conf')
    filever = Path('plugins/blh/ver')

    dm_logger_tell(server, '§cBlhControlThread§r/§e{0}§r §a 正在检查Blhlibs完整性: {1}'.format('load', 'blh.dir'), player)
    if filedir.is_dir() is not True:
        try:
            dm_logger_tell(server, '§cBlhControlThread§r/§e{0}§r §a 未找到文件: {1}'.format('load', 'blh.dir'), player)
            dm_logger_tell(server, '§cBlhControlThread§r/§e{0}§r §a 正在建立文件夹: {1}'.format('load', 'blh.dir'), player)
            os.mkdir('plugins/blh')
        except:
            pass

    dm_logger_tell(server, '§cBlhControlThread§r/§e{0}§r §a 正在检查conf完整性: {1}'.format('load', 'version'), player)
    if fileconf.is_file() is not True:
        try:
            dm_logger_tell(server, '§cBlhControlThread§r/§e{0}§r §a 未找到文件: {1}'.format('load', 'config.conf'), player)
            dm_logger_tell(server, '§cBlhControlThread§r/§e{0}§r §a 正在建立文件: {1}'.format('load', 'config.conf'), player)
            os.mknod('plugins/blh/config.conf')
        except:
            pass

    dm_logger_tell(server, '§cBlhControlThread§r/§e{0}§r §a 正在检查版本文件完整性: {1}'.format('load', 'config.conf'), player)
    if filever.is_file() is not True:
        try:
            dm_logger_tell(server, '§cBlhControlThread§r/§e{0}§r §a 未找到文件: {1}'.format('load', '版本文件'), player)
            dm_logger_tell(server, '§cBlhControlThread§r/§e{0}§r §a 正在建立文件: {1}'.format('load', '版本文件'), player)
            os.mknod('plugins/blh/ver')
            f = open('plugins/blh/ver', 'w')
            f.write('0')
        except:
            pass

    dm_logger_tell(server, '§cBlhControlThread§r/§e{0}§r §a 正在检查Blhlibs完整性: {1}'.format('load', 'demo.py'), player)
    if filedemo.is_file() is not True:
        try:
            dm_logger_tell(server, '§cBlhControlThread§r/§e{0}§r §a 未找到文件: {1}'.format('load', 'demo.py'), player)
            dm_logger_tell(server, '§cBlhControlThread§r/§e{0}§r §a 正在下载文件: {1}'.format('load', 'demo.py'), player)
            urldemopy = rooturl + '/demo.py'
            http = urllib3.PoolManager()
            res = http.request('GET', urldemopy)
            with open('plugins/blh/demo.py', 'wb') as f:
                f.write(str(res.data, encoding='utf-8'))
        except:
            pass

    dm_logger_tell(server, '§cBlhControlThread§r/§e{0}§r §a 正在检查Blhlibs完整性: {1}'.format('load', 'blivedm.py'), player)
    if fileblhdm.is_file() is not True:
        try:
            dm_logger_tell(server, '§cBlhControlThread§r/§e{0}§r §a 未找到文件: {1}'.format('load', 'blivedm.py'), player)
            dm_logger_tell(server, '§cBlhControlThread§r/§e{0}§r §a 正在下载文件: {1}'.format('load', 'blivedm.py'), player)
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
    if int(res.data) > int(ver):
        try:
            dm_logger(server, '有新版本的Blh可用!')
            dm_logger(server, '最新版本为: {0}.0.0'.format(str(res.data, encoding='utf-8')))
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
    else:
        dm_logger(server, 'blh已经是最新版本!')
        dm_logger(server, '目前版本: v{0}.0.0'.format(str(res.data, encoding='utf-8')))
        url = rooturl + '/msg'
        http = urllib3.PoolManager()
        res = http.request('GET', url)
        server.say(str(res.data, encoding='utf-8'))



def on_server_stop(server):
    global stopflag, popu, roomnames
    roomnames = []
    stopflag = False
    try:
        os.system('ps aux|grep "python3 demo.py"|grep -v grep|cut -c 9-15|xargs kill -15')
    except:
        pass

def on_mcdr_stop(server):
    global stopflag, popu, roomnames
    roomnames = []
    stopflag = False
    try:
        os.system('ps aux|grep "python3 demo.py"|grep -v grep|cut -c 9-15|xargs kill -15')
    except:
        pass

def on_unload(server):
    global stopflag, popu, roomnames
    roomnames = []
    stopflag = False
    try:
        os.system('ps aux|grep "python3 demo.py"|grep -v grep|cut -c 9-15|xargs kill -15')
    except:
        pass

def on_load(server, old):
    global stopflag, popu, roomnames
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
        server.say(str(res.data, encoding='utf-8'))

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
            check_update(server, '@a')



def on_info(server, info):
    global stopflag, popu, roomnames, stopName
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
                server.tell(info.player, '\n')
                printHelp(server, info.player, helpmsg_2)
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
                    try:
                        os.system('ps aux|grep "python3 demo.py"|grep -v grep|cut -c 9-15|xargs kill -15')
                    except:
                        pass
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
                try:
                    os.system('ps aux|grep "python3 demo.py"|grep -v grep|cut -c 9-15|xargs kill -15')
                except:
                    pass
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
            server.say(str(res.data, encoding='utf-8')) 
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
        else:
            dm_logger_tell(server, datahead.format('Warn') + '参数错误, 请!!blh help查看帮助')