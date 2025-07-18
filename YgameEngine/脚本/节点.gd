## 节点操作工具类
## 提供对 Godot 节点的常用操作封装
extends Node
class_name 引擎节点

## 实例化场景资源并添加为子节点
## [br]参数:[br]
##   - _节点: 父节点实例[br]
##   - _子节点场景路径: 要实例化的场景资源路径
## [br]返回:[br]
##   - 实例化并添加的子节点
##[codeblock]
## 引擎.节点.实例化添加子节点($Parent, "res://scenes/Child.tscn")
##[/codeblock]
func 实例化添加子节点(_节点:Node, _子节点场景路径) -> Node:
	var a = load(_子节点场景路径).instantiate()
	_节点.add_child(a)
	return a

## 清空指定节点的所有子节点
## [br]参数:[br]
##   - _节点: 要清空子节点的父节点
##[codeblock]
## 引擎.节点.清空所有子节点($Parent)
##[/codeblock]
func 清空所有子节点(_节点:Node):
	for i in _节点.get_children():
		_节点.remove_child(i)

## 将焦点设置到指定节点
## [br]参数:[br]
##   - _节点: 要获取焦点的节点
##[codeblock]
## 引擎.节点.设置焦点($Button)
##[/codeblock]
func 设置焦点(_节点:Node):
	_节点.grab_focus()

## 显示指定节点
## [br]参数:[br]
##   - _节点: 要显示的节点
##[codeblock]
## 引擎.节点.显示($Panel)
##[/codeblock]
func 显示(_节点:Node):
	_节点.show()  # 修正为 show()，原代码中的 draw() 是绘制方法

## 隐藏指定节点
## [br]参数:[br]
##   - _节点: 要隐藏的节点
##[codeblock]
## 引擎.节点.隐藏($Panel)
##[/codeblock]
func 隐藏(_节点:Node):
	_节点.hide()

## 获取指定路径的子节点
## [br]参数:[br]
##   - _节点: 父节点实例[br]
##   - _子节点路径: 子节点的路径
## [br]返回:[br]
##   - 指定路径的子节点
##[codeblock]
## var 子节点 = 引擎.节点.获取子节点($Parent, "Child/Grandchild")
##[/codeblock]
func 获取子节点(_节点:Node, _子节点路径:NodePath) -> Node:
	return _节点.get_node(_子节点路径)

## 为节点挂载脚本
## [br]参数:[br]
##   - _节点对象: 要挂载脚本的节点[br]
##   - _挂载的脚本: 要挂载的脚本资源
##[codeblock]
## 引擎.节点.挂载脚本($Node, load("res://scripts/MyScript.gd"))
##[/codeblock]
func 挂载脚本(_节点对象, _挂载的脚本):
	_节点对象.set_script(_挂载的脚本)

## 销毁指定节点
## [br]参数:[br]
##   - _节点: 要销毁的节点
##[codeblock]
## 引擎.节点.销毁指定节点($TempNode)
##[/codeblock]
func 销毁指定节点(_节点):
	_节点.queue_free()

## 检查节点实例是否有效
## [br]参数:[br]
##   - _节点: 要检查的节点
## [br]返回:[br]
##   - 如果节点有效返回true，否则返回false
##[codeblock]
## if 引擎.节点.取有效节点($Node):
##     print("节点有效")
##[/codeblock]
func 取有效节点(_节点) -> bool:
	return (_节点)

## 将节点移动到新的父节点下
## [br]参数:[br]
##   - _挪动的节点: 要移动的节点[br]
##   - _父节点: 目标父节点
##[codeblock]
## 引擎.节点.挪动到指定父节点下($Child, $NewParent)
##[/codeblock]
func 挪动到指定父节点下(_挪动的节点:Node, _父节点:Node):
	_挪动的节点.reparent(_父节点)
