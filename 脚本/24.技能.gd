extends Node
#基于 简单数据库 制作的单一已学习情况
class 基础技能:
	var 技能数据库:=引擎.数据库.技能数据库.new().获取数据库()
	var 已学习技能=[]
	
	# 学习技能
	func 学习技能(技能ID:String) -> bool:
		if not 获取是否已学习(技能ID):
			已学习技能.append(技能ID)
			return true
		else:
			return false
	# 忘记技能
	func 忘记技能(技能ID:String) -> bool:
		if 获取是否已学习(技能ID):
			已学习技能.erase(技能ID)
			引擎.调试.打印("已忘记技能: " + 技能ID + " - " + 技能数据库.获取名称(技能ID))
			return true
		else:
			return false
	# 获取已学习技能列表
	func 获取已学习技能列表() -> Array:
		return 已学习技能.duplicate(true)
	
	# 获取是否已学习
	func 获取是否已学习(技能ID:String) -> bool:
		return 已学习技能.has(技能ID)
	
	# 计算被动技能总加成
	func 计算被动技能总加成() -> Dictionary:
		var 加成列表 = {}
		for 技能ID in 已学习技能:
			var 技能类型 = 技能数据库.获取类型(技能ID)
			if 技能类型 == "被动":
				var 技能效果 = 技能数据库.获取效果(技能ID)
				for 属性名 in 技能效果:
					var 当前加成 = 技能效果[属性名]
					if 加成列表.has(属性名):
						加成列表[属性名] += 当前加成
					else:
						加成列表[属性名] = 当前加成
		return 加成列表
	
	# 清空已学习技能
	func 清空已学习技能() -> bool:
		已学习技能.clear()
		return true

# 带等级系统的技能管理类
class 等级技能:
	var 技能数据库:=引擎.数据库.技能数据库.new().获取数据库()
	var 等级配置库:Dictionary = {}
	var 已学习技能:Dictionary = {}  # 存储技能实例
	
	# 注册的检查器和处理器
	var 升级条件检查器:Dictionary = {}
	var 升级消耗处理器:Dictionary = {}
	
	func _init() -> void:
		# 加载等级配置
		if 引擎.文件.是否存在("res://系统/skill_levels.json"):
			等级配置库 = 引擎.文件.读取文件到变量("res://系统/skill_levels.json")
		else:
			引擎.调试.打印("技能等级配置文件不存在！")
	
	# ==================== 注册接口 ====================
	func 注册升级条件检查器(检查器名称:String, 检查函数:Callable) -> void:
		升级条件检查器[检查器名称] = 检查函数
		print("触发1")
	
	func 注册升级消耗处理器(处理器名称:String, 处理函数:Callable) -> void:
		升级消耗处理器[处理器名称] = 处理函数
		print("触发2")
	
	# ==================== 技能管理 ====================
	#func 学习技能(技能ID:String) -> bool:
		#if not 获取是否已学习(技能ID):
			## 检查技能是否存在且有等级配置
			#if 技能数据库.获取数据(技能ID) and 等级配置库.has(技能ID):
				#已学习技能[技能ID] = 技能实例.new(技能ID, self)
				#引擎.调试.打印("已学习技能: " + 技能ID + " - " + 技能数据库.获取名称(技能ID))
				#return true
			#else:
				#引擎.调试.打印("技能不存在或无等级配置: " + 技能ID)
				#return false
		#return false
	func 学习技能(技能ID:String) -> bool:
		if not 获取是否已学习(技能ID):
			# 1. 检查技能是否存在且有等级配置
			if not 技能数据库.获取数据(技能ID) or not 等级配置库.has(技能ID):
				引擎.调试.打印("技能不存在或无等级配置: " + 技能ID)
				return false
			
			# 2. 获取学习技能的需求（1级的升级需求）
			var 等级配置 = 等级配置库.get(技能ID, {})
			var 等级属性 = 等级配置.get("等级属性", {})
			var 一级配置 = 等级属性.get("1", {})
			var 学习需求 = 一级配置.get("升级需求", {})
			
			# 3. 获取学习配置（如果有专门的学习配置则优先使用）
			var 学习配置 = 等级配置.get("学习配置", {})
			var 学习条件检查器 = 学习配置.get("条件检查器", [])
			
			# 如果没有专门的学习配置，使用默认配置
			if 学习条件检查器.is_empty():
				学习条件检查器 = 等级配置.get("升级配置", {}).get("条件检查器", [])
			
			# 4. 检查学习条件
			var 满足学习条件 = true
			
			for 检查器名称 in 学习条件检查器:
				if 升级条件检查器.has(检查器名称):
					# 创建临时的技能实例用于检查
					var 临时技能实例 = 技能实例.new(技能ID, self)
					if not 升级条件检查器[检查器名称].call(临时技能实例, 学习需求):
						满足学习条件 = false
						break
				else:
					引擎.调试.打印错误("未注册的学习条件检查器: " + 检查器名称)
					满足学习条件 = false
					break
			
			if not 满足学习条件:
				引擎.调试.打印("不满足学习技能的条件: " + 技能ID)
				return false
			
			# 5. 处理学习消耗（如果有）
			var 学习消耗处理器 = 学习配置.get("消耗处理器", [])
			if 学习消耗处理器.is_empty():
				学习消耗处理器 = 等级配置.get("升级配置", {}).get("消耗处理器", [])
			
			var 临时技能实例 = 技能实例.new(技能ID, self)
			for 处理器名称 in 学习消耗处理器:
				if 升级消耗处理器.has(处理器名称):
					升级消耗处理器[处理器名称].call(临时技能实例, 学习需求)
			
			# 6. 学习技能
			已学习技能[技能ID] = 技能实例.new(技能ID, self)
			引擎.调试.打印("已学习技能: " + 技能ID + " - " + 技能数据库.获取名称(技能ID))
			return true
		
		return false
	
	func 忘记技能(技能ID:String) -> bool:
		if 获取是否已学习(技能ID):
			已学习技能.erase(技能ID)
			引擎.调试.打印("已忘记技能: " + 技能ID + " - " + 技能数据库.获取名称(技能ID))
			return true
		return false
	
	func 获取是否已学习(技能ID:String) -> bool:
		return 已学习技能.has(技能ID)
	
	
	func 获取已学习技能详情() -> Array:
		#"""获取包含详细信息的已学习技能列表（用于存档）"""
		var 技能详情列表 = []
		for 技能ID in 已学习技能:
			var 技能实例 = 已学习技能[技能ID]
			技能详情列表.append({
				"技能ID": 技能ID,
				"当前等级": 技能实例.当前等级,
				"熟练度": 技能实例.熟练度,
				"技能名称": 技能实例.获取技能名称()
			})
		return 技能详情列表

	func 获取存档数据() -> Dictionary:
	   # """获取完整的存档数据"""
		var 存档数据 = {
			"已学习技能": [],
			"技能状态": {}
		}
		
		for 技能ID in 已学习技能:
			var 技能实例 = 已学习技能[技能ID]
			存档数据["已学习技能"].append(技能ID)
			存档数据["技能状态"][技能ID] = {
				"当前等级": 技能实例.当前等级,
				"熟练度": 技能实例.熟练度
			}
		
		return 存档数据

	func 从存档恢复(存档数据: Dictionary) -> void:
	   # """从存档数据恢复技能状态"""
		# 清空现有数据
		已学习技能.clear()
		
		# 恢复已学习技能
		for 技能ID in 存档数据.get("已学习技能", []):
			# 重新创建技能实例
			if 技能数据库.获取数据(技能ID) and 等级配置库.has(技能ID):
				var 技能实例 = 技能实例.new(技能ID, self)
				已学习技能[技能ID] = 技能实例
				
				# 恢复技能状态
				var 技能状态 = 存档数据.get("技能状态", {}).get(技能ID, {})
				技能实例.当前等级 = 技能状态.get("当前等级", 1)
				技能实例.熟练度 = 技能状态.get("熟练度", 0.0)

	# 重写获取已学习技能列表方法，保持向后兼容
	func 获取已学习技能列表() -> Array:
		#"""获取已学习技能ID列表（兼容旧接口）"""
		return 已学习技能.keys()

	func 获取已学习技能带等级() -> Dictionary:
	   # """获取包含等级信息的已学习技能字典"""
		var 技能等级字典 = {}
		for 技能ID in 已学习技能:
			var 技能实例 = 已学习技能[技能ID]
			技能等级字典[技能ID] = {
				"当前等级": 技能实例.当前等级,
				"最大等级": 技能实例.获取最大等级(),
				"熟练度": 技能实例.熟练度,
				
			}
		return 技能等级字典
	
	func 获取技能实例(技能ID:String) -> Variant:
		return 已学习技能.get(技能ID, null)
	
	func 清空已学习技能() -> void:
		已学习技能.clear()
	
	# ==================== 加成计算 ====================
	func 计算被动技能总加成() -> Dictionary:
		var 总加成:Dictionary = {}
		
		for 技能ID in 已学习技能:
			var 技能实例 = 已学习技能[技能ID]
			if 技能数据库.获取类型(技能ID) == "被动":
				var 技能加成 = 技能实例.获取当前属性加成()
				for 属性名 in 技能加成:
					var 当前值 = 技能加成[属性名]
					if 总加成.has(属性名):
						总加成[属性名] += 当前值
					else:
						总加成[属性名] = 当前值
		
		return 总加成
	
	# ==================== 内部类：技能实例 ====================
	class 技能实例:
		var 技能ID:String
		var 等级技能系统:等级技能
		var 当前等级:int = 1
		var 熟练度:float = 0.0
		
		func _init(技能ID:String, 等级技能系统:等级技能) -> void:
			self.技能ID = 技能ID
			self.等级技能系统 = 等级技能系统
		
		# 获取基础信息
		func 获取技能名称() -> String:
			return 等级技能系统.技能数据库.获取名称(技能ID)
		
		func 获取技能类型() -> String:
			return 等级技能系统.技能数据库.获取类型(技能ID)
		
		func 获取最大等级() -> int:
			return 等级技能系统.等级配置库.get(技能ID, {}).get("最大等级", 1)
		
		func 获取升级配置() -> Dictionary:
			return 等级技能系统.等级配置库.get(技能ID, {}).get("升级配置", {})
		
		func 获取等级配置(等级:int) -> Dictionary:
			var 等级属性 = 等级技能系统.等级配置库.get(技能ID, {}).get("等级属性", {})
			return 等级属性.get(str(等级), {})
		
		# 属性加成获取
		func 获取当前属性加成() -> Dictionary:
			var 等级配置 = self.获取等级配置(当前等级)
			return 等级配置.get("属性加成", {})
		
		func 获取等级属性加成(等级:int) -> Dictionary:
			var 等级配置 = self.获取等级配置(等级)
			return 等级配置.get("属性加成", {})
		
		# 升级需求获取
		func 获取当前升级需求() -> Dictionary:
			if 当前等级 >= self.获取最大等级():
				return {}
			var 下一级配置 = self.获取等级配置(当前等级 + 1)
			return 下一级配置.get("升级需求", {})
		
		# 熟练度管理
		func 增加熟练度(数值:float,自动升级:bool=false) -> void:
			if 当前等级 >= self.获取最大等级():
				return
			熟练度 += 数值
			if 自动升级:
				尝试升级()
			
		
		
		# 核心升级逻辑
		# 修改技能实例中的尝试升级方法
		func 尝试升级() -> bool:
			if 当前等级 >= self.获取最大等级():
				return false
			
			var 升级配置 = self.获取升级配置()
			var 升级需求 = self.获取当前升级需求()
			
			# 1. 检查所有升级条件
			var 所有条件满足 = true
			var 条件检查器列表 = 升级配置.get("条件检查器", [])
			
			for 检查器名称 in 条件检查器列表:
				if 等级技能系统.升级条件检查器.has(检查器名称):
					if not 等级技能系统.升级条件检查器[检查器名称].call(self, 升级需求):
						所有条件满足 = false
						break
				else:
					引擎.调试.打印错误("未注册的检查器: " + 检查器名称)
					#引擎.调试.打印("未注册的检查器: " + 检查器名称)
					所有条件满足 = false
					break
			
			if not 所有条件满足:
				return false
			
			# 2. 处理所有消耗
			var 消耗处理器列表 = 升级配置.get("消耗处理器", [])
			
			for 处理器名称 in 消耗处理器列表:
				if 等级技能系统.升级消耗处理器.has(处理器名称):
					等级技能系统.升级消耗处理器[处理器名称].call(self, 升级需求)
			
			# 3. 升级成功（只升一级）
			当前等级 += 1
			引擎.调试.打印("技能【" + self.获取技能名称() + "】升级到" + str(当前等级) + "级！")
			
			# 关键修改：返回true但不再自动继续升级
			return true
		
		# 获取技能完整信息
		func 获取技能信息() -> Dictionary:
			return {
				"ID": 技能ID,
				"名称": self.获取技能名称(),
				"类型": self.获取技能类型(),
				"当前等级": 当前等级,
				"最大等级": self.获取最大等级(),
				"熟练度": 熟练度,
				"当前加成": self.获取当前属性加成(),
				"升级需求": self.获取当前升级需求(),
				
			}
		
		# 获取显示用的描述
		func 获取技能描述() -> String:
			var 基础描述 = 等级技能系统.技能数据库.获取描述(技能ID)
			var 当前加成 = self.获取当前属性加成()
			
			var 描述文本 = 基础描述
			描述文本 += "\n等级: " + str(当前等级) + "/" + str(self.获取最大等级())
			描述文本 += "\n当前效果："
			for 属性名 in 当前加成:
				描述文本 += "\n- " + 属性名 + ": " + str(当前加成[属性名])
			
			if 当前等级 < self.获取最大等级():
				var 升级需求 = self.获取当前升级需求()
				描述文本 += "\n升级需求："
				for 需求名 in 升级需求:
					描述文本 += "\n- " + 需求名 + ": " + str(升级需求[需求名])
			
			return 描述文本
