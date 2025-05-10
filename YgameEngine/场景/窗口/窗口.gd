extends Node
##引擎的窗口管理
class_name 引擎窗口
##用于存放面板的变量
var 对话面板=null
##用于存放询问面板的变量
var 询问面板=null

##用于游戏的的对话。[对话关闭]自带
##[codeblock]
##引擎.窗口.对话(
##        "[url=链接1]点击这里[/url]\n"+
##        "[url=链接2]点击这里2[/url]\n"+
##        "[url=对话关闭]关闭窗口[/url]"
##    ,{
##        "链接1":func():
##            print("点击1")
##            ,
##        "链接2":func():
##            print("点击2")
##            ,
##    })
##[/codeblock]
func 对话(文本:String,对话包:Dictionary={},标题:String="系统"):
	
	if 对话面板!=null:
		对话面板.queue_free()
	#
	var 面板=load("uid://1dk1hdfmbpa4").instantiate()
	add_child(面板)
	面板.文本.text=文本
	面板.标题.text=标题
	对话面板=面板 #更新
	#正确的 连接 meta_clicked 信号到处理函数
	面板.文本.meta_clicked.connect(func (meta):
		if meta == "对话关闭":
			对话面板.queue_free()
			对话面板=null
		if 对话包.has(meta):
			对话包[meta].call()
	)
		
	pass

##用于简单的询问（是/否等）的对话。
##[codeblock]
##引擎.窗口.询问("你想要做???",{
##        "确定":func():
##            print("点击确定")
##            ,
##        "取消":func():
##            print("取消了")
##            ,
##    })
##[/codeblock]
func 询问(文本:String,对话包:Dictionary={},标题:String="系统"):
	if 询问面板!=null:
		询问面板.queue_free()
	var 面板=load("uid://c6545l8ijawo8").instantiate()
	add_child(面板)
	
	面板.文本.text=文本
	面板.标题.text=标题
	询问面板=面板 #更新
	
	面板.确定.button_down.connect(func():
		if 对话包.has("确定"):
			对话包["确定"].call()
	)
	面板.取消.button_down.connect(func():
		if 对话包.has("取消"):
			对话包["取消"].call()
	)
