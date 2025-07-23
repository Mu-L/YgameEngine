##基于网络封装,目前有UDP
extends Node
class_name 引擎网络
 ## 自定义UDP客户端内部类（嵌套在引擎网络中）

class UDP客户端 extends PacketPeerUDP:		

## [br]参数:[br]
##   - 互联网协议地址ip: 目标IP地址，默认为"127.0.0.1"[br]
##   - 端口: 目标端口，默认为8777
		func UDP_连接(ip地址: String, 端口: int):
			self.connect_to_host(ip地址, 端口)

		func UDP_发送数据(数据, 编码类型:Variant):
			if 数据 is String:
				if 编码类型 == "utf8":
					self.put_packet(数据.to_utf8_buffer())
			elif 数据 is PackedByteArray:
				self.put_packet(数据)
		
		func UDP_获取可用数据包数量() -> int:
			return self.get_available_packet_count()

		func UDP_获取数据(编码类型: String = ""):
			if 编码类型=="utf8":
				return self.get_packet().get_string_from_utf8()
			else:
				return self.get_packet()

##UDP网络通信工具类
##提供UDP客户端的创建和数据收发功能，归类于引擎.网络命名空间
## 创建UDP客户端实例（返回内部自定义客户端）
func UDP_创建客户端() -> UDP客户端:
	return UDP客户端.new()
