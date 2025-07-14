extends Node

class_name 引擎图片

static func 从内存创建图片(图片地址,_x,_y,_sx,_sy):
	var 图片=load(图片地址)
	var 裁剪图片=图片.get_image()
	var _rect=Rect2i(int(_x),int(_y),int(_sx),int(_sy))
	裁剪图片=裁剪图片.get_region(_rect)#进行裁剪
	#读取裁剪图片的纹理
	var texture = ImageTexture.new() 
	texture.set_image(裁剪图片)
	return texture
