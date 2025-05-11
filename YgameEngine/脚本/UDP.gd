## UDP网络通信工具类
## 提供UDP客户端的创建和数据收发功能
extends Node
class_name 引擎UDP

## 创建一个新的UDP客户端实例
## [br]返回:[br]
##   - 新创建的UDP客户端对象
##[codeblock]
## var 客户端 = 引擎.UDP.创建客户端()
##[/codeblock]
func 创建客户端() -> PacketPeerUDP:
    return PacketPeerUDP.new()

## 设置UDP客户端的目标地址和端口（实际为指定默认发送目标）
## [br]参数:[br]
##   - _UDP客户端: UDP客户端实例[br]
##   - _互联网协议地址ip: 目标IP地址，默认为"127.0.0.1"[br]
##   - _端口: 目标端口，默认为8777
##[codeblock]
## 引擎.UDP.连接(客户端, "192.168.1.100", 9000)
##[/codeblock]
func 连接(_UDP客户端: PacketPeerUDP, _互联网协议地址ip: String = "127.0.0.1", _端口: int = 8777):
    _UDP客户端.connect_to_host(_互联网协议地址ip, _端口)

## 向已连接的目标发送字节数据
## [br]参数:[br]
##   - _UDP客户端: UDP客户端实例[br]
##   - _字节数据: 要发送的字节数组，默认为"Hello, UDP!"的UTF-8编码
##[codeblock]
## 引擎.UDP.发送字节数据(客户端, "你好".to_utf8_buffer())
##[/codeblock]
func 发送字节数据(_UDP客户端: PacketPeerUDP, _字节数据: PackedByteArray = "Hello, UDP!".to_utf8_buffer()):
    _UDP客户端.put_packet(_字节数据)

## 获取当前可用的数据包数量
## [br]参数:[br]
##   - _UDP客户端: UDP客户端实例
## [br]返回:[br]
##   - 可用数据包的数量
##[codeblock]
## if 引擎.UDP.获取可用字节数量(客户端) > 0:
##     # 有数据可接收
##[/codeblock]
func 获取可用字节数量(_UDP客户端: PacketPeerUDP) -> int:
    return _UDP客户端.get_available_packet_count()

## 从UDP客户端接收一个数据包
## [br]参数:[br]
##   - _UDP客户端: UDP客户端实例
## [br]返回:[br]
##   - 接收到的字节数组数据包
##[codeblock]
## var 数据 = 引擎.UDP.获取字节数据(客户端)
## var 文本 = 数据.get_string_from_utf8()
##[/codeblock]
func 获取字节数据(_UDP客户端: PacketPeerUDP) -> PackedByteArray:
    return _UDP客户端.get_packet()