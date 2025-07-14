## 场景管理工具类
## 提供场景切换、管理和控制的功能
extends Node
class_name 引擎场景

## 切换到指定场景
## [br]参数:[br]
##   - 场景地址: 目标场景的路径，如"res://scenes/main.tscn"
##[codeblock]
## 引擎.场景.切换场景("res://scenes/gameplay.tscn")
##[/codeblock]
func 切换场景(场景地址:String) -> void:
	取场景树().change_scene_to_file(场景地址)

## 获取当前运行的场景节点
## [br]返回:[br]
##   - 当前活动场景的根节点
##[codeblock]
## var 当前场景 = 引擎.场景.取当前场景()
## 当前场景.add_child($NewNode)
##[/codeblock]
func 取当前场景() -> Node:
	return 取场景树().current_scene

## 获取主循环的场景树实例
## [br]返回:[br]
##   - 主循环的MainLoop对象
##[codeblock]
## var 场景树 = 引擎.场景.取场景树()
## 场景树.set_pause(true)
##[/codeblock]
func 取场景树() -> MainLoop:
	return Engine.get_main_loop()

## 暂停执行指定时间（协程阻塞）
## [br]参数:[br]
##   - 秒数: 要等待的时间（秒）
##[codeblock]
## await 引擎.场景.等待(2.0)  # 等待2秒后继续执行
## print("等待结束")
##[/codeblock]
func 等待(秒数:float) -> void:
	await 取场景树().create_timer(秒数).timeout

## 销毁当前活动场景
##[codeblock]
## 引擎.场景.销毁当前场景()
##[/codeblock]
func 销毁当前场景() -> void:
	Engine.get_main_loop().current_scene.queue_free()
