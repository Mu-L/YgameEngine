extends PacketPeerUDP
class_name 自定义UDP客户端
## 连接到目标服务器
## [br]参数:[br]
##   - ip地址: 目标IP地址[br]
##   - 端口: 目标端口
func UDP_连接(ip地址: String, 端口: int):
	self.connect_to_host(ip地址, 端口)

## 发送数据（支持文本和字节）
## [br]参数:[br]
##   - 数据: 要发送的内容（字符串或字节数组）[br]
##   - 编码类型: 文本编码（默认utf8）
func UDP_发送数据(数据, 编码类型: String = "utf8"):
	if 数据 is String:
		if 编码类型 == "utf8":
			self.put_packet(数据.to_utf8_buffer())
	elif 数据 is PackedByteArray:
		self.put_packet(数据)

## 获取可用数据包数量
func UDP_获取可用数量() -> int:
	return self.get_available_packet_count()

## 获取数据（支持自动解码）
func UDP_获取数据(编码类型: String = ""):
	var 字节数据 = self.get_packet()
	if 编码类型 == "utf8":
		return 字节数据.get_string_from_utf8()
	else:
		return 字节数据
	
