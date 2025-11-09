extends Node
class 角色背包:
	## 道具ID  数量
	var 背包=[]
	var 加密=false #记录背包是否加密
	# 构造函数：初始化时设置加密状态
	func _init(加密状态: bool = false):
		self.加密 = 加密状态  # 用参数初始化加密属性
	func 获取占用数量()->int:
		return self.背包.size()
	func 获取数据()->Array:
		return self.背包
		# 添加道具到背包
	
	#数量会自动给解码可读
	func 获取索引数据(索引:int) -> Dictionary:
		if 索引 >= 0 and 索引 < self.背包.size():
			var 格子数据 = self.背包[索引].duplicate()  # 复制一份数据，避免直接修改原数组里的内容
			if self.加密 and 格子数据.has("数量"):
				var 解密后数量 = 引擎.加解密.浮点数解密(格子数据["数量"])
				格子数据["数量"] = 解密后数量
			return 格子数据
			#var 操作=引擎.加解密.浮点数解密
		return {}  # 索引越界返回空字典，方便调用处处理
		
	func 添加道具(C_道具ID: String, C_操作数量: float=1,可堆叠: bool=true):
		# 不可堆叠道具处理（新增逻辑）
		if not 可堆叠:
			# 每个道具单独占格，用三元表达式处理数量加密
			for i in range(C_操作数量):
				var 格子数据 = {
					"道具ID": C_道具ID,
					"数量": 引擎.加解密.浮点数加密(1) if self.加密 else 1,
					"唯一ID": 引擎.字符串.获取不重复随机码()  # 唯一ID不加密
				}
				self.背包.append(格子数据)
			return true
		# 原有可堆叠逻辑（完全保留，未作任何修改）
		# 查找道具是否已在背包中
		var index = 获取道具索引(C_道具ID)
		if index != -1:
			# 如果存在，增加数量			
			if self.加密:
				#加密
				if !引擎.加解密.是否作弊:
					var 操作=引擎.加解密.浮点数解密(self.背包[index]["数量"]) + C_操作数量
					self.背包[index]["数量"]=引擎.加解密.浮点数加密(操作)
					return true
				else:
					return false
			else:
				self.背包[index]["数量"] += C_操作数量
				return true
		else:
			if self.加密:
				self.背包.append({"道具ID": C_道具ID, "数量": 引擎.加解密.浮点数加密(C_操作数量)})
			else:
				# 如果不存在，添加新道具
				self.背包.append({"道具ID": C_道具ID, "数量": C_操作数量})
			return true

	# 获取道具在背包中的索引
	func 获取道具索引(C_道具ID: String) -> int:
		for i in self.背包.size():
			if self.背包[i]["道具ID"] == C_道具ID:
				return i
		return -1
		
	func 获取道具索引_唯一ID(唯一ID: String) -> int:
		for i in self.背包.size():
			if self.背包[i].has("唯一ID") and self.背包[i]["唯一ID"] == 唯一ID:
				return i
		return -1

	# 减少背包中的道具 ### 使用减少具时,请先判断数量
	func 减少道具(C_道具ID: String, C_操作数量: float=1,唯一ID: String=""):
		#唯一ID删除处理
		if 唯一ID != "":
			var index = 获取道具索引_唯一ID(唯一ID)
			if index == -1:
				return false  # 未找到该唯一道具
			self.背包.remove_at(index)
			return true
		#修复尝试通过非 唯一ID处理 直接删除道具 
		var index = 获取道具索引(C_道具ID)
		if ("唯一ID" in 获取索引数据(index)) ==true:
			print("检测到是唯一ID,且通过非ID删除,这里已拦截,请通过唯一ID删除")
			return false
		#非唯一处理 
		if self.加密:
			#加密
			if !引擎.加解密.是否作弊:
				var 操作=引擎.加解密.浮点数解密(self.背包[index]["数量"]) - C_操作数量
				self.背包[index]["数量"]=引擎.加解密.浮点数加密(操作)
				return true
			else:
				return false
		else:
			self.背包[index]["数量"] -= C_操作数量
			return true
	
	# 获取道具在背包中的数量
	func 获取道具数量(C_道具ID: String) -> float:
		var index = 获取道具索引(C_道具ID)
		if index != -1:
			if self.加密:
				return 引擎.加解密.浮点数解密(self.背包[index]["数量"])
			else:
				return self.背包[index]["数量"]
		return 0
	func 获取指定类型道具(道具数据库:引擎.数据库.道具数据库.道具 = 引擎.数据库.道具数据库.new().获取数据库(),类型:String=""):#?
		var 新组 = []
		for i in 背包:
			if 道具数据库.获取道具分类(i["道具ID"]) == 类型:
				新组.append(i)
		return 新组
		
	func 获取指定子类道具(道具数据库:引擎.数据库.道具数据库.道具 = 引擎.数据库.道具数据库.new().获取数据库(),类型:String="",子类型:String=""):#?
		var 新组 = []
		for i in 背包:
			if 道具数据库.获取道具分类(i["道具ID"]) == 类型 and 道具数据库.获取道具子类(i["道具ID"]) ==子类型 :
				新组.append(i)
		return 新组

	#先排序分类,子类,在排序等级,等级相同,在排序品质,需要传入数据库
	func 背包排序(道具数据库:引擎.数据库.道具数据库.道具, 是否反向排序: bool = true):
		# 按分类排序
		背包.sort_custom(func(a, b):
			
			var a分类 = 道具数据库.获取类型(a["道具ID"])
			var b分类 = 道具数据库.获取类型(b["道具ID"])
			if 是否反向排序:
				if a分类 < b分类:
					return true
				elif a分类 > b分类:
					return false
				else:
					# 分类相同，按子类排序
					var a子类 = 道具数据库.获取子类(a["道具ID"])
					var b子类 = 道具数据库.获取子类(b["道具ID"])
					if a子类 < b子类:
						return true
					elif a子类 > b子类:
						return false
					else:
						# 子类相同，按等级排序
						var a等级 = 道具数据库.获取等级(a["道具ID"])
						var b等级 = 道具数据库.获取等级(b["道具ID"])
						if a等级 < b等级:
							return true
						elif a等级 > b等级:
							return false
						else:
							# 等级相同，按品质排序
							var a品质 = 道具数据库.获取品质(a["道具ID"])
							var b品质 = 道具数据库.获取品质(b["道具ID"])
							if a品质 < b品质:
								return true
							elif a品质 > b品质:
								return false
							else:
								return false
			else:
				if a分类 < b分类:
					return false
				elif a分类 > b分类:
					return true
				else:
					# 分类相同，按子类排序
					var a子类 = 道具数据库.获取子类(a["道具ID"])
					var b子类 = 道具数据库.获取子类(b["道具ID"])
					if a子类 < b子类:
						return false
					elif a子类 > b子类:
						return true
					else:
						# 子类相同，按等级排序
						var a等级 = 道具数据库.获取等级(a["道具ID"])
						var b等级 = 道具数据库.获取等级(b["道具ID"])
						if a等级 < b等级:
							return false
						elif a等级 > b等级:
							return true
						else:
							# 等级相同，按品质排序
							var a品质 = 道具数据库.获取品质(a["道具ID"])
							var b品质 = 道具数据库.获取品质(b["道具ID"])
							if a品质 < b品质:
								return false
							elif a品质 > b品质:
								return true
							else:
								return false
		)

		
	
	
	
	
