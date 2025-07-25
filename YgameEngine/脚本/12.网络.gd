##基于网络封装,目前有UDP
extends Node
class_name 引擎网络

# 全局通用：字节数组转UTF8字符串

func 字节转字符串(字节数据: PackedByteArray, 编码类型: String = "utf8")->Variant:	
		if 编码类型=="utf8":
			return 字节数据.get_string_from_utf8()
		else:#未来可扩展
			return 字节数据
			
 ## 自定义UDP客户端内部类（嵌套在引擎网络中）

class UDP客户端 extends PacketPeerUDP:		
		var 发送队列=[]
		var 正在处理队列 = false  # 防止重复处理队列
## [br]参数:[br]
##   - 互联网协议地址ip: 目标IP地址，默认为"127.0.0.1"[br]
##   - 端口: 目标端口，默认为8777
		func UDP_连接(ip地址: String, 端口: int):
			self.connect_to_host(ip地址, 端口)

		func UDP_发送数据(数据, 编码类型:Variant):
			var 欲发送数据
			if 数据 is String:
				if 编码类型 == "utf8":
					欲发送数据=数据.to_utf8_buffer()
			elif 数据 is PackedByteArray:
				欲发送数据=数据
			#加入队列
			发送队列.append(欲发送数据)
			# 3. 如果队列未处理，启动处理流程
			if not 正在处理队列:
				_处理发送队列()
				
		func UDP_获取可用数据包数量() -> int:
			if self==null: return 0
			return self.get_available_packet_count()
		func UDP_获取数据(编码类型: String = ""):
			if 编码类型=="utf8":
				return self.get_packet().get_string_from_utf8()
			else:
				return self.get_packet()
		## 内部方法：按顺序发送队列中的数据
		func _处理发送队列():
			正在处理队列 = true
			# 循环发送所有队列数据（直到队列为空）
			while 发送队列.size() > 0:
				var 数据 = 发送队列.pop_front()  # 取出第一个元素（保证顺序）
				self.put_packet(数据)  # 发送
				await 引擎.场景.等待(0.01)  # 微小延迟，避免瞬间发送过多
			
			正在处理队列 = false
##UDP网络通信工具类
##提供UDP客户端的创建和数据收发功能，归类于引擎.网络命名空间
## 创建UDP客户端实例（返回内部自定义客户端）
func UDP_创建客户端() -> UDP客户端:
	return UDP客户端.new()


## 自定义UDP服务端内部类（与客户端同级，嵌套在引擎网络中）
class UDP服务端 extends Node:
	var 服务器 = UDPServer.new()  # 底层UDPServer实例
	var 客户端列表 = [] 
	var 超时时间 = 300 #心跳包，超过300秒，就主动对客户端列表删除

	## 启动服务端监听
	## [br]参数:[br]
	##   - 端口: 监听端口，默认为25555[br]
	##   - 绑定IP: 绑定的本地IP，默认为"*"
	func UDP_启动服务(端口: int = 35555, 绑定IP: String = "*"):
		var 启动结果 = 服务器.listen(端口, 绑定IP)
		if 启动结果==OK:
			print("UDP服务端启动成功，监听端口: ", 端口)
		else:
			print("UDP服务端启动失败！端口可能被占用")
		return 启动结果

	## 处理客户端连接和数据（需在_process中调用）
	func UDP_处理数据(回调字典: Dictionary = {}):
		if not 服务器.is_listening():
			return
		
		服务器.poll()

		# 处理新客户端连接
		if 服务器.is_connection_available():
			var 客户端 = 服务器.take_connection()
			var 客户端IP = 客户端.get_packet_ip()
			var 客户端端口 = 客户端.get_packet_port()
			
			# 检查该 IP:端口 是否已在列表中（避免重复添加）
			var 客户端索引 = -1
			for i in 客户端列表.size():
				if 客户端列表[i]["peer"]==客户端:
					客户端索引=i
			#不存在时返回 -1
			if (客户端索引)==-1:
				#客户端列表.append(客户端)
				客户端列表.append({"peer":客户端,"time":引擎.时间.取当前时间戳()})
				
				# 触发"客户端进入"回调（如果存在）
				if "客户端进入" in 回调字典 and 回调字典["客户端进入"] is Callable:
					回调字典["客户端进入"].call(客户端, 客户端IP, 客户端端口)
			else:#更新时间
				客户端列表[客户端索引]["time"]=引擎.时间.取当前时间戳()
				
		# 处理收到的数据
		#for i in 客户端列表.size():
		for i in range(客户端列表.size() - 1, -1, -1):
			#假装是超时心跳包
			if 引擎.时间.取当前时间戳()-客户端列表[i]["time"]>超时时间:
				#超时的客户端，讲被丢弃
				引擎.调试.打印("服务器主动对"+str(客户端列表[i]["peer"].get_packet_ip()+":"+str(客户端列表[i]["peer"].get_packet_port())+"断开了"))
				客户端列表.remove_at(i)
				continue#跳出
				
			var 客户端 = 客户端列表[i]["peer"]

			while 客户端.get_available_packet_count() > 0:
				var 数据 = 客户端.get_packet()
				var 客户端IP = 客户端.get_packet_ip()
				var 客户端端口 = 客户端.get_packet_port()
				
				# 触发"服务端收到消息"回调（如果存在）
				if "服务端收到消息" in 回调字典 and 回调字典["服务端收到消息"] is Callable:
					回调字典["服务端收到消息"].call(客户端, 数据, 客户端IP, 客户端端口)
					
	## 向指定客户端发送数据
	## [br]参数:[br]
	##   - 客户端: 目标客户端（从客户端列表获取）[br]
	##   - 数据: 发送内容（String或PackedByteArray）[br]
	##   - 编码类型: 字符串编码方式，默认为"utf8"
	func UDP_发送给客户端(客户端, 数据, 编码类型: String = "utf8"):
		if 数据 is String:
			if 编码类型 == "utf8":
				客户端.put_packet(数据.to_utf8_buffer())
		elif 数据 is PackedByteArray:
			客户端.put_packet(数据)
		else:
			print("不支持的数据类型")

	## 广播数据给所有已连接客户端
	func UDP_广播数据(数据, 编码类型: String = "utf8"):
		for 客户端 in 客户端列表:
			UDP_发送给客户端(客户端["peer"], 数据, 编码类型)

	## 停止服务端
	func UDP_停止服务():
		服务器.stop()
		客户端列表.clear()
		print("UDP服务端已停止")

	## 获取当前连接的客户端数量
	func UDP_获取客户端数量() -> int:
		return 客户端列表.size()


## 创建UDP服务端实例
func UDP_创建服务端() -> UDP服务端:
	return UDP服务端.new()
