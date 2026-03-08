# cython: language_level=3
# cython: c_string_encoding=utf-8
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import json
import os
import sys
from pathlib import Path
import re

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
            支持拖放 = False

class 技能等级编辑器:
    def __init__(self, 主窗口):
        self.主窗口 = 主窗口
        self.主窗口.title("技能等级配置编辑器")
        self.主窗口.geometry("1200x800")
        self.主窗口.minsize(800, 600)
        
        # 初始化状态变量
        self.状态变量 = tk.StringVar(value="就绪 (按Ctrl+S保存)")
        
        # 计算路径
        self.计算项目路径()
        
        # 数据存储
        self.技能列表 = {}
        self.当前技能ID = None
        self.道具数据 = {}
        self.活跃编辑框 = None  # 用于跟踪当前活跃的编辑框
        
        # 配置文件路径
        self.技能配置文件 = os.path.join(self.系统文件夹, "skill_levels.json")
        self.道具配置文件 = os.path.join(self.系统文件夹, "itemsystem.json")
        self.技能系统文件 = os.path.join(self.系统文件夹, "skillsystem.json")
        self.效果历史文件 = os.path.join(self.系统文件夹, "skill_att.json")
        
        # 确保系统文件夹存在
        self.确保目录存在(self.系统文件夹)
        
        # 加载数据
        self.初始化默认文件()
        self.加载道具数据()
        self.加载技能列表()
        self.加载效果类型历史()
        
        # 创建UI
        self.创建界面组件()
        
        # 绑定快捷键
        self.设置快捷键()

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
            
            # 从技能系统文件夹向上三级找到项目根目录
            项目根目录 = os.path.abspath(os.path.join(当前路径, "..", "..", "..", ".."))
            
            # 系统文件夹路径
            self.系统文件夹 = os.path.join(项目根目录, "系统")
            self.项目根目录 = 项目根目录
            
            # 确保系统文件夹存在
            self.确保目录存在(self.系统文件夹)
            
            print(f"当前执行路径: {当前路径}")
            print(f"项目根目录: {项目根目录}")
            print(f"系统文件夹: {self.系统文件夹}")
            
        except Exception as e:
            messagebox.showerror("路径计算错误", f"无法计算项目路径: {str(e)}")
            # fallback到当前目录
            self.项目根目录 = os.getcwd()
            self.系统文件夹 = os.path.join(self.项目根目录, "系统")
            self.确保目录存在(self.系统文件夹)

    def 确保目录存在(self, 目录):
        """确保目录存在，如果不存在则创建"""
        try:
            Path(目录).mkdir(parents=True, exist_ok=True)
            return True
        except Exception as e:
            messagebox.showerror("目录错误", f"无法创建目录 {目录}：{str(e)}")
            return False

    def 初始化默认文件(self):
        """初始化默认的配置文件"""
        if not os.path.exists(self.技能配置文件):
            默认技能 = {
               "2001": {
                    "最大等级": 3,
                    "升级配置": ["熟练度"],
                    "等级属性": {
                        "1": {
                            "属性加成": {"伤害": 1.0},
                            "升级需求": {"熟练度": 1.0}
                        },
                        "2": {
                            "属性加成": {"伤害": 2.0},
                            "升级需求": {"熟练度": 5.0}
                        },
                        "3": {
                            "属性加成": {"伤害": 3.0},
                            "升级需求": {"熟练度": 10.0}
                        }
                    }
                }
            }
                
            try:
                with open(self.技能配置文件, 'w', encoding='utf-8') as f:
                    json.dump(默认技能, f, ensure_ascii=False, indent=2)
                    self.显示提示(f"已创建默认技能数据: {self.技能配置文件}")
            except Exception as e:
                messagebox.showerror("初始化错误", f"无法创建{self.技能配置文件}：{str(e)}")

    def 加载技能列表(self):
        """从skillsystem.json加载技能列表"""
        if os.path.exists(self.技能系统文件):
            try:
                with open(self.技能系统文件, 'r', encoding='utf-8') as f:
                    技能系统数据 = json.load(f)
                
                # 加载技能列表
                for 技能ID, 技能信息 in 技能系统数据.items():
                    if 技能ID not in self.技能列表:
                        self.技能列表[技能ID] = {
                            "最大等级": 1,
                            "升级配置": [],
                            "等级属性": {}
                        }
                
                self.显示提示(f"已从skillsystem.json加载技能列表: {len(self.技能列表)}个技能", 显示弹窗=False)
            except Exception as e:
                messagebox.showerror("加载错误", f"无法加载{self.技能系统文件}：{str(e)}")
                self.技能列表 = {}
        
        # 同时加载skill_levels.json的配置（如果存在）
        if os.path.exists(self.技能配置文件):
            try:
                with open(self.技能配置文件, 'r', encoding='utf-8') as f:
                    升级配置数据 = json.load(f)
                
                # 合并数据并转换旧格式
                for 技能ID, 配置 in 升级配置数据.items():
                    if 技能ID in self.技能列表:
                        # 转换旧格式的升级配置
                        if "升级配置" in 配置 and isinstance(配置["升级配置"], dict):
                            配置["升级配置"] = self.转换旧升级配置格式(配置["升级配置"])
                        self.技能列表[技能ID].update(配置)
                
                self.显示提示(f"已合并skill_levels.json配置", 显示弹窗=False)
            except Exception as e:
                messagebox.showerror("加载错误", f"无法加载{self.技能配置文件}：{str(e)}")
    
    def 加载效果类型历史(self):
        """加载历史效果类型，用于复用"""
        if os.path.exists(self.效果历史文件):
            try:
                with open(self.效果历史文件, 'r', encoding='utf-8') as f:
                    数据 = json.load(f)
                    if "effect_types" in 数据:
                        self.效果类型历史 = 数据["effect_types"]
                self.显示提示(f"已加载效果类型历史: {len(self.效果类型历史)}种", 显示弹窗=False)
            except Exception as e:
                messagebox.showerror("加载错误", f"无法加载效果历史数据：{str(e)}")
                self.效果类型历史 = []
        else:
            self.保存效果类型历史()

    def 加载道具数据(self):
        """加载道具数据用于选择"""
        if os.path.exists(self.道具配置文件):
            try:
                with open(self.道具配置文件, 'r', encoding='utf-8') as f:
                    原始数据 = json.load(f)
                
                self.道具数据 = {}
                for 道具ID, 道具信息 in 原始数据.items():
                    名称 = 道具信息.get("名称", f"道具{道具ID}")
                    self.道具数据[道具ID] = 名称
                
                self.显示提示(f"已加载道具数据: {len(self.道具数据)}个道具", 显示弹窗=False)
            except Exception as e:
                messagebox.showerror("道具数据加载错误", f"无法加载道具数据：{str(e)}")
                self.道具数据 = {}

    def 保存数据(self):
        """保存技能数据"""
        self.保存当前技能()
        
        try:
            with open(self.技能配置文件, 'w', encoding='utf-8') as f:
                json.dump(self.技能列表, f, ensure_ascii=False, indent=2)
            self.显示提示(f"已成功保存到 {self.技能配置文件} (Ctrl+S)", 显示弹窗=False)
            if hasattr(self, '刷新技能列表'):
                self.刷新技能列表()
        except Exception as e:
            messagebox.showerror("保存错误", f"无法保存{self.技能配置文件}：{str(e)}")

    def 创建界面组件(self):
        """创建UI组件"""
        # 主框架
        self.主框架 = ttk.Frame(self.主窗口, padding="10")
        self.主框架.pack(fill=tk.BOTH, expand=True)
        
        # 左侧技能列表
        左侧框架 = ttk.Frame(self.主框架, padding="5")
        左侧框架.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=(0, 10))
        
        # 技能列表框架
        技能列表框架 = ttk.LabelFrame(左侧框架, text="技能列表", padding="5")
        技能列表框架.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        # 技能列表框
        self.技能列表框 = tk.Listbox(技能列表框架, width=30, height=30, selectmode=tk.EXTENDED)
        self.技能列表框.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        self.技能列表框.bind('<<ListboxSelect>>', self.处理技能选择)
        
        # 滚动条
        滚动条 = ttk.Scrollbar(技能列表框架, orient=tk.VERTICAL, command=self.技能列表框.yview)
        滚动条.pack(side=tk.RIGHT, fill=tk.Y)
        self.技能列表框.config(yscrollcommand=滚动条.set)
        
        # 按钮框架 - 只保留保存按钮，在技能列表下方
        按钮框架 = ttk.Frame(左侧框架, padding="5")
        按钮框架.pack(side=tk.BOTTOM, fill=tk.X, pady=(5, 0))
        
        ttk.Button(按钮框架, text="保存所有 (Ctrl+S)", command=self.保存数据).pack(fill=tk.X, pady=1)
        
        # 右侧编辑区域
        右侧框架 = ttk.Frame(self.主框架)
        右侧框架.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # 上半部分：基本信息和升级配置并排
        右上框架 = ttk.Frame(右侧框架)
        右上框架.pack(side=tk.TOP, fill=tk.X, expand=False)
        
        # 基本信息框架
        基本信息框架 = ttk.LabelFrame(右上框架, text="基本信息", padding="10")
        基本信息框架.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=(0, 10), padx=(0, 5))
        
        # 表单网格
        表单网格 = ttk.Frame(基本信息框架)
        表单网格.pack(fill=tk.X)
        
        # 技能ID
        ttk.Label(表单网格, text="技能ID:").grid(row=0, column=0, sticky=tk.W, pady=5, padx=5)
        self.ID变量 = tk.StringVar()
        ttk.Entry(表单网格, textvariable=self.ID变量, width=20, state="readonly").grid(row=0, column=1, sticky=tk.W, pady=5)
        
        # 最大等级
        ttk.Label(表单网格, text="最大等级:").grid(row=1, column=0, sticky=tk.W, pady=5, padx=5)
        self.最大等级变量 = tk.StringVar()
        ttk.Entry(表单网格, textvariable=self.最大等级变量, width=20).grid(row=1, column=1, sticky=tk.W, pady=5)
        
        # 升级配置框架
        升级配置框架 = ttk.LabelFrame(右上框架, text="升级配置", padding="10")
        升级配置框架.pack(side=tk.RIGHT, fill=tk.BOTH, expand=False, pady=(0, 10), padx=(5, 0))
        
        # 升级配置类型选择
        ttk.Label(升级配置框架, text="配置类型:").grid(row=0, column=0, sticky=tk.W, pady=5, padx=5)
        self.配置类型变量 = tk.StringVar()
        ttk.Combobox(升级配置框架, textvariable=self.配置类型变量, 
                     values=["熟练度", "道具", "属性点","等级"], width=20).grid(row=0, column=1, sticky=tk.W, pady=5)
        
        # 添加升级配置按钮
        ttk.Button(升级配置框架, text="添加配置类型", command=self.添加升级配置).grid(row=1, column=0, columnspan=2, pady=5)
        
        # 升级配置列表（类似效果列表的Treeview）
        ttk.Label(升级配置框架, text="当前升级配置:").grid(row=2, column=0, sticky=tk.W, pady=5, padx=5)
        
        # 创建升级配置Treeview
        升级配置列 = ("type", "action")
        self.升级配置树 = ttk.Treeview(升级配置框架, columns=升级配置列, show="headings", height=4)
        self.升级配置树.heading("type", text="配置类型")
        self.升级配置树.heading("action", text="")  # 空标题，因为只显示类型
        self.升级配置树.column("type", width=200, anchor=tk.W)
        self.升级配置树.column("action", width=50, anchor=tk.W)
        
        self.升级配置树.grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # 删除选中配置按钮
        ttk.Button(升级配置框架, text="删除选中配置", command=self.删除选中配置).grid(row=4, column=0, columnspan=2, pady=5)
        
        # 等级属性框架 - 独占一排
        等级属性框架 = ttk.LabelFrame(右侧框架, text="等级属性", padding="10")
        等级属性框架.pack(side=tk.TOP, fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # 等级选择和管理 - 在最上方
        等级管理框架 = ttk.Frame(等级属性框架)
        等级管理框架.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(等级管理框架, text="选择等级:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.等级选择变量 = tk.StringVar()
        self.等级选择下拉框 = ttk.Combobox(等级管理框架, textvariable=self.等级选择变量, width=10)
        self.等级选择下拉框.grid(row=0, column=1, sticky=tk.W, padx=5)
        self.等级选择下拉框.bind('<<ComboboxSelected>>', self.处理等级选择)
        self.等级选择下拉框.bind('<KeyRelease>', self.处理等级选择)
        self.等级选择下拉框.bind('<FocusOut>', self.处理等级选择)
        
        # 添加/删除等级按钮
        ttk.Button(等级管理框架, text="添加等级", command=self.添加等级).grid(row=0, column=2, padx=5)
        ttk.Button(等级管理框架, text="复制等级", command=self.复制等级).grid(row=0, column=3, padx=5)
        ttk.Button(等级管理框架, text="删除等级", command=self.删除等级).grid(row=0, column=4, padx=5)
        
        # 等级属性列表标题
        ttk.Label(等级属性框架, text="当前等级属性:").pack(anchor=tk.W, pady=(0, 5))
        
        # Treeview和滚动条 - 占据中间大部分空间
        树形框架 = ttk.Frame(等级属性框架)
        树形框架.pack(side=tk.TOP, fill=tk.BOTH, expand=True, pady=(0, 5))
        
        # 创建等级属性Treeview
        等级属性列 = ("key", "value")
        self.等级属性树 = ttk.Treeview(树形框架, columns=等级属性列, show="headings", height=12, selectmode=tk.EXTENDED)
        
        self.等级属性树.heading("key", text="属性")
        self.等级属性树.heading("value", text="值")
        self.等级属性树.column("key", width=220, anchor=tk.W)
        self.等级属性树.column("value", width=220, anchor=tk.W)
        
        # 滚动条
        属性滚动条 = ttk.Scrollbar(树形框架, orient=tk.VERTICAL, command=self.等级属性树.yview)
        self.等级属性树.configure(yscrollcommand=属性滚动条.set)
        
        self.等级属性树.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        属性滚动条.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 属性操作按钮 - 移到最下面一行
        属性按钮框架 = ttk.Frame(等级属性框架)
        属性按钮框架.pack(side=tk.BOTTOM, fill=tk.X, pady=(5, 0))
        
        # 左侧按钮组
        左侧按钮框架 = ttk.Frame(属性按钮框架)
        左侧按钮框架.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Button(左侧按钮框架, text="删除选中", command=self.删除选中属性).pack(side=tk.LEFT, padx=2)
        ttk.Button(左侧按钮框架, text="清空属性", command=self.清空属性).pack(side=tk.LEFT, padx=2)
        ttk.Button(左侧按钮框架, text="从历史添加", command=self.从历史添加属性).pack(side=tk.LEFT, padx=2)
        
        # 右侧按钮组
        右侧按钮框架 = ttk.Frame(属性按钮框架)
        右侧按钮框架.pack(side=tk.RIGHT, fill=tk.X)
        ttk.Button(右侧按钮框架, text="添加道具需求", command=self.添加道具需求).pack(side=tk.LEFT, padx=2)
        ttk.Button(右侧按钮框架, text="添加属性加成", command=self.添加属性加成).pack(side=tk.LEFT, padx=2)
        ttk.Button(右侧按钮框架, text="添加升级需求", command=self.添加升级需求).pack(side=tk.LEFT, padx=2)
        
        # 绑定双击编辑
        self.等级属性树.bind("<Double-1>", self.处理属性双击)
        self.等级属性树.bind("<<TreeviewSelect>>", self.处理属性选择)
        
        # 状态栏
        状态栏 = ttk.Label(self.主窗口, textvariable=self.状态变量, relief=tk.SUNKEN, anchor=tk.W)
        状态栏.pack(side=tk.BOTTOM, fill=tk.X)
        
        # 更新技能列表
        self.更新技能列表()
        
        # 绑定文本变化事件
        self.最大等级变量.trace_add("write", lambda *args: self.状态变量.set("有未保存的更改 (按Ctrl+S保存)"))
        self.配置类型变量.trace_add("write", lambda *args: self.状态变量.set("有未保存的更改 (按Ctrl+S保存)"))
        
        # 窗口关闭事件
        self.主窗口.protocol("WM_DELETE_WINDOW", self.处理关闭)

    def 设置快捷键(self):
        """设置快捷键"""
        self.主窗口.bind("<Control-s>", self.保存数据快捷键)
        self.主窗口.bind("<Control-S>", self.保存数据快捷键)

    def 保存数据快捷键(self, 事件=None):
        """快捷键触发的保存功能"""
        self.保存数据()
        return "break"

    def 显示提示(self, 消息, 成功=True, 显示弹窗=False):
        """显示操作提示"""
        self.状态变量.set(消息)
        
        if 显示弹窗:
            if 成功:
                messagebox.showinfo("操作成功", 消息)
            else:
                messagebox.showwarning("操作提示", 消息)

    def 更新技能列表(self):
        """更新技能列表"""
        self.技能列表框.delete(0, tk.END)
        
        # 从skillsystem.json获取技能名称
        技能名称映射 = {}
        if os.path.exists(self.技能系统文件):
            try:
                with open(self.技能系统文件, 'r', encoding='utf-8') as f:
                    技能系统数据 = json.load(f)
                for 技能ID, 技能数据 in 技能系统数据.items():
                    技能名称映射[技能ID] = 技能数据.get("名称", f"技能{技能ID}")
            except Exception:
                pass
        
        # 按ID排序显示
        for 技能ID in sorted(self.技能列表.keys(), key=int):
            技能名称 = 技能名称映射.get(技能ID, f"技能{技能ID}")
            列表文本 = f"{技能名称} (ID: {技能ID})"
            self.技能列表框.insert(tk.END, 列表文本)

    def 刷新技能列表(self):
        """刷新技能列表"""
        # 保存当前选中的技能ID
        当前选中 = self.技能列表框.curselection()
        当前技能ID = None
        if 当前选中:
            选中文本 = self.技能列表框.get(当前选中[0])
            匹配 = re.search(r'ID: (\d+)', 选中文本)
            if 匹配:
                当前技能ID = 匹配.group(1)
        
        # 重新加载数据
        self.加载技能列表()
        
        # 更新列表显示
        self.更新技能列表()
        
        # 恢复选中状态
        if 当前技能ID:
            for i, 技能文本 in enumerate(self.技能列表框.get(0, tk.END)):
                if f"ID: {当前技能ID}" in 技能文本:
                    self.技能列表框.selection_set(i)
                    self.技能列表框.see(i)
                    break
    
    def 处理技能选择(self, 事件=None):
        """处理技能选择事件"""
        选中项 = self.技能列表框.curselection()
        if not 选中项:
            return
        
        选中文本 = self.技能列表框.get(选中项[0])
        匹配 = re.search(r'ID: (\d+)', 选中文本)
        if 匹配:
            技能ID = 匹配.group(1)
            self.加载技能(技能ID)
            # 从skillsystem.json获取技能名称
            技能名称 = "未命名"
            if os.path.exists(self.技能系统文件):
                try:
                    with open(self.技能系统文件, 'r', encoding='utf-8') as f:
                        技能系统数据 = json.load(f)
                    if 技能ID in 技能系统数据:
                        技能名称 = 技能系统数据[技能ID].get("名称", f"技能{技能ID}")
                    else:
                        技能名称 = f"技能{技能ID}"
                except:
                    技能名称 = f"技能{技能ID}"
            else:
                技能名称 = f"技能{技能ID}"
            
            self.显示提示(f"已选择技能: {技能名称} (ID: {技能ID})")

    def 加载技能(self, 技能ID):
        """加载技能数据到表单"""
        if 技能ID not in self.技能列表:
            return
        
        self.当前技能ID = 技能ID
        技能 = self.技能列表[技能ID]
        
        # 加载基本信息
        self.ID变量.set(技能ID)
        self.最大等级变量.set(str(技能.get("最大等级", 1)))
        
        # 加载升级配置到Treeview
        self.加载升级配置(技能.get("升级配置", []))
        
        # 更新等级选择下拉框
        等级属性 = 技能.get("等级属性", {})
        等级列表 = sorted(等级属性.keys(), key=int)
        self.等级选择下拉框['values'] = 等级列表
        
        if 等级列表:
            self.等级选择变量.set(等级列表[0])
            self.加载等级属性(等级列表[0])
        else:
            self.等级选择变量.set("")
            self.清空属性列表()

    def 保存当前技能(self):
        """保存当前编辑的技能"""
        if not self.当前技能ID or self.当前技能ID not in self.技能列表:
            return
        
        # 先保存当前等级的属性
        self.保存当前等级()
        
        # 处理最大等级
        最大等级文本 = self.最大等级变量.get().strip()
        最大等级值 = 1
        if 最大等级文本:
            try:
                最大等级值 = int(最大等级文本)
            except ValueError:
                messagebox.showwarning("输入错误", "最大等级必须是整数！")
                return
        
        # 处理升级配置
        升级配置 = self.获取升级配置数据()
        
        # 保存数据
        if "等级属性" not in self.技能列表[self.当前技能ID]:
            self.技能列表[self.当前技能ID]["等级属性"] = {}
        
        self.技能列表[self.当前技能ID].update({
            "最大等级": 最大等级值,
            "升级配置": 升级配置
        })

    

    def 添加升级配置(self):
        """添加升级配置（只显示类型）"""
        if not self.当前技能ID:
            messagebox.showinfo("提示", "请先选择一个技能")
            return
        
        配置类型 = self.配置类型变量.get().strip()
        if not 配置类型:
            messagebox.showwarning("输入错误", "请选择配置类型！")
            return
        
        # 检查是否已存在该类型
        现有类型 = set()
        for 项 in self.升级配置树.get_children():
            数值 = self.升级配置树.item(项, "values")
            if len(数值) >= 1:
                现有类型.add(数值[0].strip())
        
        # 如果类型不存在，则添加
        if 配置类型 not in 现有类型:
            self.升级配置树.insert('', tk.END, values=(配置类型, ""))
        
        self.状态变量.set("有未保存的更改 (按Ctrl+S保存)")

    def 删除选中配置(self):
        """删除选中的升级配置（同时删除检查和扣除）"""
        选中项 = self.升级配置树.selection()
        if not 选中项:
            messagebox.showinfo("提示", "请先选择要删除的配置")
            return
        
        for 项 in 选中项:
            self.升级配置树.delete(项)
        
        self.状态变量.set("有未保存的更改 (按Ctrl+S保存)")

    def 加载升级配置(self, 升级配置):
        """加载升级配置到Treeview（只显示类型）"""
        # 清空现有配置
        for 项 in self.升级配置树.get_children():
            self.升级配置树.delete(项)
        
        # 升级配置现在是简单的列表格式
        if isinstance(升级配置, list):
            for 类型 in sorted(升级配置):
                self.升级配置树.insert('', tk.END, values=(类型, ""))
        elif isinstance(升级配置, dict):
            # 兼容旧格式，从旧格式转换
            条件检查器 = 升级配置.get("条件检查器", [])
            消耗处理器 = 升级配置.get("消耗处理器", [])
            
            # 收集所有类型（去重）
            所有类型 = set()
            for 检查器 in 条件检查器:
                if 检查器.endswith("检查"):
                    类型 = 检查器[:-2]
                    所有类型.add(类型)
            
            for 处理器 in 消耗处理器:
                if 处理器.endswith("扣除"):
                    类型 = 处理器[:-2]
                    所有类型.add(类型)
            
            for 类型 in sorted(所有类型):
                self.升级配置树.insert('', tk.END, values=(类型, ""))

    def 获取升级配置数据(self):
        """从Treeview获取升级配置数据（简单列表格式）"""
        升级配置 = []
        
        for 项 in self.升级配置树.get_children():
            数值 = self.升级配置树.item(项, "values")
            if len(数值) >= 1:
                类型 = 数值[0].strip()
                if 类型:
                    升级配置.append(类型)
        
        return 升级配置
    
    def 转换旧升级配置格式(self, 旧配置):
        """将旧的升级配置格式转换为新格式"""
        if not isinstance(旧配置, dict):
            return 旧配置
        
        条件检查器 = 旧配置.get("条件检查器", [])
        消耗处理器 = 旧配置.get("消耗处理器", [])
        
        # 收集所有类型（去重）
        所有类型 = set()
        for 检查器 in 条件检查器:
            if 检查器.endswith("检查"):
                类型 = 检查器[:-2]
                所有类型.add(类型)
        
        for 处理器 in 消耗处理器:
            if 处理器.endswith("扣除"):
                类型 = 处理器[:-2]
                所有类型.add(类型)
        
        return sorted(list(所有类型))

    def 处理等级选择(self, 事件=None):
        """处理等级选择事件"""
        if not self.当前技能ID:
            print("处理等级选择: 没有当前技能ID")
            return
        
        print(f"处理等级选择: 当前技能ID = {self.当前技能ID}")
        
        # 直接从下拉框获取当前选中的值
        当前选择 = self.等级选择下拉框.get().strip()
        print(f"处理等级选择: 当前选择 = '{当前选择}'")
        
        # 如果获取不到值，尝试从下拉框的当前索引获取
        if not 当前选择:
            当前索引 = self.等级选择下拉框.current()
            print(f"处理等级选择: 当前索引 = {当前索引}")
            if 当前索引 >= 0:
                等级列表 = self.等级选择下拉框['values']
                if 当前索引 < len(等级列表):
                    当前选择 = 等级列表[当前索引]
                    print(f"处理等级选择: 从索引获取 = '{当前选择}'")
        
        if 当前选择:
            # 确保变量同步
            self.等级选择变量.set(当前选择)
            print(f"处理等级选择: 调用加载等级属性({当前选择})")
            self.加载等级属性(当前选择)
        else:
            print("处理等级选择: 没有有效的等级选择")

    def 加载等级属性(self, 等级):
        """加载指定等级的属性到Treeview"""
        print(f"加载等级属性: {等级}")
        if not self.当前技能ID:
            print("没有当前技能ID")
            self.清空属性列表()
            return
        
        等级属性 = self.技能列表[self.当前技能ID].get("等级属性", {})
        print(f"技能的等级属性: {等级属性}")
        
        if 等级 in 等级属性:
            # 等级存在，加载属性
            属性数据 = 等级属性[等级]
            print(f"加载属性数据: {属性数据}")
            
            # 如果属性数据是空字典或None，创建默认结构
            if not 属性数据:
                print(f"等级 {等级} 的属性数据为空，创建默认结构")
                属性数据 = {"属性加成": {}, "升级需求": {}}
                # 更新数据结构
                self.技能列表[self.当前技能ID]["等级属性"][等级] = 属性数据
            
            # 如果属性数据是旧格式（直接的键值对），转换为新格式
            elif isinstance(属性数据, dict):
                # 检查是否是旧格式（直接的键值对，没有"属性加成"和"升级需求"分组）
                # 只有当数据中既没有"属性加成"也没有"升级需求"键时，才认为是旧格式
                has_old_format = "属性加成" not in 属性数据 and "升级需求" not in 属性数据
                
                if has_old_format and 属性数据:  # 确保数据不为空
                    print("检测到旧格式，正在转换...")
                    # 转换旧格式为新格式
                    新属性数据 = {"属性加成": {}, "升级需求": {}}
                    
                    for key, value in 属性数据.items():
                        if key in ["熟练度", "经验", "属性点"]:  # 升级需求类
                            新属性数据["升级需求"][key] = value
                        elif key.endswith("加成"):  # 属性加成类
                            新属性数据["属性加成"][key] = value
                        else:  # 其他属性默认归为加成
                            新属性数据["属性加成"][key] = value
                    
                    # 更新数据结构
                    self.技能列表[self.当前技能ID]["等级属性"][等级] = 新属性数据
                    属性数据 = 新属性数据
            
            self.加载属性到列表(属性数据)
        else:
            # 等级不存在，显示空列表或创建新等级
            print(f"等级 {等级} 不存在")
            self.清空属性列表()
            # 如果需要，可以自动创建新等级的属性字典
            if "等级属性" not in self.技能列表[self.当前技能ID]:
                self.技能列表[self.当前技能ID]["等级属性"] = {}
            if 等级 not in self.技能列表[self.当前技能ID]["等级属性"]:
                # 创建默认的空结构
                self.技能列表[self.当前技能ID]["等级属性"][等级] = {"属性加成": {}, "升级需求": {}}
            self.加载属性到列表({"属性加成": {}, "升级需求": {}})

    def 清空属性列表(self):
        """清空属性列表"""
        for 项 in self.等级属性树.get_children():
            self.等级属性树.delete(项)

    def 加载属性到列表(self, 等级属性):
        """将等级属性加载到Treeview（仅支持新的分离结构）"""
        # 先清空现有列表
        self.清空属性列表()
        
        # 只支持新的分离结构
        self.加载分离结构属性(等级属性)
        
        # 强制刷新界面
        self.等级属性树.update()
        self.等级属性树.update_idletasks()
    
    def 加载分离结构属性(self, 等级属性):
        """加载新的分离结构属性"""
        # 添加属性加成部分
        if "属性加成" in 等级属性:
            属性加成 = 等级属性["属性加成"]
            if isinstance(属性加成, dict):
                # 添加分组标题
                self.等级属性树.insert('', tk.END, values=("=== 属性加成 ===", ""))
                for 属性名, 属性值 in 属性加成.items():
                    self.等级属性树.insert('', tk.END, values=(f"加成_{属性名}", str(属性值)))
        
        # 添加升级需求部分
        if "升级需求" in 等级属性:
            升级需求 = 等级属性["升级需求"]
            if isinstance(升级需求, dict):
                # 添加分组标题
                self.等级属性树.insert('', tk.END, values=("=== 升级需求 ===", ""))
                
                # 添加基础需求
                # 支持多种命名方式
                可能的需求名称 = {
                    "熟练度": ["熟练度", "熟练度需求", "skill_exp", "skill_requirement"],
                    "属性点": ["属性点", "属性点需求", "attribute_points", "attr_requirement"],
                    "经验": ["经验", "经验需求", "experience", "exp_requirement"]
                }
                
                # 先处理预定义的需求类型
                升级需求副本 = 升级需求.copy()  # 创建副本避免修改原数据
                for 标准名称, 可能名称列表 in 可能的需求名称.items():
                    for 可能名称 in 可能名称列表:
                        if 可能名称 in 升级需求副本:
                            self.等级属性树.insert('', tk.END, values=(f"需求_{标准名称}", str(升级需求副本[可能名称])))
                            升级需求副本.pop(可能名称, None)  # 从副本中移除已处理的需求
                            break  # 找到匹配的就跳出内层循环
                
                # 然后处理其他未预定义的需求类型（如"等级"）
                for 需求名称, 需求值 in 升级需求副本.items():
                    if 需求名称 != "道具需求":  # 道具需求在后面单独处理
                        self.等级属性树.insert('', tk.END, values=(f"需求_{需求名称}", str(需求值)))
                
                # 添加道具需求
                if "道具需求" in 升级需求:
                    道具需求 = 升级需求["道具需求"]
                    if isinstance(道具需求, dict):
                        for 道具ID, 数量 in 道具需求.items():
                            道具名称 = self.道具数据.get(道具ID, f"未知道具{道具ID}")
                            属性名 = f"道具需求_{道具ID}"
                            属性值 = f"{道具名称} x{数量}"
                            self.等级属性树.insert('', tk.END, values=(属性名, 属性值))
    


    def 添加道具需求(self):
        """添加道具需求"""
        if not self.道具数据:
            messagebox.showinfo("提示", "没有可选的道具数据")
            return
        
        # 创建选择道具的对话框
        选择窗口 = tk.Toplevel(self.主窗口)
        选择窗口.title("选择道具")
        选择窗口.geometry("400x300")
        选择窗口.transient(self.主窗口)
        选择窗口.grab_set()
        
        # 居中显示
        选择窗口.update_idletasks()
        宽度 = 选择窗口.winfo_width()
        高度 = 选择窗口.winfo_height()
        x = (self.主窗口.winfo_width() // 2) - (宽度 // 2) + self.主窗口.winfo_x()
        y = (self.主窗口.winfo_height() // 2) - (高度 // 2) + self.主窗口.winfo_y()
        选择窗口.geometry('{}x{}+{}+{}'.format(宽度, 高度, x, y))
        
        # 道具列表
        ttk.Label(选择窗口, text="选择道具:").pack(anchor=tk.W, padx=10, pady=5)
        
        道具列表框 = tk.Listbox(选择窗口, selectmode=tk.SINGLE, height=10)
        道具列表框.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # 填充道具列表
        for 道具ID, 道具名称 in sorted(self.道具数据.items(), key=lambda x: int(x[0])):
            道具列表框.insert(tk.END, f"{道具ID} - {道具名称}")
        
        # 数量输入
        ttk.Label(选择窗口, text="数量:").pack(anchor=tk.W, padx=10, pady=5)
        数量变量 = tk.StringVar(value="1")
        ttk.Entry(选择窗口, textvariable=数量变量, width=10).pack(padx=10, pady=5)
        
        def 确认添加():
            选中索引 = 道具列表框.curselection()
            if not 选中索引:
                messagebox.showinfo("提示", "请先选择一个道具")
                return
            
            选中文本 = 道具列表框.get(选中索引[0])
            if " - " in 选中文本:
                道具ID = 选中文本.split(" - ")[0]
                道具名称 = 选中文本.split(" - ")[1]
            else:
                道具ID = 选中文本
                道具名称 = f"未知道具{道具ID}"
            
            数量文本 = 数量变量.get().strip()
            try:
                数量 = float(数量文本)
                if 数量 <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showwarning("输入错误", "数量必须是正数！")
                return
            
            # 添加到属性列表
            属性名 = f"道具需求_{道具ID}"
            属性值 = f"{道具名称} x{数量}"
            self.等级属性树.insert('', tk.END, values=(属性名, 属性值))
            
            # 立即保存当前等级的属性
            self.保存当前等级()
            self.状态变量.set("有未保存的更改 (按Ctrl+S保存)")
            选择窗口.destroy()
        
        # 按钮
        按钮框架 = ttk.Frame(选择窗口)
        按钮框架.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(按钮框架, text="确认添加", command=确认添加).pack(side=tk.LEFT, padx=5)
        ttk.Button(按钮框架, text="取消", command=选择窗口.destroy).pack(side=tk.RIGHT, padx=5)
    
    def 删除选中属性(self):
        """删除选中的属性"""
        选中项 = self.等级属性树.selection()
        if not 选中项:
            messagebox.showinfo("提示", "请先选择要删除的属性")
            return
        
        for 项 in 选中项:
            self.等级属性树.delete(项)
        
        # 立即保存当前等级的属性
        self.保存当前等级()
        self.状态变量.set("有未保存的更改 (按Ctrl+S保存)")

    def 清空属性(self):
        """清空所有属性"""
        self.清空属性列表()
        # 立即保存当前等级的属性
        self.保存当前等级()
        self.状态变量.set("有未保存的更改 (按Ctrl+S保存)")

    def 处理属性双击(self, 事件):
        """双击编辑属性"""
        self.关闭活跃编辑框()
        
        # 获取点击的单元格
        区域 = self.等级属性树.identify_region(事件.x, 事件.y)
        if 区域 != "cell":
            return
            
        列字符串 = self.等级属性树.identify_column(事件.x)
        列 = int(列字符串.replace('#', '')) - 1  # 转换为0-based索引
        
        项 = self.等级属性树.identify_row(事件.y)
        
        if not 项:
            return
        
        # 获取单元格位置和值
        try:
            x, y, 宽度, 高度 = self.等级属性树.bbox(项, 列)
            值 = self.等级属性树.item(项, "values")[列]
        except:
            return
        
        # 创建编辑框
        self.活跃编辑框 = ttk.Entry(self.等级属性树)
        self.活跃编辑框.insert(0, 值)
        self.活跃编辑框.place(x=x, y=y, width=宽度, height=高度)
        self.活跃编辑框.focus()
        
        # 保存编辑结果
        def 保存编辑(事件=None):
            if self.活跃编辑框 and 项 in self.等级属性树.get_children():
                新值 = self.活跃编辑框.get()
                try:
                    # 获取当前所有值
                    当前值 = list(self.等级属性树.item(项, "values"))
                    当前值[列] = 新值
                    self.等级属性树.item(项, values=当前值)
                    # 立即保存当前等级的属性
                    self.保存当前等级()
                    self.状态变量.set("有未保存的更改 (按Ctrl+S保存)")
                except:
                    pass
            
            self.关闭活跃编辑框()
        
        # 绑定事件
        self.活跃编辑框.bind("<FocusOut>", 保存编辑)
        self.活跃编辑框.bind("<Return>", 保存编辑)
        self.活跃编辑框.bind("<Escape>", lambda e: self.关闭活跃编辑框())

    def 处理属性选择(self, 事件):
        """处理属性选择事件"""
        pass

    def 添加等级(self):
        """添加新等级（空数据）"""
        if not self.当前技能ID:
            messagebox.showinfo("提示", "请先选择一个技能")
            return
        
        最大等级 = self.技能列表[self.当前技能ID].get("最大等级", 1)
        
        # 生成新等级
        等级属性 = self.技能列表[self.当前技能ID].get("等级属性", {})
        现有等级 = [int(等级) for 等级 in 等级属性.keys() if 等级.isdigit()]
        
        if 现有等级:
            新等级 = max(现有等级) + 1
        else:
            新等级 = 1
        
        if 新等级 > 最大等级:
            if not messagebox.askyesno("提示", f"新等级 {新等级} 超过了最大等级 {最大等级}，是否继续？"):
                return
        
        新等级 = str(新等级)
        
        # 添加新等级（空数据）
        if "等级属性" not in self.技能列表[self.当前技能ID]:
            self.技能列表[self.当前技能ID]["等级属性"] = {}
        
        self.技能列表[self.当前技能ID]["等级属性"][新等级] = {}
        
        # 更新等级选择下拉框
        等级列表 = sorted(self.技能列表[self.当前技能ID]["等级属性"].keys(), key=int)
        self.等级选择下拉框['values'] = 等级列表
        self.等级选择变量.set(新等级)
        
        self.加载等级属性(新等级)
        self.状态变量.set("有未保存的更改 (按Ctrl+S保存)")
    
    def 复制等级(self):
        """复制当前等级数据到新等级"""
        if not self.当前技能ID:
            messagebox.showinfo("提示", "请先选择一个技能")
            return
        
        当前等级 = self.等级选择变量.get().strip()
        if not 当前等级:
            messagebox.showinfo("提示", "请先选择一个要复制的等级")
            return
        
        # 检查当前等级是否存在数据
        等级属性 = self.技能列表[self.当前技能ID].get("等级属性", {})
        if 当前等级 not in 等级属性:
            messagebox.showinfo("提示", f"等级 {当前等级} 没有可复制的数据")
            return
        
        最大等级 = self.技能列表[self.当前技能ID].get("最大等级", 1)
        
        # 生成新等级
        现有等级 = [int(等级) for 等级 in 等级属性.keys() if 等级.isdigit()]
        
        if 现有等级:
            新等级 = max(现有等级) + 1
        else:
            新等级 = 1
        
        if 新等级 > 最大等级:
            if not messagebox.askyesno("提示", f"新等级 {新等级} 超过了最大等级 {最大等级}，是否继续？"):
                return
        
        新等级 = str(新等级)
        
        # 复制当前等级的数据
        要复制的数据 = 等级属性[当前等级]
        
        # 添加新等级并复制数据
        if "等级属性" not in self.技能列表[self.当前技能ID]:
            self.技能列表[self.当前技能ID]["等级属性"] = {}
        
        # 深拷贝数据
        import copy
        self.技能列表[self.当前技能ID]["等级属性"][新等级] = copy.deepcopy(要复制的数据)
        
        # 更新等级选择下拉框
        等级列表 = sorted(self.技能列表[self.当前技能ID]["等级属性"].keys(), key=int)
        self.等级选择下拉框['values'] = 等级列表
        self.等级选择变量.set(新等级)
        
        # 加载新等级的数据
        self.加载等级属性(新等级)
        self.显示提示(f"已复制等级 {当前等级} 的数据到新等级 {新等级}")
        self.状态变量.set("有未保存的更改 (按Ctrl+S保存)")
    
    def 删除等级(self):
        """删除当前等级"""
        if not self.当前技能ID:
            messagebox.showinfo("提示", "请先选择一个技能")
            return
        
        等级 = self.等级选择变量.get().strip()
        if not 等级:
            messagebox.showinfo("提示", "请先选择一个等级")
            return
        
        if not messagebox.askyesno("确认删除", f"确定要删除等级 {等级} 吗？"):
            return
        
        if "等级属性" in self.技能列表[self.当前技能ID]:
            if 等级 in self.技能列表[self.当前技能ID]["等级属性"]:
                del self.技能列表[self.当前技能ID]["等级属性"][等级]
        
        # 更新等级选择下拉框
        等级列表 = sorted(self.技能列表[self.当前技能ID]["等级属性"].keys(), key=int)
        self.等级选择下拉框['values'] = 等级列表
        
        if 等级列表:
            # 自动选择最大等级
            最大等级 = str(max(int(等级) for 等级 in 等级列表))
            self.等级选择变量.set(最大等级)
            self.加载等级属性(最大等级)
        else:
            self.等级选择变量.set("")
            self.清空属性列表()
        
        self.状态变量.set("有未保存的更改 (按Ctrl+S保存)")

    def 添加等级_空(self):
        """添加新等级（空数据）- 重复方法保持兼容性"""
        if not self.当前技能ID:
            messagebox.showinfo("提示", "请先选择一个技能")
            return
        
        最大等级 = self.技能列表[self.当前技能ID].get("最大等级", 1)
        
        # 生成新等级
        等级属性 = self.技能列表[self.当前技能ID].get("等级属性", {})
        现有等级 = [int(等级) for 等级 in 等级属性.keys() if 等级.isdigit()]
        
        if 现有等级:
            新等级 = max(现有等级) + 1
        else:
            新等级 = 1
        
        if 新等级 > 最大等级:
            if not messagebox.askyesno("提示", f"新等级 {新等级} 超过了最大等级 {最大等级}，是否继续？"):
                return
        
        新等级 = str(新等级)
        
        # 添加新等级（空数据）
        if "等级属性" not in self.技能列表[self.当前技能ID]:
            self.技能列表[self.当前技能ID]["等级属性"] = {}
        
        self.技能列表[self.当前技能ID]["等级属性"][新等级] = {}
        
        # 更新等级选择下拉框
        等级列表 = sorted(self.技能列表[self.当前技能ID]["等级属性"].keys(), key=int)
        self.等级选择下拉框['values'] = 等级列表
        self.等级选择变量.set(新等级)
        
        self.加载等级属性(新等级)
        self.状态变量.set("有未保存的更改 (按Ctrl+S保存)")

    def 保存当前等级(self):
        """保存当前等级的属性（仅支持新的分离结构）"""
        if not self.当前技能ID:
            messagebox.showinfo("提示", "请先选择一个技能")
            return
        
        等级 = self.等级选择变量.get().strip()
        if not 等级:
            messagebox.showinfo("提示", "请先选择一个等级")
            return
        
        # 从Treeview收集属性数据
        属性加成 = {}
        升级需求 = {}
        道具需求 = {}
        
        for 项 in self.等级属性树.get_children():
            数值 = self.等级属性树.item(项, "values")
            if len(数值) >= 2:
                属性名 = 数值[0].strip()
                属性值 = 数值[1].strip()
                
                # 跳过分组标题
                if 属性名.startswith("=== ") and 属性名.endswith(" ==="):
                    continue
                
                # 处理道具需求
                if 属性名.startswith("道具需求_"):
                    try:
                        道具ID = 属性名.split("_")[1]
                        # 解析数量（从"道具名称 x数量"格式）
                        if " x" in 属性值:
                            数量 = float(属性值.split(" x")[1])
                            道具需求[道具ID] = 数量
                        else:
                            # 如果格式不对，尝试直接解析数字
                            数量 = float(属性值)
                            道具需求[道具ID] = 数量
                    except:
                        pass
                # 处理属性加成
                elif 属性名.startswith("加成_"):
                    真实属性名 = 属性名[3:]  # 去掉"加成_"前缀
                    try:
                        属性加成[真实属性名] = float(属性值)
                    except ValueError:
                        属性加成[真实属性名] = 属性值
                # 处理升级需求
                elif 属性名.startswith("需求_"):
                    真实属性名 = 属性名[3:]  # 去掉"需求_"前缀
                    try:
                        升级需求[真实属性名] = float(属性值)
                    except ValueError:
                        升级需求[真实属性名] = 属性值
        
        # 构建新的分离结构
        等级属性 = {}
        
        # 属性加成部分
        if 属性加成:
            等级属性["属性加成"] = 属性加成
        
        # 升级需求部分
        if 升级需求 or 道具需求:
            需求数据 = {}
            需求数据.update(升级需求)
            if 道具需求:
                需求数据["道具需求"] = 道具需求
            等级属性["升级需求"] = 需求数据
        
        # 保存到技能数据
        if "等级属性" not in self.技能列表[self.当前技能ID]:
            self.技能列表[self.当前技能ID]["等级属性"] = {}
        
        self.技能列表[self.当前技能ID]["等级属性"][等级] = 等级属性
        
        self.显示提示(f"已保存等级 {等级} 的属性", 显示弹窗=False)

    def 关闭活跃编辑框(self):
        """关闭当前活跃的编辑框"""
        if self.活跃编辑框:
            try:
                self.活跃编辑框.destroy()
            except:
                pass
            self.活跃编辑框 = None

    def 保存效果类型历史(self):
        """保存效果类型历史"""
        try:
            with open(self.效果历史文件, 'w', encoding='utf-8') as f:
                json.dump({
                    "effect_types": self.效果类型历史
                }, f, ensure_ascii=False, indent=2)
            self.显示提示("效果类型历史已更新", 显示弹窗=False)
        except Exception as e:
            messagebox.showerror("保存错误", f"无法保存效果历史数据：{str(e)}")
    
    def 从历史添加属性(self):
        """从历史类型中选择添加属性"""
        if not self.效果类型历史:
            messagebox.showinfo("提示", "暂无历史属性类型")
            return
        
        # 确保有分组标题
        self.确保分组标题("属性加成")
        
        # 创建选择对话框
        选择窗口 = tk.Toplevel(self.主窗口)
        选择窗口.title("选择属性类型")
        选择窗口.geometry("300x400")
        选择窗口.transient(self.主窗口)
        选择窗口.grab_set()
        
        # 居中显示
        选择窗口.update_idletasks()
        宽度 = 选择窗口.winfo_width()
        高度 = 选择窗口.winfo_height()
        x = (self.主窗口.winfo_width() // 2) - (宽度 // 2) + self.主窗口.winfo_x()
        y = (self.主窗口.winfo_height() // 2) - (高度 // 2) + self.主窗口.winfo_y()
        选择窗口.geometry('{}x{}+{}+{}'.format(宽度, 高度, x, y))
        
        # 删除按钮函数
        def 删除选中历史():
            选中项 = 列表框.curselection()
            if not 选中项:
                messagebox.showinfo("提示", "请先选择要删除的属性类型")
                return
            
            类型名称 = 列表框.get(选中项[0])
            if messagebox.askyesno("确认删除", f"确定要删除历史属性类型 '{类型名称}' 吗？"):
                self.效果类型历史.remove(类型名称)
                self.保存效果类型历史()
                # 重新加载列表
                列表框.delete(0, tk.END)
                for 类型 in self.效果类型历史:
                    列表框.insert(tk.END, 类型)
                self.显示提示(f"已删除历史属性类型: {类型名称}", 显示弹窗=False)
        
        # 提示标签
        提示标签 = ttk.Label(选择窗口, text="双击可删除选中的属性类型", font=("微软雅黑", 9))
        提示标签.pack(pady=(0, 2))
        
        # 列表框
        列表框 = tk.Listbox(选择窗口, selectmode=tk.SINGLE)
        列表框.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # 添加历史类型
        for 类型 in self.效果类型历史:
            列表框.insert(tk.END, 类型)
        
        # 滚动条
        滚动条 = ttk.Scrollbar(选择窗口, orient=tk.VERTICAL, command=列表框.yview)
        滚动条.pack(side=tk.RIGHT, fill=tk.Y)
        列表框.config(yscrollcommand=滚动条.set)
        
        def 确认选择():
            选中项 = 列表框.curselection()
            if 选中项:
                类型名称 = 列表框.get(选中项[0])
                # 默认添加为属性加成，插入到属性加成分组的末尾
                
                # 找到属性加成分组的位置，在分组标题后插入
                标题文本 = "=== 属性加成 ==="
                插入位置 = 0
                
                for i, 项 in enumerate(self.等级属性树.get_children()):
                    数值 = self.等级属性树.item(项, "values")
                    if len(数值) >= 1 and 数值[0] == 标题文本:
                        插入位置 = i + 1
                    elif len(数值) >= 1 and 数值[0].startswith("加成_"):
                        插入位置 = i + 1
                    elif len(数值) >= 1 and 数值[0].startswith("=== 升级需求"):
                        # 如果遇到升级需求分组，就在这里插入
                        插入位置 = i
                        break
                
                # 添加新的属性加成
                self.等级属性树.insert("", 插入位置, values=(f"加成_{类型名称}", "1.0"))
                # 立即保存当前等级的属性
                self.保存当前等级()
                self.显示提示(f"已添加属性加成: {类型名称}", 显示弹窗=False)
            选择窗口.destroy()
        
        # 底部按钮框架
        底部框架 = ttk.Frame(选择窗口)
        底部框架.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(底部框架, text="确认添加", command=确认选择).pack(side=tk.LEFT, padx=5)
        ttk.Button(底部框架, text="删除选中", command=删除选中历史).pack(side=tk.LEFT, padx=5)
        ttk.Button(底部框架, text="取消", command=选择窗口.destroy).pack(side=tk.RIGHT, padx=5)
        
        # 双击删除功能
        def 双击删除(事件):
            选中项 = 列表框.curselection()
            if 选中项:
                删除选中历史()
        
        # 右键菜单删除功能
        def 显示右键菜单(事件):
            选中项 = 列表框.curselection()
            if 选中项:
                # 选中点击的项目
                列表框.selection_set(列表框.nearest(事件.y))
                菜单 = tk.Menu(选择窗口, tearoff=0)
                菜单.add_command(label="删除此属性类型", command=删除选中历史)
                菜单.post(事件.x_root, 事件.y_root)
        
        列表框.bind("<Double-1>", 双击删除)
        列表框.bind("<Button-3>", 显示右键菜单)
    
    def 添加属性加成(self):
        """添加属性加成"""
        # 确保有分组标题
        self.确保分组标题("属性加成")
        
        # 找到属性加成分组的位置，在分组标题后插入
        标题文本 = "=== 属性加成 ==="
        插入位置 = 0
        
        for i, 项 in enumerate(self.等级属性树.get_children()):
            数值 = self.等级属性树.item(项, "values")
            if len(数值) >= 1 and 数值[0] == 标题文本:
                插入位置 = i + 1
                break
            elif len(数值) >= 1 and 数值[0].startswith("加成_"):
                插入位置 = i + 1
        
        # 添加新的属性加成
        self.等级属性树.insert("", 插入位置, values=("加成_属性名", "1.0"))
        # 立即保存当前等级的属性
        self.保存当前等级()
        self.状态变量.set("有未保存的更改 (按Ctrl+S保存)")
    
    def 添加升级需求(self):
        """添加升级需求"""
        # 确保有分组标题
        self.确保分组标题("升级需求")
        
        # 找到升级需求分组的位置，在分组标题后插入
        标题文本 = "=== 升级需求 ==="
        插入位置 = 0
        
        for i, 项 in enumerate(self.等级属性树.get_children()):
            数值 = self.等级属性树.item(项, "values")
            if len(数值) >= 1 and 数值[0] == 标题文本:
                插入位置 = i + 1
                break
            elif len(数值) >= 1 and 数值[0].startswith("需求_"):
                插入位置 = i + 1
            elif len(数值) >= 1 and 数值[0].startswith("道具需求_"):
                插入位置 = i + 1
        
        # 添加新的升级需求
        self.等级属性树.insert("", 插入位置, values=("需求_属性名", "1.0"))
        # 立即保存当前等级的属性
        self.保存当前等级()
        self.状态变量.set("有未保存的更改 (按Ctrl+S保存)")
    
    def 确保分组标题(self, 分组名):
        """确保指定的分组标题存在"""
        标题文本 = f"=== {分组名} ==="
        
        # 检查是否已存在该分组标题
        for 项 in self.等级属性树.get_children():
            数值 = self.等级属性树.item(项, "values")
            if len(数值) >= 1 and 数值[0] == 标题文本:
                return  # 已存在，不需要添加
        
        # 不存在，添加分组标题
        if 分组名 == "属性加成":
            # 属性加成分组放在最前面
            self.等级属性树.insert("", 0, values=(标题文本, ""))
        else:
            # 升级需求分组放在属性加成后面，其他内容前面
            插入位置 = 0
            找到属性加成 = False
            
            for i, 项 in enumerate(self.等级属性树.get_children()):
                数值 = self.等级属性树.item(项, "values")
                if len(数值) >= 1:
                    if "属性加成" in 数值[0]:
                        找到属性加成 = True
                    elif 找到属性加成 and ("升级需求" in 数值[0] or 数值[0].startswith("加成_")):
                        插入位置 = i + 1
                    elif 找到属性加成 and not ("升级需求" in 数值[0] or 数值[0].startswith("加成_")):
                        插入位置 = i
                        break
            
            self.等级属性树.insert("", 插入位置, values=(标题文本, ""))
    
    def 处理关闭(self):
        """窗口关闭时保存数据"""
        self.保存数据()
        self.主窗口.destroy()

if __name__ == "__main__":
    if 支持拖放:
        主窗口 = Tk()
    else:
        主窗口 = tk.Tk()
    
    # 设置中文字体支持
    主窗口.option_add("*Font", "SimHei 10")
    
    应用 = 技能等级编辑器(主窗口)
    主窗口.mainloop()