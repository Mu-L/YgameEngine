##用于引擎管理音乐的东西,嗯
extends Node
class_name 引擎音乐
##用于背景音乐
var 背景音乐播放器:AudioStreamPlayer 
##用于管理背景音乐的分贝  #-6为一半，-80静音
var 背景音乐分贝:float=1

func _ready() -> void:
	背景音乐播放器=AudioStreamPlayer.new()
	add_child(背景音乐播放器)


#region 播放音效:通常用于一次性的短音效
##通常用于mav格式一次性的播放，
##[codeblock]
##引擎.音乐.播放音效(load("uid://vh28ybcjpqam"))
##引擎.音乐.播放音效(load("uid://vh28ybcjpqam"),0.5)
##[/codeblock]
func 播放音效(音效:AudioStream,分贝:float=1):
	var _音效:AudioStreamPlayer=AudioStreamPlayer.new()
	_音效.stream=音效
	add_child(_音效)
	_音效.finished.connect(func():
		_音效.queue_free()#播放销毁
	)
	_音效.volume_db=_线性音量转分贝(分贝)#分贝设置
	_音效.play()#播放
	pass
#endregion

## 通常用于MP3格式播放，自动循环
##[codeblock]
##引擎.音乐.播放音乐(load("uid://vh28ybcjpqam"))
##[/codeblock]
func 播放音乐(音乐:AudioStreamMP3):
	背景音乐播放器.stream=音乐
	背景音乐播放器.stream.loop=true#设置循环播放
	背景音乐播放器.play()
	pass	

##通常用于播放音乐声音分贝设置,-6为一半，-80静音,0.1-0.9 可假设为百分比 比如0.5是一半声音，0是静音
##[codeblock]
##引擎.音乐.设置声音大小(0.5)
##[/codeblock]
func 设置声音大小(分贝:float=-6):
	背景音乐分贝=_线性音量转分贝(分贝)
	背景音乐播放器.volume_db=背景音乐分贝



func _z():
	# 这是一个私有函数，不会出现在帮助文档中
	
	pass
	
func _线性音量转分贝(线性值: float) -> float:
	"""
	将特定的线性音量值(0.0-1.0)映射到对应的分贝值
	保持与原脚本相同的转换逻辑
	
	参数:
		线性值 - 特定的预设值(0.0, 0.1, ..., 0.9, 1.0)
	
	返回:
		对应的分贝值
	"""
	match 线性值:
		0.9: return -2
		0.8: return -4
		0.7: return -6
		0.6: return -8
		0.5: return -10
		0.4: return -15
		0.3: return -20
		0.2: return -25
		0.1: return -30
		0.0: return -80
		_: return 线性值  # 直接使用传入的分贝值
