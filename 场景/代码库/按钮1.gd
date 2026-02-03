# DraggableCodeSnippet.gd
# 挂到任何 Button / TextureButton 上，支持面板任意位置调整后的拖拽
@tool
extends Button
@export_multiline() var 提示的内容: String = '代码提示'
@export_multiline() var 插入的内容: String = 'print("Hello from snippet!")' :
	set(value):
		插入的内容 = value
		tooltip_text = 提示的内容

var is_dragging: bool = false
var drag_preview: Control = null
var code_edit: CodeEdit = null  # 缓存CodeEdit，避免重复查找

# 核心修改：改用全局输入监听，绕过面板坐标干扰
func _ready() -> void:
	_create_drag_preview()
	# 移除原有的gui_input连接，改用全局鼠标监听
	mouse_entered.connect(_on_mouse_enter)
	mouse_exited.connect(_on_mouse_exit)
	mouse_default_cursor_shape = CURSOR_DRAG

func _create_drag_preview() -> void:
	drag_preview = Control.new()
	drag_preview.name = "SnippetPreview"
	drag_preview.size = Vector2(180, 30)
	drag_preview.modulate = Color(0.9, 0.9, 1.0, 0.75)
	
	var bg = ColorRect.new()
	bg.color = Color(0.2, 0.4, 0.8, 0.6)
	bg.anchor_right = 1.0
	bg.anchor_bottom = 1.0
	drag_preview.add_child(bg)
	
	var label = Label.new()
	label.text = "松开插入代码"
	label.add_theme_font_size_override("font_size", 12)
	label.add_theme_color_override("font_color", Color.WHITE)
	label.anchor_right = 1.0
	label.anchor_bottom = 1.0
	label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	label.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	drag_preview.add_child(label)
	
	get_tree().root.add_child(drag_preview)
	drag_preview.hide()

# 鼠标进入按钮时，开始监听全局输入
func _on_mouse_enter() -> void:
	get_viewport().input.connect(_on_global_input)

# 鼠标离开按钮时，停止监听全局输入
func _on_mouse_exit() -> void:
	if get_viewport().input.is_connected(_on_global_input):
		get_viewport().input.disconnect(_on_global_input)

# 全局输入处理（核心：不受面板位置影响）
func _on_global_input(event: InputEvent) -> void:
	# 先缓存CodeEdit，避免每次事件都查找
	if code_edit == null:
		var script_editor = EditorInterface.get_script_editor()
		code_edit = _get_current_code_edit(script_editor)
	if code_edit == null:
		return

	# 左键按下：开始拖拽（必须是在按钮范围内按下才生效）
	if event is InputEventMouseButton and event.button_index == MOUSE_BUTTON_LEFT:
		if event.pressed:
			# 检查按下位置是否在按钮的全局范围内（适配面板位置）
			if self.get_global_rect().has_point(event.global_position):
				is_dragging = true
				_update_preview_position(event.global_position)
				drag_preview.show()
		else:
			# 左键松开：插入代码
			if is_dragging:
				is_dragging = false
				drag_preview.hide()
				# 只有鼠标在CodeEdit范围内才插入
				if code_edit.get_global_rect().has_point(event.global_position):
					code_edit.insert_text_at_caret(插入的内容)
					code_edit.grab_focus()
					var line = code_edit.get_caret_line() + 1
					var col = code_edit.get_caret_column() + 1
					print("已插入代码到：第%d行 第%d列" % [line, col])
			# 重置缓存的CodeEdit
			code_edit = null

	# 鼠标移动：更新预览和光标位置
	elif event is InputEventMouseMotion and is_dragging:
		_update_preview_position(event.global_position)
		# 检查鼠标是否在CodeEdit全局范围内
		var code_edit_global_rect = code_edit.get_global_rect()
		if not code_edit_global_rect.has_point(event.global_position):
			var label = drag_preview.get_child(1) as Label
			if label:
				label.text = "移到代码区可预览位置"
			return

		# 全局坐标转CodeEdit本地坐标（精准定位）
		var local_mouse = code_edit.global_to_local(event.global_position)
		var pos_info = code_edit.get_line_column_at_pos(local_mouse.round())
		
		if pos_info != null:
			code_edit.set_caret_line(pos_info.y, true)
			code_edit.set_caret_column(pos_info.x, true)
			var label = drag_preview.get_child(1) as Label
			if label:
				label.text = "插入到：%d:%d" % [pos_info.y + 1, pos_info.x + 1]

func _update_preview_position(global_pos: Vector2) -> void:
	if drag_preview:
		drag_preview.global_position = global_pos + Vector2(20, 20)

func _get_current_code_edit(script_ed: ScriptEditor) -> CodeEdit:
	if not script_ed:
		return null
	var editor = script_ed.get_current_editor()
	if not editor:
		return null
	return _find_code_edit_recursive(editor)

func _find_code_edit_recursive(node: Node) -> Node:
	if node is CodeEdit:
		return node
	for child in node.get_children():
		var found = _find_code_edit_recursive(child)
		if found:
			return found
	return null

# 清理资源
func _exit_tree() -> void:
	# 断开全局输入连接，避免内存泄漏
	if get_viewport().input.is_connected(_on_global_input):
		get_viewport().input.disconnect(_on_global_input)
	if is_instance_valid(drag_preview):
		drag_preview.queue_free()
		drag_preview = null
	code_edit = null
