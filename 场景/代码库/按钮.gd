# DraggableCodeSnippet.gd
# 挂到任何 Button / TextureButton 上，让它支持拖拽插入代码到 Script 编辑器

@tool  # 让它在编辑器里也能运行
extends Button  # 如果你按钮是 TextureButton，就改成 extends TextureButton
@export_multiline() var 提示的内容: String = '代码提示'
@export_multiline() var 插入的内容: String = 'print("Hello from snippet!")' :
	set(value):
		插入的内容 = value
		tooltip_text = 提示的内容#"拖拽插入：\n" + value  # 可选：鼠标悬停显示代码预览

	
var is_dragging: bool = false
var drag_preview: Control = null

func _ready() -> void:
	# 每个按钮自己创建一个预览（避免共用一个导致混乱）
	_create_drag_preview()
	
	# 连接自己的 gui_input
	gui_input.connect(_on_gui_input)
	
	# 可选：设置鼠标指针为可拖拽样式
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
	
	# 预览先隐藏，挂到场景树根（或插件根）以便 global_position 工作
	get_tree().root.add_child(drag_preview)
	drag_preview.hide()

func _exit_tree() -> void:
	if is_instance_valid(drag_preview):
		drag_preview.queue_free()

func _on_gui_input(event: InputEvent) -> void:
	# 先找当前 Script 编辑器里的 CodeEdit（复用你原来的函数）
	var script_editor = EditorInterface.get_script_editor()  # Godot 4.x 标准写法
	var code_edit = _get_current_code_edit(script_editor)
	
	if code_edit == null:
		if event is InputEventMouseButton and event.pressed:
			print("请先打开一个 .gd 脚本！")
		return
	
	if event is InputEventMouseButton and event.button_index == MOUSE_BUTTON_LEFT:
		if event.pressed:
			is_dragging = true
			_update_preview_position(event.global_position)
			drag_preview.show()
		
		else:  # 松手
			is_dragging = false
			drag_preview.hide()
			
			# 插入当前光标位置（因为拖拽中已实时移动光标）
			code_edit.insert_text_at_caret(插入的内容)
			code_edit.grab_focus()
			
			var line = code_edit.get_caret_line() + 1
			var col  = code_edit.get_caret_column() + 1
			print("已插入代码到：第%d行 第%d列" % [line, col])
	
	elif event is InputEventMouseMotion and is_dragging:
		_update_preview_position(event.global_position)
		# ─────────────── 新增判断 ───────────────
		var local_mouse = code_edit.get_local_mouse_position()
		var rect = code_edit.get_rect()  # 或直接用 get_global_rect() 再转
		if not rect.has_point(local_mouse):
			# 鼠标不在 CodeEdit 里 → 不要算位置，也不要动光标
			if drag_preview.get_child_count() > 1:
				var label = drag_preview.get_child(1) as Label
				if label:
					label.text = "移到代码区可预览位置"
			return
		# ────────────────────────────────────────
		# 实时更新 CodeEdit 光标位置
		#var local_mouse = code_edit.get_local_mouse_position()
		var pos_info = code_edit.get_line_column_at_pos(local_mouse as Vector2i)
		
		if pos_info != null:
			code_edit.set_caret_line(pos_info.y, true)
			code_edit.set_caret_column(pos_info.x, true)
			
			# 更新预览文字（更友好）
			if drag_preview.get_child_count() > 1:
				var label = drag_preview.get_child(1) as Label
				if label:
					label.text = "插入到：%d:%d" % [pos_info.y + 1, pos_info.x + 1]

func _update_preview_position(global_pos: Vector2) -> void:
	if drag_preview:
		drag_preview.global_position = global_pos + Vector2(20, 20)

# 复用你原来的 _get_current_text_editor，但改名 + 简化（建议放进 autoload 或单独脚本）
func _get_current_code_edit(script_ed: ScriptEditor) -> CodeEdit:
	if not script_ed:
		return null
	
	var editor = script_ed.get_current_editor()
	if not editor:
		return null
	
	# 常见路径：尝试找 CodeEdit（Godot 4.x 结构可能微变，可用递归找）
	var code_edit = _find_code_edit_recursive(editor)
	return code_edit if code_edit is CodeEdit else null

func _find_code_edit_recursive(node: Node) -> Node:
	if node is CodeEdit:
		return node
	for child in node.get_children():
		var found = _find_code_edit_recursive(child)
		if found:
			return found
	return null
