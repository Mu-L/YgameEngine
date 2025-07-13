##用于统一管理音乐的东西,嗯
extends Node
class_name 引擎音乐
##用于背景音乐
var 背景音乐播放器:AudioStreamPlayer 
##用于管理背景音乐的音量
var 背景音乐音量:float=1
##用于管理音效的音量
var 音效音量:float=1

func _ready() -> void:
	背景音乐播放器=AudioStreamPlayer.new()
	add_child(背景音乐播放器)

#region 播放音效:通常用于一次性的短音效
##通常用于mav格式一次性的播放，
##[codeblock]
##引擎.音乐.播放音效(load("uid://vh28ybcjpqam"))
##引擎.音乐.播放音效(load("uid://vh28ybcjpqam"),0.5)
##[/codeblock]
func 播放音效(音效:AudioStream,指定音量:float=-1):
	var _音效:AudioStreamPlayer=AudioStreamPlayer.new()
	_音效.stream=音效
	add_child(_音效)
	_音效.finished.connect(func():
		_音效.queue_free()#播放销毁
	)
	var 实际音量 = 指定音量 if 指定音量 >= 0 else 音效音量

	_音效.volume_db=linear_to_db(实际音量)#分贝设置
	_音效.play()#播放
	
#endregion

## 通常用于MP3格式播放，自动循环
##[codeblock]
##引擎.音乐.播放音乐(load("uid://vh28ybcjpqam"))
##[/codeblock]
func 播放音乐(音乐:AudioStreamMP3):
	背景音乐播放器.stream=音乐
	背景音乐播放器.stream.loop=true#设置循环播放
	背景音乐播放器.play()
		

##通常用于播放音乐声音设置,0.5为一半，0是静音
##[codeblock]
##引擎.音乐.设置背景声音大小(0.5)
##[/codeblock]
func 设置背景声音大小(音量:float=0.5):
	背景音乐音量=音量
	背景音乐播放器.volume_db=linear_to_db(背景音乐音量)


##通常用于播放音效声音设置,0.5为一半，0是静音
##[codeblock]
##引擎.音乐.设置音效声音大小(0.5)
##[/codeblock]
func 设置音效声音大小(音量:float=0.5):
	音效音量=音量
	
