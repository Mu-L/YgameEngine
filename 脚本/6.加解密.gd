##加解密相关
extends Node
class_name 引擎加解密

##var md=取md5随机值()
##print("每日的内置md5:",md,"玩家需要使用匹配的礼包码:",解MD5(md))
##可用于每日签到Q群礼包码
func 取md5随机值():
	var 随机码 =str(ceil(randi_range(10000, 1000000000)))
	var 随机码MD5 = 随机码.md5_text()
	return 随机码MD5
	
func 取md5随机值_每日更新():
	var 随机码 =str(引擎.时间.获取到现在所经历的天数())
	var 随机码MD5 = 随机码.md5_text()
	return 随机码MD5

func 解MD5随机值(_str:String):
	
	var 取INT = _str.left(10) as int
	var 加密Int = 取INT * 3 + 1
	var 加密sha256 = str(加密Int).sha256_text().left(20)
	var 最终正确码 = 加密sha256.md5_text()
	return 最终正确码


##用于数值加密,防CE
var 是否作弊 = false #可用于标记是否作弊，假设浮点数被修改
func 浮点数加密(浮点数:float) -> String:
	var _字符串 = str(浮点数)
	var 数字转中文 = ['零', '一', '二', '三', '四', '五', '六', '七', '八', '九']
	var 数字 = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
	
	for i in 10:
		_字符串 = _字符串.replace(str(数字[i]), 数字转中文[i])
	
	var MD5哈希 = _字符串.md5_text()
	_字符串 = _字符串 + ":" + MD5哈希
	return _字符串

func 浮点数解密(中文字符串: String) -> float:
	var 部分 = 中文字符串.split(":")
	
	if 部分.size() != 2:
		是否作弊 = true
	else:
		var 中文字符部分 = 部分[0]
		var 哈希部分 = 部分[1]
		
		if 哈希部分 != 中文字符部分.md5_text():
			是否作弊 = true
	
	var 数字转中文 = ['零', '一', '二', '三', '四', '五', '六', '七', '八', '九']
	var 数字 = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
	var 结果 = 中文字符串
	
	for i in range(10):
		结果 = 结果.replace(数字转中文[i], 数字[i])
	return float(结果)

# 加密：先Base64编码，再按位置间隔重组（先取奇数位，再取偶数位）
func 字符串加密(data: String) -> String:
	# 先进行Base64编码
	var 编码字符串 = Marshalls.utf8_to_base64(data)
	# 按位置间隔重组：先取索引0,2,4...的字符，再取索引1,3,5...的字符
	var 奇数位字符 = ""  # 奇数索引位置的字符（0开始算）
	var 偶数位字符 = ""  # 偶数索引位置的字符
	var 索引 = 0
	
	for 字符 in 编码字符串:
		if 索引 % 2 == 0:
			奇数位字符 += 字符  # 0,2,4...位置
		else:
			偶数位字符 += 字符  # 1,3,5...位置
		索引 += 1
	
	# 组合结果：奇数位字符 + 偶数位字符
	return 奇数位字符 + 偶数位字符

# 解密：先还原位置顺序，再Base64解码
func 字符串解密(加密字符串: String) -> String:
	var 长度 = 加密字符串.length()
	# 计算奇数位字符的数量（向上取整）
	var 奇数位数量 = (长度 + 1) / 2
	# 拆分出奇数位和偶数位字符
	var 奇数位字符 = 加密字符串.substr(0, 奇数位数量)
	var 偶数位字符 = 加密字符串.substr(奇数位数量)
	# 还原原始顺序
	var 编码字符串 = ""
	var 最大索引 = max(奇数位字符.length(), 偶数位字符.length())
	for i in range(最大索引):
		# 先加奇数位字符
		if i < 奇数位字符.length():
			编码字符串 += 奇数位字符[i]
		# 再加偶数位字符
		if i < 偶数位字符.length():
			编码字符串 += 偶数位字符[i]
	# 进行Base64解码
	return Marshalls.base64_to_utf8(编码字符串)

#引擎.加解密.加密浮点数字典.new()
class 加密浮点数字典: 
	# 存储加密后的键值对（{键: 加密值}）
	var _加密数据: Dictionary = {}
	# 引用加解密工具
	var _加解密工具 = 引擎.加解密
	
	# 构造函数：接收明文字典并加密
	func _init(明文字典: Dictionary = {}) -> void:
		加密(明文字典)
	
	# 加密并存储明文字典（可用于初始化或更新）
	func 加密(明文字典: Dictionary) -> void:
		_加密数据.clear()
		for 键 in 明文字典:
			# 假设值为浮点数，如需支持其他类型可扩展
			_加密数据[键] = _加解密工具.浮点数加密(明文字典[键])
	
	# 新增/更新单个键值（加密存储）
	func 加密设置(键: String, 值: float) -> void:
		_加密数据[键] = _加解密工具.浮点数加密(值)
	
	# 获取单个解密后的值（核心场景用）
	func 获取属性(键: String) -> float:
		if 键 not in _加密数据:
			return 0.0
		return _加解密工具.浮点数解密(_加密数据[键])
	
	# 获取所有解密后的值（非核心场景用）
	func 获取所有属性() -> Dictionary:
		var 明文字典 = {}
		for 键 in _加密数据:
			明文字典[键] = 获取属性(键)
		return 明文字典
	
	# 清空加密数据
	func 清空() -> void:
		_加密数据.clear()
	
	func 获取加密数据() -> Dictionary:
		return _加密数据.duplicate()  # 返回副本，外部修改不影响内部数据
