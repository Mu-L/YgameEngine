# 引擎/绘制.gd（自动加载：引擎 → 绘制）
extends Control    


# 封装：内部绘制矩形的节点类（支持字典配置参数）
class 内部绘制矩形 extends Node2D:
	# 接收绘制配置字典（默认空字典，防止传参为空）
	var 绘制配置: Dictionary = {}
	
	func _draw() -> void:
		# 从字典提取参数，缺省自动补默认值
		var 矩形区域 = 绘制配置.get("矩形区域", Rect2(0, 0, 100, 100))  # 默认100x100矩形
		var 颜色 = 绘制配置.get("颜色", Color(1, 0, 0))                # 默认红色
		var 是否填充 = 绘制配置.get("是否填充", true)                 # 默认填充
		var 描边宽度 = 绘制配置.get("描边宽度", 0.0)                 # 默认描边宽度33
		var 是否抗锯齿 = 绘制配置.get("是否抗锯齿", true)              # 默认开启抗锯齿
		
		# 调用原生绘制方法
		draw_rect(矩形区域, 颜色, 是否填充, 描边宽度, 是否抗锯齿)
		
		# 等待3秒后销毁自身（保留原有逻辑）
		await get_tree().create_timer(3.0).timeout  # 替代“引擎.场景.等待”（通用写法）
		queue_free()

# 对外暴露的绘制矩形方法（接收字典配置，可选参数）
func 绘制矩形(配置: Dictionary = {}) -> void:
	# 创建内部绘制矩形节点
	var 矩形节点 = 内部绘制矩形.new()
	# 赋值配置字典（核心：把外部传的配置传给节点）
	矩形节点.绘制配置 = 配置
	# 设置唯一名称（保留随机数逻辑）
	矩形节点.name = "矩形" + str(randf())  # 替代“引擎.数学.随机_取0到1的浮点数”（通用写法）
	# 添加为子节点
	add_child(矩形节点)

# ===================== 枚举中文映射（核心常量） =====================

# 水平对齐方式
# 枚举常量
const 水平对齐_左对齐 = HorizontalAlignment.HORIZONTAL_ALIGNMENT_LEFT
const 水平对齐_居中 = HorizontalAlignment.HORIZONTAL_ALIGNMENT_CENTER
const 水平对齐_右对齐 = HorizontalAlignment.HORIZONTAL_ALIGNMENT_RIGHT
const 水平对齐_填充 = HorizontalAlignment.HORIZONTAL_ALIGNMENT_FILL

# 仅保留正向映射（字符串→枚举）
const 水平对齐映射 = {
	"左对齐": 水平对齐_左对齐,
	"居中": 水平对齐_居中,
	"右对齐": 水平对齐_右对齐,
	"填充": 水平对齐_填充
}

# 文本排版方向枚举常量
const 排版方向_自动 = TextServer.DIRECTION_AUTO
const 排版方向_从左到右 = TextServer.DIRECTION_LTR
const 排版方向_从右到左 = TextServer.DIRECTION_RTL
const 排版方向_继承 = TextServer.DIRECTION_INHERITED
# 文本排版方向
const 排版方向映射 = {
	"自动": 排版方向_自动,
	"从左到右": 排版方向_从左到右,
	"从右到左": 排版方向_从右到左,
	"继承": 排版方向_继承
}


# 文本排版朝向
# 文本排版朝向枚举常量
const 排版朝向_水平 = TextServer.ORIENTATION_HORIZONTAL
const 排版朝向_垂直 = TextServer.ORIENTATION_VERTICAL
const 排版朝向映射 = {
	"水平": 排版朝向_水平,
	"垂直": 排版朝向_垂直
}

# 两端对齐标志（Flags 支持组合，用数组传多个）
const 对齐标志_无 = TextServer.JUSTIFICATION_NONE
const 对齐标志_Kashida调整 = TextServer.JUSTIFICATION_KASHIDA
const 对齐标志_单词间距调整 = TextServer.JUSTIFICATION_WORD_BOUND
const 对齐标志_移除首尾空格 = TextServer.JUSTIFICATION_TRIM_EDGE_SPACES
const 对齐标志_仅最后制表符后对齐 = TextServer.JUSTIFICATION_AFTER_LAST_TAB
const 对齐标志_省略号修剪对齐 = TextServer.JUSTIFICATION_CONSTRAIN_ELLIPSIS
const 对齐标志_跳过最后一行 = TextServer.JUSTIFICATION_SKIP_LAST_LINE
const 对齐标志_跳过有字符的最后一行 = TextServer.JUSTIFICATION_SKIP_LAST_LINE_WITH_VISIBLE_CHARS
const 对齐标志_单行强制对齐 = TextServer.JUSTIFICATION_DO_NOT_SKIP_SINGLE_LINE
const 对齐标志映射 = {
	"无": 对齐标志_无,
	"Kashida调整": 对齐标志_Kashida调整,
	"单词间距调整": 对齐标志_单词间距调整,
	"移除首尾空格": 对齐标志_移除首尾空格,
	"仅最后制表符后对齐": 对齐标志_仅最后制表符后对齐,
	"省略号修剪对齐": 对齐标志_省略号修剪对齐,
	"跳过最后一行": 对齐标志_跳过最后一行,
	"跳过有字符的最后一行": 对齐标志_跳过有字符的最后一行,
	"单行强制对齐": 对齐标志_单行强制对齐
}


# 全局配置（可外部调整）
var 字体: FontFile = load("res://ziti.otf")  # 替换为你的字体路径
var 字体大小: int = 25  # 字体大小
var 单条提示高度: float = 40.0  # 每条提示的高度（控制上下间距）
var 最大显示数量: int = 20  # 最多同时显示的提示数
var 提示总时长: float = 1.0  # 单条提示显示总时长
var 渐变时长: float = 0.5  # 渐变消失时长
var _提示节点列表: Array = []  # 存储所有提示节点
var _is_editor: bool = false  # 标记是否在编辑器模式









# ===================== 内部文本绘制节点类 =====================
class 内部绘制文本 extends Node2D:
	var 文本配置: Dictionary = {}
	
	func _draw() -> void:
		# 1. 基础参数提取（缺省补官方默认值）
		var 字体: Font = 文本配置.get("字体", ThemeDB.fallback_font)
		var 绘制位置: Vector2 = 文本配置.get("绘制位置", Vector2(0, 0))
		var 文本内容: String = 文本配置.get("文本内容", "")
		var 裁剪宽度: float = 文本配置.get("裁剪宽度", -1.0)
		var 字体大小: int = 文本配置.get("字体大小", 16)
		var 文本颜色: Color = 文本配置.get("文本颜色", Color(1, 1, 1, 1))
		var 过采样系数: float = 文本配置.get("过采样系数", 0.0)
		
		# 2. 解析水平对齐（仅支持中文传参）
		var 水平对齐 = 水平对齐映射.get(文本配置.get("水平对齐", "左对齐"), HorizontalAlignment.HORIZONTAL_ALIGNMENT_LEFT)
		
		# 3. 解析排版方向（仅支持中文传参）
		var 排版方向 = 排版方向映射.get(文本配置.get("排版方向", "自动"), TextServer.DIRECTION_AUTO)
		
		# 4. 解析排版朝向（仅支持中文传参）
		var 排版朝向 = 排版朝向映射.get(文本配置.get("排版朝向", "水平"), TextServer.ORIENTATION_HORIZONTAL)
		
		# 5. 解析两端对齐标志（仅支持中文，数组/单字符串）
		var 对齐标志输入 = 文本配置.get("对齐标志", ["单词间距调整", "跳过最后一行"])
		var 最终对齐标志 = 0
		# 数组传多个标志（组合Flags）
		if typeof(对齐标志输入) == TYPE_ARRAY:
			for 标志名 in 对齐标志输入:
				最终对齐标志 |= 对齐标志映射.get(标志名, 0)
		# 单字符串传标志
		elif typeof(对齐标志输入) == TYPE_STRING:
			最终对齐标志 = 对齐标志映射.get(对齐标志输入, 3)
		
		# 6. 调用原生 draw_string（全参数映射）
		draw_string(
			字体,
			绘制位置,
			文本内容,
			水平对齐,
			裁剪宽度,
			字体大小,
			文本颜色,
			最终对齐标志,
			排版方向,
			排版朝向,
			过采样系数
		)
		
		# 7. 保留3秒销毁逻辑
		await get_tree().create_timer(3.0).timeout
		queue_free()

# ===================== 对外暴露的绘制文本方法 =====================
func 绘制文本(配置: Dictionary = {}) -> void:
	var 文本节点 = 内部绘制文本.new()
	文本节点.文本配置 = 配置
	文本节点.name = "文本_" + str(randf())
	add_child(文本节点)

#
#
#
#
#






















#
#
#
#
#
#
#
#
#
#
#
#
## 内部提示节点类（对标 内部绘制矩形 写法）
#class 内部绘制提示 extends Node2D:
	## 节点内部属性
	#var 文本: String = ""
	#var 基础坐标: Vector2 = Vector2.ZERO
	#var 剩余时长: float = 0.0
	#var 透明度: float = 1.0
	#var 字体: FontFile = null
	#var 字体大小: int = 25
	#var 单条提示高度: float = 40.0
	#var 渐变时长: float = 0.5
#
	## 初始化（接收外部参数）
	#func _init(文本内容: String, 基础位置: Vector2, 字体资源: FontFile, 字号: int, 行高: float, 渐变时间: float, 总时长: float):
		#文本 = 文本内容
		#基础坐标 = 基础位置
		#字体 = 字体资源
		#字体大小 = 字号
		#单条提示高度 = 行高
		#渐变时长 = 渐变时间
		#剩余时长 = 总时长
		#透明度 = 1.0
#
	## 每帧更新倒计时和透明度
	#func _process(delta: float):
		#剩余时长 -= delta
		#
		## 渐变消失逻辑
		#if 剩余时长 <= 0.0 or 透明度 <= 0.001:
			#queue_free()  # 自动销毁（对标矩形的queue_free）
		#elif 剩余时长 < 渐变时长:
			#透明度 = max(0.001, 剩余时长 / 渐变时长)
		#
		#queue_redraw()  # 触发重绘
#
	## 绘制提示（对标矩形的_draw）
	#func _draw():
		#if not 字体 or 文本.is_empty() or 透明度 <= 0.001:
			#return
		#
		## 计算文字尺寸和背景矩形
		#var 文字尺寸 = 字体.get_string_size(文本, 字体大小)
		#var 矩形边距 = 5
		#var 提示矩形 = Rect2(
			#0 - 矩形边距,
			#0 - 文字尺寸.y - 矩形边距,
			#文字尺寸.x + 矩形边距 * 2,
			#文字尺寸.y + 矩形边距 * 2
		#)
		#
		## 绘制背景
		#var 背景透明度 = max(0.0, 0.7 * 透明度)
		#draw_rect(提示矩形, Color(0, 0, 0, 背景透明度), true)
		## 绘制边框
		#var 边框透明度 = max(0.0, 透明度)
		#draw_rect(提示矩形, Color(1, 1, 1, 边框透明度), false, 1.0, false)
		## 绘制文字
		#draw_string(
			#字体,
			#Vector2(0, 0),
			#文本,
			#HorizontalAlignment.HORIZONTAL_ALIGNMENT_LEFT,
			#-1.0,
			#字体大小,
			#Color(1, 1, 1, 边框透明度)
		#)
#
	## 节点销毁时清理引用
	#func _exit_tree():
		#引擎.绘制._移除提示节点引用(self)
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
## 核心方法：绘制提示（完全对标绘制矩形的写法）
#func 绘制提示(文本: String) -> void:
	## 编辑器模式禁用
	#_is_editor = Engine.is_editor_hint()
	#if _is_editor or 文本.is_empty():
		#return
	#
	## 初始化字体容错
	#if not 字体:
		#字体 = ThemeDB.fallback_font
		#字体.fixed_size = 字体大小
	#
	## 计算基础坐标（适配视口）
	#var viewport_size = get_viewport_rect().size
	#var 基础坐标 = Vector2(viewport_size.x / 2 - 100, viewport_size.y - 150)
	#
	## 超出最大数量时销毁最旧提示
	#if _提示节点列表.size() >= 最大显示数量:
		#var 最旧节点 = _提示节点列表.pop_front()
		#if is_instance_valid(最旧节点):
			#最旧节点.queue_free()
	#
	## 创建新提示节点（对标矩形的new()方式）
	#var 提示=内部绘制提示.new(
		#文本,
		#基础坐标,
		#字体,
		#字体大小,
		#单条提示高度,
		#渐变时长,
		#提示总时长
	#)
	## 命名规则对标矩形（用随机数避免重复）
	#提示.name="提示"+str(引擎.数学.随机_取0到1的浮点数())
	## 添加子节点（对标矩形的add_child）
	#add_child(提示)
	#
	## 加入列表并更新位置
	#_提示节点列表.append(提示)
	#_更新所有提示节点位置()
#
## 内部方法：移除提示节点引用
#func _移除提示节点引用(目标节点: Node2D):
	#if 目标节点 in _提示节点列表:
		#_提示节点列表.erase(目标节点)
	#_更新所有提示节点位置()
#
## 内部方法：更新所有提示的位置
#func _更新所有提示节点位置():
	#for i in range(_提示节点列表.size()):
		#var 目标节点 = _提示节点列表[i]
		#if not is_instance_valid(目标节点):
			#continue
		## 计算向上偏移
		#var 偏移量 = (_提示节点列表.size() - 1 - i) * 单条提示高度
		#var 最终坐标 = 目标节点.基础坐标 - Vector2(0, 偏移量)
		## 限制在视口内
		#var viewport_rect = get_viewport_rect()
		#最终坐标.x = clamp(最终坐标.x, 0, viewport_rect.size.x)
		#最终坐标.y = clamp(最终坐标.y, 0, viewport_rect.size.y)
		## 设置节点位置
		#目标节点.position = 最终坐标
#
## 测试用输入触发（可根据需要删除/调整）
#func _input(event: InputEvent) -> void:
	#if _is_editor:
		#return
	#
	#if Input.is_action_just_pressed("ui_accept"):
		#var 随机文本列表 = [
			#"获得金币 x101",
			#"体力 +51",
			#"解锁新成就！",
			#"操作提示：按Z键攻击",
			#"警告：生命值过低！"
		#]
		#var 随机文本 = 随机文本列表[randi() % 随机文本列表.size()]
		#绘制提示(随机文本)
