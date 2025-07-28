extends Node
class 角色背包:
	## 道具ID  数量
	var 背包=[]
	func 查询背包()->Array:
		return self.背包
		# 添加道具到背包
	func 添加道具(C_道具ID: String, C_操作数量: int=1):
		
		# 查找道具是否已在背包中
		var index = 获取道具索引(C_道具ID)
		if index != -1:
			# 如果存在，增加数量
			self.背包[index]["数量"] += C_操作数量
		else:
			# 如果不存在，添加新道具
			self.背包.append({"道具ID": C_道具ID, "数量": C_操作数量})

	# 减少背包中的道具 ### 使用减少具时,请先判断数量
	func 减少道具(C_道具ID: String, C_操作数量: int=1):
		var index = 获取道具索引(C_道具ID)
		self.背包[index]["数量"] -= C_操作数量

	# 获取道具在背包中的索引
	func 获取道具索引(C_道具ID: String) -> int:
		for i in self.背包.size():
			if self.背包[i]["道具ID"] == C_道具ID:
				return i
		return -1
	# 获取道具在背包中的数量
	func 获取道具数量(C_道具ID: String) -> int:
		var index = 获取道具索引(C_道具ID)
		if index != -1:
			return self.背包[index]["数量"]
		return 0
	
	
func 创建背包() -> 角色背包:
	return 角色背包.new()
