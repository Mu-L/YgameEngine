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
	var NPC={};
	
	func _init() -> void:
		if 引擎.文件.是否存在("res://系统/npcsystem.json"):
			NPC=引擎.文件.读取文件到变量("res://系统/npcsystem.json")
	func 获取数据库():
		return NPC
	
	pass



class NPC技能数据库:
	var NPC技能={};
	
	func _init() -> void:
		if 引擎.文件.是否存在("res://系统/npcskillsystem.json"):
			NPC技能=引擎.文件.读取文件到变量("res://系统/npcskillsystem.json")
	func 获取数据库():
		return NPC技能
	
	pass


class 技能数据库:
	var 技能={};
	
	func _init() -> void:
		if 引擎.文件.是否存在("res://系统/skillsystem.json"):
			技能=引擎.文件.读取文件到变量("res://系统/skillsystem.json")
	func 获取数据库():
		return 技能
	
	pass
