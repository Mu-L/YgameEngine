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

##基于资源封装的东西
var 资源:引擎资源

##基于字符串封装的东西
var 字符串:引擎字符串

##基于窗口封装的东西
var 程序窗口:引擎程序窗口

##基于json封装的东西
var Json序列化:引擎Json序列化
	
##基于UDP封装的东西
var UDP:引擎UDP

##基于缓动封装的东西
var 缓动:引擎缓动

##基于场景封装的东西
var 场景:引擎场景

##基于随机封装的东西
var 随机:引擎随机

##基于字节数据封装的东西
var 字节数据:引擎字节数据
func _ready():
	
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
#endregion

#region 初始化 [addons\YgameEngine\脚本\资源.gd] 添加资源系统
	var 资源节点 = load("uid://dh5hqmlerkso6").new()
	资源节点.name="资源"
	add_child(资源节点)
	self.资源 = 资源节点
#endregion

#region 初始化 [addons\YgameEngine\脚本\字符串.gd] 添加字符串系统
	var 字符串节点 = load("uid://dt2gymmpyidg5").new()
	字符串节点.name="字符串"
	add_child(字符串节点)
	self.字符串 = 字符串节点
#endregion

#region 初始化 [addons\YgameEngine\脚本\程序窗口.gd] 添加程序窗口系统
	var 程序窗口节点 = load("uid://bou86tafpgqhs").new()
	程序窗口节点.name="窗口"
	add_child(程序窗口节点)
	self.程序窗口 = 程序窗口节点
#endregion

#region 初始化 [addons\YgameEngine\脚本\Json序列化.gd] 添加Json序列化系统
	var Json序列化节点 = load("uid://b476u8oavjn4q").new()
	Json序列化节点.name="Json序列化"
	add_child(Json序列化节点)
	self.Json序列化 = Json序列化节点
#endregion

#region 初始化 [addons\YgameEngine\脚本\UDP.gd] 添加UDP系统
	var UDP节点 = load("uid://cx6o0o5p5i3m4").new()
	UDP节点.name="UDP"
	add_child(UDP节点)
	self.UDP = UDP节点
#endregion

##region 初始化 [addons\YgameEngine\脚本\缓动.gd] 添加缓动系统
	var 缓动节点 = load("uid://ccoc56d5ll7gu").new()
	缓动节点.name="缓动"
	add_child(缓动节点)
	self.缓动 = 缓动节点
#endregion
##region 初始化 [addons\YgameEngine\脚本\场景.gd] 添加场景系统
	var 场景节点 = load("uid://cmmdxughbtv03").new()
	场景节点.name="场景"
	add_child(场景节点)
	self.场景 = 场景节点
#endregion

##region 初始化 [addons\YgameEngine\脚本\字节数据.gd] 添加字节数据系统
	var 字节数据节点 = load("uid://w0jiirwvkqsr").new()
	字节数据节点.name="字节数据"
	add_child(字节数据节点)
	self.字节数据 = 字节数据节点
#endregion

##region 初始化 [addons\YgameEngine\脚本\随机.gd] 添加随机系统
	var 随机节点 = load("uid://bgpwgbmomhiew").new()
	随机节点.name="随机"
	add_child(随机节点)
	self.随机 = 随机节点
#endregion