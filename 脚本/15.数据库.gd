extends Node
####道具数据库 读取:res://系统/itemsystem.json
####NPC数据库  读取:res://系统/npcsystem.json
####NPC技能数据库 读取:res://系统/npcskillsystem.json
###技能数据库 读取:res://系统/skillsystem.json
class 道具数据库:
	var 道具库 = {}
	
	func _init() -> void:
		if 引擎.文件.是否存在("res://系统/itemsystem.json"):
			道具库=引擎.文件.读取文件到变量("res://系统/itemsystem.json")
	func 获取数据库() -> 道具:
		return 道具.new(道具库)
	
	class 道具:
		var 道具数据: Dictionary
		
		func _init(原始数据: Dictionary) -> void:
			道具数据 = 原始数据.duplicate(true)  # 深度复制
		
		# 核心：通用获取属性方法（复用逻辑，减少重复）
		func _获取属性(道具ID: String, 属性名: String, 默认值) -> Variant:
			if not 道具数据.has(道具ID):
				引擎.调试.打印("道具ID不存在: " + 道具ID)
				return 默认值
			var 道具信息 = 道具数据[道具ID]
			return 道具信息[属性名] if 道具信息.has(属性名) else 默认值
		
		# 1. 按ID查询道具完整信息
		func 获取数据(道具ID: String) -> Dictionary:
			return 道具数据[道具ID].duplicate() if 道具数据.has(道具ID) else {}
		
		# 2. 获取道具效果（复用通用方法）
		func 获取效果(道具ID: String) -> Dictionary:
			var 效果 = _获取属性(道具ID, "效果", {})
			return 效果.duplicate()  if 效果 is Dictionary else {}
		
		# 3. 各类属性获取（全部复用通用方法，精简代码）
		func 获取名称(道具ID: String) -> String:
			return _获取属性(道具ID, "名称", "")
		func 获取图标路径(道具ID: String) -> String:
			return _获取属性(道具ID, "相对图标路径", "")
		func 获取描述(道具ID: String) -> String:
			return _获取属性(道具ID, "描述", "")
				
		func 获取类型(道具ID: String) -> String:
			return _获取属性(道具ID, "类型", "")
		
		func 获取子类(道具ID: String) -> String:
			return _获取属性(道具ID, "子类型", "")
		
		func 获取价格(道具ID: String) -> float:
			return _获取属性(道具ID, "价格", 0.0)
		
		func 获取等级(道具ID: String) -> float:
			return _获取属性(道具ID, "等级", 0.0)
		
		func 获取品质(道具ID: String) -> float:
			return _获取属性(道具ID, "品质", 0.0)
		
		# 4. 获取完整数据
		func 获取完整数据() -> Dictionary:
			return 道具数据.duplicate(true)
	


class NPC数据库:
	var NPC库 = {}  # 统一存储变量名
	func _init() -> void:
		if 引擎.文件.是否存在("res://系统/npcsystem.json"):  # 假设NPC数据文件路径
			NPC库 = 引擎.文件.读取文件到变量("res://系统/npcsystem.json")
	
	func 获取数据库(npcId:String="") -> NPC:
		return NPC.new(NPC库,npcId)
	
	class NPC:
		var NPC数据: Dictionary
		var npcId:String=""
		func _init(原始数据: Dictionary,npcId:String="") -> void:
			self.NPC数据 = 原始数据.duplicate(true)  # 深度复制，避免外部修改
			self.npcId=npcId
		# 通用属性获取方法（复用逻辑）
		func _获取属性(NPCID: String, 属性名: String, 默认值) -> Variant:
			# 优先使用传入的NPCID；如果未传，则使用实例的默认npcId
			var targetId = NPCID if NPCID != "" else self.npcId
			
			# 若最终仍无有效ID，返回默认值并提示
			if targetId == "":
				引擎.调试.打印("未指定NPCID且无默认ID")
				return 默认值
			
			# 检查ID是否存在
			if not NPC数据.has(targetId):
				引擎.调试.打印("NPCID不存在: " + targetId)
				return 默认值
			
			# 返回属性值（不存在则用默认值）
			var npc信息 = NPC数据[targetId]
			return npc信息[属性名] if npc信息.has(属性名) else 默认值
		# 1. 获取指定NPC的完整数据
		func 获取数据(NPCID: String) -> Dictionary:
			return NPC数据[NPCID].duplicate() if NPC数据.has(NPCID) else {}
		
		# 2. 基础信息获取（对应JSON字段）
		func 获取名称(NPCID: String="") -> String:
			return _获取属性(NPCID, "名称", "")
		
		func 获取种族(NPCID: String="") -> String:
			return _获取属性(NPCID, "种族", "")
		
		func 获取等级(NPCID: String="") -> float:
			return _获取属性(NPCID, "等级", 0.0)
		
		func 获取阵营(NPCID: String="") -> String:
			return _获取属性(NPCID, "阵营", "")
		
		func 获取描述(NPCID: String="") -> String:
			return _获取属性(NPCID, "描述", "")
		
		func 获取图标路径(NPCID: String="") -> String:
			return _获取属性(NPCID, "图标路径", "")
		
		
		# 3. 属性列表获取（单独处理嵌套字典）
		func 获取属性列表(NPCID: String="") -> Dictionary:
			var 属性 = _获取属性(NPCID, "属性列表", {})
			return 属性.duplicate() if 属性 is Dictionary else {}
		
		# 5. 获取全部NPC数据（用于批量操作）
		func 获取完整数据() -> Dictionary:
			return NPC数据.duplicate(true)


class NPC技能数据库:
	var NPC技能库 = {}  # 统一存储变量名，与NPC数据库保持一致
	
	func _init() -> void:
		if 引擎.文件.是否存在("res://系统/npcskillsystem.json"):
			NPC技能库 = 引擎.文件.读取文件到变量("res://系统/npcskillsystem.json")
	
	# 与NPC数据库保持一致：返回通用数据库操作实例
	func 获取数据库() -> NPC技能:
		return NPC技能.new(NPC技能库)
	
	class NPC技能:
		var 数据: Dictionary  # 存储所有NPC的技能数据
		
		func _init(原始数据: Dictionary) -> void:
			数据 = 原始数据.duplicate(true)  # 深度复制
		
		# 2. 随机选择技能（返回技能项实例）
		func 获取随机技能(NPCID: String) -> 技能项:
			# 内部临时获取技能列表（不对外暴露）
			var 技能列表 = []
			if 数据.has(NPCID):
				for 技能项字典 in 数据[NPCID]:
					技能列表.append(技能项.new(技能项字典))
			
			if 技能列表.is_empty():
				return 技能项.new({})
			
			var 总几率 = 0.0
			for 技能项实例 in 技能列表:
				总几率 += 技能项实例.获取几率()
			
			if 总几率 <= 0:
				return 技能项.new({})
			
			var 随机值 = randf() * 总几率
			var 累计几率 = 0.0
			for 技能项实例 in 技能列表:
				累计几率 += 技能项实例.获取几率()
				if 随机值 <= 累计几率:
					return 技能项实例
			
			return 技能项.new({})
		
		# 3. 获取全部NPC技能数据（原始字典）
		func 获取完整数据() -> Dictionary:
			return 数据.duplicate(true)
	
	# 新增：技能项内部类（封装原索引获取方法）
	class 技能项:
		var 技能数据: Dictionary  # 单个技能项的原始数据
		
		func _init(技能项字典: Dictionary) -> void:
			技能数据 = 技能项字典.duplicate(true)  # 复制数据
		
		# 原获取技能方法（挪入此类，无需NPCID和索引，直接操作当前技能项）
		func 获取技能ID() -> String:
			return 技能数据.get("技能", "")
		
		# 原获取几率方法（挪入此类）
		func 获取几率() -> float:
			return 技能数据.get("几率", 0.0)
		
		# 原获取属性方法（挪入此类）
		func 获取属性(属性名: String, 默认值 = null) -> Variant:
			return 技能数据.get(属性名, 默认值)
		
		# 获取当前技能项的完整字典数据
		func 获取数据() -> Dictionary:
			return 技能数据.duplicate(true)


class 技能数据库:
	var 技能库={};
	
	func _init() -> void:
		if 引擎.文件.是否存在("res://系统/skillsystem.json"):
			技能库=引擎.文件.读取文件到变量("res://系统/skillsystem.json")
	func 获取数据库()-> 技能:
		return 技能.new(技能库)
	class 技能:
		var 技能数据: Dictionary
		
		func _init(原始数据: Dictionary) -> void:
			技能数据 = 原始数据.duplicate(true)  # 深度复制，避免外部修改原数据
		
		# 核心：通用获取属性方法（复用逻辑，减少重复代码）
		func _获取属性(技能ID: String, 属性名: String, 默认值) -> Variant:
			if not 技能数据.has(技能ID):
				引擎.调试.打印("技能ID不存在: " + 技能ID)
				return 默认值
			var 技能信息 = 技能数据[技能ID]
			return 技能信息[属性名] if 技能信息.has(属性名) else 默认值
		
		# 1. 按ID查询技能完整信息
		func 获取数据(技能ID: String) -> Dictionary:
			return 技能数据[技能ID].duplicate() if 技能数据.has(技能ID) else {}
		
		# 2. 获取技能效果（复用通用方法）
		func 获取效果(技能ID: String) -> Dictionary:
			var 效果 = _获取属性(技能ID, "效果", {})
			return 效果.duplicate() if 效果 is Dictionary else {}
		
		# 3. 各类属性获取（与JSON字段名完全一致）
		func 获取名称(技能ID: String) -> String:
			return _获取属性(技能ID, "名称", "")
		
		func 获取图标路径(技能ID: String) -> String:  # 与JSON的"图标相对路径"对应
			return _获取属性(技能ID, "图标相对路径", "")
		
		func 获取伤害(技能ID: String) -> float:  # 与JSON的"伤害"对应
			return _获取属性(技能ID, "伤害", 0.0)
		
		func 获取消耗(技能ID: String) -> float:  # 与JSON的"消耗"对应
			return _获取属性(技能ID, "消耗", 0.0)
		
		func 获取伤害类型(技能ID: String) -> String:  # 与JSON的"伤害类型"对应
			return _获取属性(技能ID, "伤害类型", "")
		
		func 获取目标(技能ID: String) -> float:  # 与JSON的"目标"对应
			return _获取属性(技能ID, "目标", 0.0)
		
		func 获取射程(技能ID: String) -> float:  # 与JSON的"射程"对应
			return _获取属性(技能ID, "射程", 0.0)
		
		func 获取伤害倍率(技能ID: String) -> float:  # 与JSON的"伤害倍率"对应
			return _获取属性(技能ID, "伤害倍率", 0.0)
		
		func 获取描述(技能ID: String) -> String:  # 与JSON的"描述"对应
			return _获取属性(技能ID, "描述", "")
		
		func 获取类型(技能ID: String) -> String:  # 与JSON的"类型"对应
			return _获取属性(技能ID, "类型", "")
		
		# 4. 获取完整数据
		func 获取完整数据() -> Dictionary:
			return 技能数据.duplicate(true)	
	pass


class 掉落数据库:
	var 掉落库 = {}  #
	
	func _init() -> void:
		if 引擎.文件.是否存在("res://系统/drop_data.json"):
			掉落库 = 引擎.文件.读取文件到变量("res://系统/drop_data.json")
	
	# 与NPC数据库保持一致：返回通用数据库操作实例
	func 获取数据库() -> 掉落:
		return 掉落.new(掉落库)
	class 掉落:
		var 掉落数据: Dictionary
		func _init(原始数据: Dictionary) -> void:
			掉落数据 = 原始数据.duplicate(true)  # 深度复制，避免外部修改原数据
		pass
		# 1. 获取完整数据
		func 获取完整数据() -> Dictionary:
			return 掉落数据.duplicate(true)	
		func 开始掉落(配置:String,等级:float=1.0,宝物是否重复:bool=true):
			var 最终掉落=[]
			var 掉落表=掉落数据[配置]
			if 掉落表.类别=="掉落":
				for i in 掉落表.掉落:					
					if 引擎.数学.随机_取0到1的浮点数() < i.掉落几率:
						if 等级>=i.最小等级 and 等级<=i.最大等级:
							var 掉落数量=引擎.数学.随机_取范围整数(i.掉落最小数量,i.掉落最大数量)
							最终掉落.append({物品ID=i.物品ID,数量=掉落数量})
				return 最终掉落
			if 掉落表.类别 == "宝物":
				if 宝物是否重复==true:
					var 权重表 = []
					
					for 宝物 in 掉落表.宝物:
						权重表.append([宝物.物品ID, 宝物.权重])
					
					var 掉落次数 = int(掉落表.权重的掉落数量)
					for i in 掉落次数:
						# 1. 权重选择具体物品ID
						var 选中物品ID = 引擎.数学.随机_权重选择(权重表)
						
						# 2. 根据物品ID找到对应的宝物对象
						var 选中宝物 = null  # GDScript 中用 null 表示空
						for 宝物 in 掉落表.宝物:
							if 宝物.物品ID == 选中物品ID:
								选中宝物 = 宝物
								break
						
						# 3. 获取该宝物的数量范围并随机
						if 选中宝物 != null:  # GDScript 中判断非空
							var 数量 = 引擎.数学.随机_取范围整数(
								选中宝物.掉落最小数量,
								选中宝物.掉落最大数量
							)
							#print("选中物品: ", 选中物品ID, "，数量: ", 数量)
							最终掉落.append({物品ID=选中物品ID,数量=数量})	
					return 最终掉落
				#var 最终掉落 = []
				if 宝物是否重复==false:
					var 目标掉落次数 = int(掉落表.权重的掉落数量)
					var 剩余宝物 = 掉落表.宝物.duplicate()  # 复制宝物列表，用于移除已选
					
					# for 循环最多执行 目标掉落次数 次
					for i in  目标掉落次数:
						# 若剩余宝物为空，提前终止（避免重复）
						if 剩余宝物.is_empty():
							break
						
						# 1. 基于剩余宝物构建权重表
						var 权重表 = []
						for 宝物 in 剩余宝物:
							权重表.append([宝物.物品ID, 宝物.权重])
						
						# 2. 权重选择物品ID
						var 选中物品ID = 引擎.数学.随机_权重选择(权重表)
						
						# 3. 找到宝物并从剩余列表中移除
						var 选中宝物 = null
						for j in range(剩余宝物.size()):
							if 剩余宝物[j].物品ID == 选中物品ID:
								选中宝物 = 剩余宝物[j]
								剩余宝物.remove_at(j)
								break
						
						# 4. 计算数量并添加
						if 选中宝物 != null:
							var 数量 = 引擎.数学.随机_取范围整数(
								选中宝物.掉落最小数量,
								选中宝物.掉落最大数量
							)
							最终掉落.append({ "物品ID"=选中物品ID, "数量"=数量 })
					
					return 最终掉落
				

class 增益数据库:
	var 增益库 = {}  # 统一存储变量名
	
	func _init() -> void:
		if 引擎.文件.是否存在("res://系统/buffSystem.json"):
			增益库 = 引擎.文件.读取文件到变量("res://系统/buffSystem.json")
		
	# 
	func 获取数据库() -> 增益:
		return 增益.new(增益库)
	
	class 增益:
		var 增益数据: Dictionary
		func _init(原始数据: Dictionary) -> void:
			增益数据 = 原始数据.duplicate(true)  # 深度复制，避免外部修改原数据
		pass
		# 核心：通用获取属性方法（复用逻辑，减少重复代码）
		func _获取属性(增益ID: String, 属性名: String, 默认值) -> Variant:
			if not 增益数据.has(增益ID):
				引擎.调试.打印("增益ID不存在: " + 增益ID)
				return 默认值
			var 增益信息 = 增益数据[增益ID]
			return 增益信息[属性名] if 增益信息.has(属性名) else 默认值
			
		func 获取名称(增益ID:String) -> String:
			return _获取属性(增益ID, "名称", "")
		
		func 获取持续类型(增益ID:String) -> String:
			return _获取属性(增益ID, "持续类型", "")
		
		func 获取堆叠次数(增益ID:String) -> float:
			return _获取属性(增益ID, "堆叠次数", 1.0)
		
		func 获取规则(增益ID:String) -> String:
			return _获取属性(增益ID, "规则", "")
		
		func 获取描述(增益ID:String) -> String:
			return _获取属性(增益ID, "描述", "")
		
		func 获取持续值(增益ID:String) -> float:
			return _获取属性(增益ID, "持续值", 0.0)
		
		func 获取图标(增益ID:String) -> String:
			return _获取属性(增益ID, "图标路径", "")
		
		func 获取效果列表(增益ID:String) -> Dictionary:
			var 效果 = _获取属性(增益ID, "效果", {})
			return 效果.duplicate() if 效果 is Dictionary else {}
		func 获取数据(增益ID: String) -> Dictionary:
			return 增益数据[增益ID].duplicate() if 增益数据.has(增益ID) else {}
		func 获取完整数据() -> Dictionary:
			return 增益数据.duplicate(true)		

class 增益效果数据库:
	var 增益库 = {}  # 统一存储变量名
	
	func _init() -> void:
		if 引擎.文件.是否存在("res://系统/buff.json"):
			增益库 = 引擎.文件.读取文件到变量("res://系统/buff.json")
		
	# 
	func 获取数据库() -> 增益:
		return 增益.new(增益库)
	class 增益:
		var 增益数据: Dictionary
		func _init(原始数据: Dictionary) -> void:
			增益数据 = 原始数据.duplicate(true)  # 深度复制，避免外部修改原数据
		func 获取技能增益数据(技能ID:String)->Dictionary:
			var 获取的字典={}
			if 增益数据.技能.has(技能ID):
				获取的字典=增益数据.技能[技能ID]
			return 获取的字典
		func 获取物品增益数据(物品ID:String)->Dictionary:
			var 获取的字典={}
			if 增益数据.物品.has(物品ID):
				获取的字典=增益数据.物品[物品ID]
			return 获取的字典
		func 计算增益技能(技能ID:String)->Array:
			var 模拟数组=[]
			var 增益效果数据=获取技能增益数据(技能ID)
			if 增益效果数据.has("增益"):
				for 增益 in 增益效果数据.增益:
					var 随机值 = 引擎.数学.随机_取0到1的浮点数()  # 生成0.0到1.0之间的随机数
					if 随机值 <= 增益.几率:
						模拟数组.append(增益.ID)
			return 模拟数组
		func 计算增益物品(物品ID:String)->Array:
			var 模拟数组=[]
			var 增益效果数据=获取物品增益数据(物品ID)
			if 增益效果数据.has("增益"):
				for 增益 in 增益效果数据.增益:
					var 随机值 = 引擎.数学.随机_取0到1的浮点数()  # 生成0.0到1.0之间的随机数
					if 随机值 <= 增益.几率:
						模拟数组.append(增益.ID)
			return 模拟数组
