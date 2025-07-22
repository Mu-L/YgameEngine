## Json序列化工具类
## 提供JSON数据与GDScript数据类型的相互转换功能
extends Node
class_name 引擎Json序列化



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
