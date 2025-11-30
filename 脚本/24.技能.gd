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

class 等级技能:
	pass
