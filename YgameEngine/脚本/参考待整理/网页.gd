## 关于网页请求get post的东西
##
## 
extends Node2D
class_name 网页  
  
##用于一次性GET请求
####await 网页.请求(self,"https://xx..com/updata.json")
static func 请求_GET(请求链接: String,响应头:PackedStringArray=PackedStringArray(),请求类型:HTTPClient.Method=HTTPClient.Method.METHOD_GET,请求数据:String=""):
	请求链接=URL_编码(请求链接)
	var 网页节点 = HTTPRequest.new()
	Engine.get_main_loop().current_scene.add_child(网页节点)
	### 执行一个 GET 请求。以下 URL 会将写入作为 JSON 返回。
	var error = 网页节点.request(请求链接,响应头,请求类型,请求数据)
	if error!=OK:
		return {"请求状态":error,"网页状态码":-1}
	else :	
		var 返回值=await 网页节点.request_completed
		return {"请求状态":返回值[0],"网页状态码":返回值[1],"响应头":返回值[2],"内容":返回值[3].get_string_from_utf8()}
	网页节点.queue_free()
	
##用于一次性GET请求,但是拥有解析JSON到字典的能力
##
##await 网页.请求并解析JSON(self,"https://xx..com/updata.json")
##
##节点位置：鬼知道请求需要一个临时存放节点的位置，所以正常导入一个

static func 请求_GET并解析JSON(请求链接: String,响应头:PackedStringArray=PackedStringArray(),请求类型:HTTPClient.Method=HTTPClient.Method.METHOD_GET,请求数据:String=""):
	请求链接=URL_编码(请求链接)
	var 网页节点 = HTTPRequest.new()
	Engine.get_main_loop().current_scene.add_child(网页节点)
	### 执行一个 GET 请求。以下 URL 会将写入作为 JSON 返回。
	var error = 网页节点.request(请求链接,响应头,请求类型,请求数据)
	if error!=OK:
		return {"请求状态":error,"网页状态码":-1}
	else :	
		var 返回值=await 网页节点.request_completed
		return {"请求状态":返回值[0],"网页状态码":返回值[1],"响应头":返回值[2],"内容":JSON.parse_string(返回值[3].get_string_from_utf8())}
	网页节点.queue_free()



##还没做好
static func 请求_POST(请求链接: String,响应头:PackedStringArray=PackedStringArray(),请求类型:HTTPClient.Method=HTTPClient.Method.METHOD_POST,请求数据:String=""):
	请求链接=URL_编码(请求链接)
	var 网页节点 = HTTPRequest.new()
	var body = JSON.new().stringify({"name": "Godette"})
	var error = 网页节点.request("https://afdian.net/api/open/query-order", 响应头, 请求类型, body)
	if error != OK:
		push_error("在HTTP请求中发生了一个错误。")


## 能够一次性,下载文件的接口,你并不需要关心进度,只知道完成了会返回
static func 请求下载文件(直链地址:String,存放地址:String="res://Update.zip"):
	直链地址=URL_编码(直链地址)
	var 网页节点 = HTTPRequest.new()
	Engine.get_main_loop().current_scene.add_child(网页节点)
	网页节点.download_file=存放地址 #存放下载的zip位置

	var error = 网页节点.request(直链地址)
	if error!=OK:
		return {"请求状态":error,"网页状态码":-1}
	else:
		var 返回值= await 网页节点.request_completed
		return {"请求状态":返回值[0],"网页状态码":返回值[1],"响应头":返回值[2],"内容":返回值[3].get_string_from_utf8()}
	网页节点.queue_free()
	
## 用于你需要实时监听下载的文件实时更新,示例:
##var 网页节点= 网页.请求下载文件_响应("https://8973.kstore.space/update/game.rar").网页节点
##	#while (网页.取当前下载文件的大小(网页节点)!=网页.取响应下载文件的大小(网页节点)):
##		#await 场景.等待(0.5)
##		#调试.注释打印("下载中","%s/%s" % [网页.取当前下载文件的大小(网页节点),网页.取响应下载文件的大小(网页节点)])
##	#调试.打印("下载完成") 
static func 请求下载文件_响应(直链地址:String,存放地址:String="user://Update.zip"):
	直链地址=URL_编码(直链地址)
	print("开始请求下载")	
	var 网页节点 = HTTPRequest.new()
	Engine.get_main_loop().current_scene.add_child(网页节点)
	网页节点.download_file=存放地址 #存放下载的zip位置

	var error = 网页节点.request(直链地址)
	if error!=OK:
		return {"请求状态":error,"网页状态码":-1}
	else:
		return {"请求状态":0,"网页状态码":200,"网页节点":网页节点}
#		
## 取到需要下载文件的总大小,单位为:byte
static func 取响应下载文件的大小(网页节点:Node):	
	return 网页节点.get_body_size()
	
## 取已经下载多少文件的大小,单位为:byte
static func 取当前下载文件的大小(网页节点:Node):
	return 网页节点.get_downloaded_bytes()

##对URL进行友好的编码转换,只对非英文转换编码
##网页.URL_编码("https://www.xxx.com/update/场景.zip")
static func URL_编码(链接:String):
	#var 字符串="https://8973.kstore.space/update/场景-场景.zip"
	var 新字符串=""
	for i in 链接:
		if i.unicode_at(0)<=122:#英文字母最大到122
			新字符串+=i
		else:
			新字符串+=i.uri_encode()
	return 新字符串
	
##URL链接解码
static func URL_解码(链接:String):
	return 链接.uri_decode()	
	
