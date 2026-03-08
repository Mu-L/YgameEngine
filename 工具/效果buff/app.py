# cython: language_level=3
# cython: c_string_encoding=utf-8
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import json
import os
import sys
import time
from pathlib import Path

class Buff效果编辑器:
    def __init__(self, 主窗口):
        self.主窗口 = 主窗口
        self.主窗口.title("Buff效果编辑器")
        self.主窗口.geometry("1200x800")
        self.主窗口.minsize(800, 600)
        
        # 初始化状态变量
        self.状态变量 = tk.StringVar(value="就绪 (自动保存已启用，可手动点击保存按钮)")
        
        # 数据存储
        self.道具数据 = {}
        self.技能数据 = {}
        self.Buff数据 = {}
        self.Buff系统数据 = {}
        self.当前选中类型 = tk.StringVar(value="技能")
        self.当前选中ID = None
        
        # 自动保存相关变量
        self.上次保存时间 = 0
        self.保存节流间隔 = 0.5  # 0.5秒内不重复保存，避免性能问题
        
        # 文件路径配置
        self.计算文件路径()
        
        # 初始化并加载数据
        self.加载道具数据()
        self.加载技能数据()
        self.加载Buff系统数据()
        self.加载Buff配置数据()
        
        # 创建UI
        self.创建界面组件()
        
        # 绑定快捷键
        self.设置快捷键()
    
    def 计算文件路径(self):
        """计算项目根目录和文件路径"""
        try:
            if getattr(sys, 'frozen', False):
                当前路径 = os.path.dirname(sys.executable)
            else:
                当前路径 = os.path.dirname(os.path.abspath(__file__))
            
            # 项目根目录（系统文件夹的父目录）
            self.项目根目录 = os.path.abspath(os.path.join(当前路径, "..", "..", "..", ".."))
            self.系统文件夹 = os.path.join(self.项目根目录, "系统")
            
            # 确保系统文件夹存在
            os.makedirs(self.系统文件夹, exist_ok=True)
            
            # 文件路径
            self.道具文件 = os.path.join(self.系统文件夹, "itemsystem.json")
            self.技能文件 = os.path.join(self.系统文件夹, "skillsystem.json")
            self.Buff系统文件 = os.path.join(self.系统文件夹, "buffSystem.json")
            self.Buff配置文件 = os.path.join(self.系统文件夹, "buff.json")
            
            print(f"道具文件: {self.道具文件}")
            print(f"技能文件: {self.技能文件}")
            print(f"Buff系统文件: {self.Buff系统文件}")
            print(f"Buff配置文件: {self.Buff配置文件}")
            
        except Exception as e:
            messagebox.showerror("路径计算错误", f"无法计算项目路径: {str(e)}")
            self.项目根目录 = os.getcwd()
            self.系统文件夹 = os.path.join(self.项目根目录, "系统")
            os.makedirs(self.系统文件夹, exist_ok=True)
            
            self.道具文件 = os.path.join(self.系统文件夹, "itemsystem.json")
            self.技能文件 = os.path.join(self.系统文件夹, "skillsystem.json")
            self.Buff系统文件 = os.path.join(self.系统文件夹, "buffSystem.json")
            self.Buff配置文件 = os.path.join(self.系统文件夹, "buff.json")
    
    def 设置快捷键(self):
        """设置快捷键"""
        self.主窗口.bind("<Control-s>", self.保存数据快捷键)
        self.主窗口.bind("<Control-S>", self.保存数据快捷键)
    
    def 保存数据快捷键(self, 事件=None):
        """快捷键触发的保存功能"""
        self.保存Buff配置数据(强制=True)
        return "break"
    
    def 加载道具数据(self):
        """加载道具数据"""
        if os.path.exists(self.道具文件):
            try:
                with open(self.道具文件, 'r', encoding='utf-8') as f:
                    self.道具数据 = json.load(f)
                self.显示提示(f"已加载道具数据: {len(self.道具数据)}个道具", 显示弹窗=False)
            except Exception as e:
                messagebox.showerror("加载错误", f"无法加载道具数据：{str(e)}")
                self.道具数据 = {}
        else:
            self.显示提示("道具文件不存在", 显示弹窗=False)
    
    def 加载技能数据(self):
        """加载技能数据"""
        if os.path.exists(self.技能文件):
            try:
                with open(self.技能文件, 'r', encoding='utf-8') as f:
                    self.技能数据 = json.load(f)
                self.显示提示(f"已加载技能数据: {len(self.技能数据)}个技能", 显示弹窗=False)
            except Exception as e:
                messagebox.showerror("加载错误", f"无法加载技能数据：{str(e)}")
                self.技能数据 = {}
        else:
            self.显示提示("技能文件不存在", 显示弹窗=False)
    
    def 加载Buff系统数据(self):
        """加载Buff系统数据（buffSystem.json）"""
        if os.path.exists(self.Buff系统文件):
            try:
                with open(self.Buff系统文件, 'r', encoding='utf-8') as f:
                    self.Buff系统数据 = json.load(f)
                self.显示提示(f"已加载Buff系统数据: {len(self.Buff系统数据)}个Buff", 显示弹窗=False)
            except Exception as e:
                messagebox.showerror("加载错误", f"无法加载Buff系统数据：{str(e)}")
                self.Buff系统数据 = {}
        else:
            messagebox.showwarning("警告", "Buff系统文件不存在！")
            self.Buff系统数据 = {}
    
    def 加载Buff配置数据(self):
        """加载Buff配置数据（buff.json）"""
        if os.path.exists(self.Buff配置文件):
            try:
                with open(self.Buff配置文件, 'r', encoding='utf-8') as f:
                    self.Buff数据 = json.load(f)
                self.显示提示(f"已加载Buff配置数据", 显示弹窗=False)
            except Exception as e:
                messagebox.showerror("加载错误", f"无法加载Buff配置数据：{str(e)}")
                self.Buff数据 = {"技能": {}, "物品": {}}
        else:
            # 初始化空的Buff配置结构
            self.Buff数据 = {"技能": {}, "物品": {}}
            self.显示提示("Buff配置文件不存在，将创建新文件", 显示弹窗=False)
    
    def 保存Buff配置数据(self, 强制=False, 手动保存=False):
        """保存Buff配置数据到buff.json，添加节流控制"""
        # 节流控制：如果不是强制保存，且距离上次保存不足指定间隔，则不保存
        当前时间 = time.time()
        if not 强制 and (当前时间 - self.上次保存时间) < self.保存节流间隔:
            return
            
        try:
            with open(self.Buff配置文件, 'w', encoding='utf-8') as f:
                json.dump(self.Buff数据, f, ensure_ascii=False, indent=2)
            self.上次保存时间 = 当前时间
            # 手动保存时显示弹窗，自动保存时不显示
            self.显示提示(f"已保存Buff配置", 显示弹窗=手动保存)
        except Exception as e:
            messagebox.showerror("保存错误", f"无法保存Buff配置数据：{str(e)}")
    
    def 获取或创建配置(self, 类型, ID):
        """获取或创建指定类型和ID的配置（更新为包含几率的结构）"""
        if 类型 not in self.Buff数据:
            self.Buff数据[类型] = {}
        
        if ID not in self.Buff数据[类型]:
            self.Buff数据[类型][ID] = {
                "范围": "我方",
                "增益": []  # 现在存储的是 {"ID": "...", "几率": 1.0} 对象
            }
        return self.Buff数据[类型][ID]
    
    def 创建界面组件(self):
    
        """创建UI组件（优化布局，确保左侧面板可有效压缩）"""
        # 主框架使用网格布局，方便控制比例
        self.主框架 = ttk.Frame(self.主窗口, padding="10")
        self.主框架.pack(fill=tk.BOTH, expand=True)
        
        # 设置列权重，控制各区域扩展优先级
        self.主框架.columnconfigure(0, weight=2)   # 左侧区域（最低优先级）
        self.主框架.columnconfigure(1, weight=3)   # 中间区域
        self.主框架.columnconfigure(2, weight=4)   # 右侧区域（最高优先级）
        self.主框架.rowconfigure(0, weight=1)
        
        # ---------------------- 左侧面板：技能/道具列表 ----------------------
        左侧框架 = ttk.LabelFrame(self.主框架, text="技能/道具列表", padding="3")
        左侧框架.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        
        # 左侧框架内部布局配置
        左侧框架.columnconfigure(0, weight=1)
        左侧框架.rowconfigure(2, weight=1)  # 列表区域可扩展
        左侧框架.rowconfigure(4, weight=1)  # 详情区域不可扩展
        
        # 1. 类型切换（技能/道具）
        类型切换框架 = ttk.Frame(左侧框架)
        类型切换框架.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        
        ttk.Radiobutton(类型切换框架, text="技能", variable=self.当前选中类型, 
                    value="技能", command=self.更新项目列表).pack(side=tk.LEFT, padx=3)
        ttk.Radiobutton(类型切换框架, text="道具", variable=self.当前选中类型, 
                    value="物品", command=self.更新项目列表).pack(side=tk.LEFT, padx=3)
        
        # 2. 搜索框
        搜索框架 = ttk.Frame(左侧框架)
        搜索框架.grid(row=1, column=0, sticky="ew", pady=(0, 8))
        搜索框架.columnconfigure(1, weight=1)
        
        ttk.Label(搜索框架, text="搜索:").grid(row=0, column=0, sticky="w")
        self.搜索变量 = tk.StringVar()
        self.搜索变量.trace_add("write", lambda *args: self.更新项目列表())
        搜索输入框 = ttk.Entry(搜索框架, textvariable=self.搜索变量, width=15)  # 限制宽度
        搜索输入框.grid(row=0, column=1, sticky="ew", padx=3)
        
        # 3. 项目列表框（带滚动条）
        列表滚动框架 = ttk.Frame(左侧框架)
        列表滚动框架.grid(row=2, column=0, sticky="nsew")
        列表滚动框架.columnconfigure(0, weight=1)
        列表滚动框架.rowconfigure(0, weight=1)
        
        self.项目列表框 = tk.Listbox(
            列表滚动框架, 
            width=18,  # 较小的初始宽度
            height=10, 
            selectmode=tk.SINGLE,
            font=('SimHei', 12)  # 稍小的字体
        )
        self.项目列表框.grid(row=0, column=0, sticky="nsew")
        self.项目列表框.bind('<<ListboxSelect>>', self.加载项目配置)
        
        项目滚动条 = ttk.Scrollbar(列表滚动框架, orient=tk.VERTICAL, command=self.项目列表框.yview)
        项目滚动条.grid(row=0, column=1, sticky="ns")
        self.项目列表框.config(yscrollcommand=项目滚动条.set)
        
        # 4. 项目详情
        详情框架 = ttk.LabelFrame(左侧框架, text="详情", padding="3")
        详情框架.grid(row=4, column=0, sticky="nsew", pady=(8, 0))
        详情框架.columnconfigure(0, weight=1)
        详情框架.rowconfigure(0, weight=1)  # 新增：让详情框架的第0行可扩展
        self.项目详情文本 = tk.Text(
            详情框架, 
            height=8,  # 限制高度
            wrap=tk.WORD,
            width=20,  # 限制宽度
            font=('SimHei', 12)
        )
        self.项目详情文本.grid(row=0, column=0, sticky="nsew")
        
        # ---------------------- 中间面板：Buff列表 ----------------------
        中间框架 = ttk.LabelFrame(self.主框架, text="Buff列表 (可选增益)", padding="5")
        中间框架.grid(row=0, column=1, sticky="nsew", padx=(0, 10))
        中间框架.columnconfigure(0, weight=1)
        中间框架.rowconfigure(2, weight=1)
        
        # 1. Buff搜索框
        Buff搜索框架 = ttk.Frame(中间框架)
        Buff搜索框架.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        Buff搜索框架.columnconfigure(1, weight=1)
        
        ttk.Label(Buff搜索框架, text="搜索Buff:").grid(row=0, column=0, sticky="w")
        self.Buff搜索变量 = tk.StringVar()
        self.Buff搜索变量.trace_add("write", lambda *args: self.更新Buff列表())
        ttk.Entry(Buff搜索框架, textvariable=self.Buff搜索变量).grid(row=0, column=1, sticky="ew", padx=5)
        
        # 2. Buff列表框（带滚动条）
        Buff滚动框架 = ttk.Frame(中间框架)
        Buff滚动框架.grid(row=2, column=0, sticky="nsew")
        Buff滚动框架.columnconfigure(0, weight=1)
        Buff滚动框架.rowconfigure(0, weight=1)
        
        self.Buff列表框 = tk.Listbox(Buff滚动框架, width=20, height=10, selectmode=tk.SINGLE)
        self.Buff列表框.grid(row=0, column=0, sticky="nsew")
        
        Buff滚动条 = ttk.Scrollbar(Buff滚动框架, orient=tk.VERTICAL, command=self.Buff列表框.yview)
        Buff滚动条.grid(row=0, column=1, sticky="ns")
        self.Buff列表框.config(yscrollcommand=Buff滚动条.set)
        
        # ---------------------- 右侧面板：配置编辑 ----------------------
        右侧框架 = ttk.LabelFrame(self.主框架, text="Buff配置编辑", padding="10")
        右侧框架.grid(row=0, column=2, sticky="nsew")
        右侧框架.columnconfigure(0, weight=1)
        右侧框架.rowconfigure(3, weight=1)  # 增益列表区域可扩展
        
        # 1. 当前选中项目信息
        标题框架 = ttk.Frame(右侧框架)
        标题框架.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        self.当前项目标签 = ttk.Label(标题框架, text="未选择项目", font=("Arial", 12, "bold"))
        self.当前项目标签.pack(side=tk.LEFT)
        
        # 2. 范围选择
        范围框架 = ttk.LabelFrame(右侧框架, text="生效范围", padding="5")
        范围框架.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        
        self.范围变量 = tk.StringVar(value="我方")
        范围选项 = ["我方", "敌方", "使用者"]
        
        for 选项 in 范围选项:
            ttk.Radiobutton(范围框架, text=选项, variable=self.范围变量, 
                        value=选项, command=self.更新范围).pack(side=tk.LEFT, padx=10)
        
        # 3. 增益列表
        增益框架 = ttk.LabelFrame(右侧框架, text="增益列表", padding="5")
        增益框架.grid(row=3, column=0, sticky="nsew")
        增益框架.columnconfigure(0, weight=1)
        增益框架.rowconfigure(0, weight=1)
        
        # 增益按钮框架 - 添加了保存按钮
        增益按钮框架 = ttk.Frame(增益框架)
        增益按钮框架.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        
        ttk.Button(增益按钮框架, text="添加选中Buff到增益", command=self.添加Buff到增益).pack(side=tk.LEFT, padx=2)
        ttk.Button(增益按钮框架, text="移除选中增益", command=self.移除选中增益).pack(side=tk.LEFT, padx=2)
        ttk.Button(增益按钮框架, text="清空增益列表", command=self.清空增益列表).pack(side=tk.LEFT, padx=2)
        # 新增保存按钮
        ttk.Button(增益按钮框架, text="保存配置", command=lambda: self.保存Buff配置数据(强制=True, 手动保存=True)).pack(side=tk.LEFT, padx=2)
        # 创建带滚动条的Canvas用于显示带滑块的Buff项
        self.增益滚动框架 = ttk.Frame(增益框架)
        self.增益滚动框架.grid(row=0, column=0, sticky="nsew")
        
        self.增益Canvas = tk.Canvas(self.增益滚动框架)
        self.增益滚动条 = ttk.Scrollbar(
            self.增益滚动框架, 
            orient="vertical", 
            command=self.增益Canvas.yview
        )
        self.增益内容框架 = ttk.Frame(self.增益Canvas)  # 用于存放所有Buff项
        
        # 配置滚动区域
        self.增益内容框架.bind(
            "<Configure>",
            lambda e: self.增益Canvas.configure(scrollregion=self.增益Canvas.bbox("all"))
        )
        
        self.增益Canvas.create_window((0, 0), window=self.增益内容框架, anchor="nw")
        self.增益Canvas.configure(yscrollcommand=self.增益滚动条.set)
        
        # 布局Canvas和滚动条
        self.增益Canvas.pack(side="left", fill="both", expand=True)
        self.增益滚动条.pack(side="right", fill="y")
        
        # 状态栏
        状态栏 = ttk.Label(self.主窗口, textvariable=self.状态变量, relief=tk.SUNKEN, anchor=tk.W)
        状态栏.pack(side=tk.BOTTOM, fill=tk.X)
        
        # 初始化列表
        self.更新项目列表()
        self.更新Buff列表()
    
   
    def 更新项目列表(self):
        """更新技能/道具列表"""
        self.项目列表框.delete(0, tk.END)
        搜索关键词 = self.搜索变量.get().lower()
        
        if self.当前选中类型.get() == "技能":
            数据源 = self.技能数据
        else:
            数据源 = self.道具数据
        
        for ID in sorted(数据源.keys(), key=lambda x: int(x) if x.isdigit() else x):
            数据 = 数据源[ID]
            名称 = 数据.get("名称", "未命名")
            
            if 搜索关键词 in 名称.lower() or 搜索关键词 in ID.lower():
                self.项目列表框.insert(tk.END, f"ID: {ID} - {名称}")
    
    def 更新Buff列表(self):
        """更新Buff列表"""
        self.Buff列表框.delete(0, tk.END)
        搜索关键词 = self.Buff搜索变量.get().lower()
        
        for BuffID in sorted(self.Buff系统数据.keys(), key=lambda x: int(x) if x.isdigit() else x):
            Buff数据 = self.Buff系统数据[BuffID]
            名称 = Buff数据.get("名称", "未命名")
            描述 = Buff数据.get("描述", "")
            
            if (搜索关键词 in 名称.lower() or 
                搜索关键词 in BuffID.lower() or 
                搜索关键词 in 描述.lower()):
                self.Buff列表框.insert(tk.END, f"ID: {BuffID} - {名称}")
    
    def 加载项目配置(self, 事件=None):
        """加载选中项目的配置"""
        选中索引 = self.项目列表框.curselection()
        if not 选中索引:
            return
        
        选中文本 = self.项目列表框.get(选中索引[0])
        self.当前选中ID = 选中文本.split("ID: ")[1].split(" - ")[0]
        名称 = 选中文本.split(" - ")[1]
        
        # 更新标题
        self.当前项目标签.config(text=f"{self.当前选中类型.get()}: {self.当前选中ID} - {名称}")
        
        # 显示项目详情
        self.显示项目详情()
        
        # 获取或创建配置
        配置 = self.获取或创建配置(self.当前选中类型.get(), self.当前选中ID)
        
        # 设置范围
        self.范围变量.set(配置.get("范围", "我方"))
        
        # 更新增益列表
        self.更新增益列表显示(配置.get("增益", []))
    
    def 显示项目详情(self):
        """显示选中项目的详情"""
        self.项目详情文本.delete(1.0, tk.END)
        
        if not self.当前选中ID:
            return
        
        if self.当前选中类型.get() == "技能":
            数据 = self.技能数据.get(self.当前选中ID, {})
        else:
            数据 = self.道具数据.get(self.当前选中ID, {})
        
        详情 = []
        详情.append(f"ID: {self.当前选中ID}")
        详情.append(f"名称: {数据.get('名称', '未命名')}")
        
        if self.当前选中类型.get() == "技能":
            详情.append(f"类型: {数据.get('类型', '未知')}")
            详情.append(f"伤害: {数据.get('伤害', 0)}")
            详情.append(f"消耗: {数据.get('消耗', 0)}")
            详情.append(f"伤害类型: {数据.get('伤害类型', '未知')}")
            详情.append(f"描述: {数据.get('描述', '无')}")
        else:
            详情.append(f"类型: {数据.get('类型', '未知')}")
            详情.append(f"子类型: {数据.get('子类型', '未知')}")
            详情.append(f"价格: {数据.get('价格', 0)}")
            详情.append(f"描述: {数据.get('描述', '无')}")
        
        self.项目详情文本.insert(tk.END, "\n".join(详情))
    
    def 更新范围(self):
        """更新当前项目的范围设置"""
        if not self.当前选中ID:
            return
        
        配置 = self.获取或创建配置(self.当前选中类型.get(), self.当前选中ID)
        配置["范围"] = self.范围变量.get()
        self.显示提示(f"已更新范围为: {self.范围变量.get()}", 显示弹窗=False)
        self.保存Buff配置数据()  # 范围变更后自动保存
    
    def 添加Buff到增益(self):
        """添加选中的Buff到增益列表（使用默认几率1.0）"""
        if not self.当前选中ID:
            messagebox.showinfo("提示", "请先选择一个技能/道具")
            return
        
        Buff选中索引 = self.Buff列表框.curselection()
        if not Buff选中索引:
            messagebox.showinfo("提示", "请先选择一个Buff")
            return
        
        Buff选中文本 = self.Buff列表框.get(Buff选中索引[0])
        BuffID = Buff选中文本.split("ID: ")[1].split(" - ")[0]
        
        # 获取Buff详情验证存在性
        if BuffID not in self.Buff系统数据:
            messagebox.showwarning("警告", f"Buff ID {BuffID} 不存在于系统中")
            return
        
        # 获取当前配置
        配置 = self.获取或创建配置(self.当前选中类型.get(), self.当前选中ID)
        
        # 检查是否已存在（根据ID）
        已存在 = any(item["ID"] == BuffID for item in 配置["增益"])
        if 已存在:
            messagebox.showinfo("提示", f"Buff {BuffID} 已在增益列表中")
            return
        
        # 添加包含ID和默认几率的对象，确保初始值保留两位小数
        配置["增益"].append({
            "ID": BuffID,
            "几率": round(1.0, 2)  # 默认100%，保留两位小数
        })
        
        # 更新显示
        self.更新增益列表显示(配置["增益"])
        self.显示提示(f"已添加Buff: {BuffID} - {self.Buff系统数据[BuffID].get('名称', '未知')} (默认几率: 100%)",显示弹窗=False)
        self.保存Buff配置数据()  # 添加Buff后自动保存


    
    def 移除选中增益(self):
        """移除选中的增益项"""
        if not self.当前选中ID:
            messagebox.showinfo("提示", "请先选择一个技能/道具")
            return
        
        # 获取当前配置
        配置 = self.获取或创建配置(self.当前选中类型.get(), self.当前选中ID)
        
        if not 配置["增益"]:
            messagebox.showinfo("提示", "增益列表为空")
            return
        
        # 询问要删除哪一项
        删除选项 = [f"{item['ID']} - {self.Buff系统数据.get(item['ID'], {}).get('名称', '未知')}" 
                    for item in 配置["增益"]]
        
        if 删除选项:
            选中项 = simpledialog.askstring(
                "选择删除项", 
                "请输入要删除的Buff ID或名称:\n" + "\n".join(删除选项)
            )
            
            if 选中项:
                for i, item in enumerate(配置["增益"]):
                    if 选中项 in item["ID"] or 选中项 in self.Buff系统数据.get(item["ID"], {}).get("名称", ""):
                        移除项 = 配置["增益"].pop(i)
                        self.更新增益列表显示(配置["增益"])
                        self.显示提示(f"已移除: {移除项['ID']}", 显示弹窗=False)
                        self.保存Buff配置数据()  # 移除Buff后自动保存
                        return
                
                messagebox.showinfo("提示", "未找到匹配的Buff项")
    
    def 清空增益列表(self):
        """清空增益列表"""
        if not self.当前选中ID:
            messagebox.showinfo("提示", "请先选择一个技能/道具")
            return
        
        if messagebox.askyesno("确认清空", "确定要清空增益列表吗？"):
            # 获取当前配置
            配置 = self.获取或创建配置(self.当前选中类型.get(), self.当前选中ID)
            配置["增益"] = []  # 清空包含几率的数组
            
            # 更新显示
            self.更新增益列表显示([])
            self.显示提示("增益列表已清空",显示弹窗=False)
            self.保存Buff配置数据()  # 清空列表后自动保存
    
    def 更新增益列表显示(self, 增益列表):
        """更新增益列表显示，为每个Buff项添加独立滑块"""
        # 清除现有内容
        for widget in self.增益内容框架.winfo_children():
            widget.destroy()
        
        # 为每个增益项创建带滑块的行
        for 索引, 增益项 in enumerate(增益列表):
            BuffID = 增益项["ID"]
            # 确保从数据加载时就保留两位小数
            几率 = round(增益项["几率"], 2)
            
            # 从Buff系统数据中获取详细信息
            Buff数据 = self.Buff系统数据.get(BuffID, {})
            Buff名称 = Buff数据.get("名称", "未知")
            Buff描述 = Buff数据.get("描述", "无描述")
            
            # 创建当前行的框架
            行框架 = ttk.Frame(self.增益内容框架)
            行框架.grid(row=索引, column=0, sticky="ew", pady=2, padx=2)
            行框架.columnconfigure(1, weight=1)  # 让描述区域可扩展
            
            # Buff信息标签
            信息标签 = ttk.Label(
                行框架, 
                text=f"ID: {BuffID} - {Buff名称}\n    描述: {Buff描述}",
                justify=tk.LEFT
            )
            信息标签.grid(row=0, column=0, sticky="w", padx=5)
            
            # 几率控制区域
            几率控制框架 = ttk.Frame(行框架)
            几率控制框架.grid(row=0, column=1, sticky="e", padx=5)
            
            ttk.Label(几率控制框架, text="几率:").pack(side=tk.LEFT)
            
            # 为每个滑块创建独立的变量，使用列表存储以避免闭包引用问题
            几率变量 = [tk.DoubleVar(value=几率)]  # 使用列表包装
            
            滑块 = ttk.Scale(
                几率控制框架, 
                from_=0.0, 
                to=1.0, 
                orient=tk.HORIZONTAL, 
                variable=几率变量[0],  # 引用列表中的变量
                length=100  # 保持较短的滑块长度
            )
            滑块.pack(side=tk.LEFT, padx=5)
            
            # 几率显示（显示两位小数的百分比）
            几率显示 = ttk.Label(几率控制框架, text=f"{int(几率*100)}%", width=4)
            几率显示.pack(side=tk.LEFT)
            
            # 添加删除按钮 - 修复了变量名错误
            def 创建删除函数(当前索引):
                def 删除当前项():
                    if self.当前选中ID:
                        配置 = self.获取或创建配置(self.当前选中类型.get(), self.当前选中ID)
                        if 当前索引 < len(配置["增益"]):
                            移除项 = 配置["增益"].pop(当前索引)  # 修复变量名错误
                            self.更新增益列表显示(配置["增益"])
                            self.显示提示(f"已移除: {移除项['ID']}", 显示弹窗=False)
                            self.保存Buff配置数据()  # 删除后自动保存
                return 删除当前项
            
            ttk.Button(
                行框架, 
                text="删除", 
                command=创建删除函数(索引),
                width=5
            ).grid(row=0, column=2, padx=5)
            
            # 使用functools.partial替代lambda，避免闭包引用问题
            from functools import partial
            
            def 实时更新几率(当前索引, 当前BuffID, 变量列表, 显示控件, event=None):
                # 限制滑块值为两位小数
                新几率 = round(变量列表[0].get(), 2)
                变量列表[0].set(新几率)  # 更新变量确保显示一致
                显示控件.config(text=f"{int(新几率*100)}%")
                
                # 更新数据，确保存储两位小数
                if self.当前选中ID:
                    配置 = self.获取或创建配置(self.当前选中类型.get(), self.当前选中ID)
                    if 当前索引 < len(配置["增益"]):
                        配置["增益"][当前索引]["几率"] = 新几率
                        self.保存Buff配置数据()  # 几率变更后自动保存
            
            # 绑定滑块事件，使用partial传递参数
            滑块.bind("<Motion>", partial(实时更新几率, 索引, BuffID, 几率变量, 几率显示))
            滑块.bind("<ButtonRelease-1>", partial(实时更新几率, 索引, BuffID, 几率变量, 几率显示))
            
            # 绑定变量变化事件
            def 更新显示回调(变量列表, 显示控件, *args):
                新几率 = round(变量列表[0].get(), 2)
                显示控件.config(text=f"{int(新几率*100)}%")
            
            几率变量[0].trace_add("write", partial(更新显示回调, 几率变量, 几率显示))
        
        # 添加分隔线
        ttk.Separator(self.增益内容框架).grid(row=len(增益列表), column=0, sticky="ew", pady=5)
    
    def 显示提示(self, 消息, 成功=True, 显示弹窗=None):
        """显示操作提示"""
        self.状态变量.set(消息)
        
        if 显示弹窗 or (显示弹窗 is None and 成功):
            if 成功:
                messagebox.showinfo("操作成功", 消息)
            else:
                messagebox.showwarning("提示", 消息)

if __name__ == "__main__":
    根窗口 = tk.Tk()
    应用 = Buff效果编辑器(根窗口)
    根窗口.mainloop()