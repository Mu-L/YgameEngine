@tool
extends EditorPlugin

# 插件面板的根节点
var panel: Control
#插件启动函数
func _enable_plugin() -> void:
	# Add autoloads here.
	add_autoload_singleton("引擎", "res://addons/YgameEngine/脚本/0.引擎.gd")
	print("引擎插件已启动，全局'引擎.xxx'可使用")
	# 1. 加载插件UI面板
	var scene = load("res://addons/YgameEngine/场景/代码库/代码块.tscn")
	panel = scene.instantiate()
	# 2. 将面板添加到编辑器的底部面板（也可改为top/left/right）
	add_control_to_bottom_panel(panel, "代码片段拖拽")
	
	#
	

#插件关闭函数
func _disable_plugin() -> void:
	remove_autoload_singleton("引擎")
		# 插件卸载时清理
	remove_control_from_bottom_panel(panel)
	panel.queue_free()
	print("引擎插件已注销，全局'引擎.xxx'不再可用")
	

	
func _enter_tree() -> void:
	# Initialization of the plugin goes here.
	pass

func _exit_tree() -> void:
	# Clean-up of the plugin goes here.
	pass
