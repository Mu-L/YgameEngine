extends Node

class 道具数据库:
	var 道具库;
	func _init() -> void:
		道具库=引擎.文件.读取文件到变量("res://系统/itemsystem.json")
	func 获取数据库():
		return 道具库
	
	# 1. 按ID精准查询道具完整信息
	func 按ID查询道具(道具ID: String) -> Dictionary:
		if 道具库.has(道具ID):
			return 道具库[道具ID].duplicate()  # 返回副本避免外部修改
		return {}  # 不存在返回空字典
	
	# 2. 获取指定ID道具的单个属性
	func 获取道具属性(道具ID: String, 属性名: String) -> Variant:
		var 道具信息 = 按ID查询道具(道具ID)
		if 道具信息.is_empty():
			引擎.调试.打印("道具ID不存在: " + 道具ID)
			return null
		
		if 道具信息.has(属性名):
			return 道具信息[属性名]
		引擎.调试.打印("道具" + 道具ID + "不存在属性: " + 属性名)
		return null
	
	# 3. 获取指定ID道具的效果字典
	func 获取道具效果(道具ID: String) -> Dictionary:
		# 直接调用属性获取方法，指定"效果"属性
		var 效果 = 获取道具属性(道具ID, "效果")
		if 效果 == null:
			return {}  # 无效果返回空字典
		return 效果.duplicate()  # 返回副本避免外部修改

func 加载道具库() -> 道具数据库:
	var 道具库=道具数据库.new()
	return 道具库
