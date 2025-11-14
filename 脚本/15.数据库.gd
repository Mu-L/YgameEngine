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
				print("道具ID不存在: " + 道具ID)
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
	
	func 获取数据库() -> NPC:
		return NPC.new(NPC库)
	
	class NPC:
		var NPC数据: Dictionary
		
		func _init(原始数据: Dictionary) -> void:
			NPC数据 = 原始数据.duplicate(true)  # 深度复制，避免外部修改
		
		# 通用属性获取方法（复用逻辑）
		func _获取属性(NPCID: String, 属性名: String, 默认值) -> Variant:
			if not NPC数据.has(NPCID):
				print("NPCID不存在: " + NPCID)
				return 默认值
			var npc信息 = NPC数据[NPCID]
			return npc信息[属性名] if npc信息.has(属性名) else 默认值
		
		# 1. 获取指定NPC的完整数据
		func 获取数据(NPCID: String) -> Dictionary:
			return NPC数据[NPCID].duplicate() if NPC数据.has(NPCID) else {}
		
		# 2. 基础信息获取（对应JSON字段）
		func 获取名称(NPCID: String) -> String:
			return _获取属性(NPCID, "名称", "")
		
		func 获取种族(NPCID: String) -> String:
			return _获取属性(NPCID, "种族", "")
		
		func 获取等级(NPCID: String) -> float:
			return _获取属性(NPCID, "等级", 0.0)
		
		func 获取阵营(NPCID: String) -> String:
			return _获取属性(NPCID, "阵营", "")
		
		func 获取描述(NPCID: String) -> String:
			return _获取属性(NPCID, "描述", "")
		
		func 获取图标路径(NPCID: String) -> String:
			return _获取属性(NPCID, "图标路径", "")
		
		# 3. 属性列表获取（单独处理嵌套字典）
		func 获取属性列表(NPCID: String) -> Dictionary:
			var 属性 = _获取属性(NPCID, "属性列表", {})
			return 属性.duplicate() if 属性 is Dictionary else {}
		
		# 5. 获取全部NPC数据（用于批量操作）
		func 获取完整数据() -> Dictionary:
			return NPC数据.duplicate(true)



class NPC技能数据库:
	var NPC技能库 = {}
	
	func _init() -> void:
		if 引擎.文件.是否存在("res://系统/npcskillsystem.json"):
			NPC技能库 = 引擎.文件.读取文件到变量("res://系统/npcskillsystem.json")
	
	func 获取数据库() -> NPC技能:
		return NPC技能.new(NPC技能库)
	
	class NPC技能:
		var 数据: Dictionary
		
		func _init(原始数据: Dictionary) -> void:
			数据 = 原始数据.duplicate(true)
		
		# 获取指定NPC、指定索引的技能ID（对应JSON的"技能"字段）
		func 获取技能(NPCID: String, 索引: int) -> String:
			if not 数据.has(NPCID) or 索引 < 0 or 索引 >= 数据[NPCID].size():
				return ""
			return 数据[NPCID][索引].get("技能", "")
		
		# 获取指定NPC、指定索引的技能几率（对应JSON的"几率"字段）
		func 获取几率(NPCID: String, 索引: int) -> float:
			if not 数据.has(NPCID) or 索引 < 0 or 索引 >= 数据[NPCID].size():
				return 0.0
			return 数据[NPCID][索引].get("几率", 0.0)


class 技能数据库:
	var 技能库={};
	
	func _init() -> void:
		if 引擎.文件.是否存在("res://系统/skillsystem.json"):
			技能库=引擎.文件.读取文件到变量("res://系统/skillsystem.json")
	func 获取数据库():
		return 技能.new(技能库)
	class 技能:
		var 技能数据: Dictionary
		
		func _init(原始数据: Dictionary) -> void:
			技能数据 = 原始数据.duplicate(true)  # 深度复制，避免外部修改原数据
		
		# 核心：通用获取属性方法（复用逻辑，减少重复代码）
		func _获取属性(技能ID: String, 属性名: String, 默认值) -> Variant:
			if not 技能数据.has(技能ID):
				print("技能ID不存在: " + 技能ID)
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
		
		func 获取图标相对路径(技能ID: String) -> String:  # 与JSON的"图标相对路径"对应
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
