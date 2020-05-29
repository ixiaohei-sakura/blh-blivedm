# WebSocket 哔哩哔哩弹幕姬
#### [国内下载源] https://gitee.com/ixiaohei-sakura/MCDR-BlhClient

## 写在前面:
#### 此插件使用了`subprocess.Popen`启动一个单独的WebSocketBlh程序，负责获取他的`sys.stdout`,再接下来输入到游戏之中.

#### WebSocketBlh获取: [作者xfgryujk] https://github.com/xfgryujk/blivedm
#### blh-Websocket-plugin [作者ixiaohei] https://github.com/ixiaohei-sakura/blh-blivedm

性能对比:
方式|弹幕完整性|程序性能
--|:--:|--:
WebSocket|100%: 不可能丢弹幕,数据种类多|快速，不报错
Post|30%: 弹幕发送速度过快无法接受，且无法查询礼物、人气等数据|查询速度低，还可能被屏蔽，且经常报错

## 食用方式:
#### 将它拖进plugins目录下后并重载他后,请不要管他了. 把一切都交给他完成吧,包括创建目录,下载文件.
#### tips: 第一次启动时许多服务不会启动,请重载. 需要安装的库: asyncio, aiohttp|其中,aiohttp不安装会报错,asyncio不安装服务不会启动.
#### 注意, 您需要安装在主服务器的只有[弹幕姬客户端兼Socket服务端](https://github.com/ixiaohei-sakura/blh-blivedm/blob/master/BlhClient.py)而并非[Socket跨服客户端](https://github.com/ixiaohei-sakura/blh-blivedm/blob/master/BlhClient.py)请注意, 这两个文件虽然是协同运行, 但是 绝对 不可以放在同一个MCDR下. 那会搞乱一切BLH命令的
#### 更新方式: 输入!!blh reload 会自动检查更新
#### !!blh checkud 会检查更新
#### !!blh ud 强制下载更新(不管是不是最新版本)


## 目前版本:
#### 最新版本为0.4.3-alpha!
#### 立即下载！
##### tips: 1.0.0 2.0.0 3.0.0 等等虫子版本无法直接更新,需要手动下载OvO
#### 新增了一个功能: 跨服
#### 跨服设置:请下载BlhSocketClient.py后修改其内容变量: id='Creative' 改为您的服务器id, 如创造服,生存服.



