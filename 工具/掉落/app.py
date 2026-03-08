# cython: language_level=3
# cython: c_string_encoding=utf-8
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import json
import os
import sys
from pathlib import Path
import re

# 尝试多种方式导入tkinterdnd2（如果需要拖放功能）
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
                print("警告: 未安装tkinterdnd2库或无法导入，拖放功能将不可用。")
                print("请尝试使用以下命令安装：")
                print("pip install --upgrade tkinterdnd2")


class 掉落编辑器:
    def __init__(self, 主窗口):
        self.主窗口 = 主窗口
        self.主窗口.title("Godot掉落编辑器 ver1.4（单文件多配置版）")
        self.主窗口.geometry("1500x750")
        self.主窗口.minsize(1500, 750)
        
        # 初始化状态变量
        self.状态变量 = tk.StringVar(value="就绪 (按Ctrl+S保存)")
        self.未保存标记 = False  # 标记是否有未保存内容
        
        # 计算路径
        self.计算项目路径()
        
        # ------------------------------
        # 新增：颜色配置初始化（在数据加载前执行）
        # ------------------------------
        self.初始化颜色配置()  # 加载item_color.json
        self.是否启用自定义底色 = tk.BooleanVar(value=True)  # 强制启用自定义底色（适配需求）
        
        # 数据存储（改为单文件多配置项）
        self.物品数据 = {}  # 从itemsystem.json加载的物品数据
        self.所有掉落数据 = {}  # 整个drop_data.json的内容，键是配置项名（如"掉落_全局"）
        self.当前配置键 = ""  # 当前编辑的配置项键名
        self.当前掉落数据 = {}  # 当前编辑的配置项数据
        self.当前掉落类型 = ""  # "掉落"或"宝物"
        self.活跃编辑框 = None  # 跟踪当前活跃的编辑框
        
        # 配置文件路径（改为单文件）
        self.物品系统文件 = os.path.join(self.系统文件夹, "itemsystem.json")
        self.掉落数据文件 = os.path.join(self.系统文件夹, "drop_data.json")  # 单文件存储所有配置项
        self.颜色配置文件 = os.path.join(self.系统文件夹, "item_color.json")  # 新增：颜色配置文件路径
        
        # 配置提示选项
        self.显示成功提示弹窗 = True  # 是否显示成功提示弹窗
        
        # 确保目录存在
        self.确保目录存在(self.系统文件夹)
        
        # 创建UI
        self.创建界面组件()
        
        # 初始化并加载数据
        self.加载物品数据()
        self.加载所有掉落数据()  # 加载单文件中的所有配置项
        
        # 绑定快捷键
        self.设置快捷键()
    
    # ------------------------------
    # 新增：颜色配置相关方法（核心优化）
    # ------------------------------
    def 初始化颜色配置(self):
        """初始化颜色配置（默认值+加载item_color.json）"""
        # 兜底默认值（防止配置文件缺失）
        self.默认列表底色 = "#ffffff"  # 默认白底
        self.默认列表文字色 = "black"   # 默认黑字
        self.品质颜色映射 = {           # 默认品质-颜色映射
            1.0: "#00FF00", 2.0: "#0000FF", 3.0: "#FF00FF",
            4.0: "#FFFF00", 5.0: "#FF8C00", 6.0: "#FF0000"
        }

    def 加载颜色配置(self):
        """加载item_color.json中的底色和品质颜色映射"""
        if not os.path.exists(self.颜色配置文件):
            self.显示提示(f"未找到item_color.json，使用默认样式（白底黑字）", 显示弹窗=False)
            return
        
        try:
            with open(self.颜色配置文件, 'r', encoding='utf-8') as f:
                配置数据 = json.load(f)
            
            # 读取默认底色（优先使用配置中的值）
            if "默认底色" in 配置数据 and isinstance(配置数据["默认底色"], str):
                self.默认列表底色 = 配置数据["默认底色"]
            # 读取默认文字色
            if "默认颜色" in 配置数据 and isinstance(配置数据["默认颜色"], str):
                self.默认列表文字色 = 配置数据["默认颜色"]
            # 读取品质颜色映射（转换为float键，确保匹配道具品质值）
            if "品质颜色映射" in 配置数据 and isinstance(配置数据["品质颜色映射"], dict):
                临时映射 = {}
                for 品质_str, 颜色 in 配置数据["品质颜色映射"].items():
                    try:
                        品质_float = float(品质_str)  # 品质值统一转为浮点数（如"1.0"→1.0）
                        临时映射[品质_float] = 颜色
                    except ValueError:
                        self.显示提示(f"item_color.json中品质值'{品质_str}'无效，跳过", 成功=False, 显示弹窗=False)
                if 临时映射:  # 仅当配置有效时更新
                    self.品质颜色映射 = 临时映射
        
            self.显示提示(f"已加载颜色配置（底色：{self.默认列表底色}）", 显示弹窗=False)
        except Exception as e:
            self.显示提示(f"加载item_color.json失败：{str(e)}，使用默认样式", 成功=False, 显示弹窗=False)

    def 获取道具文字颜色(self, 道具品质):
        """根据道具品质值，获取对应的文字颜色（匹配品质颜色映射）"""
        try:
            品质_float = float(道具品质)  # 确保品质值为浮点数
            # 优先匹配精确品质值，无匹配则返回默认文字色
            return self.品质颜色映射.get(品质_float, self.默认列表文字色)
        except (ValueError, TypeError):
            # 若品质值无效（如文本），返回默认文字色
            return self.默认列表文字色

    # ------------------------------
    # 原有方法：路径计算（无修改）
    # ------------------------------
    def 计算项目路径(self):
        """计算项目根目录和系统文件夹路径"""
        try:
            # 获取当前执行文件的路径
            if getattr(sys, 'frozen', False):
                # 当程序被打包为exe时
                当前路径 = os.path.dirname(sys.executable)
            else:
                # 开发环境中
                当前路径 = os.path.dirname(os.path.abspath(__file__))
            
            # 从addons\YgameEngine\工具\向上三级找到项目根目录
            项目根目录 = os.path.abspath(os.path.join(当前路径, "..", "..", "..",".."))
            
            # 系统文件夹路径
            self.系统文件夹 = os.path.join(项目根目录, "系统")
            
            # 确保系统文件夹存在
            self.确保目录存在(self.系统文件夹)
            
            # 显示路径信息（调试用）
            print(f"当前执行路径: {当前路径}")
            print(f"项目根目录: {项目根目录}")
            print(f"系统文件夹: {self.系统文件夹}")
            
        except Exception as e:
            messagebox.showerror("路径计算错误", f"无法计算项目路径: {str(e)}")
            # fallback到当前目录
            self.系统文件夹 = os.path.join(os.getcwd(), "系统")
            self.确保目录存在(self.系统文件夹)
    
    # ------------------------------
    # 原有方法：快捷键设置（无修改）
    # ------------------------------
    def 设置快捷键(self):
        """设置快捷键"""
        # 绑定Ctrl+S保存
        self.主窗口.bind("<Control-s>", self.保存数据快捷键)
        self.主窗口.bind("<Control-S>", self.保存数据快捷键)
        # 绑定到主框架
        self.主框架.bind("<Control-s>", self.保存数据快捷键)
        self.主框架.bind("<Control-S>", self.保存数据快捷键)
    
    def 保存数据快捷键(self, 事件=None):
        """快捷键触发的保存功能"""
        self.保存数据()
        return "break"
    
    # ------------------------------
    # 原有方法：提示显示（无修改）
    # ------------------------------
    def 显示提示(self, 消息, 成功=True, 显示弹窗=None):
        """显示操作提示"""
        # 更新状态栏
        self.状态变量.set(消息)
        
        # 显示弹窗（如果需要）
        if 显示弹窗 or (显示弹窗 is None and self.显示成功提示弹窗):
            if 成功:
                messagebox.showinfo("操作成功", 消息)
            else:
                messagebox.showwarning("操作提示", 消息)
    
    def 更新状态栏(self):
        """根据未保存状态更新状态栏"""
        if self.未保存标记:
            self.状态变量.set("有未保存的更改 (按Ctrl+S保存)")
        else:
            self.状态变量.set(f"已保存到: {os.path.basename(self.掉落数据文件)}")
    
    # ------------------------------
    # 原有方法：目录创建（无修改）
    # ------------------------------
    def 确保目录存在(self, 目录):
        """确保目录存在，如果不存在则创建"""
        try:
            Path(目录).mkdir(parents=True, exist_ok=True)
            self.显示提示(f"目录已准备就绪: {目录}", 显示弹窗=False)
            return True
        except Exception as e:
            messagebox.showerror("目录错误", f"无法创建目录 {目录}：{str(e)}")
            return False
    
    # ------------------------------
    # 原有方法：物品数据加载（修改：添加颜色配置加载+列表样式设置）
    # ------------------------------
    def 加载物品数据(self):
        """加载物品数据，用于显示ID+名称（新增：加载颜色配置+样式适配）"""
        # 新增：加载颜色配置（每次刷新物品列表时重新加载，确保配置更新生效）
        self.加载颜色配置()
        
        if os.path.exists(self.物品系统文件):
            try:
                with open(self.物品系统文件, 'r', encoding='utf-8') as f:
                    self.物品数据 = json.load(f)
                self.显示提示(f"已加载物品数据: {len(self.物品数据)}个物品", 显示弹窗=False)
                # 更新物品列表（新增：传入颜色配置，设置列表样式）
                self.更新物品列表()
                self.初始化掉落树颜色样式()
            except Exception as e:
                messagebox.showerror("加载错误", f"无法加载{self.物品系统文件}：{str(e)}")
                self.物品数据 = {}
        else:
            #messagebox.showwarning("警告", f"未找到物品系统文件：{self.物品系统文件}")
            self.物品数据 = {}
    
    # ------------------------------
    # 原有方法：UI创建（无修改，确保物品列表框架变量名正确）
    # ------------------------------
    def 创建界面组件(self):
        """创建UI组件"""
        # 主框架
        self.主框架 = ttk.Frame(self.主窗口, padding="10")
        self.主框架.pack(fill=tk.BOTH, expand=True)
        
        # 文件操作工具栏
        文件工具栏 = ttk.Frame(self.主框架)
        文件工具栏.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(文件工具栏, text="新建配置项", command=self.新建配置项).pack(side=tk.LEFT, padx=2)
        ttk.Button(文件工具栏, text="保存文件 (Ctrl+S)", command=self.保存数据).pack(side=tk.LEFT, padx=2)
        ttk.Button(文件工具栏, text="刷新物品列表", command=self.加载物品数据).pack(side=tk.LEFT, padx=2)
        
        # 当前文件路径显示
        self.当前文件路径变量 = tk.StringVar(value=os.path.basename(self.掉落数据文件))
        ttk.Label(文件工具栏, textvariable=self.当前文件路径变量).pack(side=tk.RIGHT, padx=10)
        
        # 主内容区域
        内容总框架 = ttk.Frame(self.主框架)
        内容总框架.pack(fill=tk.BOTH, expand=True)
        
        # 左侧配置项列表框架（原文件列表改为配置项列表）
        左侧配置项框架 = ttk.LabelFrame(内容总框架, text="配置项列表（drop_data.json）", padding="5")
        左侧配置项框架.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))
        
        # 配置项列表框
        self.配置项列表框 = tk.Listbox(左侧配置项框架, width=25, height=35)
        self.配置项列表框.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.配置项列表框.bind('<<ListboxSelect>>', self.处理配置项选择)
        
        # 配置项列表滚动条
        配置项滚动条 = ttk.Scrollbar(左侧配置项框架, orient=tk.VERTICAL, command=self.配置项列表框.yview)
        配置项滚动条.pack(side=tk.RIGHT, fill=tk.Y)
        self.配置项列表框.config(yscrollcommand=配置项滚动条.set)
        
        # 配置项操作按钮区域
        配置项按钮框架 = ttk.Frame(左侧配置项框架)
        配置项按钮框架.pack(fill=tk.X, pady=5, padx=5)
        
        ttk.Button(配置项按钮框架, text="删除选中配置项", command=self.删除选中配置项).pack(padx=2, pady=2, fill=tk.X, expand=True)
        ttk.Button(配置项按钮框架, text="刷新配置项", command=self.加载所有掉落数据).pack(padx=2, pady=2, fill=tk.X, expand=True)
        
        # 左侧物品列表框架
        左侧物品框架 = ttk.LabelFrame(内容总框架, text="物品列表 (ID+名称)", padding="5")
        左侧物品框架.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=(5, 10))
        
        # 物品列表（关键：确保变量名为self.物品列表框，后续用于设置样式）
        self.物品列表框 = tk.Listbox(左侧物品框架, width=30, height=35, selectmode=tk.SINGLE,font=("SimHei", 12,"bold"))
        self.物品列表框.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        self.物品列表框.bind('<<ListboxSelect>>', self.处理物品选择)
        
        # 物品列表滚动条
        物品滚动条 = ttk.Scrollbar(左侧物品框架, orient=tk.VERTICAL, command=self.物品列表框.yview)
        物品滚动条.pack(side=tk.RIGHT, fill=tk.Y)
        self.物品列表框.config(yscrollcommand=物品滚动条.set)
        
        # 添加到掉落列表的按钮
        ttk.Button(左侧物品框架, text="添加到掉落列表", command=self.添加选中物品到掉落列表).pack(fill=tk.X, pady=5, padx=5)
        
        # 中间掉落列表
        中间框架 = ttk.LabelFrame(内容总框架, text="掉落列表", padding="5")
        中间框架.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # 掉落控制总框架：整合类型显示、权重设置、操作按钮
        self.掉落控制总框架 = ttk.Frame(中间框架)
        self.掉落控制总框架.pack(fill=tk.X, pady=(0, 10))
        
        # 掉落类型显示
        self.掉落类型变量 = tk.StringVar(value="未选择配置项")
        ttk.Label(self.掉落控制总框架, textvariable=self.掉落类型变量, font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=5)
        
        # 权重的掉落数量（仅宝物类型）
        ttk.Label(self.掉落控制总框架, text="权重的掉落数量:").pack(side=tk.LEFT, padx=5)
        self.权重掉落数量变量 = tk.StringVar(value="1.0")
        ttk.Entry(self.掉落控制总框架, textvariable=self.权重掉落数量变量, width=10).pack(side=tk.LEFT, padx=5)
        
        # 操作按钮区域（删除/清空按钮）
        掉落按钮框架 = ttk.Frame(self.掉落控制总框架)
        掉落按钮框架.pack(side=tk.RIGHT, padx=5)
        
        ttk.Button(掉落按钮框架, text="删除选中项", command=self.删除选中掉落项).pack(side=tk.LEFT, padx=2)
        ttk.Button(掉落按钮框架, text="清空列表", command=self.清空掉落列表).pack(side=tk.LEFT, padx=2)
        
        # 掉落列表树
        列 = ()  # 后面根据类型动态设置
        self.掉落树 = ttk.Treeview(中间框架, columns=列, show="headings", height=25, selectmode=tk.EXTENDED)
        
        # 掉落列表滚动条
        掉落滚动条 = ttk.Scrollbar(中间框架, orient=tk.VERTICAL, command=self.掉落树.yview)
        self.掉落树.configure(yscrollcommand=掉落滚动条.set)
        
        # 掉落列表布局
        self.掉落树.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        掉落滚动条.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 状态栏
        状态栏 = ttk.Label(self.主窗口, textvariable=self.状态变量, relief=tk.SUNKEN, anchor=tk.W)
        状态栏.pack(side=tk.BOTTOM, fill=tk.X)
        
        # 绑定编辑框内容变化事件
        self.权重掉落数量变量.trace_add("write", lambda *args: [setattr(self, '未保存标记', True), self.更新状态栏()])
        
        # 窗口关闭事件
        self.主窗口.protocol("WM_DELETE_WINDOW", self.处理关闭)
    
    # ------------------------------
    # 原有方法：掉落数据加载（无修改）
    # ------------------------------
    def 加载所有掉落数据(self):
        """加载drop_data.json中的所有配置项，若文件不存在则自动创建"""
        self.配置项列表框.delete(0, tk.END)  # 清空列表
        self.所有掉落数据 = {}  # 重置数据
        
        # 检查文件是否存在，不存在则创建空文件
        if not os.path.exists(self.掉落数据文件):
            try:
                # 直接创建空的JSON文件
                with open(self.掉落数据文件, 'w', encoding='utf-8') as f:
                    json.dump({}, f, ensure_ascii=False, indent=2)
                self.显示提示(f"已自动创建 {os.path.basename(self.掉落数据文件)}", 显示弹窗=False)
            except Exception as e:
                messagebox.showerror("创建文件错误", f"无法创建文件：{str(e)}")
                self.配置项列表框.insert(tk.END, "无配置项（可新建）")
                return
        
        # 加载文件
        try:
            with open(self.掉落数据文件, 'r', encoding='utf-8') as f:
                self.所有掉落数据 = json.load(f)
            
            # 显示配置项到列表
            if self.所有掉落数据:
                for 配置项键 in self.所有掉落数据.keys():
                    self.配置项列表框.insert(tk.END, 配置项键)
                self.显示提示(f"已加载 {len(self.所有掉落数据)} 个配置项", 显示弹窗=False)
            else:
                self.配置项列表框.insert(tk.END, "无配置项（可新建）")
        except Exception as e:
            messagebox.showerror("加载错误", f"加载drop_data.json时出错：{str(e)}")
            self.所有掉落数据 = {}

    
    # ------------------------------
    # 原有方法：配置项选择（无修改）
    # ------------------------------
    def 处理配置项选择(self, 事件):
        """处理配置项列表中的选择，加载选中的配置项数据"""
        选中项 = self.配置项列表框.curselection()
        if not 选中项:
            return
            
        配置项键 = self.配置项列表框.get(选中项[0])
        # 跳过提示文本
        if 配置项键 == "无配置项（可新建）":
            return
            
        # 检查配置项是否存在
        if 配置项键 in self.所有掉落数据:
            self.加载配置项数据(配置项键, self.所有掉落数据[配置项键])
        else:
            messagebox.showerror("错误", f"配置项 '{配置项键}' 不存在或已损坏")
    
    # ------------------------------
    # 原有方法：配置项数据加载（无修改）
    # ------------------------------
    def 加载配置项数据(self, 配置项键, 数据):
        """加载指定配置项的数据到编辑区域"""
        # 验证数据格式
        if "类别" not in 数据:
            raise Exception("配置项格式不正确，缺少'类别'字段")
        
        类型 = 数据["类别"]
        if 类型 not in ["掉落", "宝物"]:
            raise Exception(f"不支持的类型: {类型}，仅支持'掉落'和'宝物'")
        
        # 设置当前类型和数据
        self.当前配置键 = 配置项键
        self.当前掉落类型 = 类型
        self.掉落类型变量.set(f"当前配置: {配置项键} (类型: {类型})")
        self.当前掉落数据 = 数据.copy()
        
        # 设置列表列
        self.设置掉落列表列(类型)
        
        # 清空现有列表
        for 项 in self.掉落树.get_children():
            self.掉落树.delete(项)
        # 初始化掉落树颜色样式（每次加载都刷新，确保配置变更生效）
        self.初始化掉落树颜色样式()
        # 加载数据到列表
        if 类型 == "掉落":
            # 隐藏权重相关控件（掉落类型不需要）
            for widget in self.掉落控制总框架.winfo_children():
                if isinstance(widget, ttk.Label) and widget["text"] == "权重的掉落数量:":
                    widget.pack_forget()
                if isinstance(widget, ttk.Entry) and widget["textvariable"] == self.权重掉落数量变量:
                    widget.pack_forget()
            
            if "掉落" in 数据:
                for 项 in 数据["掉落"]:
                    物品ID = 项.get("物品ID", "")
                    名称 = self.物品数据.get(物品ID, {}).get("名称", "未知物品")
                    
                    # 替换原有 self.掉落树.insert("", tk.END, values=(...))
                    tag = self.获取物品品质tag(物品ID)
                    self.掉落树.insert("", tk.END, values=(
                        物品ID,
                        名称,
                        str(项.get("掉落几率", 0)),
                        str(项.get("最小等级", 0)),
                        str(项.get("最大等级", 0)),
                        str(项.get("掉落最小数量", 1)),
                        str(项.get("掉落最大数量", 1))
                    ), tags=(tag,))
        
        else:  # 宝物类型
            # 显示权重相关控件（宝物类型需要）
            for widget in self.掉落控制总框架.winfo_children():
                if isinstance(widget, ttk.Label) and widget["text"] == "权重的掉落数量:":
                    widget.pack(side=tk.LEFT, padx=5)
                if isinstance(widget, ttk.Entry) and widget["textvariable"] == self.权重掉落数量变量:
                    widget.pack(side=tk.LEFT, padx=5)
            
            # 设置权重掉落数量
            self.权重掉落数量变量.set(str(数据.get("权重的掉落数量", 1.0)))
            
            if "宝物" in 数据:
                for 项 in 数据["宝物"]:
                    物品ID = 项.get("物品ID", "")
                    名称 = self.物品数据.get(物品ID, {}).get("名称", "未知物品")
                    
                    # 替换原有 self.掉落树.insert("", tk.END, values=(...))
                    tag = self.获取物品品质tag(物品ID)
                    self.掉落树.insert("", tk.END, values=(
                        物品ID,
                        名称,
                        str(项.get("权重", 0)),
                        str(项.get("掉落最小数量", 1)),
                        str(项.get("掉落最大数量", 1))
                    ), tags=(tag,))
        
        self.未保存标记 = False  # 加载新配置项后重置未保存标记
        self.更新状态栏()
    
    # ------------------------------
    # 原有方法：物品列表更新（修改核心：添加样式设置）
    # ------------------------------
    def 更新物品列表(self):
        """更新物品列表，显示ID+名称（新增：应用底色和品质文字色）"""
        self.物品列表框.delete(0, tk.END)  # 清空原有列表
        
        # 遍历物品数据，逐个插入列表项并设置样式
        for 物品索引, (物品ID, 物品数据) in enumerate(self.物品数据.items()):
            物品名称 = 物品数据.get('名称', '未命名')
            列表文本 = f"{物品ID} - {物品名称}"
            
            # 1. 插入列表项
            self.物品列表框.insert(tk.END, 列表文本)
            当前项索引 = 物品索引  # 列表项索引（与循环索引一致）
            
            # 2. 获取当前道具的文字颜色（根据品质）
            道具品质 = 物品数据.get("品质", 0.0)  # 从物品数据中读取品质值
            文字颜色 = self.获取道具文字颜色(道具品质)  # 匹配品质颜色映射
            
            # 3. 验证索引有效性（防止异常）
            if not isinstance(当前项索引, int) or 当前项索引 < 0:
                self.显示提示(f"物品ID:{物品ID}的列表索引无效，跳过样式设置", 成功=False, 显示弹窗=False)
                continue
            
            # 4. 应用样式（底色+文字色）
            try:
                if self.是否启用自定义底色.get():
                    # 启用自定义底色：应用默认底色+品质文字色
                    self.物品列表框.itemconfig(
                        当前项索引,
                        background=self.默认列表底色,  # 从item_color.json加载的默认底色
                        foreground=文字颜色             # 从品质颜色映射匹配的文字色
                    )
                else:
                    # 禁用自定义底色：仅应用文字色（使用系统默认底色）
                    self.物品列表框.itemconfig(
                        当前项索引,
                        foreground=文字颜色
                    )
            except tk.TclError as e:
                # 样式设置失败时兜底（防止程序崩溃）
                self.物品列表框.itemconfig(
                    当前项索引,
                    background="#ffffff",  # 兜底白底
                    foreground="black"     # 兜底黑字
                )
                self.显示提示(f"物品ID:{物品ID}样式设置失败：{str(e)}，使用默认样式", 成功=False, 显示弹窗=False)
    
    # ------------------------------
    # 新增：掉落树颜色样式初始化（核心优化）
    # ------------------------------
    def 初始化掉落树颜色样式(self):
        """为掉落树(Treeview)注册各品质的tag样式"""
        for 品质, 颜色 in self.品质颜色映射.items():
            tag = f"品质_{品质}"
            self.掉落树.tag_configure(tag, foreground=颜色, background=self.默认列表底色)
        self.掉落树.tag_configure('默认', foreground=self.默认列表文字色, background=self.默认列表底色)

    def 获取物品品质tag(self, 物品ID):
        """根据物品ID获取对应的tag名"""
        物品 = self.物品数据.get(物品ID, {})
        品质 = 物品.get('品质', None)
        try:
            品质 = float(品质)
        except (ValueError, TypeError):
            return '默认'
        if 品质 in self.品质颜色映射:
            return f"品质_{品质}"
        return '默认'

    # ------------------------------
    # 以下为原有方法，无修改（确保功能完整性）
    # ------------------------------
    def 处理物品选择(self, 事件):
        """处理物品选择事件"""
        pass  # 仅用于选择，添加由按钮触发
    
    def 添加选中物品到掉落列表(self):
        """将选中的物品添加到掉落列表"""
        if not self.当前掉落类型:
            messagebox.showinfo("提示", "请先新建或选择一个配置项")
            return
            
        选中项 = self.物品列表框.curselection()
        if not 选中项:
            messagebox.showinfo("提示", "请先选择一个物品")
            return
            
        选中文本 = self.物品列表框.get(选中项[0])
        匹配 = re.search(r'^(\d+)', 选中文本)
        if 匹配:
            物品ID = 匹配.group(1)
            
            # 根据当前掉落类型创建不同的掉落项
            if self.当前掉落类型 == "掉落":
                # 正常掉落项，默认数量为1-1
                tag = self.获取物品品质tag(物品ID)
                self.掉落树.insert("", tk.END, values=(
                    物品ID,
                    self.物品数据[物品ID].get('名称', '未命名'),
                    "0.3",   # 掉落几率
                    "1.0",   # 最小等级
                    "10.0",  # 最大等级
                    "1.0",   # 掉落最小数量
                    "1.0"    # 掉落最大数量
                ), tags=(tag,))
                self.更新当前配置数据()
                self.未保存标记 = True  # 标记未保存
                self.更新状态栏()
                
            elif self.当前掉落类型 == "宝物":
                # 宝物掉落项，默认数量为1-1
                tag = self.获取物品品质tag(物品ID)
                self.掉落树.insert("", tk.END, values=(
                    物品ID,
                    self.物品数据[物品ID].get('名称', '未命名'),
                    "10.0",  # 权重
                    "1.0",   # 掉落最小数量
                    "1.0"    # 掉落最大数量
                ), tags=(tag,))
                self.更新当前配置数据()
                self.未保存标记 = True  # 标记未保存
                self.更新状态栏()
    
    def 新建配置项(self):
        """新建配置项，可选择掉落类型和输入配置项名称"""
        # 询问用户是否保存当前更改
        if self.未保存标记:
            if messagebox.askyesno("提示", "是否保存当前配置项的更改？"):
                self.保存数据()
        
        # 创建对话框让用户输入配置项名称和选择类型
        配置窗口 = tk.Toplevel(self.主窗口)
        配置窗口.title("新建配置项")
        配置窗口.geometry("350x200")
        配置窗口.resizable(False, False)
        配置窗口.transient(self.主窗口)
        配置窗口.grab_set()
        
        # 居中显示
        配置窗口.update_idletasks()
        宽度 = 配置窗口.winfo_width()
        高度 = 配置窗口.winfo_height()
        x = (self.主窗口.winfo_width() // 2) - (宽度 // 2) + self.主窗口.winfo_x()
        y = (self.主窗口.winfo_height() // 2) - (高度 // 2) + self.主窗口.winfo_y()
        配置窗口.geometry('{}x{}+{}+{}'.format(宽度, 高度, x, y))
        
        # 配置项名称输入
        ttk.Label(配置窗口, text="配置项名称 (如: 全局 或 宝物_怪物ID):", font=("Arial", 10)).pack(pady=(15, 5), padx=10, anchor=tk.W)
        名称输入 = ttk.Entry(配置窗口, width=40)
        名称输入.pack(pady=(0, 15), padx=10)
        名称输入.insert(0, "全局")  # 默认名称
        
        # 类型选择
        ttk.Label(配置窗口, text="请选择掉落类型:", font=("Arial", 10)).pack(pady=(5, 5), padx=10, anchor=tk.W)
        类型选择 = ttk.Combobox(配置窗口, values=["掉落", "宝物"], width=37)
        类型选择.current(0)
        类型选择.pack(pady=(0, 15), padx=10)
        
        # 结果变量
        self.新建配置结果 = {
            "名称": "",
            "类型": "",
            "确认": False
        }
        
        def 确认选择():
            名称 = 名称输入.get().strip()
            if not 名称:
                messagebox.showwarning("输入错误", "配置项名称不能为空")
                return
                
            if 名称 in self.所有掉落数据:
                if not messagebox.askyesno("名称已存在", f"配置项 '{名称}' 已存在，是否覆盖？"):
                    return
            
            self.新建配置结果["名称"] = 名称
            self.新建配置结果["类型"] = 类型选择.get()
            self.新建配置结果["确认"] = True
            配置窗口.destroy()
        
        ttk.Button(配置窗口, text="确认", command=确认选择).pack(pady=10)
        
        self.主窗口.wait_window(配置窗口)
        
        if not self.新建配置结果["确认"]:
            return
            
        配置项名称 = self.新建配置结果["名称"]
        选择的类型 = self.新建配置结果["类型"]
        
        # 初始化数据
        self.当前配置键 = 配置项名称
        self.当前掉落类型 = 选择的类型
        self.掉落类型变量.set(f"当前配置: {配置项名称} (类型: {选择的类型})")
        
        if 选择的类型 == "掉落":
            # 初始化正常掉落数据
            self.当前掉落数据 = {
                "类别": "掉落",
                "掉落": []
            }
            # 设置列表列
            self.设置掉落列表列("掉落")
            # 隐藏权重相关控件
            for widget in self.掉落控制总框架.winfo_children():
                if isinstance(widget, ttk.Label) and widget["text"] == "权重的掉落数量:":
                    widget.pack_forget()
                if isinstance(widget, ttk.Entry) and widget["textvariable"] == self.权重掉落数量变量:
                    widget.pack_forget()
        
        else:
            # 初始化宝物掉落数据
            self.当前掉落数据 = {
                "类别": "宝物",
                "权重的掉落数量": 1.0,
                "宝物": []
            }
            # 设置列表列
            self.设置掉落列表列("宝物")
            # 显示权重相关控件
            for widget in self.掉落控制总框架.winfo_children():
                if isinstance(widget, ttk.Label) and widget["text"] == "权重的掉落数量:":
                    widget.pack(side=tk.LEFT, padx=5)
                if isinstance(widget, ttk.Entry) and widget["textvariable"] == self.权重掉落数量变量:
                    widget.pack(side=tk.LEFT, padx=5)
            
            # 设置默认值
            self.权重掉落数量变量.set("1.0")
        
        # 清空列表
        for 项 in self.掉落树.get_children():
            self.掉落树.delete(项)
        
        # 更新到所有掉落数据
        self.所有掉落数据[配置项名称] = self.当前掉落数据
        
        # 刷新配置项列表
        self.加载所有掉落数据()
        # 选中新创建的配置项
        for i, item in enumerate(self.配置项列表框.get(0, tk.END)):
            if item == 配置项名称:
                self.配置项列表框.selection_set(i)
                self.配置项列表框.see(i)
                break
        
        self.未保存标记 = True  # 新配置项标记为未保存
        self.更新状态栏()
    
    def 设置掉落列表列(self, 类型):
        """根据类型设置掉落列表的列"""
        # 清空现有列
        self.掉落树["columns"] = ()
        
        if 类型 == "掉落":
            # 正常掉落的列
            列 = ("物品ID", "名称", "掉落几率", "最小等级", "最大等级", "最小数量", "最大数量")
            self.掉落树["columns"] = 列
            
            # 设置列
            self.掉落树.heading("物品ID", text="物品ID")
            self.掉落树.heading("名称", text="名称")
            self.掉落树.heading("掉落几率", text="掉落几率")
            self.掉落树.heading("最小等级", text="最小等级")
            self.掉落树.heading("最大等级", text="最大等级")
            self.掉落树.heading("最小数量", text="掉落最小数量")
            self.掉落树.heading("最大数量", text="掉落最大数量")
            
            # 设置列宽
            self.掉落树.column("物品ID", width=80, anchor=tk.CENTER)
            self.掉落树.column("名称", width=120, anchor=tk.W)
            self.掉落树.column("掉落几率", width=80, anchor=tk.CENTER)
            self.掉落树.column("最小等级", width=80, anchor=tk.CENTER)
            self.掉落树.column("最大等级", width=80, anchor=tk.CENTER)
            self.掉落树.column("最小数量", width=80, anchor=tk.CENTER)
            self.掉落树.column("最大数量", width=80, anchor=tk.CENTER)
            
        else:
            # 宝物掉落的列
            列 = ("物品ID", "名称", "权重", "最小数量", "最大数量")
            self.掉落树["columns"] = 列
            
            # 设置列
            self.掉落树.heading("物品ID", text="物品ID")
            self.掉落树.heading("名称", text="名称")
            self.掉落树.heading("权重", text="权重")
            self.掉落树.heading("最小数量", text="掉落最小数量")
            self.掉落树.heading("最大数量", text="掉落最大数量")
            
            # 设置列宽
            self.掉落树.column("物品ID", width=80, anchor=tk.CENTER)
            self.掉落树.column("名称", width=150, anchor=tk.W)
            self.掉落树.column("权重", width=80, anchor=tk.CENTER)
            self.掉落树.column("最小数量", width=80, anchor=tk.CENTER)
            self.掉落树.column("最大数量", width=80, anchor=tk.CENTER)
        
        # 绑定双击编辑事件
        self.掉落树.bind("<Double-1>", self.处理掉落项双击)
    
    def 保存数据(self):
        """保存所有配置项到drop_data.json文件"""
        if not self.所有掉落数据:
            if messagebox.askyesno("提示", "当前没有任何配置项，确定要保存空文件吗？"):
                pass
            else:
                return
        
        # 先更新当前配置项的数据
        if self.当前配置键:
            self.更新当前配置数据()
        
        try:
            with open(self.掉落数据文件, 'w', encoding='utf-8') as f:
                json.dump(self.所有掉落数据, f, ensure_ascii=False, indent=2)
            
            self.未保存标记 = False  # 保存成功后重置未保存标记
            self.更新状态栏()
            
            # 保存后刷新配置项列表
            self.加载所有掉落数据()
            self.显示提示(f"已成功保存到 {os.path.basename(self.掉落数据文件)}",显示弹窗=False)
            
        except Exception as e:
            messagebox.showerror("保存失败", f"保存文件时出错: {str(e)}")
    
    
    
    def 更新当前配置数据(self):
        """更新当前配置项的数据到所有掉落数据中"""
        if not self.当前配置键 or not self.当前掉落类型:
            return
        
        if self.当前掉落类型 == "掉落":
            # 更新正常掉落数据
            self.当前掉落数据["掉落"] = []
            for 项 in self.掉落树.get_children():
                数值 = self.掉落树.item(项, "values")
                if len(数值) >= 7:
                    try:
                        self.当前掉落数据["掉落"].append({
                            "物品ID": 数值[0],
                            "掉落几率": float(数值[2]),
                            "最小等级": float(数值[3]),
                            "最大等级": float(数值[4]),
                            "掉落最小数量": float(数值[5]),
                            "掉落最大数量": float(数值[6])
                        })
                    except ValueError as e:
                        messagebox.showwarning("数据格式警告", f"数值转换错误: {str(e)}\n该项将被忽略")
        
        else:
            # 更新宝物掉落数据
            # 先更新权重的掉落数量
            try:
                self.当前掉落数据["权重的掉落数量"] = float(self.权重掉落数量变量.get())
            except ValueError:
                messagebox.showwarning("数据格式警告", "权重的掉落数量必须是数字")
                self.当前掉落数据["权重的掉落数量"] = 1.0
            
            # 更新宝物列表
            self.当前掉落数据["宝物"] = []
            for 项 in self.掉落树.get_children():
                数值 = self.掉落树.item(项, "values")
                if len(数值) >= 5:
                    try:
                        self.当前掉落数据["宝物"].append({
                            "物品ID": 数值[0],
                            "权重": float(数值[2]),
                            "掉落最小数量": float(数值[3]),
                            "掉落最大数量": float(数值[4])
                        })
                    except ValueError as e:
                        messagebox.showwarning("数据格式警告", f"数值转换错误: {str(e)}\n该项将被忽略")
        
        # 更新到所有掉落数据中
        self.所有掉落数据[self.当前配置键] = self.当前掉落数据
    
    def 处理掉落项双击(self, 事件):
        """双击编辑掉落项"""
        # 关闭任何已存在的编辑框
        self.关闭活跃编辑框()
        
        区域 = self.掉落树.identify_region(事件.x, 事件.y)
        if 区域 != "cell":
            return
            
        # 解析列索引
        列字符串 = self.掉落树.identify_column(事件.x)
        列 = int(列字符串.replace('#', '')) - 1  # 转换为0-based索引
        
        # 物品ID列和名称列不允许编辑
        if 列 == 0 or 列 == 1:
            return
            
        项 = self.掉落树.identify_row(事件.y)
        
        # 获取单元格位置和当前值
        x, y, 宽度, 高度 = self.掉落树.bbox(项, 列)
        值 = self.掉落树.item(项, "values")[列]
        
        # 创建编辑框
        输入框 = ttk.Entry(self.掉落树)
        输入框.place(x=x, y=y, width=宽度, height=高度)
        输入框.insert(0, 值)
        输入框.focus()
        
        # 保存当前编辑框引用
        self.活跃编辑框 = 输入框
        
        # 保存编辑结果
        def 保存编辑(事件=None):
            # 检查项目是否仍然存在
            if 项 not in self.掉落树.get_children():
                输入框.destroy()
                self.活跃编辑框 = None
                return
                
            新值 = 输入框.get()
            数值列表 = list(self.掉落树.item(项, "values"))
            数值列表[列] = 新值
            self.掉落树.item(项, values=数值列表)
            输入框.destroy()
            self.活跃编辑框 = None
            self.更新当前配置数据()
            self.未保存标记 = True  # 标记未保存
            self.更新状态栏()
        
        输入框.bind("<FocusOut>", 保存编辑)
        输入框.bind("<Return>", 保存编辑)
        输入框.bind("<Escape>", lambda e: [输入框.destroy(), setattr(self, '活跃编辑框', None)])
    
    def 关闭活跃编辑框(self):
        """关闭当前活跃的编辑框"""
        if self.活跃编辑框:
            try:
                self.活跃编辑框.destroy()
            except:
                pass
            self.活跃编辑框 = None
    
    def 删除选中掉落项(self):
        """删除选中的掉落项"""
        # 关闭任何活跃的编辑框
        self.关闭活跃编辑框()
        
        # 获取所有选中的项
        选中项 = self.掉落树.selection()
        if not 选中项:
            messagebox.showinfo("提示", "请先选择要删除的项")
            return
            
        # 逐个删除选中项
        数量 = len(选中项)
        for 项 in 选中项:
            self.掉落树.delete(项)
            
        self.更新当前配置数据()
        self.未保存标记 = True  # 标记未保存
        self.更新状态栏()
    
    def 清空掉落列表(self):
        """清空掉落列表"""
        if not self.掉落树.get_children():
            messagebox.showinfo("提示", "列表已经为空")
            return
            
        if messagebox.askyesno("确认", "确定要清空当前配置项的所有掉落项吗？"):
            # 清空列表
            for 项 in self.掉落树.get_children():
                self.掉落树.delete(项)
            
            self.更新当前配置数据()
            self.未保存标记 = True  # 标记未保存
            self.更新状态栏()
    
    def 处理关闭(self):
        """窗口关闭时保存数据"""
        if self.未保存标记:
            if messagebox.askyesno("提示", "是否保存当前更改？"):
                self.保存数据()
        self.主窗口.destroy()

    def 删除选中配置项(self):
        选中项 = self.配置项列表框.curselection()
        if not 选中项:
            messagebox.showinfo("提示", "请先选择要删除的配置项")
            return
        
        配置项键 = self.配置项列表框.get(选中项[0])
        if 配置项键 == "无配置项（可新建）":
            return
        
        if not messagebox.askyesno("确认删除", f"确定要删除配置项 '{配置项键}' 吗？\n此操作不可恢复！"):
            return
        
        try:
            if 配置项键 == self.当前配置键:
                # 清空当前编辑状态
                self.当前配置键 = ""
                self.当前掉落数据 = {}
                self.当前掉落类型 = ""
                self.掉落类型变量.set("未选择配置项")
                for 项 in self.掉落树.get_children():
                    self.掉落树.delete(项)
                # 隐藏权重控件
                for widget in self.掉落控制总框架.winfo_children():
                    if isinstance(widget, ttk.Label) and widget["text"] == "权重的掉落数量:":
                        widget.pack_forget()
                    if isinstance(widget, ttk.Entry) and widget["textvariable"] == self.权重掉落数量变量:
                        widget.pack_forget()
            
            # 删除内存数据
            if 配置项键 in self.所有掉落数据:
                del self.所有掉落数据[配置项键]
            
            # 【关键修复】删除后立即保存，确保文件同步
            self.保存数据()  
            
            self.显示提示(f"配置项 '{配置项键}' 已成功删除")
            self.加载所有掉落数据()
            self.更新状态栏()
            
        except Exception as e:
            messagebox.showerror("删除失败", f"删除配置项时出错: {str(e)}")


if __name__ == "__main__":
    # 根据是否有dnd支持选择不同的根窗口类型
    if 支持拖放:
        根窗口 = Tk()  # 使用tkinterdnd2的Tk
    else:
        根窗口 = tk.Tk()  # 使用标准Tk
    
    # 新增：设置中文字体（防止中文乱码）
    根窗口.option_add("*Font", "SimHei 10")
        
    应用 = 掉落编辑器(根窗口)
    根窗口.mainloop()