extends Node
class_name 引擎对象

#测试,后续待完善
func 实例化(对象路径:String):
	var 实例化;
	var 对象=load(对象路径)
	if 对象 is PackedScene:
		实例化=对象.instantiate()
	else:
		实例化=对象.new()
	return 实例化
