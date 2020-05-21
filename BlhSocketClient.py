import socket
import time
from threading import Thread

###########可更改常量开始###########
id = 'Creative'
selfaddr = '127.0.0.1'
minPort = 1000
maxPort = 9999
###########可更改常量结束###########

stopFlag = True
Client_thread = None
s = socket.socket()
randomPort = minPort
ADDRESS = (selfaddr, randomPort)
try_start: Thread

class ServerStatus(object):
    def __init__(self, server_is_alive, is_server_stop):
        self.server_is_alive = server_is_alive
        self.server_stop = is_server_stop
server_status = ServerStatus(True, False)

def recvServer(server):
    global stopFlag
    while stopFlag:
        try:
            buff = s.recv(2048).decode(encoding='utf8')
            if buff == 'stop_and_exit':
                server_status.server_is_alive = False
                server_status.server_stop = True
                stopFlag = False
                return
            elif buff == '\n' or buff == '\r' or buff == '\n\r' or buff == '':
                server_status.server_is_alive = False
                server_status.server_stop = True
                stopFlag = False
                return
            server.say(buff)
        except: pass
    return

def init_Client(server):
    global ADDRESS, randomPort
    try:
        while True:
            try:
                s.connect(ADDRESS)
            except:
                randomPort += 1
                s.close
            else:
                ADDRESS = (selfaddr, randomPort)
                break
        server.say(s.recv(2048).decode(encoding='utf8'))
        s.sendall(bytes('[id]:{0}\n'.format(id), encoding='UTF-8'))
        time.sleep(0.5)
        s.sendall("Blh客户端启动成功!".encode('utf8'))
        s.setblocking(False)
    except:
        return False
    Client_thread = Thread(target=recvServer, args=[server])
    Client_thread.setDaemon(True)
    Client_thread.start()
    return True

def stop_all():
    global s, Client_thread
    try:
        s.shutdown(2)
        s.close()
    except:pass

    try:
        Client_thread.join(0.0)
        try_start.join(0.0)
    except:pass
    return

def init_loop(server):
    while True:
        if init_Client(server) == True:
            break
        time.sleep(1)

def on_load(server, old):
    global try_start
    try_start = Thread(target=init_loop, args=[server])
    try_start.start()

def on_unload(server):
    stop_all()

def on_server_stop(server, __):
    stop_all()

def on_mcdr_stop(server):
    stop_all()

def on_info(server, info):
    if info.content.startswith('!!blh'):
        args = info.content.split(' ')
        if len(args) == 2 and args[1] == 'reload':
            stop_all()
            server.say('正在重载')
            time.sleep(2)
            server.load_plugin('BlhSocketClient.py')
        elif len(args) == 2 and args[1] == 'stop':
            stop_all()
            server.say('已停止BlhSocketClient')
        else:
            s.sendall(bytes(info.content, encoding='utf-8'))
