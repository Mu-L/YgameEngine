extends Node

# 放置对战核心类
class 放置对战 extends Node:
	class 角色数据:
		var id:int
		var 速度:float
		var 可攻击:bool
		var 生命值:float
		var 攻击力:float
		var 距离:float
		
		func _init(数据字典: Dictionary = {}):
			self.id = 数据字典.get("id", 1000)
			self.速度 = 数据字典.get("速度", 1.0)
			self.可攻击 = 数据字典.get("可攻击", true)
			self.生命值 = 数据字典.get("生命值", 100.0)
			self.攻击力 = 数据字典.get("攻击力", 10.0)
			self.距离 = 数据字典.get("距离", 1.0)
	
	# 舞台速度
	var 舞台速度 = 1.0 
	
	# 角色数据
	var 我方数据: 角色数据 = 角色数据.new()
	var 敌方数据: 角色数据 = 角色数据.new()
	
	# 新增：存储回调的字典对象（而非直接挂载到类实例）
	var 回调对象: Dictionary = {}
	
	# 战斗状态标记
	var 战斗已结束 = false
	
	func _init(我方初始数据: Dictionary, 敌方初始数据: Dictionary, 舞台的速度:float=1.0) -> void:
		self.我方数据 = 角色数据.new(我方初始数据)
		self.敌方数据 = 角色数据.new(敌方初始数据)
		self.舞台速度 = 舞台的速度
		引擎.调试.打印("1V1战斗舞台已启动")
	
	# 修正后的回调注入方法（核心：创建空对象，传递给封包函数）
	func 回调(封包函数: Callable):
		# 1. 创建空字典作为回调挂载的对象（完全按你的思路）
		var 对象 = {}
		# 2. 执行封包函数，把回调挂载到空对象上
		封包函数.call(self.我方数据, self.敌方数据, 对象)
		# 3. 保存这个回调对象供后续调用
		self.回调对象 = 对象
		# 4. 注入完成后启动战斗
		self.开始()
	
	func 开始():
		战斗已结束 = false
		启动攻击循环("我方")
		启动攻击循环("敌方")
	
	func 启动攻击循环(阵营: String):
		_攻击循环协程(阵营)
	
	func _攻击循环协程(阵营: String):
		await 引擎.场景.等待(0.01)
		while not 战斗已结束:
			var 己方数据 = 我方数据 if 阵营 == "我方" else 敌方数据
			var 对方数据 = 敌方数据 if 阵营 == "我方" else 我方数据
			
			# 从回调对象中读取对应回调（匹配封包函数里的命名）
			var 攻击回调 = 回调对象.我攻击回调 if 阵营 == "我方" else 回调对象.敌方攻击回调
			
			if not 己方数据.可攻击:
				await 引擎.场景.等待(0.1)
				continue
			
			var 当前速度 = max(己方数据.速度, 0.1)
			var 攻击间隔 = 舞台速度 / 当前速度
			await 引擎.场景.等待(攻击间隔)
			
			if 战斗已结束:
				break
			
			# 执行回调对象里的攻击回调
			if 攻击回调 != null:
				攻击回调.call()
			
			检查战斗结果()
	
	func 检查战斗结果():
		if 战斗已结束:
			return
		
		if 敌方数据.生命值 <= 0:
			战斗已结束 = true
			# 执行回调对象里的胜利回调
			if 回调对象.胜利回调 != null:
				回调对象.胜利回调.call()
		
		elif 我方数据.生命值 <= 0:
			战斗已结束 = true
			# 执行回调对象里的失败回调
			if 回调对象.失败回调 != null:
				回调对象.失败回调.call()
