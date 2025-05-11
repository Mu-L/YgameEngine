@tool
##Dream Mod 10.0
extends Node

##统一管理音乐的东西
var 音乐:引擎音乐 
##统一管理窗口的的东西
var 窗口:引擎窗口

##统一管理按钮的东西
var 按钮:引擎按钮

##统一管理文件的东西
var 文件:引擎文件

##基于listitem封装的东西
var 列表:引擎列表

##基于节点的东西
var 节点:引擎节点

##基于调试封装的东西
var 调试:引擎调试
func _ready() -> void:
	

#region 初始化 回调_按钮.gd 接管所有按钮脚本回调。请使用[按钮信号.gd]拖入按钮控件配置相关属性
	#载入[addons\YgameEngine\脚本\按钮.gd]
	var 按钮节点 = load("uid://d0xhr42vcl758").new()
	按钮节点.name="按钮"
	add_child(按钮节点)
	self.按钮 = 按钮节点

#endregion

#region 初始化[addons\YgameEngine\脚本\音乐.gd] 添加音乐系统
	var 音乐节点 = load("uid://cigc82l4kfasw").new()
	音乐节点.name="音乐"
	add_child(音乐节点)
	self.音乐 = 音乐节点
#endregion


#region 初始化 [addons\YgameEngine\场景\窗口\窗口.gd],窗口的东西。
	var 窗口节点 = load("uid://bnyxil46lij8e").new()
	窗口节点.name="对话"
	add_child(窗口节点)
	self.窗口 = 窗口节点
#endregion
	
#region 初始化 [addons\YgameEngine\脚本\文件.gd] 添加文件系统
	var 文件节点 = load("uid://c1v6dd331585h").new()
	文件节点.name="文件"
	add_child(文件节点)
	self.文件 = 文件节点
#endregion

#region 初始化 [addons\YgameEngine\脚本\列表.gd] 添加列表系统
	var 列表节点 = load("uid://ddvmv08fc64oj").new()
	列表节点.name="列表"
	add_child(列表节点)
	self.列表 = 列表节点
#endregion

#region 初始化 [addons\YgameEngine\脚本\节点.gd] 添加节点系统
	var 节点节点 = load("uid://bsf7wletqiugu").new()
	节点节点.name="节点"
	add_child(节点节点)
	self.节点 = 节点节点
#endregion

#region 初始化 [addons\YgameEngine\脚本\调试.gd] 添加调试系统
	var 调试节点 = load("uid://boaf24oyvwawd").new()
	调试节点.name="调试"
	add_child(调试节点)
	self.调试 = 调试节点
