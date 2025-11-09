@tool
##Ygame Mod 10.0
#引擎.xx
extends Node 
###基于网络封装
#var 网络:引擎网络
# 关键：添加一个类型别名，让"引擎.网络类型"指向"引擎网络"类
# 用于类型声明时识别"引擎.网络"层级

##基于调试封装的东西
var 调试=preload("uid://boaf24oyvwawd").new()
##统一管理按钮的东西
var 按钮=preload("uid://d0xhr42vcl758").new()
##基于场景封装的东西
var 场景=preload("uid://cmmdxughbtv03").new()

##统一管理对话的的东西
var 对话=preload("uid://bnyxil46lij8e").new()

##统一屏幕的的东西
var 屏幕=preload("uid://cy1l67aptkolr").new()

##统一加解密的的东西
var 加解密=preload("uid://chwg4gxgysd33").new()

##统一管理文件的东西
var 文件=preload("uid://c1v6dd331585h").new()

##统一数学的东西
var 数学=preload("uid://be3m8f3yuqecj").new()

##基于自己时间的东西
var 时间=preload("uid://7ufr514c01sm").new()
##基于字符串封装的东西
var 字符串=preload("uid://dt2gymmpyidg5").new()

##基于自己理解的东西,节点统称为对象
var 对象=preload("uid://wva6ajc1nv8o").new()

##基于自己理解的东西,节点统称为对象
var 图片=preload("uid://dil0tsqss7i21").new()
# 1. 预加载网络模块的类（用于类型关联）
const 网络类 = preload("uid://bp4iapmx88yhl")  # 指向12.网络.gd（引擎网络类）
# 2. 网络实例（加载并初始化）
var 网络: 网络类 = 网络类.new()
	
# 1. 预加载背包的类（用于类型关联）
const 角色背包类 = preload("uid://48vedp8jko7w")  # 指向13.背包.gd（引擎网络类）

#弱网
const 弱网类= preload("uid://bawh8cqwmt7iw") #指向14.弱网(引擎弱网)
var 弱网:弱网类=弱网类.new()

const 数据库=preload("uid://xymsomt1qyx2") #指向15.数据库

#17装备,尝试减少变量
const 装备类=preload("uid://dcdsmt5sxbyc4")
#18角色属性类,尝试减少变量
const 角色属性类=preload("uid://c03n37bu8xg7d")

const 角色经验类=preload("uid://do1r5cs2spqr4")
const 生命魔法类=preload("uid://u3hfm4s7vyyi")
const 怪物类=preload("uid://vitkmt6enhkh")
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
	#指向12.网络.gd（引擎网络类）
	网络.name = "网络"
	add_child(网络)  # 挂载到引擎节点
	

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
