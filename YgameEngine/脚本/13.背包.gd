extends Node
class 角色背包:
	## 道具ID  数量
	var 背包=[]
	var 加密=false
	func 查询背包()->Array:
		return self.背包
		# 添加道具到背包
	func 添加道具(C_道具ID: String, C_操作数量: float=1):
		#print(self.背包)
		# 查找道具是否已在背包中
		var index = 获取道具索引(C_道具ID)
		if index != -1:
			# 如果存在，增加数量
			
			if self.加密:
				#加密
				print()
				var 操作=引擎.加解密.浮点数解密(self.背包[index]["数量"]) + C_操作数量
				self.背包[index]["数量"]=引擎.加解密.浮点数加密(操作)
			else:
				self.背包[index]["数量"] += C_操作数量
		else:
			if self.加密:
				self.背包.append({"道具ID": C_道具ID, "数量": 引擎.加解密.浮点数加密(C_操作数量)})
			else:
				# 如果不存在，添加新道具
				self.背包.append({"道具ID": C_道具ID, "数量": C_操作数量})

	# 获取道具在背包中的索引
	func 获取道具索引(C_道具ID: String) -> int:
		for i in self.背包.size():
			if self.背包[i]["道具ID"] == C_道具ID:
				return i
		return -1
	

	# 减少背包中的道具 ### 使用减少具时,请先判断数量
	func 减少道具(C_道具ID: String, C_操作数量: float=1):
		var index = 获取道具索引(C_道具ID)
		#self.背包[index]["数量"] -= C_操作数量
		if self.加密:
			#加密
			var 操作=引擎.加解密.浮点数解密(self.背包[index]["数量"]) - C_操作数量
			self.背包[index]["数量"]=引擎.加解密.浮点数加密(操作)
		else:
			self.背包[index]["数量"] -= C_操作数量
	
	# 获取道具在背包中的数量
	func 获取道具数量(C_道具ID: String) -> float:
		var index = 获取道具索引(C_道具ID)
		if index != -1:
			if self.加密:
				return 引擎.加解密.浮点数解密(self.背包[index]["数量"])
			else:
				return self.背包[index]["数量"]
		return 0
	
	
func 创建背包(加密:bool=false) -> 角色背包:
	var a=角色背包.new()
	a.加密=加密
	return a
	
	
	
	
	
###如果有附加 好麻烦
	#func 添加道具(C_道具ID: String, C_操作数量: int = 1, 回调: Callable = Callable()):
		#var 临时道具 = {
			#"道具ID": C_道具ID,
			#"数量": C_操作数量,
			#"附加": {}
		#}
		#
		#if 回调.is_valid():
			#回调.call(临时道具)
		#
		#var 回调设置的附加属性 = 临时道具.附加
		##print("回调中设置的附加属性：", 回调设置的附加属性)
		#
		#var index = 获取道具索引(C_道具ID, 回调设置的附加属性)
		##print("索引：", index, " 当前背包：", self.背包)  # 打印当前背包状态
		#if index != -1:
			#self.背包[index]["数量"] += C_操作数量
		#else:
			#背包.append(临时道具)
			##print("添加新道具后：",self.背包)  # 确认添加成功
#
	#func 获取道具索引(C_道具ID: String, 目标扩展: Dictionary = {}) -> int:
		##print("查找索引，当前背包：", 背包)  # 打印当前背包
		#for i in self.背包.size():
			#var 道具 =  self.背包[i]
			#if 道具["道具ID"] != C_道具ID:
				#continue
			#
			#var 道具扩展 = 道具["附加"]
			#if 道具扩展 == 目标扩展:
				#return i
		#return -1
