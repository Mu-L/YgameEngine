extends Node
#基于 简单数据库 制作的单一已学习情况
class 基础技能:
	var 技能数据库:=引擎.数据库.技能数据库.new().获取数据库()
	var 已学习技能=[]
	func 学习技能(技能ID:String):
		pass
	func 获取已学习技能列表()->Array:
		return 已学习技能.duplicate(true)
	func 获取是否已学习(技能ID)->bool:
		var 已学习=false
		return 已学习	
	func 计算被动技能总加成()->Dictionary:
		var 加成列表={}
		var 技能ID:String=""
		var 技能类型=技能数据库.获取类型(技能ID)
		if 技能类型=="被动":
			pass
		return 加成列表

class 等级技能:
	pass
