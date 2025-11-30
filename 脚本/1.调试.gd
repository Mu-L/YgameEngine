## 调试工具类
## 提供调试模式下的增强打印功能
extends Node
class_name 引擎调试

## 带颜色的调试打印
## [br]参数:[br]
##   - 打印的内容: 要打印的文本或变量[br]

func 打印(...打印的内容: Array) -> void:
	var 来源 = get_stack()[1]
	# 手动拼接可变参数内容
	var 内容 = ""
	for i in 打印的内容.size():
		内容 += str(打印的内容[i])  # 先转成字符串，避免类型错误
		# 除了最后一个元素，后面加空格分隔
		if i != 打印的内容.size() - 1:
			内容 += " "
	
	print_rich("%s\t%s:%s\t [color=green]%s[/color]" % [
		来源["source"],
		来源["function"],
		来源["line"],
		内容
	])
## 带注释的调试打印（仅在调试模式下输出）
## [br]参数:[br]
##   - 注释: 打印内容的前缀说明[br]
func 注释打印(注释: String, ...打印的内容: Array) -> void:
	var 来源 = get_stack()[1]
	
	# 处理可变参数：拼接所有内容为字符串
	var 内容 = ""
	for i in 打印的内容.size():
		内容 += str(打印的内容[i])  # 转为字符串避免类型错误
		if i != 打印的内容.size() - 1:
			内容 += " "  # 元素间用空格分隔
	
	print_rich("%s\t%s:%s\t[color=red]%s:\t[/color][color=green]%s[/color]" % [
		来源["source"],
		来源["function"],
		来源["line"],
		注释,
		内容
	])



func 打印错误(...打印的内容: Array) -> void:
	var 来源 = get_stack()[1]
	# 手动拼接可变参数内容
	var 内容 = ""
	for i in 打印的内容.size():
		内容 += str(打印的内容[i])  # 先转成字符串，避免类型错误
		# 除了最后一个元素，后面加空格分隔
		if i != 打印的内容.size() - 1:
			内容 += " "
	
	printerr("%s\t%s:%s\t %s" % [
		来源["source"],
		来源["function"],
		来源["line"],
		内容
	])
	
## 格式化打印字典内容
## [br]参数:[br]
##   - 字典: 要打印的字典对象[br]
##   - 注释: 打印标题，默认为"无"
##[codeblock]
## print字典(player.stats, "玩家属性")
##[/codeblock]
func 打印字典(字典:Dictionary, 注释:String = "无"):
	if 取调试模式():
		var 来源 = get_stack()[1]
		print_rich("[color=yellow]%s-----------------------------------字典打印开始---------------------------------[/color]" % [注释])
		print("{")
		for i in 字典:
			print("  %s = %s" % [i, 字典[i]])
		print("} \t [color=yellow] -%s\t%s:%s\t [/color]" % [来源["source"],来源["function"],来源["line"]])
		print_rich("[color=yellow]%s-----------------------------------字典打印结束---------------------------------[/color]\n\n" % [注释])

## 格式化打印数组中的字典
## [br]参数:[br]
##   - 数组字典: 包含字典的数组[br]
##   - 注释: 打印标题，默认为"无"
##[codeblock]
## print数组字典(items_list, "物品列表")
##[/codeblock]
func 打印数组(数组:Array, 注释:String = "无"):
	if 取调试模式():
		var 来源 = get_stack()[1]
		#p#rint_rich("%s\t%s:%s\t" % [来源["source"],来源["function"],来源["line"]])
		print_rich("[color=cyan]%s-----------------------------------数组打印开始---------------------------------[/color]" % [注释])
		print("[")
		for i in range(数组.size()):
			print("  [%d] = %s" % [i, 数组[i]])
		print("]\t [color=yellow] -%s\t%s:%s\t [/color]" % [来源["source"],来源["function"],来源["line"]])
		print_rich("[color=cyan]%s-----------------------------------数组打印结束---------------------------------[/color]\n\n" % [注释])

## 检查当前是否处于调试模式
## [br]返回:[br]
##   - 如果是调试构建返回true，发布版本返回false
##[codeblock]
## if 引擎.调试.取调试模式():
##     print("当前处于调试模式")
##[/codeblock]
func 取调试模式() -> bool:
	return OS.is_debug_build()
