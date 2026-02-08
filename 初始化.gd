@tool
extends EditorPlugin

# 插件面板的根节点
var panel: Control
#插件启动函数
const AUTOLOAD_NAME = "引擎"
const AUTOLOAD_PATH = "res://addons/YgameEngine/脚本/0.引擎.gd"
func _enable_plugin() -> void:
	#print("启动插件")
	_move_autoload_to_top(AUTOLOAD_NAME)
	print("引擎 已添加并尝试置顶,引擎插件已启动，全局'引擎.xxx'可使用")
	#print("优先指向1?")
	
	pass


#插件关闭函数
func _disable_plugin() -> void:
	remove_autoload_singleton("引擎")
	# 插件卸载时清理
	#remove_control_from_bottom_panel(panel)
	if dock:
		remove_dock(dock)  # 从编辑器移除dock
		dock.queue_free()  # 释放dock容器
		dock = null
	if panel:
		panel.queue_free()  # 释放你的自定义面板
		panel = null
	print("引擎插件已注销，全局'引擎.xxx'不再可用")
# 保存dock和面板的引用，用于插件停用后清理
var dock: EditorDock = null

func _enter_tree() -> void:
	#print("自动触发加载")
	##用于检测是否有更新,并用错误提示标记红线
	
	##
	# 再挪到最前面（hack方式）
	
	## 1. 加载插件UI面板
	var scene = load("res://addons/YgameEngine/场景/代码库/代码块.tscn")
	panel = scene.instantiate()
	## 2. 将面板添加到编辑器的底部面板（也可改为top/left/right）
	#add_control_to_bottom_panel(panel, "代码片段拖拽") #已废弃
	
	## 2. 改用新的add_dock()方法添加到底部面板（核心修改部分）
	# 创建EditorDock容器（这是新方法必须的载体）
	dock = EditorDock.new()
	# 设置面板标题（对应原来的title参数）
	dock.title = "引擎代码片段"
	# 指定默认停靠位置为底部（关键：替代原来的bottom_panel）
	dock.default_slot = EditorDock.DOCK_SLOT_BOTTOM
	# 将你的自定义面板添加到dock容器中
	dock.add_child(panel)
	# 最终添加这个dock到编辑器
	add_dock(dock)

#func _exit_tree() -> void:
	## Clean-up of the plugin goes here.
	#pass

func _move_autoload_to_top(autoload_name: String) -> void:
	#print(get_autoload_list())
	#print("触发",ResourceUID.path_to_uid("uid://b130wwbl6uxq1"))
	var 路径=get_autoload_list()
	#先卸载全部
	for i in 路径:
		remove_autoload_singleton(i)
		print("自动卸载",i)
	#优先添加引擎
	add_autoload_singleton(AUTOLOAD_NAME, AUTOLOAD_PATH)
	#在添加其他
	for i in 路径:
		if i!="引擎":
			var res=load(路径[i].trim_prefix("*")).resource_path
			add_autoload_singleton(i,res)
	
#获取类似{ "游戏": "*res://游戏.gd", "业务按钮": "*res://业务按钮.gd", "引擎": "*uid://rxpcxfu68go3" }
func get_autoload_list() -> Dictionary:
	var 字典: Dictionary = {}  # 键：名称  值：路径（带*前缀）
	for prop in ProjectSettings.get_property_list():
		if prop.name.begins_with("autoload/"):
			var name = prop.name.trim_prefix("autoload/")
			var path = ProjectSettings.get_setting(prop.name)
			字典[name] = path
	
	return 字典
