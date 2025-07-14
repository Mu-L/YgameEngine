##一个自主创建包围盒检测的东西
## 包围盒.包围盒检测筛选属性(Vector2(100,100),Vector2(100,100),"a")
## 包围盒.包围盒检测筛选属性(Vector2(100,100),Vector2(100,100))
extends Node

class_name 引擎包围盒
##内部的包围盒检测
static func 包围盒检测(包围盒位置:Vector2,包围盒尺寸:Vector2):
	var 检测2D=Area2D.new()
	var 检测2D碰撞体=CollisionShape2D.new()
	var 检测2D物理矩形=RectangleShape2D.new()
	检测2D物理矩形.extents = 包围盒尺寸
	检测2D碰撞体.shape = 检测2D物理矩形
	检测2D.add_child(检测2D碰撞体)
	Engine.get_main_loop().current_scene.add_child(检测2D)
	检测2D.position=包围盒位置
	检测2D.z_index = 11
	var 形状2D查询 = PhysicsShapeQueryParameters2D.new()
	形状2D查询.set_shape(检测2D物理矩形)
	形状2D查询.collide_with_areas = true
	
	形状2D查询.transform = Transform2D(0, 包围盒位置)
	var 查询数据 =Engine.get_main_loop().current_scene.get_world_2d().direct_space_state.intersect_shape(形状2D查询)
	
	延迟销毁(检测2D)
	return 查询数据
	
static func 延迟销毁(节点):
	await Engine.get_main_loop().create_timer(1.0).timeout
	节点.queue_free()
	pass
	
##检测包围盒 并返回碰到属性的碰撞的列表
static func 包围盒检测筛选属性(包围盒位置:Vector2,包围盒尺寸:Vector2,筛选属性:String=""):
	var 筛选过后的列表=包围盒检测(包围盒位置,包围盒尺寸)
	for i in range(筛选过后的列表.size(), 0, - 1):
		if 筛选属性!="":#不是空的时候执行
			if (筛选属性 in 筛选过后的列表[i-1].collider)==false:
				筛选过后的列表.remove_at(i - 1)
	return 筛选过后的列表
	
