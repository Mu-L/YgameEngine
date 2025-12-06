@tool
##Ygame Mod 10.0
#引擎.xx
extends Node 
###基于网络封装
#var 网络:引擎网络
# 关键：添加一个类型别名，让"引擎.网络类型"指向"引擎网络"类
# 用于类型声明时识别"引擎.网络"层级

##基于调试封装的东西
var 调试=preload("res://addons/YgameEngine/脚本/1.调试.gd").new()
##统一管理按钮的东西
var 按钮=preload("res://addons/YgameEngine/脚本/按钮/2.按钮.gd").new()
##基于场景封装的东西
var 场景:=preload("res://addons/YgameEngine/脚本/3.场景.gd").new()

##统一管理对话的的东西
var 对话=preload("res://addons/YgameEngine/场景/对话/4.对话.gd").new()

##统一屏幕的的东西
#var 屏幕=preload("res://addons/YgameEngine/脚本/5.屏.gd")#.new()
const 屏幕类 = preload("res://addons/YgameEngine/脚本/5.屏幕.gd")  # 指向12.网络.gd（引擎网络类）
# 2. 网络实例（加载并初始化）
var 屏幕: 屏幕类 = 屏幕类.new()

##统一加解密的的东西
var 加解密=preload("res://addons/YgameEngine/脚本/6.加解密.gd").new()

##统一管理文件的东西
var 文件:=preload("res://addons/YgameEngine/脚本/7.文件.gd").new()

##统一数学的东西
var 数学=preload("res://addons/YgameEngine/脚本/8.数学.gd").new()

##基于自己时间的东西
var 时间=preload("res://addons/YgameEngine/脚本/9.时间.gd").new()
##基于字符串封装的东西
var 字符串:=preload("res://addons/YgameEngine/脚本/10.字符串.gd").new()

##基于自己理解的东西,节点统称为对象
var 对象=preload("res://addons/YgameEngine/脚本/11.对象.gd").new()

##基于自己理解的东西,节点统称为对象
var 图片=preload("res://addons/YgameEngine/脚本/16.图片.gd").new()
# 1. 预加载网络模块的类（用于类型关联）
const 网络类 = preload("res://addons/YgameEngine/脚本/12.网络.gd")  # 指向12.网络.gd（引擎网络类）
# 2. 网络实例（加载并初始化）
var 网络: 网络类 = 网络类.new()
	
# 1. 预加载背包的类（用于类型关联）
const 角色背包类 = preload("res://addons/YgameEngine/脚本/13.背包.gd")  # 指向13.背包.gd（引擎网络类）

#弱网
const 弱网类= preload("res://addons/YgameEngine/脚本/14.弱网.gd") #指向14.弱网(引擎弱网)
var 弱网:弱网类=弱网类.new()

const 数据库=preload("res://addons/YgameEngine/脚本/15.数据库.gd") #指向15.数据库

#17装备,尝试减少变量
const 装备类=preload("res://addons/YgameEngine/脚本/17.装备.gd")
#18角色属性类,尝试减少变量
const 角色属性类=preload("res://addons/YgameEngine/脚本/18.角色属性.gd")

const 角色经验类=preload("res://addons/YgameEngine/脚本/19.角色经验.gd")
const 生命魔法类=preload("res://addons/YgameEngine/脚本/20.生命魔法.gd")
const 怪物类=preload("res://addons/YgameEngine/脚本/21.怪物.gd")
const 舞台类=preload("res://addons/YgameEngine/脚本/22.舞台.gd")
const 增益类=preload("res://addons/YgameEngine/脚本/23.增益.gd")
const 技能类=preload("res://addons/YgameEngine/脚本/24.技能.gd")
##############以下，待融入参考，


###基于listitem封装的东西
#var 列表:引擎列表
#
#
###基于资源封装的东西
#var 资源:引擎资源
#
#
###基于窗口封装的东西
#var 程序窗口:引擎程序窗口

#
###基于缓动封装的东西
#var 缓动:引擎缓动
#
###基于字节数据封装的东西
#var 字节数据:引擎字节数据







func _init() -> void:
	pass
##region 初始化 回调_按钮.gd 接管所有按钮脚本回调。请使用[按钮信号.gd]拖入按钮控件配置相关属性
	##载入[addons\YgameEngine\脚本\2.按钮.gd]
	#var 按钮脚本 = load("uid://d0xhr42vcl758").new()
	#按钮脚本.name="按钮"
	#add_child(按钮脚本)
	#self.按钮 = 按钮脚本
	##endregion
func _ready():
	#引擎.调试.打印("触发10?")
	#指向12.网络.gd（引擎网络类）
	网络.name = "网络"
	add_child(网络)  # 挂载到引擎节点
	
	屏幕.name="屏幕"
	add_child(屏幕)

##以下待修复，融入
#
##region 初始化 [addons\YgameEngine\脚本\列表.gd] 添加列表系统
	#var 列表节点 = load("uid://ddvmv08fc64oj").new()
	#列表节点.name="列表"
	#add_child(列表节点)
	#self.列表 = 列表节点
##endregion
#
#
##region 初始化 [addons\YgameEngine\脚本\资源.gd] 添加资源系统
	#var 资源节点 = load("uid://dh5hqmlerkso6").new()
	#资源节点.name="资源"
	#add_child(资源节点)
	#self.资源 = 资源节点
##endregion
#
#
#
##region 初始化 [addons\YgameEngine\脚本\程序窗口.gd] 添加程序窗口系统
	#var 程序窗口节点 = load("uid://bou86tafpgqhs").new()
	#程序窗口节点.name="窗口"
	#add_child(程序窗口节点)
	#self.程序窗口 = 程序窗口节点
##endregion
#
#
#
###region 初始化 [addons\YgameEngine\脚本\缓动.gd] 添加缓动系统
	#var 缓动节点 = load("uid://ccoc56d5ll7gu").new()
	#缓动节点.name="缓动"
	#add_child(缓动节点)
	#self.缓动 = 缓动节点
##endregion
#
#
###region 初始化 [addons\YgameEngine\脚本\字节数据.gd] 添加字节数据系统
	#var 字节数据节点 = load("uid://w0jiirwvkqsr").new()
	#字节数据节点.name="字节数据"
	#add_child(字节数据节点)
	#self.字节数据 = 字节数据节点
##endregion
