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
var 松开的tab数量=0
var 点击=false
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
			print("点击",)
			点击=true
			#print("选中的内容?:",code_edit.get_selected_text())
		# ... 前面的代码不变 ...
			
		else:  # 松手
			if 点击==false:
				print("执行拖拽程序逻辑")
				is_dragging = false
				drag_preview.hide()
				
				# 步骤1：获取基础信息
				var caret_line = code_edit.get_caret_line()
				var current_line_text = code_edit.get_line(caret_line)
				# 修正tab数量（pos_info.x从0开始，所以减1，避免负数）
				var target_tab_count = max(0, 松开的tab数量 - 1)
				print("目标插入tab数量：", target_tab_count)
				
				# 步骤2：清空当前行所有开头空白（你的核心逻辑）
				var stripped_line = current_line_text.lstrip(" \t")
				if stripped_line != current_line_text:
					code_edit.set_line(caret_line, stripped_line)
					code_edit.set_caret_column(0)  # 光标移到行首，确保插入位置准确
				
				# 步骤3：处理代码片段（清空自身缩进 + 按tab数量加缩进）
				var processed_code = 拖拽(插入的内容, target_tab_count)
				print("处理后的代码：", processed_code)
				
				# 步骤4：插入最终代码
				var 插入的代码片段=processed_code
				插入代码片段定位光标(code_edit,插入的代码片段,"拖拽")
				#code_edit.insert_text_at_caret(processed_code)
				#code_edit.grab_focus()
				#
				## 日志输出
				#var line = code_edit.get_caret_line() + 1
				#var col  = code_edit.get_caret_column() + 1
				#print("已插入代码到：第%d行 第%d列" % [line, col])
			##else:  # 松手
			#
			if 点击==true:
				
				print("执行点击程序逻辑")
				print("选中的内容2",code_edit.get_selected_text())
				is_dragging = false
				drag_preview.hide()
				
				#print(松开的tab数量)#拿到挪到到第几个tab,之前都清空了
				# 1. 获取光标所在行的缩进字符
				var caret_line = code_edit.get_caret_line()
				var current_line_text = code_edit.get_line(caret_line)
				var indent = _get_indent_from_line(current_line_text)
				
				# 2. 处理插入的代码，从第二行开始添加缩进
				var 插入的代码片段 = _add_indent_to_codeB(插入的内容, indent)
				#print("处理插入的代码:",processed_code) 输出:处理插入的代码:引擎.数学.向下取整($)
				
				##2.5核心添加更好玩的东西
				var 选择的内容=code_edit.get_selected_text()
				if 选择的内容!="":
					#使用占位符 $
					print(选择的内容) #a
					插入的代码片段 = 插入的代码片段.replace("$", 选择的内容)  # 核心替换代码
					pass
				else:
					插入的代码片段 = 插入的代码片段.replace("$", "")
				##
				
		   		##把| 替换			
				## 3. 插入处理后的代码
				
				插入代码片段定位光标(code_edit,插入的代码片段)
	
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
					print("第",pos_info.y + 1,"行")
					print("第",pos_info.x + 1,"tab")
					松开的tab数量=pos_info.x + 1
					点击=false
func 插入代码片段定位光标(code_edit,插入的代码片段,定位="点击"):
	# 1. 核心判断：插入内容是否是多行（是否包含换行符）
				var 是否多行 = 插入的代码片段.find("\n") != -1

				# 2. 找 | 的位置，并计算基础偏移
				var 光标行偏移 = 0
				var 光标列偏移 = 0
				var 待插入文本 = 插入的代码片段

				var 占位符位置 = 插入的代码片段.find("|")
				if 占位符位置 != -1:
					var 占位符前文本 = 插入的代码片段.substr(0, 占位符位置)
					var 占位符前行列表 = 占位符前文本.split("\n")
					# 基础偏移计算（和你原有逻辑一致）
					光标行偏移 = 占位符前行列表.size() - 1
					光标列偏移 = 占位符前行列表[-1].length() if 占位符前行列表.size() > 0 else 0
					# 👉 按你的思路：多行场景加补偿值（核心！）
					if 是否多行:
						光标列偏移 -= 1  # 列偏移-1，抵消多行的列渲染偏差
						if 定位=="拖拽":
							光标列偏移+=4
					# 移除 |
					待插入文本 = 插入的代码片段.replace("|", "")

				# 3. 记录插入前的光标基准（行+列）
				var 插入起始行 = code_edit.get_caret_line()
				var 插入起始列 = code_edit.get_caret_column()

				# 4. 插入代码
				code_edit.insert_text_at_caret(待插入文本)
				code_edit.grab_focus()

				# 5. 定位光标（分支处理单行/多行）
				if 占位符位置 != -1:
					var 目标行 = 插入起始行 + 光标行偏移
					var 目标列 = 插入起始列 + 光标列偏移
					
					code_edit.set_caret_line(目标行, true)
					code_edit.set_caret_column(目标列, true)

				# 日志
				var 当前行 = code_edit.get_caret_line() + 1
				var 当前列 = code_edit.get_caret_column() + 1
				print("多行？%s | 最终光标：第%d行 第%d列" % [是否多行, 当前行, 当前列])

# 新增：提取一行代码的缩进字符（空格/tab）
func _get_indent_from_line(line_text: String) -> String:
	var indent = ""
	for char in line_text:
		if char == " " or char == "\t":
			indent += char
		else:
			break
	return indent

# 新增：给多行代码从第二行开始添加缩进
# 新增：给多行代码添加缩进（核心逻辑：tab数量 + 清空片段缩进）
func 拖拽(code: String, target_tab_count: int) -> String:
	# 步骤1：分析代码片段，计算每行的原始层级差（核心！保留片段自身缩进关系）
	var lines = code.split("\n", true)
	var raw_indent_levels = []  # 存储每行原始缩进层级（1个tab=1级）
	var clean_lines = []        # 存储清空缩进后的纯代码
	
	# 1.1 遍历每行，计算原始层级 + 清空缩进
	for line in lines:
		# 计算当前行原始缩进层级（兼容tab/4空格）
		var level = 0
		var idx = 0
		while idx < line.length() and line[idx] in [" ", "\t"]:
			if line[idx] == "\t":
				level += 1
			elif idx % 4 == 3:  # 4个空格 = 1个tab
				level += 1
			idx += 1
		raw_indent_levels.append(level)
		
		# 清空当前行所有缩进，得到纯代码
		clean_lines.append(_clear_all_leading_whitespace(line))
	
	# 1.2 计算片段的基础层级（第一行的缩进层级），用于算层级差
	var base_level = raw_indent_levels[0] if raw_indent_levels.size() > 0 else 0
	var level_diffs = []  # 每行相对于第一行的层级差
	for level in raw_indent_levels:
		level_diffs.append(level - base_level)
	
	# 步骤2：生成最终缩进（松开的tab数量 + 片段自身层级差）
	var processed_lines = []
	var base_indent = "\t".repeat(target_tab_count)  # 松开的tab数量作为基础缩进
	for i in range(clean_lines.size()):
		# 最终缩进 = 基础缩进 + 片段自身层级差对应的tab
		var diff_indent = "\t".repeat(level_diffs[i])
		processed_lines.append(base_indent + diff_indent + clean_lines[i])
	
	# 步骤3：拼接成最终代码
	return "\n".join(processed_lines)
#func 拖拽(code: String, target_tab_count: int) -> String:
	## 步骤1：清空代码片段所有行的原始缩进（彻底去掉自带的\t/空格）
	#var clean_lines = []
	#var lines = code.split("\n", true)
	#for line in lines:
		#clean_lines.append(_clear_all_leading_whitespace(line))
	#
	## 步骤2：生成基础缩进字符（根据松开的tab数量）
	#var base_indent = "\t".repeat(target_tab_count)  # 1个tab=1级
	#
	## 步骤3：给每行添加缩进（第一行=基础缩进，第二行+=1级，匹配你的习惯）
	#var processed_lines = []
	#for i in range(clean_lines.size()):
		#if i == 0:
			## 第一行：仅基础缩进
			#processed_lines.append(base_indent + clean_lines[i])
		#else:
			## 第二行及以后：基础缩进 + 1级（保留片段的层级关系）
			#processed_lines.append(base_indent + "\t" + clean_lines[i])
	#
	## 步骤4：拼接成最终代码
	#return "\n".join(processed_lines)
func _add_indent_to_codeB(code: String, indent: String) -> String:
	# 按换行符分割代码行（兼容 \n 和 \r\n）
	var lines = code.split("\n", true)
	if lines.size() <= 1:
		return code  # 单行代码无需处理
	
	var processed_lines = [lines[0]]  # 第一行保持原样
	# 从第二行开始，每行开头添加缩进
	for i in range(1, lines.size()):
		processed_lines.append(indent + lines[i])
	print(processed_lines)
	# 重新拼接成完整字符串
	return "\n".join(processed_lines)
 #新增：给多行代码从第二行开始添加缩进（适配你的需求）


# 新增：暴力清空行开头所有的 \t/空格（核心工具函数）
func _clear_all_leading_whitespace(line: String) -> String:
	var start_idx = 0
	# 遍历字符，直到找到第一个非 \t/空格 的字符
	while start_idx < line.length():
		var c = line[start_idx]
		if c != "\t" and c != " ":
			break
		start_idx += 1
	# 截取从第一个有效字符开始的内容
	return line.substr(start_idx)
func _get_line_leading_whitespace(code_edit: CodeEdit, line: int) -> String:
	if line < 0 or line >= code_edit.get_line_count():
		return ""
	
	var text = code_edit.get_line(line)
	var indent = ""
	
	for c in text:
		if c in [" ", "\t"]:
			indent += c
		else:
			break
			
	return indent
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
