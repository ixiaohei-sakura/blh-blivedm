import socket
import time
from threading import Thread

stopFlag = True
Client_thread = None
id = 'Creative'
s = socket.socket()
restart_num = 100
restart_counter = 0

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
    global Client_thread
    try:
        s.connect(('127.0.0.1', 8812))
        server.say(s.recv(2048).decode(encoding='utf8'))
        s.sendall(bytes('[id]:{0}\n'.format(id), encoding='UTF-8'))
        time.sleep(0.5)
        s.sendall("Blh客户端启动成功!".encode('utf8'))
        s.setblocking(False)
    except Exception as exc:
        server.say('启动失败!原因: {0}'.format(exc))
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
    except:pass
    return



def on_load(server, old):
    global restart_counter
    if init_Client(server) == False:
        stop_all()
        time.sleep(1)
        try:restart_counter = old.restart_counter+1
        except:pass
        if restart_counter <= restart_num:
            server.load_plugin('BlhSocketClient.py')
        else:
            restart_counter = 0
            return
    else:restart_counter = 0

def on_unload(server):
    stop_all()

def on_info(server, info):
    global restart_counter
    if info.content.startswith('!!blh'):
        args = info.content.split(' ')
        if len(args) == 2 and args[1] == 'reload':
            restart_counter = 0
            stop_all()
            server.say('正在重载')
            time.sleep(2)
            server.load_plugin('BlhSocketClient.py')
        elif len(args) == 2 and args[1] == 'stopc':
            restart_counter = 0
            stop_all()
            server.say('已停止BlhSocketClient')
        else:
            s.sendall(bytes(info.content, encoding='utf-8'))