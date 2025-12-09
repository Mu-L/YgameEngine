extends Node
# ===================== 1. 补全字典（核心） =====================
# 中文枚举
const 过渡类型_线性 = Tween.TRANS_LINEAR          # 匀速（无变速）
const 过渡类型_正弦 = Tween.TRANS_SINE            # 正弦曲线（平滑变速）
const 过渡类型_四舍五入 = Tween.TRANS_QUAD        # 二次方曲线
const 过渡类型_立方 = Tween.TRANS_CUBIC          # 三次方曲线
const 过渡类型_四次方 = Tween.TRANS_QUART         # 四次方曲线
const 过渡类型_五次方 = Tween.TRANS_QUINT         # 五次方曲线
const 过渡类型_指数 = Tween.TRANS_EXPO            # 指数曲线
const 过渡类型_圆周 = Tween.TRANS_CIRC            # 圆周曲线
const 过渡类型_弹性 = Tween.TRANS_ELASTIC         # 弹性回弹（常用）
const 过渡类型_回退 = Tween.TRANS_BACK            # 先回退再前进
const 过渡类型_弹跳 = Tween.TRANS_BOUNCE          # 弹跳效果（常用）
# 补全过渡类型字典：中文串 → 枚举值
const 过渡类型 = {
	"线性": Tween.TRANS_LINEAR,
	"正弦": Tween.TRANS_SINE,
	"四舍五入": Tween.TRANS_QUAD,
	"立方": Tween.TRANS_CUBIC,
	"四次方": Tween.TRANS_QUART,
	"五次方": Tween.TRANS_QUINT,
	"指数": Tween.TRANS_EXPO,
	"圆周": Tween.TRANS_CIRC,
	"弹性": Tween.TRANS_ELASTIC,
	"回退": Tween.TRANS_BACK,
	"弹跳": Tween.TRANS_BOUNCE
}

# 二、缓动模式（Easings）- 控制过渡曲线的应用方向
const 缓动类型_入 = Tween.EASE_IN                # 先慢后快（常用）
const 缓动类型_出 = Tween.EASE_OUT               # 先快后慢（常用）
const 缓动类型_入出 = Tween.EASE_IN_OUT          # 先慢后快再慢（最常用）
const 缓动类型_出入 = Tween.EASE_OUT_IN          # 先快后慢再快
# 补全缓动类型字典：中文串 → 枚举值
const 缓动类型 = {
	"入": Tween.EASE_IN,
	"出": Tween.EASE_OUT,
	"入出": Tween.EASE_IN_OUT,
	"出入": Tween.EASE_OUT_IN
}

# 新增：属性名中文映射（核心）
# 键：中文属性名 → 值：引擎原生属性名
const 属性名映射 = {
	# 位置相关
	"坐标": "position",
	"全局坐标": "global_position",
	# 旋转相关
	"旋转": "rotation",
	"全局旋转": "global_rotation",
	"角度": "rotation_degrees", # 角度制旋转
	# 缩放相关
	"缩放": "scale",
	"全局缩放": "global_scale",
	# 大小相关
	"大小": "size",
	#辅助
	"可见性": "visible",
	# 颜色相关
	"透明度": "modulate",
	"颜色": "modulate",
	"自身颜色": "self_modulate"
	
}
# ===================== 缓动类（仅改取值逻辑，其余完全不变）=====================
class 缓动:
	var 原生补间: Tween

	func _init():
		原生补间 = Engine.get_main_loop().current_scene.create_tween()
	# 核心：动画方法（按你的参考示例改写取值逻辑）
	func 动画(_参数: Dictionary) -> 缓动:
		# 安全取值（完全保留你的代码）
		var 物体 = _参数.get("对象", _参数.get("物体", null))
		#var 属性 = _参数.get("属性", _参数.get("对象属性", "position"))
		var 目标 = _参数.get("目标", _参数.get("目标值", Vector2(0, 0)))
		var 时间 = _参数.get("时间", _参数.get("时长", 1.0))
			# ========== 1. 解析属性名（中文→原生） ==========
		var 属性输入值 = _参数.get("属性", _参数.get("对象属性", "坐标")) # 默认值改为中文"坐标"
		# 中文→原生映射，兼容中文/原生两种写法
		var 属性 = 属性名映射.get(属性输入值, 属性输入值)
		# ========== 按你的参考示例改写：get安全取值 + 兼容字符串/常量 ==========
		# 1. 先取用户输入（字符串/常量），默认值用枚举常量
		var 过渡输入值 = _参数.get("过渡类型", 过渡类型_弹性)
		# 2. 如果是字符串 → 从映射字典取；否则直接用（常量），兜底默认弹性
		var 过渡样式 = 过渡类型.get(过渡输入值, 过渡输入值) if typeof(过渡输入值) == TYPE_STRING else 过渡输入值
		# 最终兜底：防止传了无效值（比如乱码/数字），确保是合法枚举
		过渡样式 = 过渡类型.get(过渡样式, 过渡类型_弹性)
		
		# 缓动类型同理（和你的参考逻辑完全一致）
		var 缓动输入值 = _参数.get("缓动类型", 缓动类型_入出)
		var 缓动样式 = 缓动类型.get(缓动输入值, 缓动输入值) if typeof(缓动输入值) == TYPE_STRING else 缓动输入值
		缓动样式 = 缓动类型.get(缓动样式, 缓动类型_入出)
		# ==================================================

		if is_instance_valid(物体):
			#print(属性,"--",属性 in 物体)
			
			if 属性 in 物体:
				原生补间.tween_property(物体, 属性, 目标, 时间).set_trans(过渡样式).set_ease(缓动样式)
			else:
				引擎.调试.打印("缓动可能填了",属性,"无效属性")
				
		return self  # 返回self，支持链式调用

	# 以下所有方法完全保留你的原始代码
	func 回调(_参数: Dictionary) -> 缓动:
		var 函数 = _参数.get("函数", _参数.get("独立函数", null))
		var 延迟 = _参数.get("延迟", 0.0)
		if 函数:
			原生补间.tween_callback(函数).set_delay(延迟)
		return self

	func 并行() -> 缓动:
		原生补间.parallel()
		return self

	func 串联() -> 缓动:
		原生补间.chain()
		return self

	func 结束():
		原生补间.kill()
