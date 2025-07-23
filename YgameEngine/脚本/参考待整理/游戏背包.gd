#游戏背包
var Q_角色包裹=[]
##角色包裹是数组,填充{"道具ID":"001","数量":1}
# 添加道具到背包
func S_背包_添加道具(C_道具ID: String, C_操作数量: int):
	
	# 查找道具是否已在背包中
	var index = S_背包_获取道具索引(C_道具ID)
	if index != -1:
		# 如果存在，增加数量
		Q_角色包裹[index]["数量"] += C_操作数量
	else:
		# 如果不存在，添加新道具
		Q_角色包裹.append({"道具ID": C_道具ID, "数量": C_操作数量})

# 减少背包中的道具 ### 使用减少具时,请先判断数量
func S_背包_减少道具(C_道具ID: String, C_操作数量: int):
	var index = S_背包_获取道具索引(C_道具ID)
	Q_角色包裹[index]["数量"] -= C_操作数量

# 获取道具在背包中的索引
func S_背包_获取道具索引(C_道具ID: String) -> int:
	for i in Q_角色包裹.size():
		if Q_角色包裹[i]["道具ID"] == C_道具ID:
			return i
	return -1
# 获取道具在背包中的数量
func S_背包_获取道具数量(C_道具ID: String) -> int:
	var index = S_背包_获取道具索引(C_道具ID)
	if index != -1:
		return Q_角色包裹[index]["数量"]
	return 0
	
	
	#用于储存运行的掉落
var Y_掉落表:={}
func S_掉落表_加入(C_掉落ID:String):
	if Y_掉落表.get(C_掉落ID)==null:
		Y_掉落表[C_掉落ID]={"掉落ID":C_掉落ID,"数量":0}
	Y_掉落表[C_掉落ID]["数量"]=Y_掉落表[C_掉落ID]["数量"]+1
	

func S_掉落表_获取():
	return Y_掉落表
func S_掉落表_清空():
	Y_掉落表={}
#func S_掉落物品(C_怪物ID):
	#var J_怪物种族=P_怪物配置.get(C_怪物ID).种族
	#var J_怪物等级=P_怪物配置.get(C_怪物ID).等级
	#调试.注释打印("怪物种族",J_怪物种族)
	#for X_掉落 in p_掉落配置.get("种族").get(J_怪物种族):
#
		#if int(J_怪物等级)>int(X_掉落.最小等级) and int(J_怪物等级)<int(X_掉落.最大等级):
			##print("ID",X_掉落.掉落物品ID,"名称:",p_物品配置.get(X_掉落.掉落物品ID).get("名称"),"几率:",X_掉落.掉落几率)
		##		pass
			#if 随机.取0到1的浮点数()<=float(X_掉落.掉落几率):
				#S_掉落表_加入(X_掉落.掉落物品ID)
	#
