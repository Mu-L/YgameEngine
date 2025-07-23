extends Node
class_name 引擎正则
"""
var regex = RegEx.new()
	regex.compile("\\w") # 去除特殊字符和中文?
	var results = ""
	for result in regex.search_all("asd@11"):
		results+=result.get_string()
	print(results)
"""

func 正则匹配(正则,字符串:String)->String:
	var regex = RegEx.new()
	regex.compile(正则) # Negated whitespace character class.
	var 返回值 = ""
	for result in regex.search_all(字符串):
		返回值+=result.get_string()
	return 返回值

#func _ready() -> void:
#	print("测试正则")
#	var text="";
#	text+="测试中的富文本试下多选项吧\n"
#	text+="[url=1]试一下[/url]\n"
#	text+="[url=2]第2个[/url]\n"
#	var 字符串=text
#	字符串=正则表达式类.new().正则匹配('(?<=])[^[/\\n]',字符串)
#	print("正则返回:",字符串)
