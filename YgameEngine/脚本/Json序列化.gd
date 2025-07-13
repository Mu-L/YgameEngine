## Json序列化工具类
## 提供JSON数据与GDScript数据类型的相互转换功能
extends Node
class_name 引擎Json序列化

## 读取指定目录下所有JSON文件并转换为字典
## [br]参数:[br]
##   - 目录: 要读取的JSON文件所在目录路径
## [br]返回:[br]
##   - 包含所有JSON文件内容的字典，键为文件名，值为解析后的JSON数据
##[codeblock]
## var json数据 = 引擎.Json序列化.读取json文件夹_到字典("res://data/json/")
## print(json数据)
##[/codeblock]
func 读取json文件夹_到字典(目录) -> Dictionary:
	var 变量 = {}  # 用于存储解析后JSON数据的字典
	var XML文件夹目录 = 目录
	var 读取XML文件 = 引擎.文件.扫描文件(XML文件夹目录) 
	
	for i in 读取XML文件.size():
		var 子文件 = 读取XML文件[i]
		var file = FileAccess.open(子文件, FileAccess.READ)
		var npc文本 = file.get_as_text()
		var 解析的npcjson = JSON.parse_string(npc文本)
		变量[读取XML文件[i]] = 解析的npcjson
	
	return 变量

## 将GDScript数据类型转换为JSON格式字符串
## [br]参数:[br]
##   - _数据: 要转换的GDScript变量（如字典、数组等）
## [br]返回:[br]
##   - JSON格式的字符串
##[codeblock]
## var json文本 = 引擎.Json序列化.数据转json文本({"name": "player", "level": 10})
## print(json文本)  # 输出: {"name": "player", "level": 10}
##[/codeblock]
func 数据转json文本(_数据: Variant) -> String:
	return JSON.stringify(_数据)

## 将JSON格式字符串解析为GDScript数据类型
## [br]参数:[br]
##   - _json文本: 要解析的JSON格式字符串
## [br]返回:[br]
##   - 解析后的GDScript变量（如字典、数组等）
##[codeblock]
## var 数据 = 引擎.Json序列化.解析到数据("{\"name\": \"player\", \"level\": 10}")
## print(数据.name)  # 输出: player
##[/codeblock]
func 解析到数据(_json文本: String) -> Variant:
	return JSON.parse_string(_json文本)
