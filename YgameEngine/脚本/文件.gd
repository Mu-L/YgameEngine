##引擎文件专属
extends Node
class_name 引擎文件

##用于扫描文件的东西,返回:["a/a.gd", "b/b.gd", "c.gd"]
##[codeblock]
##var 读取文件数组=引擎.文件.扫描文件("res://data/",true,["gd","json"]) #指定找gd + json
##var 读取文件数组=引擎.文件.扫描文件("res://data/",true) #递归扫子目录
##var 读取文件数组=引擎.文件.扫描文件("res://data/") #默认不扫子目录
##[/codeblock]
func 扫描文件(路径:String, 是否扫描子目录:bool = false, 指定格式:Array = []) -> Array:
	var 文件列表 = []
	var 目录 = DirAccess.open(路径)
	if 目录:
		目录.list_dir_begin()
		var 文件名 = 目录.get_next()
		while 文件名 != "":
			if 目录.current_is_dir():
				if 是否扫描子目录:
					var 子目录路径 = 路径 + "/" + 文件名
					var 子文件列表 = 扫描文件(子目录路径, 是否扫描子目录, 指定格式)
					for 子文件 in 子文件列表:
						文件列表.append(文件名 + "/" + 子文件)
			else:
				var 扩展名 = 文件名.get_extension()
				if 指定格式.is_empty() or 指定格式.find(扩展名) != -1:
					文件列表.append(文件名)
			文件名 = 目录.get_next()
		目录.list_dir_end()
	else:
		print("尝试访问路径时出错。")
	return 文件列表

##获取文件的MD5哈希值(用于文件校验)
##[codeblock]
##var md5 = 引擎.文件.获取MD5值("res://data/savegame.dat")
##print("文件MD5: ", md5)
##[/codeblock]
func 获取MD5值(文件路径:String):
	return FileAccess.get_md5(文件路径)

##加载Godot资源(如场景、纹理、脚本等)
##[codeblock]
##var scene = 引擎.文件.加载资源("res://scenes/main.tscn")
##add_child(scene.instantiate())
##[/codeblock]
func 加载资源(_文件: String):
	return load(_文件)

## 智能检查文件或资源是否存在(自动处理物理文件和导入资源)
## 优先检查物理文件，不存在时再检查导入资源
## 参数:[br]
##   - 文件路径: 要检查的文件路径
## 返回:[br]
##   - 如果文件或资源存在返回true，否则返回false
##[codeblock]
##if 引擎.文件.是否存在("res://scripts/player.gd"):           # 检查普通文件
##if 引擎.文件.是否存在("res://images/player.png"):          # 检查导入资源
##if 引擎.文件.是否存在("res://fonts/my_font.tres"):         # 检查TRES资源
##[/codeblock]
func 是否存在(文件路径:String) -> bool:
	# 优先检查物理文件是否存在
	if FileAccess.file_exists(文件路径):
		return true
	# 物理文件不存在时，检查是否为已导入的资源
	return ResourceLoader.exists(文件路径)

## 将文本内容保存到指定文件
## [br]参数:[br]
##   - 文本: 要保存的文本内容[br]
##   - 文件地址: 保存路径，默认为"user://save_game.dat"
## [br]异常:[br]
##   - 如果文件无法打开，会抛出错误
##[codeblock]
##引擎.文件.保存文本到文件("游戏进度数据", "user://save_game.dat")
##引擎.文件.保存文本到文件("配置信息", "user://config.txt")
##[/codeblock]
func 保存文本到文件(文本, 文件地址:String = "user://save_game.dat"):
	var _文件 = FileAccess.open(文件地址, FileAccess.WRITE)
	if _文件:
		_文件.store_string(文本)
		_文件.close() # 确保关闭文件
	else:
		push_error("无法打开文件进行写入: " + 文件地址)

## 从指定文件读取文本内容
## [br]参数:[br]
##   - 文件地址: 读取路径，默认为"user://save_game.dat"
## [br]返回:[br]
##   - 成功时返回文件内容字符串，失败时返回空字符串
##[codeblock]
##var 保存数据 = 引擎.文件.读取文件到文本("user://save_game.dat")
##var 配置内容 = 引擎.文件.读取文件到文本("user://config.txt")
##[/codeblock]
func 读取文件到文本(文件地址:String = "user://save_game.dat") -> String:
	var _文件 = FileAccess.open(文件地址, FileAccess.READ)
	if _文件:
		var 读取文本 = _文件.get_as_text()
		_文件.close() # 确保关闭文件
		return 读取文本
	else:
		push_error("无法打开文件进行读取: " + 文件地址)
		return ""

## 加载外部PCK或ZIP资源包
## [br]参数:[br]
##   - 路径资源: 要加载的资源包路径，默认为"user://update.zip"
## [br]返回:[br]
##   - 加载成功返回true，失败返回false
##[codeblock]
## 引擎.文件.加载PCK("user://custom_content.pck")
##[/codeblock]
func 加载PCK(路径资源:String = "user://update.zip") -> bool:
	return ProjectSettings.load_resource_pack(路径资源)