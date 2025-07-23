extends Node
class_name 引擎对象

## 向下取整
##[codeblock]
##引擎.对象.实例化(对象路径)
##[/codeblock]
func 实例化(对象路径:String):
	var 实例化;
	var 对象=load(对象路径)
	if 对象 is PackedScene:
		实例化=对象.instantiate()
	else:
		实例化=对象.new()
	return 实例化
	

## 实例化场景资源并添加为子对象
## [br]参数:[br]
##   - 父对象: 接收子对象的父级对象（Node类型）[br]
##   - 子对象场景路径: 要实例化的场景资源路径
## [br]返回:[br]
##   - 实例化并添加的子对象
##[codeblock]
## 引擎.对象.实例化添加子对象($Parent, "res://scenes/Child.tscn")
##[/codeblock]
func 实例化添加子对象(父对象:Node, 子对象场景路径) -> Node:
	var 子对象 = 实例化(子对象场景路径)
	父对象.add_child(子对象)
	return 子对象

## 清空指定对象的所有子对象
## [br]参数:[br]
##   - 目标对象: 要清空子对象的父对象
##[codeblock]
## 引擎.对象.清空所有子对象($Parent)
##[/codeblock]
func 清空所有子对象(目标对象:Node):
	for 子对象 in 目标对象.get_children():
		目标对象.remove_child(子对象)

## 将焦点设置到指定对象
## [br]参数:[br]
##   - 目标对象: 要获取焦点的对象（如按钮、输入框等）
##[codeblock]
## 引擎.对象.设置焦点($Button)
##[/codeblock]
func 设置焦点(目标对象:Node):
	目标对象.grab_focus()

## 显示指定对象
## [br]参数:[br]
##   - 目标对象: 要显示的对象
##[codeblock]
## 引擎.对象.显示($Panel)
##[/codeblock]
func 显示(目标对象:Node):
	目标对象.show()

## 隐藏指定对象
## [br]参数:[br]
##   - 目标对象: 要隐藏的对象
##[codeblock]
## 引擎.对象.隐藏($Panel)
##[/codeblock]
func 隐藏(目标对象:Node):
	目标对象.hide()

## 获取指定路径的子对象
## [br]参数:[br]
##   - 父对象: 父级对象实例[br]
##   - 子对象路径: 子对象的路径（如"Child/Grandchild"）
## [br]返回:[br]
##   - 指定路径的子对象
##[codeblock]
## var 子对象 = 引擎.对象.获取子对象($Parent, "Child/Grandchild")
##[/codeblock]
func 获取子对象(父对象:Node, 子对象路径:NodePath) -> Node:
	return 父对象.get_node(子对象路径)

## 为对象挂载脚本
## [br]参数:[br]
##   - 目标对象: 要挂载脚本的对象[br]
##   - 脚本资源: 要挂载的脚本资源（通过load()加载）
##[codeblock]
## 引擎.对象.挂载脚本($Node, load("res://scripts/MyScript.gd"))
##[/codeblock]
func 挂载脚本(目标对象:Node, 脚本资源):
	目标对象.set_script(脚本资源)

## 销毁指定对象
## [br]参数:[br]
##   - 目标对象: 要销毁的对象
##[codeblock]
## 引擎.对象.销毁对象($TempNode)
##[/codeblock]
func 销毁对象(目标对象:Node):
	目标对象.queue_free()

## 检查对象实例是否有效
## [br]参数:[br]
##   - 目标对象: 要检查的对象
## [br]返回:[br]
##   - 如果对象有效返回true，否则返回false
##[codeblock]
## if 引擎.对象.对象是否有效($Node):
##     print("对象有效")
##[/codeblock]
func 对象是否有效(目标对象:Node) -> bool:
	return is_instance_valid(目标对象)  # 优化：判断节点是否真正有效（处理已销毁但未回收的情况）

## 将对象移动到新的父对象下
## [br]参数:[br]
##   - 待移动对象: 要移动的对象[br]
##   - 目标父对象: 新的父级对象
##[codeblock]
## 引擎.对象.移动到父对象下($Child, $NewParent)
##[/codeblock]
func 移动到父对象下(待移动对象:Node, 目标父对象:Node):
	待移动对象.reparent(目标父对象)
