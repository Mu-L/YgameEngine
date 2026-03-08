import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import os
import sys
import importlib.util
from pathlib import Path
import json
import time

# 尝试多种方式导入tkinterdnd2
支持拖放 = False
try:
    from tkinterdnd2 import Tk, DND_FILES
    支持拖放 = True
except ImportError:
    try:
        from tkinterdnd2.tkinterdnd2 import Tk, DND_FILES
        支持拖放 = True
    except ImportError:
        try:
            from tkinterdnd2 import TixTk as Tk, DND_FILES
            支持拖放 = True
        except ImportError:
            # 尝试添加可能的安装路径
            站点包路径 = [
                os.path.join(sys.prefix, "Lib", "site-packages"),
                os.path.join(os.path.expanduser("~"), "AppData", "Local", "Programs", "Python", "Python312", "Lib", "site-packages"),
                os.path.join(os.path.expanduser("~"), ".local", "lib", "python3.12", "site-packages")
            ]
            
            for 路径 in 站点包路径:
                if os.path.exists(路径) and 路径 not in sys.path:
                    sys.path.append(路径)
            
            try:
                from tkinterdnd2 import Tk, DND_FILES
                支持拖放 = True
            except ImportError:
                支持拖放 = False

class 多标签数据库编辑器:
    def __init__(self, 根窗口):
        self.根窗口 = 根窗口
        self.根窗口.title("数据库编辑器")
        self.根窗口.geometry("1200x900")
        self.根窗口.minsize(800, 600)
        
        # 获取当前路径作为工作目录，兼容打包后的环境
        if getattr(sys, 'frozen', False):
            # 当程序被打包为exe时，需要特殊处理
            if hasattr(sys, '_MEIPASS'):
                # PyInstaller 打包后的临时目录
                # 但是模块文件夹在 _internal 子目录中
                internal_dir = os.path.join(sys._MEIPASS, '_internal')
                if os.path.exists(internal_dir):
                    self.工作目录 = internal_dir
                else:
                    self.工作目录 = sys._MEIPASS
            else:
                # 回退到exe所在目录
                self.工作目录 = os.path.dirname(sys.executable)
        else:
            # 开发环境中
            self.工作目录 = os.path.dirname(os.path.abspath(__file__))
        
        # 存储每个标签页的编辑器实例
        self.编辑器实例 = {}
        
        # 创建标签控件
        self.标签控件 = ttk.Notebook(self.根窗口)
        self.标签控件.pack(fill=tk.BOTH, expand=True)
        
        # 绑定标签切换事件
        self.标签控件.bind("<<NotebookTabChanged>>", self.切换标签)
        
        # 初始化标签页
        self.初始化标签页()
        
        # 设置全局快捷键
        self.设置全局快捷键()
    
    def 初始化标签页(self):
        """初始化所有标签页"""
        # 自定义标签页排序顺序
        自定义排序顺序 = ["道具", "掉落", "技能", "NPC", "NPC技能", "Buff", "效果buff","技能系统","补丁"]
        
        # 获取工作目录下的所有符合条件的文件夹
        符合条件的文件夹 = []
        try:
            print(f"扫描目录: {self.工作目录}")
            
            # 首先检查当前工作目录
            for 文件夹名称 in os.listdir(self.工作目录):
                文件夹路径 = os.path.join(self.工作目录, 文件夹名称)
                print(f"检查: {文件夹名称} -> {文件夹路径}")
                # 检查是否是文件夹且包含app.py文件
                if os.path.isdir(文件夹路径):
                    app_py路径 = os.path.join(文件夹路径, "app.py")
                    print(f"  app.py路径: {app_py路径} (存在: {os.path.exists(app_py路径)})")
                    if os.path.exists(app_py路径):
                        符合条件的文件夹.append(文件夹名称)
            
            # 如果在当前目录没找到，尝试在父目录查找
            if not 符合条件的文件夹:
                父目录 = os.path.dirname(self.工作目录)
                print(f"在当前目录未找到模块，在父目录查找: {父目录}")
                if os.path.exists(父目录):
                    for 文件夹名称 in os.listdir(父目录):
                        文件夹路径 = os.path.join(父目录, 文件夹名称)
                        if os.path.isdir(文件夹路径):
                            app_py路径 = os.path.join(文件夹路径, "app.py")
                            if os.path.exists(app_py路径):
                                符合条件的文件夹.append(文件夹名称)
                                print(f"在父目录找到: {文件夹名称}")
            
            # 如果还是没找到，尝试在exe同级目录查找
            if not 符合条件的文件夹 and getattr(sys, 'frozen', False):
                exe目录 = os.path.dirname(sys.executable)
                print(f"在exe目录查找: {exe目录}")
                if os.path.exists(exe目录):
                    for 文件夹名称 in os.listdir(exe目录):
                        文件夹路径 = os.path.join(exe目录, 文件夹名称)
                        if os.path.isdir(文件夹路径):
                            app_py路径 = os.path.join(文件夹路径, "app.py")
                            if os.path.exists(app_py路径):
                                符合条件的文件夹.append(文件夹名称)
                                print(f"在exe目录找到: {文件夹名称}")
                                
        except Exception as e:
            messagebox.showerror("错误", f"扫描文件夹时出错: {str(e)}")
            print(f"错误: {e}")
        
        print(f"符合条件的文件夹: {符合条件的文件夹}")
        
        # 按照自定义顺序排序文件夹
        排序后的文件夹 = []
        # 先添加自定义顺序中的文件夹
        for 名称 in 自定义排序顺序:
            if 名称 in 符合条件的文件夹:
                排序后的文件夹.append(名称)
                符合条件的文件夹.remove(名称)
        # 再添加剩余的文件夹（按默认顺序）
        排序后的文件夹.extend(sorted(符合条件的文件夹))
        
        if not 排序后的文件夹:
            # 如果没有找到任何模块，显示错误信息
            error_msg = "未找到任何模块文件夹！\\n请确保以下文件夹存在：\\nBuff/, NPC/, NPC技能/, 技能/, 掉落/, 效果buff/, 道具/"
            ttk.Label(self.标签控件, text=error_msg, padding=20).pack(fill=tk.BOTH, expand=True)
            messagebox.showerror("错误", error_msg)
            return
        
        # 按照排序后的顺序创建标签页
        for 文件夹名称 in 排序后的文件夹:
            # 创建标签页框架
            标签页框架 = ttk.Frame(self.标签控件)
            # 添加标签页
            self.标签控件.add(标签页框架, text=文件夹名称)
            # 存储标签页框架引用
            self.编辑器实例[文件夹名称] = {"框架": 标签页框架, "实例": None}
    
    def 切换标签(self, 事件=None):
        """切换标签时重新加载对应编辑器数据"""
        # 获取当前选中的标签页索引
        当前索引 = self.标签控件.select()
        if not 当前索引:
            return
            
        # 获取标签页文本（即文件夹名称）
        文件夹名称 = self.标签控件.tab(当前索引, "text")
        
        # 如果编辑器已加载，重新加载数据
        if self.编辑器实例[文件夹名称]["实例"] is not None:
            self.重新加载编辑器数据(文件夹名称)
        else:
            # 动态加载并初始化编辑器
            self.加载编辑器(文件夹名称)
    
    def 重新加载编辑器数据(self, 文件夹名称):
        """重新加载编辑器数据"""
        编辑器实例 = self.编辑器实例[文件夹名称]["实例"]
        if 编辑器实例 is None:
            return
            
        try:
            # 清空并重新初始化编辑器，而不仅仅是加载数据
            # 首先销毁所有子组件
            for 子组件 in self.编辑器实例[文件夹名称]["框架"].winfo_children():
                子组件.destroy()
            
            # 重新初始化编辑器实例
            文件夹路径 = os.path.join(self.工作目录, 文件夹名称)
            app_file_path = os.path.join(文件夹路径, "app.py")
            
            # 读取app.py文件内容
            with open(app_file_path, 'r', encoding='utf-8') as f:
                app_code = f.read()
            
            # 创建一个新的临时命名空间
            临时命名空间 = {
                'tk': tk,
                'ttk': ttk,
                'filedialog': filedialog,
                'messagebox': messagebox,
                'simpledialog': simpledialog,
                'json': json,
                'os': os,
                'sys': sys,
                'time': time,
                'Path': Path,
                '__file__': app_file_path,
                '支持拖放': 支持拖放,
                'Tk': Tk if 支持拖放 else tk.Tk,
                'DND_FILES': DND_FILES if 支持拖放 else None,
            }
            
            # 保存原始的sys.argv[0]，之后恢复
            原始_argv0 = sys.argv[0]
            sys.argv[0] = app_file_path
            
            try:
                # 执行app.py代码
                exec(app_code, 临时命名空间)
                
                # 找出主类
                编辑器类 = None
                编辑器类列表 = []
                for 名称, 对象 in 临时命名空间.items():
                    if isinstance(对象, type) and 名称.endswith("编辑器"):
                        编辑器类列表.append((名称, 对象))
                
                # 按照类名长度排序，优先选择更长的类名
                编辑器类列表.sort(key=lambda x: len(x[0]), reverse=True)
                if 编辑器类列表:
                    编辑器类 = 编辑器类列表[0][1]
                
                if 编辑器类:
                     # 创建新的框架包装器
                     class 框架包装器:
                         def __init__(self, 框架, 标题):
                             self.框架 = 框架
                             self.标题 = 标题
                             # 存储一些常用窗口属性的默认值
                             self.winfo_width = lambda: 1200
                             self.winfo_height = lambda: 800
                             self.minsize = lambda w=None, h=None: None
                             self.maxsize = lambda w=None, h=None: None
                             self.geometry = lambda s=None: None
                             self.configure = self.框架.configure
                             self.bind = self.框架.bind
                             self.unbind = self.框架.unbind
                             self.focus_set = self.框架.focus_set
                             self.protocol = lambda *args: None  # 忽略协议处理
                             self.resizable = lambda w=None, h=None: None
                             
                             # 添加_tkinter窗口路径属性
                             self._w = self.框架._w
                             # 添加tk属性
                             self.tk = self.框架.tk
                             # 添加winfo_toplevel方法，返回实际的顶层窗口
                             self.winfo_toplevel = lambda: self.框架.winfo_toplevel()
                             # 添加winfo_parent方法
                             self.winfo_parent = lambda: self.框架.winfo_parent()
                             # 添加winfo_id方法
                             self.winfo_id = lambda: self.框架.winfo_id()
                             
                         def title(self, t=None):
                             """忽略标题设置"""
                             return self.标题
                             
                         def wm_transient(self, master=None):
                             """处理临时窗口，避免传递包装器对象"""
                             if master is self:
                                 master = self.框架
                             return self.框架.tk.call('wm', 'transient', self._w, master._w if hasattr(master, '_w') else master)
                             
                         def __str__(self):
                             """返回正确的窗口路径名，用于Tkinter命令"""
                             return self._w
                             
                         def __repr__(self):
                             """返回正确的窗口路径名，用于调试和Tkinter命令"""
                             return self._w
                             
                         def __getattr__(self, attr):
                             """将其他属性和方法委托给实际的Frame"""
                             try:
                                 return getattr(self.框架, attr)
                             except AttributeError:
                                 # 如果Frame也没有该属性，返回一个空操作函数
                                 return lambda *args, **kwargs: None
                
                # 创建包装后的框架
                包装后的框架 = 框架包装器(self.编辑器实例[文件夹名称]["框架"], 文件夹名称)
                
                # 重新初始化编辑器
                self.编辑器实例[文件夹名称]["实例"] = 编辑器类(包装后的框架)
                
                # 确保所有组件正确显示
                self.编辑器实例[文件夹名称]["框架"].update_idletasks()
                
                # 显示重新加载成功提示
                self.显示状态提示(f"{文件夹名称} 编辑器已重新加载")
            finally:
                # 恢复原始的sys.argv[0]
                sys.argv[0] = 原始_argv0
        except Exception as e:
            messagebox.showerror("重新加载错误", f"重新加载 {文件夹名称} 编辑器失败: {str(e)}")
    
    def 加载编辑器(self, 文件夹名称):
        """动态加载编辑器"""
        文件夹路径 = os.path.join(self.工作目录, 文件夹名称)
        app_file_path = os.path.join(文件夹路径, "app.py")
        
        try:
            # 读取app.py文件内容
            with open(app_file_path, 'r', encoding='utf-8') as f:
                app_code = f.read()
            
            # 创建一个临时命名空间
            临时命名空间 = {
                'tk': tk,
                'ttk': ttk,
                'filedialog': filedialog,
                'messagebox': messagebox,
                'simpledialog': simpledialog,
                'json': json,
                'os': os,
                'sys': sys,
                'time': time,
                'Path': Path,
                '__file__': app_file_path,  # 正确设置__file__变量为编辑器的app.py路径
                '支持拖放': 支持拖放,  # 传递拖放支持状态给编辑器
                'Tk': Tk if 支持拖放 else tk.Tk,  # 传递正确的Tk类
                'DND_FILES': DND_FILES if 支持拖放 else None,  # 传递拖放常量
            }
            
            # 保存原始的sys.argv[0]，之后恢复
            原始_argv0 = sys.argv[0]
            # 设置sys.argv[0]为当前编辑器的app.py路径
            sys.argv[0] = app_file_path
            
            # 创建一个包装类，为Frame添加title等方法以兼容编辑器
            class 框架包装器:
                def __init__(self, 框架, 标题):
                    self.框架 = 框架
                    self.标题 = 标题
                    # 存储一些常用窗口属性的默认值
                    self.winfo_width = lambda: 1200
                    self.winfo_height = lambda: 800
                    self.minsize = lambda w=None, h=None: None
                    self.maxsize = lambda w=None, h=None: None
                    self.geometry = lambda s=None: None
                    self.configure = self.框架.configure
                    self.bind = self.框架.bind
                    self.unbind = self.框架.unbind
                    self.focus_set = self.框架.focus_set
                    self.protocol = lambda *args: None  # 忽略协议处理
                    self.resizable = lambda w=None, h=None: None
                    
                    # 添加_tkinter窗口路径属性
                    self._w = self.框架._w
                    # 添加tk属性
                    self.tk = self.框架.tk
                    # 添加winfo_toplevel方法，返回实际的顶层窗口
                    self.winfo_toplevel = lambda: self.框架.winfo_toplevel()
                    # 添加winfo_parent方法
                    self.winfo_parent = lambda: self.框架.winfo_parent()
                    # 添加winfo_id方法
                    self.winfo_id = lambda: self.框架.winfo_id()
                    
                def title(self, t=None):
                    """忽略标题设置"""
                    return self.标题
                    
                def wm_transient(self, master=None):
                    """处理临时窗口，避免传递包装器对象"""
                    if master is self:
                        master = self.框架
                    return self.框架.tk.call('wm', 'transient', self._w, master._w if hasattr(master, '_w') else master)
                    
                def __str__(self):
                    """返回正确的窗口路径名，用于Tkinter命令"""
                    return self._w
                    
                def __repr__(self):
                    """返回正确的窗口路径名，用于调试和Tkinter命令"""
                    return self._w
                    
                def __getattr__(self, attr):
                    """将其他属性和方法委托给实际的Frame"""
                    try:
                        return getattr(self.框架, attr)
                    except AttributeError:
                        # 如果Frame也没有该属性，返回一个空操作函数
                        return lambda *args, **kwargs: None
            
            # 创建包装后的框架
            包装后的框架 = 框架包装器(self.编辑器实例[文件夹名称]["框架"], 文件夹名称)
            
            # 执行app.py代码
            exec(app_code, 临时命名空间)
            
            # 找出主类并初始化
            编辑器类 = None
            编辑器类列表 = []
            for 名称, 对象 in 临时命名空间.items():
                if isinstance(对象, type) and 名称.endswith("编辑器"):
                    编辑器类列表.append((名称, 对象))
            
            # 按照类名长度排序，优先选择更长的类名（通常是更具体的编辑器类）
            编辑器类列表.sort(key=lambda x: len(x[0]), reverse=True)
            if 编辑器类列表:
                编辑器类 = 编辑器类列表[0][1]
            
            if 编辑器类:
                # 清空标签页框架
                for 子组件 in self.编辑器实例[文件夹名称]["框架"].winfo_children():
                    子组件.destroy()
                
                # 使用包装后的框架初始化编辑器
                self.编辑器实例[文件夹名称]["实例"] = 编辑器类(包装后的框架)
                
                # 确保所有组件正确显示
                self.编辑器实例[文件夹名称]["框架"].update_idletasks()
            else:
                messagebox.showerror("错误", f"在 {文件夹名称}/app.py 中未找到编辑器类")
                
        except Exception as e:
            messagebox.showerror("加载错误", f"加载 {文件夹名称} 编辑器失败: {str(e)}")
        finally:
            # 恢复原始的sys.argv[0]
            sys.argv[0] = 原始_argv0
    
    def 设置全局快捷键(self):
        """设置全局快捷键"""
        # 绑定Ctrl+S保存快捷键
        self.根窗口.bind("<Control-s>", self.全局保存)
        self.根窗口.bind("<Control-S>", self.全局保存)
    
    def 全局保存(self, 事件=None):
        """全局保存功能"""
        # 获取当前选中的标签页索引
        当前索引 = self.标签控件.select()
        if not 当前索引:
            return
            
        # 获取标签页文本（即文件夹名称）
        文件夹名称 = self.标签控件.tab(当前索引, "text")
        
        # 获取当前编辑器实例
        当前编辑器 = self.编辑器实例.get(文件夹名称, {}).get("实例")
        if 当前编辑器:
            # 尝试各种可能的保存方法
            保存成功 = False
            try:
                if hasattr(当前编辑器, '保存数据快捷键'):
                    当前编辑器.保存数据快捷键()
                    保存成功 = True
                elif hasattr(当前编辑器, '保存数据'):
                    当前编辑器.保存数据()
                    保存成功 = True
                elif hasattr(当前编辑器, '保存NPC数据'):
                    当前编辑器.保存NPC数据()
                    保存成功 = True
                elif hasattr(当前编辑器, '保存Buff配置数据'):
                    当前编辑器.保存Buff配置数据(强制=True)
                    保存成功 = True
                elif hasattr(当前编辑器, '保存'):
                    当前编辑器.保存()
                    保存成功 = True
                elif hasattr(当前编辑器, 'save'):
                    当前编辑器.save()
                    保存成功 = True
                
                if 保存成功:
                    # 显示保存成功提示
                    self.显示状态提示(f"{文件夹名称} 数据已保存")
            except Exception as e:
                messagebox.showerror("保存错误", f"保存 {文件夹名称} 数据时出错: {str(e)}")
        
        # 阻止事件传播
        return "break"
    
    def 显示状态提示(self, 消息):
        """显示状态提示"""
        # 检查是否已有状态栏
        if not hasattr(self, '状态栏'):
            self.状态栏 = ttk.Label(self.根窗口, text="", relief=tk.SUNKEN, anchor=tk.W)
            self.状态栏.pack(side=tk.BOTTOM, fill=tk.X)
        
        # 更新状态栏文本
        self.状态栏.config(text=消息)
        
        # 2秒后清除提示
        self.根窗口.after(2000, lambda: self.状态栏.config(text=""))

if __name__ == "__main__":
    # 根据是否支持拖放选择根窗口类
    if 支持拖放:
        根窗口 = Tk()
    else:
        根窗口 = tk.Tk()
    应用 = 多标签数据库编辑器(根窗口)
    根窗口.mainloop()