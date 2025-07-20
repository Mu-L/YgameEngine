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
