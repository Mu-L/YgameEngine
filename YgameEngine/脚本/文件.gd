##引擎文件专属
extends Node
class_name 引擎文件

##用于扫描文件的东西,返回:["a/a.gd", "b/b.gd", "c.gd"]
##[codeblock]
##var 读取文件数组=扫描文件("res://data/",true,["gd","json"]) #指定找gd + json
##var 读取文件数组=扫描文件("res://data/",true) #递归扫子目录
##var 读取文件数组=扫描文件("res://data/") #默认不扫子目录
##[/codeblock]
func 扫描文件(路径:String, 是否递归:bool = false, 指定格式:Array = []) -> Array:
	var 文件列表 = []
	var 目录 = DirAccess.open(路径)
	if 目录:
		目录.list_dir_begin()
		var 文件名 = 目录.get_next()
		while 文件名 != "":
			if 目录.current_is_dir():
				if 是否递归:
					var 子目录路径 = 路径 + "/" + 文件名
					var 子文件列表 = 扫描文件(子目录路径, 是否递归, 指定格式)
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
