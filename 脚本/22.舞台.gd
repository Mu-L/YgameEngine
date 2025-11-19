extends Node
class 放置对战 extends Node:
	class 角色数据:
		var id:int
		var 速度:float
		var 可攻击:bool
		var 生命值:float
		var 攻击力:float
		var 距离:float
		# 添加构造函数，初始化字段
		func _init(数据字典: Dictionary = {}):
			self.id=数据字典.get("id", 1000)
			self.速度 = 数据字典.get("速度", 1.0)
			self.可攻击 = 数据字典.get("可攻击", true)
			self.生命值 = 数据字典.get("生命值", 100.0)
			self.攻击力 = 数据字典.get("攻击力", 10.0)
			self.距离 = 数据字典.get("距离", 1.0)
	#舞台速度
	var 舞台速度=1.0 #攻击速度的初始值
	
	var 我方数据: 角色数据 = 角色数据.new()
	var 敌方数据: 角色数据 = 角色数据.new()
	# 攻击回调（外部注入）
	var 我方攻击回调 = null  # func(我方数据, 敌方数据)
	var 敌方攻击回调 = null  # func(敌方数据, 我方数据)
	
	# 胜负回调（战斗结束时触发）
	var 胜利回调 = null  # func() 我方胜利时触发
	var 失败回调 = null  # func() 敌方胜利时触发
	
	# 战斗是否结束的标记
	var 战斗已结束 = false
	
	func _init(我方初始数据: Dictionary, 敌方初始数据: Dictionary,舞台的速度:float=1.0) -> void:
		# 初始化默认数据
		self.我方数据 = 角色数据.new(我方初始数据)
		self.敌方数据 = 角色数据.new(敌方初始数据)
		#self.我方数据=引擎.数学.字典填充更新(self.我方数据,我方初始数据)
		#self.敌方数据=引擎.数学.字典填充更新(self.敌方数据,敌方初始数据)
		self.舞台速度=舞台的速度
		开始()
		引擎.调试.打印("战斗舞台已启动")
	
	func 开始():
		战斗已结束 = false
		启动攻击循环("我方")
		启动攻击循环("敌方")
		#call_deferred("启动攻击循环","我方")
		#call_deferred("启动攻击循环","敌方")
	
	func 启动攻击循环(阵营: String):
		#print(我方数据,敌方数据)
		while not 战斗已结束:  # 战斗结束则退出循环
			var 己方数据 = 我方数据 if 阵营 == "我方" else 敌方数据
			var 敌方数据 = 敌方数据 if 阵营 == "我方" else 我方数据
			var 攻击回调 = 我方攻击回调 if 阵营 == "我方" else 敌方攻击回调
			
			# 检查是否可攻击
			if not 己方数据.可攻击:
				await 引擎.场景.等待(0.1)
				continue
			
			# 计算攻击间隔（实时读取速度）
			var 当前速度 = max(己方数据.速度, 0.1)
			var 攻击间隔 = 舞台速度 / 当前速度
			#引擎.调试.打印("等",攻击间隔,"cs",当前速度)
			await 引擎.场景.等待(攻击间隔)
			
			# 再次检查战斗状态（防止等待期间战斗已结束）
			if 战斗已结束:
				break
			
			# 触发攻击
			if 攻击回调 != null:
				攻击回调.call(己方数据, 敌方数据)
			
			# 攻击后检查生命值（判断胜负）
			检查战斗结果()
	
	# 检查双方生命值，判断胜负
	func 检查战斗结果():
		if 战斗已结束:
			return
		
		# 敌方生命值≤0 → 我方胜利
		if 敌方数据.生命值 <= 0:
			战斗已结束 = true
			引擎.调试.打印("我方胜利！")
			if 胜利回调 != null:
				胜利回调.call(敌方数据)
		
		# 我方生命值≤0 → 敌方胜利
		elif 我方数据.生命值 <= 0:
			战斗已结束 = true
			引擎.调试.打印("敌方胜利！")
			if 失败回调 != null:
				失败回调.call()
