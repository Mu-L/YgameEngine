import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import json
import os
import sys
from pathlib import Path

class 地图编辑器:
    def __init__(self, 主窗口):
        self.主窗口 = 主窗口
        self.主窗口.title("地图编辑器")
        self.主窗口.geometry("1000x700")  # 调整窗口高度
        self.主窗口.minsize(800, 600)
        
        # 地图配置信息 - 可自定义设置行列数
        self.地图配置 = {
            "行数": 5,    # 第一排为5个格子
            "列数": 6,    # 共6列
            "格子大小": 80  # 每个格子的大小（像素）
        }
        
        # 初始化状态变量
        self.状态变量 = tk.StringVar(value="就绪 (按Ctrl+S保存)")
        
        # 先初始化关键变量，避免属性错误
        self.选中格子ID变量 = tk.StringVar(value="")
        self.信息树 = None
        self.当前选中格子 = None
        self.地图属性树 = None  # 地图属性树
        
        # 计算路径
        self.计算项目路径()
        
        # 数据存储
        self.地图数据 = {}  # 所有地图数据，格式: {地图名称: {"格子数据": {}, "属性": {}}}
        self.当前地图名称 = None  # 当前编辑的地图名称
        self.NPC列表 = {}  # NPC数据
        
        # 配置文件路径
        self.NPC数据文件 = os.path.join(self.系统文件夹, "npcsystem.json")
        self.地图数据文件 = os.path.join(self.系统文件夹, "map_data.json")
        self.配置文件 = os.path.join(self.系统文件夹, "map_config.json")
        
        # 确保目录存在
        self.确保目录存在(self.系统文件夹)
        
        # 先创建UI组件
        self.创建界面组件()
        
        # 加载配置和数据
        self.加载配置()
        self.加载NPC数据()
        self.加载地图数据()
        
        # 绑定快捷键
        self.设置快捷键()
    
    def 计算项目路径(self):
        """计算项目根目录和系统文件夹路径，回退3级目录"""
        try:
            # 获取当前执行文件的路径
            if getattr(sys, 'frozen', False):
                # 当程序被打包为exe时
                当前路径 = os.path.dirname(sys.executable)
            else:
                # 开发环境中
                当前路径 = os.path.dirname(os.path.abspath(__file__))
            
            # 回退3级目录
            上级目录1 = os.path.dirname(当前路径)
            上级目录2 = os.path.dirname(上级目录1)
            项目根目录 = os.path.dirname(上级目录2)
            
            # 系统文件夹路径 - 项目根目录下的系统文件夹
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
    
    def 加载配置(self):
        """加载地图配置"""
        if os.path.exists(self.配置文件):
            try:
                with open(self.配置文件, 'r', encoding='utf-8') as f:
                    配置 = json.load(f)
                    # 更新配置，保留未在配置文件中定义的默认值
                    self.地图配置.update(配置)
                self.状态变量.set(f"已加载配置: {self.地图配置['行数']}x{self.地图配置['列数']} 格子")
            except Exception as e:
                messagebox.showerror("配置加载错误", f"无法加载配置文件：{str(e)}")
        else:
            # 保存默认配置
            self.保存配置()
    
    def 保存配置(self):
        """保存地图配置"""
        try:
            with open(self.配置文件, 'w', encoding='utf-8') as f:
                json.dump(self.地图配置, f, ensure_ascii=False, indent=2)
            self.状态变量.set(f"配置已保存: {self.地图配置['行数']}x{self.地图配置['列数']} 格子")
        except Exception as e:
            messagebox.showerror("配置保存错误", f"无法保存配置文件：{str(e)}")
    
    def 设置快捷键(self):
        """设置快捷键"""
        # 绑定Ctrl+S保存
        self.主窗口.bind("<Control-s>", self.保存当前地图快捷键)
        self.主窗口.bind("<Control-S>", self.保存当前地图快捷键)
        
        # 为信息树绑定Ctrl+S快捷键
        self.信息树.bind("<Control-s>", self.保存当前地图快捷键)
        self.信息树.bind("<Control-S>", self.保存当前地图快捷键)
        self.地图属性树.bind("<Control-s>", self.保存当前地图快捷键)
        self.地图属性树.bind("<Control-S>", self.保存当前地图快捷键)
    
    def 保存当前地图快捷键(self, 事件=None):
        """快捷键触发的保存功能，先应用信息修改再保存地图"""
        # 应用格子信息修改
        if self.当前选中格子 and self.信息树 and self.信息树.get_children():
            self.应用信息修改()
            
        # 应用地图属性修改
        if self.当前地图名称 and self.地图属性树 and self.地图属性树.get_children():
            self.应用地图属性修改()
            
        if self.当前地图名称:
            self.保存当前地图()
        return "break"
    
    def 确保目录存在(self, 目录):
        """确保目录存在，如果不存在则创建"""
        try:
            Path(目录).mkdir(parents=True, exist_ok=True)
            self.状态变量.set(f"目录已准备就绪: {目录}")
            return True
        except Exception as e:
            messagebox.showerror("目录错误", f"无法创建目录 {目录}：{str(e)}")
            return False
    
    def 加载NPC数据(self):
        """加载NPC数据"""
        if os.path.exists(self.NPC数据文件):
            try:
                with open(self.NPC数据文件, 'r', encoding='utf-8') as f:
                    self.NPC列表 = json.load(f)
                self.状态变量.set(f"已加载NPC数据: {len(self.NPC列表)}个NPC")
            except Exception as e:
                messagebox.showerror("加载错误", f"无法加载{self.NPC数据文件}：{str(e)}")
                self.NPC列表 = {}
        else:
            # 如果NPC数据文件不存在，创建一个示例文件
            self.NPC列表 = {
                "1": {"名称": "村民A", "描述": "普通村民"},
                "2": {"名称": "商人", "描述": "出售物品的商人"},
                "3": {"名称": "守卫", "描述": "保护村庄的守卫"}
            }
            try:
                with open(self.NPC数据文件, 'w', encoding='utf-8') as f:
                    json.dump(self.NPC列表, f, ensure_ascii=False, indent=2)
                self.状态变量.set(f"已创建示例NPC数据: {self.NPC数据文件}")
            except Exception as e:
                messagebox.showerror("创建NPC文件错误", f"无法创建NPC数据文件：{str(e)}")
                self.NPC列表 = {}
    
    def 加载地图数据(self):
        """加载地图数据"""
        if os.path.exists(self.地图数据文件):
            try:
                with open(self.地图数据文件, 'r', encoding='utf-8') as f:
                    原始数据 = json.load(f)
                
                # 处理旧版本数据（没有属性字段的）
                self.地图数据 = {}
                for 地图名称, 地图内容 in 原始数据.items():
                    # 如果是旧格式（直接存储格子数据），转换为新格式
                    if isinstance(地图内容, dict) and "格子数据" not in 地图内容:
                        self.地图数据[地图名称] = {
                            "格子数据": 地图内容,
                            "属性": {}  # 新增属性字段
                        }
                    else:
                        self.地图数据[地图名称] = 地图内容
                
                self.状态变量.set(f"已加载地图数据: {len(self.地图数据)}个地图")
                self.更新地图列表()
            except Exception as e:
                messagebox.showerror("加载错误", f"无法加载{self.地图数据文件}：{str(e)}")
                self.地图数据 = {}
        else:
            self.状态变量.set(f"未找到地图数据文件，将创建新文件")
            self.地图数据 = {}
            self.更新地图列表()
    
    def 保存所有地图(self):
        """保存所有地图数据到JSON文件"""
        try:
            with open(self.地图数据文件, 'w', encoding='utf-8') as f:
                json.dump(self.地图数据, f, ensure_ascii=False, indent=2)
            self.状态变量.set(f"所有地图已保存到 {self.地图数据文件}")
            return True
        except Exception as e:
            messagebox.showerror("保存错误", f"无法保存{self.地图数据文件}：{str(e)}")
            return False
    
    def 保存当前地图(self):
        """保存当前编辑的地图数据，只保存有内容的格子"""
        if not self.当前地图名称:
            return False
            
        # 计算总格数
        总格数 = self.地图配置["行数"] * self.地图配置["列数"]
        
        # 收集格子数据，只保存有内容的格子
        格子数据 = {}
        for 格子ID in range(1, 总格数 + 1):  # 1-总格数的格子ID
            格子框架 = self.格子字典.get(str(格子ID))
            if 格子框架:
                NPCID = 格子框架.npc_id
                信息 = 格子框架.info
                
                # 只保存有NPC或有信息的格子
                if NPCID or 信息:
                    格子数据[str(格子ID)] = {
                        "NPCID": NPCID,
                        "信息": 信息
                    }
        
        # 获取地图属性
        地图属性 = {}
        if self.地图属性树:
            for 项 in self.地图属性树.get_children():
                数值 = self.地图属性树.item(项, "values")
                if len(数值) >= 2 and 数值[0]:  # 确保证键名不为空
                    地图属性[数值[0]] = 数值[1]
        
        # 更新地图数据
        self.地图数据[self.当前地图名称] = {
            "格子数据": 格子数据,
            "属性": 地图属性
        }
        
        # 保存到文件
        return self.保存所有地图()
    
    def 创建界面组件(self):
        """创建UI组件"""
        # 主框架
        self.主框架 = ttk.Frame(self.主窗口, padding="10")
        self.主框架.pack(fill=tk.BOTH, expand=True)
        
        # 左侧地图列表
        左侧框架 = ttk.LabelFrame(self.主框架, text="地图列表", padding="5")
        左侧框架.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=(0, 10))
        
        # 地图列表
        self.地图列表框 = tk.Listbox(左侧框架, width=30, height=30)
        self.地图列表框.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        self.地图列表框.bind('<<ListboxSelect>>', self.处理地图选择)
        
        # 滚动条
        滚动条 = ttk.Scrollbar(左侧框架, orient=tk.VERTICAL, command=self.地图列表框.yview)
        滚动条.pack(side=tk.RIGHT, fill=tk.Y)
        self.地图列表框.config(yscrollcommand=滚动条.set)
        
        # 地图操作按钮
        按钮框架 = ttk.Frame(左侧框架, padding="5")
        按钮框架.pack(fill=tk.X)
        
        ttk.Button(按钮框架, text="新建地图", command=self.新建地图).pack(fill=tk.X, pady=2)
        ttk.Button(按钮框架, text="删除地图", command=self.删除地图).pack(fill=tk.X, pady=2)
        ttk.Button(按钮框架, text="重命名地图", command=self.重命名地图).pack(fill=tk.X, pady=2)
        ttk.Button(按钮框架, text="保存当前地图 (Ctrl+S)", command=self.保存当前地图快捷键).pack(fill=tk.X, pady=2)
        ttk.Button(按钮框架, text="保存所有地图", command=self.保存所有地图).pack(fill=tk.X, pady=2)
        ttk.Button(按钮框架, text="刷新NPC列表", command=self.加载NPC数据).pack(fill=tk.X, pady=2)
        ttk.Button(按钮框架, text="地图配置", command=self.打开配置对话框).pack(fill=tk.X, pady=2)
        
        # 右侧编辑区域
        右侧框架 = ttk.Frame(self.主框架)
        右侧框架.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # 地图标题
        self.地图标题变量 = tk.StringVar(value="未选择地图")
        ttk.Label(右侧框架, textvariable=self.地图标题变量, font=("SimHei", 14, "bold")).pack(pady=10)
        
        # 创建标签页控件，用于分组显示地图编辑区和属性编辑区
        标签页控件 = ttk.Notebook(右侧框架)
        标签页控件.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # 地图编辑区标签页
        地图编辑页 = ttk.Frame(标签页控件)
        标签页控件.add(地图编辑页, text="地图编辑")
        
        # 地图属性编辑区标签页
        属性编辑页 = ttk.Frame(标签页控件)
        标签页控件.add(属性编辑页, text="地图属性")
        
        # ============= 地图编辑区内容 =============
        网格描述 = f"{self.地图配置['行数']}×{self.地图配置['列数']}"
        self.地图框架 = ttk.LabelFrame(地图编辑页, text=f"地图编辑区 ({网格描述})", padding="10")
        self.地图框架.pack(fill=tk.BOTH, expand=True)
        
        # 创建格子容器
        self.格子容器 = ttk.Frame(self.地图框架)
        self.格子容器.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 初始化格子字典
        self.格子字典 = {}
        
        # 创建网格 - 行数x列数
        self.创建地图格子()
        
        # 当前选中格子信息编辑区
        self.信息编辑框架 = ttk.LabelFrame(地图编辑页, text="格子信息编辑", padding="10")
        self.信息编辑框架.pack(fill=tk.X, pady=10)
        
        # 选中格子ID显示
        ttk.Label(self.信息编辑框架, text="选中格子ID:").grid(row=0, column=0, sticky=tk.W, pady=5, padx=5)
        ttk.Label(self.信息编辑框架, textvariable=self.选中格子ID变量).grid(row=0, column=1, sticky=tk.W, pady=5)
        
        # 信息键值对编辑
        ttk.Label(self.信息编辑框架, text="信息键值对:").grid(row=1, column=0, sticky=tk.NW, pady=5, padx=5)
        
        # 信息编辑区域
        信息编辑容器 = ttk.Frame(self.信息编辑框架)
        信息编辑容器.grid(row=1, column=1, columnspan=2, sticky=tk.NSEW, pady=5)
        
        # 信息列表
        self.信息树 = ttk.Treeview(信息编辑容器, columns=("key", "value"), show="headings", height=5)
        self.信息树.heading("key", text="键")
        self.信息树.heading("value", text="值")
        self.信息树.column("key", width=150, anchor=tk.W)
        self.信息树.column("value", width=300, anchor=tk.W)
        
        # 信息列表滚动条
        信息滚动条 = ttk.Scrollbar(信息编辑容器, orient=tk.VERTICAL, command=self.信息树.yview)
        self.信息树.configure(yscrollcommand=信息滚动条.set)
        
        self.信息树.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        信息滚动条.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 信息操作按钮
        信息按钮框架 = ttk.Frame(self.信息编辑框架)
        信息按钮框架.grid(row=2, column=1, columnspan=2, sticky=tk.W, pady=5)
        
        ttk.Button(信息按钮框架, text="添加信息项", command=self.添加信息项).pack(side=tk.LEFT, padx=2)
        ttk.Button(信息按钮框架, text="删除选中项", command=self.删除选中信息项).pack(side=tk.LEFT, padx=2)
        ttk.Button(信息按钮框架, text="应用修改", command=self.应用信息修改).pack(side=tk.LEFT, padx=2)
        
        # 双击编辑信息
        self.信息树.bind("<Double-1>", self.处理信息双击)
        
        # ============= 地图属性编辑区内容 =============
        self.地图属性框架 = ttk.LabelFrame(属性编辑页, text="地图属性编辑", padding="10")
        self.地图属性框架.pack(fill=tk.BOTH, expand=True)
        
        # 地图属性键值对编辑
        ttk.Label(self.地图属性框架, text="地图属性键值对:").grid(row=0, column=0, sticky=tk.NW, pady=5, padx=5)
        
        # 地图属性编辑区域
        地图属性编辑容器 = ttk.Frame(self.地图属性框架)
        地图属性编辑容器.grid(row=0, column=1, columnspan=2, sticky=tk.NSEW, pady=5)
        
        # 地图属性列表
        self.地图属性树 = ttk.Treeview(地图属性编辑容器, columns=("key", "value"), show="headings", height=10)
        self.地图属性树.heading("key", text="键")
        self.地图属性树.heading("value", text="值")
        self.地图属性树.column("key", width=150, anchor=tk.W)
        self.地图属性树.column("value", width=300, anchor=tk.W)
        
        # 地图属性列表滚动条
        地图属性滚动条 = ttk.Scrollbar(地图属性编辑容器, orient=tk.VERTICAL, command=self.地图属性树.yview)
        self.地图属性树.configure(yscrollcommand=地图属性滚动条.set)
        
        self.地图属性树.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        地图属性滚动条.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 地图属性操作按钮
        地图属性按钮框架 = ttk.Frame(self.地图属性框架)
        地图属性按钮框架.grid(row=1, column=1, columnspan=2, sticky=tk.W, pady=5)
        
        ttk.Button(地图属性按钮框架, text="添加属性项", command=self.添加地图属性项).pack(side=tk.LEFT, padx=2)
        ttk.Button(地图属性按钮框架, text="删除选中项", command=self.删除选中地图属性项).pack(side=tk.LEFT, padx=2)
        ttk.Button(地图属性按钮框架, text="应用地图属性修改", command=self.应用地图属性修改).pack(side=tk.LEFT, padx=2)
        
        # 双击编辑地图属性
        self.地图属性树.bind("<Double-1>", self.处理地图属性双击)
        
        # 状态栏
        状态栏 = ttk.Label(self.主窗口, textvariable=self.状态变量, relief=tk.SUNKEN, anchor=tk.W)
        状态栏.pack(side=tk.BOTTOM, fill=tk.X)
        
        # 窗口关闭事件
        self.主窗口.protocol("WM_DELETE_WINDOW", self.处理关闭)
    
    def 创建地图格子(self):
        """创建地图格子"""
        # 清除现有格子前先清除选中状态
        self.当前选中格子 = None
        # 确保信息编辑区组件已初始化再调用清空方法
        if self.信息树 is not None:
            self.清空信息编辑区()
        
        # 清除现有格子
        for 格子 in self.格子容器.winfo_children():
            # 先解绑事件再销毁，防止事件触发
            格子.unbind("<Button-1>")
            格子.unbind("<Button-3>")  # 解绑右键事件
            if hasattr(格子, 'ID标签'):
                格子.ID标签.unbind("<Button-1>")
                格子.ID标签.unbind("<Button-3>")
            if hasattr(格子, 'NPC标签'):
                格子.NPC标签.unbind("<Button-1>")
                格子.NPC标签.unbind("<Button-3>")
            格子.destroy()
        self.格子字典.clear()
        
        # 创建新格子 - 行数x列数
        行数 = self.地图配置["行数"]
        列数 = self.地图配置["列数"]
        
        for 行 in range(行数):
            for 列 in range(列数):
                格子ID = 行 * 列数 + 列 + 1  # 计算格子ID (1-总格数)
                格子框架 = 格子组件(self.格子容器, 格子ID, self)
                格子框架.grid(row=行, column=列, padx=2, pady=2)
                self.格子字典[str(格子ID)] = 格子框架
        
        # 更新地图框架标题
        网格描述 = f"{行数}×{列数}"
        self.地图框架.config(text=f"地图编辑区 ({网格描述})")
    
    def 打开配置对话框(self):
        """打开地图配置对话框"""
        # 保存当前地图
        if self.当前地图名称:
            self.保存当前地图快捷键()
        
        # 创建对话框
        对话框 = tk.Toplevel(self.主窗口)
        对话框.title("地图配置")
        对话框.geometry("300x200")
        对话框.transient(self.主窗口)
        对话框.grab_set()
        
        # 居中显示
        对话框.update_idletasks()
        宽度 = 对话框.winfo_width()
        高度 = 对话框.winfo_height()
        x = (self.主窗口.winfo_width() // 2) - (宽度 // 2) + self.主窗口.winfo_x()
        y = (self.主窗口.winfo_height() // 2) - (高度 // 2) + self.主窗口.winfo_y()
        对话框.geometry('{}x{}+{}+{}'.format(宽度, 高度, x, y))
        
        # 配置项
        ttk.Label(对话框, text="行数:").grid(row=0, column=0, sticky=tk.W, padx=20, pady=(20, 5))
        行数变量 = tk.StringVar(value=str(self.地图配置["行数"]))
        ttk.Entry(对话框, textvariable=行数变量, width=10).grid(row=0, column=1, sticky=tk.W, pady=(20, 5))
        
        ttk.Label(对话框, text="列数:").grid(row=1, column=0, sticky=tk.W, padx=20, pady=5)
        列数变量 = tk.StringVar(value=str(self.地图配置["列数"]))
        ttk.Entry(对话框, textvariable=列数变量, width=10).grid(row=1, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(对话框, text="格子大小(像素):").grid(row=2, column=0, sticky=tk.W, padx=20, pady=5)
        格子大小变量 = tk.StringVar(value=str(self.地图配置["格子大小"]))
        ttk.Entry(对话框, textvariable=格子大小变量, width=10).grid(row=2, column=1, sticky=tk.W, pady=5)
        
        # 提示信息
        ttk.Label(对话框, text="注意: 修改会影响所有地图的显示", 
                 foreground="red", font=("SimHei", 8)).grid(row=3, column=0, columnspan=2, pady=10)
        
        # 按钮
        def 应用配置():
            try:
                新行数 = int(行数变量.get())
                新列数 = int(列数变量.get())
                新格子大小 = int(格子大小变量.get())
                
                if 新行数 < 1 or 新列数 < 1 or 新格子大小 < 30:
                    messagebox.showerror("输入错误", "请输入有效的数值（行数和列数至少为1，格子大小至少为30）")
                    return
                
                # 更新配置
                self.地图配置["行数"] = 新行数
                self.地图配置["列数"] = 新列数
                self.地图配置["格子大小"] = 新格子大小
                
                # 保存配置
                self.保存配置()
                
                # 重新创建格子
                self.创建地图格子()
                
                # 如果有当前地图，重新加载
                if self.当前地图名称:
                    self.加载地图到界面(self.当前地图名称)
                
                对话框.destroy()
                messagebox.showinfo("配置更新", "地图配置已更新")
            except ValueError:
                messagebox.showerror("输入错误", "请输入有效的整数")
        
        按钮框架 = ttk.Frame(对话框)
        按钮框架.grid(row=4, column=0, columnspan=2, pady=10)
        
        ttk.Button(按钮框架, text="取消", command=对话框.destroy).pack(side=tk.LEFT, padx=10)
        ttk.Button(按钮框架, text="应用", command=应用配置).pack(side=tk.LEFT, padx=10)
    
    def 处理关闭(self):
        """窗口关闭时保存数据"""
        if self.当前地图名称:
            self.保存当前地图快捷键()
        self.主窗口.destroy()
    
    def 更新地图列表(self):
        """更新地图列表"""
        self.地图列表框.delete(0, tk.END)
        for 地图名称 in self.地图数据.keys():
            self.地图列表框.insert(tk.END, 地图名称)
    
    def 新建地图(self):
        """新建地图"""
        # 先保存当前地图
        if self.当前地图名称:
            self.保存当前地图快捷键()
            
        地图名称 = simpledialog.askstring("新建地图", "请输入地图名称:")
        if 地图名称 and 地图名称 not in self.地图数据:
            # 新地图默认不包含任何格子数据和属性
            self.地图数据[地图名称] = {
                "格子数据": {},
                "属性": {}
            }
            self.更新地图列表()
            self.保存所有地图()
            
            # 选择新创建的地图
            for i, 名称 in enumerate(self.地图数据.keys()):
                if 名称 == 地图名称:
                    self.地图列表框.selection_set(i)
                    self.地图列表框.see(i)
                    self.处理地图选择(None)
                    break
    
    def 删除地图(self):
        """删除当前选中的地图"""
        选中索引 = self.地图列表框.curselection()
        if not 选中索引:
            messagebox.showinfo("提示", "请先选择一个地图")
            return
            
        地图名称 = self.地图列表框.get(选中索引[0])
        
        if messagebox.askyesno("确认删除", f"确定要删除地图 '{地图名称}' 吗？"):
            if 地图名称 in self.地图数据:
                del self.地图数据[地图名称]
                
                # 如果删除的是当前地图，清空编辑区
                if 地图名称 == self.当前地图名称:
                    self.当前地图名称 = None
                    self.地图标题变量.set("未选择地图")
                    self.清空所有格子()
                    self.清空信息编辑区()
                    self.清空地图属性编辑区()
                
                self.更新地图列表()
                self.保存所有地图()
    
    def 重命名地图(self):
        """重命名当前选中的地图"""
        # 先保存当前地图
        if self.当前地图名称:
            self.保存当前地图快捷键()
            
        选中索引 = self.地图列表框.curselection()
        if not 选中索引:
            messagebox.showinfo("提示", "请先选择一个地图")
            return
            
        旧名称 = self.地图列表框.get(选中索引[0])
        新名称 = simpledialog.askstring("重命名地图", "请输入新地图名称:", initialvalue=旧名称)
        
        if 新名称 and 新名称 != 旧名称 and 新名称 not in self.地图数据:
            # 复制数据
            self.地图数据[新名称] = self.地图数据[旧名称]
            # 删除旧数据
            del self.地图数据[旧名称]
            
            # 如果重命名的是当前地图，更新当前名称
            if 旧名称 == self.当前地图名称:
                self.当前地图名称 = 新名称
                self.地图标题变量.set(f"当前编辑: {新名称}")
            
            self.更新地图列表()
            self.保存所有地图()
    
    def 处理地图选择(self, 事件):
        """处理地图选择事件"""
        # 先保存当前地图
        if self.当前地图名称:
            self.保存当前地图快捷键()
        
        选中项 = self.地图列表框.curselection()
        if not 选中项:
            return
            
        # 加载选中的地图
        地图名称 = self.地图列表框.get(选中项[0])
        if 地图名称 in self.地图数据:
            self.当前地图名称 = 地图名称
            self.地图标题变量.set(f"当前编辑: {地图名称}")
            self.加载地图到界面(地图名称)
            self.加载地图属性到编辑区(地图名称)
            self.状态变量.set(f"已加载地图: {地图名称}")
            # 清空信息编辑区
            self.清空信息编辑区()
    
    def 加载地图到界面(self, 地图名称):
        """将地图数据加载到界面"""
        if 地图名称 not in self.地图数据:
            return
            
        地图内容 = self.地图数据[地图名称]
        格子数据 = 地图内容.get("格子数据", {})
        
        # 清空所有格子
        self.清空所有格子()
        
        # 加载数据到格子
        for 格子ID, 格子数据 in 格子数据.items():
            格子框架 = self.格子字典.get(格子ID)
            if 格子框架:
                格子框架.set_npc_id(格子数据.get("NPCID", ""))
                格子框架.set_info(格子数据.get("信息", {}))
    
    def 加载地图属性到编辑区(self, 地图名称):
        """加载地图属性到编辑区"""
        # 清空现有项
        for 项 in self.地图属性树.get_children():
            self.地图属性树.delete(项)
        
        if 地图名称 not in self.地图数据:
            return
            
        地图内容 = self.地图数据[地图名称]
        地图属性 = 地图内容.get("属性", {})
        
        # 添加属性项
        for 键, 值 in 地图属性.items():
            self.地图属性树.insert("", tk.END, values=(键, 值))
    
    def 清空所有格子(self):
        """清空所有格子的数据"""
        for 格子框架 in self.格子字典.values():
            格子框架.set_npc_id("")
            格子框架.set_info({})
    
    def 处理格子点击(self, 格子组件, 显示NPC对话框=True):
        """处理格子点击事件，控制是否显示NPC对话框"""
        if not self.当前地图名称:
            messagebox.showinfo("提示", "请先选择或创建一个地图")
            return
            
        # 先保存当前编辑的信息
        if self.当前选中格子 and self.当前选中格子 != 格子组件:
            if self.信息树 and self.信息树.get_children():
                self.应用信息修改()
            
        # 更新选中状态 - 添加组件存在性检查
        if self.当前选中格子 and self.当前选中格子.winfo_exists():
            self.当前选中格子.set_selected(False)
        
        格子组件.set_selected(True)
        self.当前选中格子 = 格子组件
        
        # 更新信息编辑区
        self.选中格子ID变量.set(str(格子组件.格子ID))
        self.加载格子信息到编辑区(格子组件)
        
        # 根据参数决定是否显示NPC选择对话框
        if 显示NPC对话框:
            self.显示NPC选择对话框(格子组件)
    
    def 加载格子信息到编辑区(self, 格子组件):
        """加载格子信息到编辑区"""
        # 清空现有项
        for 项 in self.信息树.get_children():
            self.信息树.delete(项)
        
        # 添加信息项
        信息 = 格子组件.get_info()
        for 键, 值 in 信息.items():
            self.信息树.insert("", tk.END, values=(键, 值))
    
    def 清空信息编辑区(self):
        """清空信息编辑区"""
        self.选中格子ID变量.set("")
        if self.信息树 is not None:
            for 项 in self.信息树.get_children():
                self.信息树.delete(项)
        self.当前选中格子 = None
    
    def 清空地图属性编辑区(self):
        """清空地图属性编辑区"""
        if self.地图属性树 is not None:
            for 项 in self.地图属性树.get_children():
                self.地图属性树.delete(项)
    
    def 添加信息项(self):
        """添加新的格子信息项，默认为"属性键": "0.0" """
        if not self.当前选中格子:
            messagebox.showinfo("提示", "请先选择一个格子")
            return
            
        键 = "属性键"
        值 = "0.0"
        
        # 检查键是否已存在，如果存在则添加数字后缀
        现有键 = [self.信息树.item(项, "values")[0] for 项 in self.信息树.get_children()]
        if 键 in 现有键:
            计数 = 1
            while f"{键}{计数}" in 现有键:
                计数 += 1
            键 = f"{键}{计数}"
            
        self.信息树.insert("", tk.END, values=(键, 值))
    
    def 添加地图属性项(self):
        """添加新的地图属性项，默认为"属性键": "值" """
        if not self.当前地图名称:
            messagebox.showinfo("提示", "请先选择一个地图")
            return
            
        键 = "地图属性键"
        值 = "值"
        
        # 检查键是否已存在，如果存在则添加数字后缀
        现有键 = [self.地图属性树.item(项, "values")[0] for 项 in self.地图属性树.get_children()]
        if 键 in 现有键:
            计数 = 1
            while f"{键}{计数}" in 现有键:
                计数 += 1
            键 = f"{键}{计数}"
            
        self.地图属性树.insert("", tk.END, values=(键, 值))
    
    def 删除选中信息项(self):
        """删除选中的格子信息项"""
        选中项 = self.信息树.selection()
        if not 选中项:
            messagebox.showinfo("提示", "请先选择要删除的信息项")
            return
            
        for 项 in 选中项:
            self.信息树.delete(项)
    
    def 删除选中地图属性项(self):
        """删除选中的地图属性项"""
        选中项 = self.地图属性树.selection()
        if not 选中项:
            messagebox.showinfo("提示", "请先选择要删除的属性项")
            return
            
        for 项 in 选中项:
            self.地图属性树.delete(项)
    
    def 应用信息修改(self):
        """应用格子信息修改到格子"""
        if not self.当前选中格子:
            messagebox.showinfo("提示", "请先选择一个格子")
            return
            
        # 收集信息数据
        信息 = {}
        for 项 in self.信息树.get_children():
            数值 = self.信息树.item(项, "values")
            if len(数值) >= 2 and 数值[0]:  # 确保证键名不为空
                信息[数值[0]] = 数值[1]
        
        # 更新格子信息
        self.当前选中格子.set_info(信息)
        self.状态变量.set("格子信息已更新 (按Ctrl+S保存)")
    
    def 应用地图属性修改(self):
        """应用地图属性修改"""
        if not self.当前地图名称:
            messagebox.showinfo("提示", "请先选择一个地图")
            return
            
        # 收集地图属性数据
        地图属性 = {}
        for 项 in self.地图属性树.get_children():
            数值 = self.地图属性树.item(项, "values")
            if len(数值) >= 2 and 数值[0]:  # 确保证键名不为空
                地图属性[数值[0]] = 数值[1]
        
        # 更新地图属性
        if self.当前地图名称 in self.地图数据:
            self.地图数据[self.当前地图名称]["属性"] = 地图属性
            self.状态变量.set("地图属性已更新 (按Ctrl+S保存)")
    
    def 处理信息双击(self, 事件):
        """双击编辑格子信息项"""
        区域 = self.信息树.identify_region(事件.x, 事件.y)
        if 区域 != "cell":
            return
            
        # 解析列索引
        列字符串 = self.信息树.identify_column(事件.x)
        列 = int(列字符串.replace('#', '')) - 1  # 转换为0-based索引
        
        项 = self.信息树.identify_row(事件.y)
        
        # 获取单元格位置和当前值
        x, y, 宽度, 高度 = self.信息树.bbox(项, 列)
        值 = self.信息树.item(项, "values")[列]
        
        # 创建编辑框
        输入框 = ttk.Entry(self.信息树)
        输入框.place(x=x, y=y, width=宽度, height=高度)
        输入框.insert(0, 值)
        输入框.focus()
        
        # 保存当前编辑框引用
        self.信息编辑框 = 输入框
        
        # 保存编辑结果
        def 保存编辑(事件=None):
            # 检查项目是否仍然存在
            if 项 not in self.信息树.get_children():
                输入框.destroy()
                return
                
            新值 = 输入框.get()
            数值列表 = list(self.信息树.item(项, "values"))
            数值列表[列] = 新值
            self.信息树.item(项, values=数值列表)
            输入框.destroy()
        
        输入框.bind("<FocusOut>", 保存编辑)
        输入框.bind("<Return>", 保存编辑)
        输入框.bind("<Escape>", lambda e: 输入框.destroy())
    
    def 处理地图属性双击(self, 事件):
        """双击编辑地图属性项"""
        区域 = self.地图属性树.identify_region(事件.x, 事件.y)
        if 区域 != "cell":
            return
            
        # 解析列索引
        列字符串 = self.地图属性树.identify_column(事件.x)
        列 = int(列字符串.replace('#', '')) - 1  # 转换为0-based索引
        
        项 = self.地图属性树.identify_row(事件.y)
        
        # 获取单元格位置和当前值
        x, y, 宽度, 高度 = self.地图属性树.bbox(项, 列)
        值 = self.地图属性树.item(项, "values")[列]
        
        # 创建编辑框
        输入框 = ttk.Entry(self.地图属性树)
        输入框.place(x=x, y=y, width=宽度, height=高度)
        输入框.insert(0, 值)
        输入框.focus()
        
        # 保存编辑结果
        def 保存编辑(事件=None):
            # 检查项目是否仍然存在
            if 项 not in self.地图属性树.get_children():
                输入框.destroy()
                return
                
            新值 = 输入框.get()
            数值列表 = list(self.地图属性树.item(项, "values"))
            数值列表[列] = 新值
            self.地图属性树.item(项, values=数值列表)
            输入框.destroy()
        
        输入框.bind("<FocusOut>", 保存编辑)
        输入框.bind("<Return>", 保存编辑)
        输入框.bind("<Escape>", lambda e: 输入框.destroy())
    
    def 显示NPC选择对话框(self, 格子组件):
        """显示NPC选择对话框"""
        # 先保存当前编辑的信息
        if self.当前选中格子 and self.信息树 and self.信息树.get_children():
            self.应用信息修改()
            
        if not self.NPC列表:
            messagebox.showinfo("提示", "未找到NPC数据，请先确保npcsystem.json存在")
            return
            
        # 创建对话框
        对话框 = tk.Toplevel(self.主窗口)
        对话框.title("选择NPC")
        对话框.geometry("400x400")
        对话框.transient(self.主窗口)
        对话框.grab_set()
        
        # 居中显示
        对话框.update_idletasks()
        宽度 = 对话框.winfo_width()
        高度 = 对话框.winfo_height()
        x = (self.主窗口.winfo_width() // 2) - (宽度 // 2) + self.主窗口.winfo_x()
        y = (self.主窗口.winfo_height() // 2) - (高度 // 2) + self.主窗口.winfo_y()
        对话框.geometry('{}x{}+{}+{}'.format(宽度, 高度, x, y))
        
        # 搜索框
        ttk.Label(对话框, text="搜索NPC:").pack(anchor=tk.W, padx=10, pady=(10, 5))
        搜索变量 = tk.StringVar()
        搜索框 = ttk.Entry(对话框, textvariable=搜索变量)
        搜索框.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        # NPC列表
        列表框框架 = ttk.Frame(对话框)
        列表框框架.pack(fill=tk.BOTH, expand=True, padx=10)
        
        NPC列表框 = tk.Listbox(列表框框架, width=50)
        NPC列表框.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 滚动条
        滚动条 = ttk.Scrollbar(列表框框架, orient=tk.VERTICAL, command=NPC列表框.yview)
        滚动条.pack(side=tk.RIGHT, fill=tk.Y)
        NPC列表框.config(yscrollcommand=滚动条.set)
        
        # 填充NPC列表
        self.NPC_ID列表 = []
        for NPCID, NPC数据 in self.NPC列表.items():
            NPC名称 = NPC数据.get("名称", "未命名")
            NPC列表框.insert(tk.END, f"{NPCID}: {NPC名称}")
            self.NPC_ID列表.append(NPCID)
        
        # 搜索功能
        def 过滤NPC(*args):
            搜索文本 = 搜索变量.get().lower()
            NPC列表框.delete(0, tk.END)
            self.NPC_ID列表 = []
            
            for NPCID, NPC数据 in self.NPC列表.items():
                NPC名称 = NPC数据.get("名称", "未命名").lower()
                if 搜索文本 in NPCID.lower() or 搜索文本 in NPC名称:
                    NPC列表框.insert(tk.END, f"{NPCID}: {NPC数据.get('名称', '未命名')}")
                    self.NPC_ID列表.append(NPCID)
        
        搜索变量.trace_add("write", 过滤NPC)
        
        # 选择按钮
        def 确认选择():
            选中索引 = NPC列表框.curselection()
            if 选中索引:
                NPCID = self.NPC_ID列表[选中索引[0]]
                格子组件.set_npc_id(NPCID)
                # 更新信息编辑区
                if self.当前选中格子 == 格子组件:
                    self.加载格子信息到编辑区(格子组件)
                对话框.destroy()
        
        按钮框架 = ttk.Frame(对话框)
        按钮框架.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(按钮框架, text="清除选择", command=lambda: [格子组件.set_npc_id(""), 对话框.destroy()]).pack(side=tk.LEFT, padx=5, expand=True)
        ttk.Button(按钮框架, text="取消", command=对话框.destroy).pack(side=tk.LEFT, padx=5, expand=True)
        ttk.Button(按钮框架, text="确认", command=确认选择).pack(side=tk.LEFT, padx=5, expand=True)
        
        # 双击选择
        NPC列表框.bind("<Double-1>", lambda e: 确认选择())
        
        # 等待对话框关闭
        self.主窗口.wait_window(对话框)


class 格子组件(tk.Frame):
    """地图格子组件 - 使用tk.Frame以支持背景色设置"""
    def __init__(self, 父容器, 格子ID, 地图编辑器):
        super().__init__(父容器, relief="solid", bd=1, highlightthickness=0)
        self.格子ID = 格子ID
        self.地图编辑器 = 地图编辑器
        self.npc_id = ""
        self.info = {}
        self.选中 = False
        
        # 设置格子大小
        self.grid_propagate(False)
        self.configure(width=地图编辑器.地图配置["格子大小"], 
                      height=地图编辑器.地图配置["格子大小"],
                      bg="white")
        
        # 创建格子内容
        self.创建内容()
        
        # 绑定点击事件，确保事件不会冒泡
        self.bind("<Button-1>", self.左键点击事件)
        self.bind("<Button-3>", self.右键点击事件)  # 绑定右键事件
        # 防止子组件捕获点击事件
        self.ID标签.bind("<Button-1>", self.左键点击事件)
        self.ID标签.bind("<Button-3>", self.右键点击事件)
        self.NPC标签.bind("<Button-1>", self.左键点击事件)
        self.NPC标签.bind("<Button-3>", self.右键点击事件)
    
    def 创建内容(self):
        """创建格子内容"""
        # 格子ID标签
        self.ID标签 = tk.Label(self, text=f"ID: {self.格子ID}", font=("SimHei", 8),
                               bg="white")
        self.ID标签.pack(anchor=tk.NW, padx=2, pady=2)
        
        # NPC信息标签
        self.NPC标签 = tk.Label(self, text="无NPC", font=("SimHei", 9), 
                                wraplength=self.地图编辑器.地图配置["格子大小"]-10,
                                bg="white")
        self.NPC标签.pack(expand=True)
    
    def 左键点击事件(self, event):
        """左键点击事件 - 选择格子并显示NPC选择对话框"""
        # 检查组件是否仍然存在
        if not self.winfo_exists():
            return "break"
            
        # 阻止事件进一步传播
        event.widget = self  # 确保事件源是格子本身
        # 通知地图编辑器，显示NPC对话框
        self.地图编辑器.处理格子点击(self, 显示NPC对话框=True)
        return "break"  # 阻止事件继续传播
    
    def 右键点击事件(self, event):
        """右键点击事件 - 只选择格子不显示NPC选择对话框"""
        # 检查组件是否仍然存在
        if not self.winfo_exists():
            return "break"
            
        # 阻止事件进一步传播
        event.widget = self  # 确保事件源是格子本身
        # 通知地图编辑器，不显示NPC对话框
        self.地图编辑器.处理格子点击(self, 显示NPC对话框=False)
        return "break"  # 阻止事件继续传播
    
    def set_npc_id(self, npc_id):
        """设置NPC ID并更新显示"""
        self.npc_id = npc_id
        
        # 更新显示
        if npc_id and npc_id in self.地图编辑器.NPC列表:
            NPC名称 = self.地图编辑器.NPC列表[npc_id].get("名称", "未知NPC")
            self.NPC标签.config(text=f"NPC: {npc_id}\n{NPC名称}")
        else:
            self.NPC标签.config(text="无NPC")
        
        # 更新状态
        self.地图编辑器.状态变量.set("格子数据已更新 (按Ctrl+S保存)")
    
    def get_npc_id(self):
        """获取NPC ID"""
        return self.npc_id
    
    def set_info(self, info):
        """设置格子信息"""
        self.info = info.copy()
    
    def get_info(self):
        """获取格子信息"""
        return self.info.copy()
    
    def set_selected(self, 选中状态):
        """设置选中状态，添加组件存在性检查"""
        # 检查组件是否仍然存在
        if not self.winfo_exists():
            return
            
        self.选中 = 选中状态
        if 选中状态:
            self.configure(bg="#a0c8ff", bd=2)
            self.ID标签.configure(bg="#a0c8ff")
            self.NPC标签.configure(bg="#a0c8ff")
        else:
            self.configure(bg="white", bd=1)
            self.ID标签.configure(bg="white")
            self.NPC标签.configure(bg="white")


if __name__ == "__main__":
    根窗口 = tk.Tk()
    应用 = 地图编辑器(根窗口)
    根窗口.mainloop()
    