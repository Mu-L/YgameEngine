extends Node
class_name 引擎时间


"""
预存一个2024年1月1号0点0分的时间戳
"""
const 时间戳:=1704038400 #储存了一个2024年1月1号的0点0分的时间戳
static func 获取预设的时间戳():
	return 时间戳
	pass
static func 获取到现在所经历的秒数():
	return 取当前时间戳_秒()-时间戳
	
static func 获取到现在所经历的天数():
	return 获取到现在所经历的秒数()/86400

static func 获取到现在所经历的周数():
	return 获取到现在所经历的秒数()/604800

static func 获取到现在所经历的月数():
	return 获取到现在所经历的秒数()/86400


"""
时间
"""
static func 取时分秒():
	return Time.get_time_dict_from_system()

## 取当前电脑的时间戳,10位数,秒,浮点数
static func 取当前时间戳_秒():
	return Time.get_unix_time_from_system()
	
