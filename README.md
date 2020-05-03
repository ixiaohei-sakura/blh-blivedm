# blh-blivedm
### [中文](README_cn.md)
#### This plug-in use 'subprocess.Popen' to start a websocketblh program, which is responsible for obtaining its 'sys.stdout', and then put it into the game

# WebSocket 哔哩哔哩弹幕姬

###### 此插件使用了`subprocess.Popen`启动一个单独的WebSocketBlh程序，负责获取他的`sys.stdout`,再接下来输入到游戏之中.

###### WebSocketBlh获取: [作者xfgryujk] https://github.com/xfgryujk/blivedm
###### blh-Websocket-plugin [作者ixiaohei] https://github.com/ixiaohei-sakura/blh-blivedm

性能对比:
方式|弹幕完整性|程序性能
--|:--:|--:
WebSocket|100%: 不可能丢弹幕,数据种类多|快速，不报错
Post|30%: 弹幕发送速度过快无法接受，且无法查询礼物、人气等数据|查询速度低，还可能被屏蔽，且经常报错

