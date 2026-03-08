# cython: language_level=3
# cython: c_string_encoding=utf-8
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
import os
import sys
from pathlib import Path
import re

# 尝试导入拖放库（备用）
支持拖放 = False
try:
    from tkinterdnd2 import Tk, DND_FILES
    支持拖放 = True
except ImportError:
    try:
        from tkinterdnd2.tkinterdnd2 import Tk, DND_FILES
        支持拖放 = True
    except ImportError:
        支持拖放 = False


class NPC技能列表编辑器:
    def __init__(self, 主窗口):
        self.主窗口 = 主窗口
        self.主窗口.title("Godot NPC技能列表编辑器 ver1.2（优化版）")
        self.主窗口.geometry("900x800")
        self.主窗口.minsize(900, 600)
        
        # 状态与路径变量
        self.状态变量 = tk.StringVar(value="就绪 (按Ctrl+S保存)")
        self.计算项目路径()
        
        # 数据存储核心
        self.NPC技能数据 = {}  # {NPCID: [{技能: 技能ID, 几率: 0.5, ...动态属性...}, ...]}
        self.NPC列表 = {}       # {NPCID: NPC名称}
        self.技能列表 = {}      # {技能ID: 技能名称}
        self.当前NPCID = None   # 当前选中的NPC ID
        self.当前技能项 = None  # 当前选中的技能项索引
        self.活跃编辑框 = None # 跟踪动态属性的编辑框
        self.剪贴板 = None     # 用于复制粘贴属性
        
        # 配置文件路径
        self.NPC技能文件 = os.path.join(self.系统文件夹, "npcskillsystem.json")
        self.NPC数据文件 = os.path.join(self.系统文件夹, "npcsystem.json")
        self.技能数据文件 = os.path.join(self.系统文件夹, "skillsystem.json")
        
        # 配置选项
        self.显示成功弹窗 = True
        
        # 初始化流程
        self.加载依赖数据()
        self.初始化_NPC技能文件()
        self.加载_NPC技能数据()
        
        # 创建界面
        self.创建界面组件()
        
        # 绑定快捷键
        self.设置快捷键()
    
    def 计算项目路径(self):
        """计算系统文件夹路径"""
        try:
            if getattr(sys, 'frozen', False):
                当前路径 = os.path.dirname(sys.executable)
            else:
                当前路径 = os.path.dirname(os.path.abspath(__file__))
            
            项目根目录 = os.path.abspath(os.path.join(当前路径, "..", "..", "..", ".."))
            self.系统文件夹 = os.path.join(项目根目录, "系统")
            self.确保目录存在(self.系统文件夹)
            
            print(f"系统文件夹路径: {self.系统文件夹}")
        except Exception as e:
            messagebox.showerror("路径错误", f"路径计算失败：{str(e)}\n将使用当前目录下的'系统'文件夹")
            self.系统文件夹 = os.path.join(os.getcwd(), "系统")
            self.确保目录存在(self.系统文件夹)
    
    def 确保目录存在(self, 目录):
        """确保目录存在"""
        try:
            Path(目录).mkdir(parents=True, exist_ok=True)
            self.显示提示(f"目录就绪：{目录}", 显示弹窗=False)
            return True
        except Exception as e:
            messagebox.showerror("目录错误", f"创建目录 {目录} 失败：{str(e)}")
            return False
    
    def 显示提示(self, 消息, 成功=True, 显示弹窗=False):
        """显示提示信息"""
        self.状态变量.set(消息)
        if 显示弹窗 or (显示弹窗 is None and self.显示成功弹窗):
            if 成功:
                messagebox.showinfo("操作成功", 消息)
            else:
                messagebox.showwarning("提示", 消息)
    
    def 加载依赖数据(self):
        """加载NPC和技能数据"""
        # 加载NPC数据
        if os.path.exists(self.NPC数据文件):
            try:
                with open(self.NPC数据文件, 'r', encoding='utf-8') as f:
                    NPC原始数据 = json.load(f)
                self.NPC列表 = {
                    NPCID: 数据.get("名称", f"未命名NPC_{NPCID}") 
                    for NPCID, 数据 in NPC原始数据.items()
                }
                self.显示提示(f"加载NPC数据：共 {len(self.NPC列表)} 个NPC", 显示弹窗=False)
            except Exception as e:
                messagebox.showerror("加载失败", f"读取NPC数据文件错误：{str(e)}")
                self.NPC列表 = {}
        else:
            messagebox.showwarning("文件缺失", f"未找到NPC数据文件：{self.NPC数据文件}")
            self.NPC列表 = {}
        
        # 加载技能数据
        if os.path.exists(self.技能数据文件):
            try:
                with open(self.技能数据文件, 'r', encoding='utf-8') as f:
                    技能原始数据 = json.load(f)
                self.技能列表 = {
                    技能ID: 数据.get("名称", f"未命名技能_{技能ID}") 
                    for 技能ID, 数据 in 技能原始数据.items()
                }
                self.显示提示(f"加载技能数据：共 {len(self.技能列表)} 个技能", 显示弹窗=False)
            except Exception as e:
                messagebox.showerror("加载失败", f"读取技能数据文件错误：{str(e)}")
                self.技能列表 = {}
        else:
            #messagebox.showwarning("文件缺失", f"未找到技能数据文件：{self.技能数据文件}")
            self.技能列表 = {}
    
    def 初始化_NPC技能文件(self):
        """初始化技能文件"""
        if not os.path.exists(self.NPC技能文件):
            默认技能数据 = {
                "1001": [  # 石头
                    {"技能": "2001", "几率": 1.0, "测试属性": 1.0},
                    {"技能": "2002", "几率": 0.3, "范围": 5.0}
                ],
                "1002": [  # 青蛇
                    {"技能": "2001", "几率": 0.8, "伤害倍率": 1.2},
                    {"技能": "2003", "几率": 0.5, "恢复量": 10.0}
                ]
            }
            
            有效默认数据 = {}
            for NPCID, 技能列表 in 默认技能数据.items():
                if NPCID in self.NPC列表:
                    有效技能 = [
                        技能项 for 技能项 in 技能列表 
                        if 技能项["技能"] in self.技能列表
                    ]
                    if 有效技能:
                        有效默认数据[NPCID] = 有效技能
            
            try:
                with open(self.NPC技能文件, 'w', encoding='utf-8') as f:
                    json.dump(有效默认数据, f, ensure_ascii=False, indent=2)
                self.显示提示(f"初始化NPC技能文件：{self.NPC技能文件}")
            except Exception as e:
                messagebox.showerror("初始化失败", f"创建NPC技能文件错误：{str(e)}")
    
    def 加载_NPC技能数据(self):
        """加载技能数据"""
        if os.path.exists(self.NPC技能文件):
            try:
                with open(self.NPC技能文件, 'r', encoding='utf-8') as f:
                    self.NPC技能数据 = json.load(f)
                # 数据校验
                for NPCID, 技能列表 in self.NPC技能数据.items():
                    有效技能列表 = []
                    for 技能项 in 技能列表:
                        if "技能" in 技能项 and 技能项["技能"]:
                            if "几率" not in 技能项:
                                技能项["几率"] = 1.0
                            有效技能列表.append(技能项)
                    self.NPC技能数据[NPCID] = 有效技能列表
                self.显示提示(f"加载NPC技能数据：共 {len(self.NPC技能数据)} 个NPC配置", 显示弹窗=False)
            except Exception as e:
                messagebox.showerror("加载失败", f"读取NPC技能文件错误：{str(e)}")
                self.NPC技能数据 = {}
        else:
            self.NPC技能数据 = {}
    
    def 保存_NPC技能数据(self):
        """保存所有数据（合并保存逻辑）"""
        try:
            # 自动保存当前编辑项
            if self.当前NPCID and self.当前技能项 is not None:
                self.保存当前技能项()
            
            with open(self.NPC技能文件, 'w', encoding='utf-8') as f:
                json.dump(self.NPC技能数据, f, ensure_ascii=False, indent=2)
            self.显示提示(f"已保存到：{os.path.basename(self.NPC技能文件)} (Ctrl+S)")
        except Exception as e:
            messagebox.showerror("保存失败", f"写入NPC技能文件错误：{str(e)}")
    
    def 设置快捷键(self):
        """设置快捷键"""
        # 保存快捷键
        self.主窗口.bind("<Control-s>", self.保存快捷键)
        self.主窗口.bind("<Control-S>", self.保存快捷键)
        
        # 复制粘贴快捷键
        self.属性编辑树.bind("<Control-c>", self.复制属性)
        self.属性编辑树.bind("<Control-C>", self.复制属性)
        self.属性编辑树.bind("<Control-v>", self.粘贴属性)
        self.属性编辑树.bind("<Control-V>", self.粘贴属性)
    
    def 保存快捷键(self, 事件=None):
        """保存快捷键处理"""
        self.保存_NPC技能数据()
        return "break"
    
    def 复制属性(self, 事件=None):
        """复制选中的属性"""
        选中项 = self.属性编辑树.selection()
        if not 选中项:
            return
        
        属性名, 属性值 = self.属性编辑树.item(选中项[0], "values")
        self.剪贴板 = (属性名, 属性值)
        self.状态变量.set(f"已复制属性: {属性名} = {属性值}")
    
    def 粘贴属性(self, 事件=None):
        """粘贴属性"""
        if not self.剪贴板 or not self.当前NPCID or self.当前技能项 is None:
            return
        
        属性名, 属性值 = self.剪贴板
        当前技能列表 = self.NPC技能数据.get(self.当前NPCID, [])
        技能项 = 当前技能列表[self.当前技能项]
        
        # 检查属性名是否重复
        if 属性名 in 技能项:
            self.显示提示(f"属性名“{属性名}”已存在，无法粘贴", 成功=False)
            return
        
        # 添加属性
        try:
            属性值 = float(属性值)
        except ValueError:
            pass  # 保留文本格式
        
        技能项[属性名] = 属性值
        self.属性编辑树.insert("", tk.END, values=(属性名, str(属性值)))
        self.状态变量.set(f"已粘贴属性: {属性名} = {属性值}")
        
        # 更新技能数据并刷新列表，保留选中状态
        当前技能列表[self.当前技能项] = 技能项
        self.NPC技能数据[self.当前NPCID] = 当前技能列表
        self.刷新技能列表并保留选中()
    
    def 创建界面组件(self):
        """创建界面组件"""
        self.主框架 = ttk.Frame(self.主窗口, padding="10")
        self.主框架.pack(fill=tk.BOTH, expand=True)
        
        # ---------------------- 左侧：NPC列表区域 ----------------------
        左侧框架 = ttk.Frame(self.主框架, width=220)
        左侧框架.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10), pady=(0, 5))
        
        # NPC列表框
        self.NPC列表框 = tk.Listbox(左侧框架, width=20, height=35, selectmode=tk.SINGLE)
        self.NPC列表框.pack(side=tk.TOP, fill=tk.X, pady=5)
        self.NPC列表框.bind('<<ListboxSelect>>', self.处理NPC选择)
        
        # 列表操作按钮
        NPC按钮框架 = ttk.Frame(左侧框架)
        NPC按钮框架.pack(fill=tk.X, pady=5)
        ttk.Button(NPC按钮框架, text="刷新NPC列表", command=self.刷新NPC列表).pack(fill=tk.X, pady=2)
        ttk.Button(NPC按钮框架, text="刷新技能列表", command=self.刷新技能列表).pack(fill=tk.X, pady=2)
        
        # 提示设置
        提示框架 = ttk.Frame(左侧框架)
        提示框架.pack(fill=tk.X, pady=5)
        self.弹窗变量 = tk.BooleanVar(value=self.显示成功弹窗)
        ttk.Checkbutton(
            提示框架, text="显示成功弹窗", variable=self.弹窗变量,
            command=lambda: setattr(self, '显示成功弹窗', self.弹窗变量.get())
        ).pack(anchor=tk.W)
        
        # ---------------------- 中间：技能列表+操作区域 ----------------------
        中间框架 = ttk.Frame(self.主框架)
        中间框架.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=(0, 5))
        
        # 技能列表Treeview
        self.技能列表树 = ttk.Treeview(
            中间框架, columns=("技能名称", "属性预览"), 
            show="headings", selectmode="browse", height=25
        )
        self.技能列表树.heading("技能名称", text="技能名称（ID）")
        self.技能列表树.heading("属性预览", text="属性预览（含几率）")
        self.技能列表树.column("技能名称", width=100, anchor=tk.W)
        self.技能列表树.column("属性预览", width=150, anchor=tk.W)
        
        # 技能列表滚动条
        技能滚动条 = ttk.Scrollbar(中间框架, orient=tk.VERTICAL, command=self.技能列表树.yview)
        技能滚动条.pack(side=tk.RIGHT, fill=tk.Y)
        self.技能列表树.config(yscrollcommand=技能滚动条.set)
        
        self.技能列表树.pack(side=tk.TOP, fill=tk.BOTH, expand=True, pady=5)
        self.技能列表树.bind('<<TreeviewSelect>>', self.处理技能项选择)
        
        # 技能操作按钮（移至列表下方）
        技能按钮框架 = ttk.Frame(中间框架)
        技能按钮框架.pack(fill=tk.X, pady=5)
        ttk.Button(技能按钮框架, text="添加技能到NPC", command=self.添加技能到NPC).pack(side=tk.LEFT, padx=5)
        ttk.Button(技能按钮框架, text="从NPC移除技能", command=self.从NPC移除技能).pack(side=tk.LEFT, padx=5)
        ttk.Button(技能按钮框架, text="保存配置 (Ctrl+S)", command=self.保存_NPC技能数据).pack(side=tk.RIGHT, padx=5)
        
        # ---------------------- 右侧：动态属性编辑区域 ----------------------
        右侧框架 = ttk.Frame(self.主框架, width=200)
        右侧框架.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0), pady=(0, 5))
        
        # 技能选择下拉框
        ttk.Label(右侧框架, text="选择技能：").pack(anchor=tk.W, pady=2)
        self.选中技能变量 = tk.StringVar()
        技能下拉框 = ttk.Combobox(
            右侧框架, textvariable=self.选中技能变量, 
            values=self.生成技能下拉选项(), state="readonly"
        )
        技能下拉框.pack(fill=tk.X, pady=2)
        
        # 动态属性编辑区域
        ttk.Label(右侧框架, text="动态属性（含几率）：").pack(anchor=tk.W, pady=5)
        self.属性编辑树 = ttk.Treeview(
            右侧框架, columns=("属性名", "属性值"), 
            show="headings", selectmode="browse", height=15
        )
        self.属性编辑树.heading("属性名", text="属性名（双击编辑）")
        self.属性编辑树.heading("属性值", text="属性值（双击编辑）")
        self.属性编辑树.column("属性名", width=120, anchor=tk.W)
        self.属性编辑树.column("属性值", width=150, anchor=tk.W)
        
        # 属性滚动条
        属性滚动条 = ttk.Scrollbar(右侧框架, orient=tk.VERTICAL, command=self.属性编辑树.yview)
        属性滚动条.pack(side=tk.RIGHT, fill=tk.Y)
        self.属性编辑树.config(yscrollcommand=属性滚动条.set)
        
        self.属性编辑树.pack(fill=tk.X, pady=5)
        self.属性编辑树.bind("<Double-1>", self.处理属性双击编辑)  # 双击编辑属性名/值
        
        # 动态属性操作按钮
        属性按钮框架 = ttk.Frame(右侧框架)
        属性按钮框架.pack(fill=tk.X, pady=5)
        ttk.Button(属性按钮框架, text="添加新属性", command=self.添加动态属性).pack(side=tk.LEFT, padx=2)
        ttk.Button(属性按钮框架, text="删除选中属性", command=self.删除动态属性).pack(side=tk.LEFT, padx=2)
        ttk.Button(属性按钮框架, text="复制(Ctrl+C)", command=self.复制属性).pack(side=tk.RIGHT, padx=2)
        ttk.Button(属性按钮框架, text="粘贴(Ctrl+V)", command=self.粘贴属性).pack(side=tk.RIGHT, padx=2)
        
        # ---------------------- 状态栏 ----------------------
        状态栏 = ttk.Label(self.主窗口, textvariable=self.状态变量, relief=tk.SUNKEN, anchor=tk.W)
        状态栏.pack(side=tk.BOTTOM, fill=tk.X)
        
        # 初始化列表显示
        self.刷新NPC列表()
    
    def 生成技能下拉选项(self):
        """生成技能下拉选项"""
        return [f"{名称} (ID: {ID})" for ID, 名称 in self.技能列表.items()] if self.技能列表 else ["无可用技能"]
    
    def 刷新NPC列表(self):
        """刷新NPC列表"""
        self.NPC列表框.delete(0, tk.END)
        for NPCID in sorted(self.NPC列表.keys(), key=lambda x: int(x) if x.isdigit() else x):
            self.NPC列表框.insert(tk.END, f"{self.NPC列表[NPCID]} (ID: {NPCID})")
        self.显示提示(f"NPC列表已刷新：共 {len(self.NPC列表)} 个NPC", 显示弹窗=False)
    
    def 刷新技能列表(self):
        """刷新技能列表（不保留选中状态的基础方法）"""
        if not self.当前NPCID:
            return
        
        self.技能列表树.delete(*self.技能列表树.get_children())
        当前技能列表 = self.NPC技能数据.get(self.当前NPCID, [])
        
        for 索引, 技能项 in enumerate(当前技能列表):
            技能ID = 技能项["技能"]
            技能名称 = self.技能列表.get(技能ID, f"未知技能_{技能ID}")
            
            # 生成属性预览文本（包含几率）
            属性预览 = []
            for 属性名, 属性值 in 技能项.items():
                if 属性名 != "技能":  # 排除技能ID
                    属性预览.append(f"{属性名}: {属性值}")
            
            self.技能列表树.insert(
                "", tk.END, values=(f"{技能名称} (ID: {技能ID})", ", ".join(属性预览)),
                tags=(str(索引),)
            )
        
        # 清空右侧编辑面板
        self.清空编辑面板()
        self.显示提示(f"已加载NPC【{self.NPC列表.get(self.当前NPCID, '未知NPC')}】的技能列表", 显示弹窗=False)
    
    def 刷新技能列表并保留选中(self):
        """刷新技能列表，同时保留当前选中的技能项状态"""
        if not self.当前NPCID:
            return
        
        # 1. 记录当前选中状态
        选中项 = self.技能列表树.selection()
        原选中索引 = None
        if 选中项:
            原选中索引 = self.技能列表树.item(选中项[0], "tags")[0]  # 获取原技能项索引
        
        # 2. 清空并重新加载技能列表树
        self.技能列表树.delete(*self.技能列表树.get_children())
        当前技能列表 = self.NPC技能数据.get(self.当前NPCID, [])
        
        for 索引, 技能项 in enumerate(当前技能列表):
            技能ID = 技能项["技能"]
            技能名称 = self.技能列表.get(技能ID, f"未知技能_{技能ID}")
            
            # 生成属性预览文本（包含几率）
            属性预览 = []
            for 属性名, 属性值 in 技能项.items():
                if 属性名 != "技能":  # 排除技能ID
                    属性预览.append(f"{属性名}: {属性值}")
            
            self.技能列表树.insert(
                "", tk.END, values=(f"{技能名称} (ID: {技能ID})", ", ".join(属性预览)),
                tags=(str(索引),)
            )
        
        # 3. 恢复选中状态
        if 原选中索引 is not None and 原选中索引.isdigit():
            原选中索引 = int(原选中索引)
            # 遍历查找对应索引的项并选中
            for 项 in self.技能列表树.get_children():
                项索引 = self.技能列表树.item(项, "tags")[0]
                if int(项索引) == 原选中索引:
                    self.技能列表树.selection_set(项)
                    self.技能列表树.see(项)  # 滚动到可见位置
                    break
    
    def 清空编辑面板(self):
        """清空编辑面板"""
        self.选中技能变量.set("")
        self.属性编辑树.delete(*self.属性编辑树.get_children())
        self.当前技能项 = None
        self.关闭活跃编辑框()
    
    def 关闭活跃编辑框(self):
        """关闭活跃的编辑框"""
        if self.活跃编辑框:
            try:
                self.活跃编辑框.destroy()
            except Exception:
                pass
            self.活跃编辑框 = None
    
    def 处理NPC选择(self, 事件=None):
        """处理NPC选择"""
        选中索引 = self.NPC列表框.curselection()
        if not 选中索引:
            return
        
        选中文本 = self.NPC列表框.get(选中索引[0])
        匹配 = re.search(r'ID: (\d+)', 选中文本)
        if 匹配:
            self.当前NPCID = 匹配.group(1)
            self.刷新技能列表()
        else:
            self.当前NPCID = None
            self.显示提示("未识别的NPC ID格式", 成功=False)
    
    def 处理技能项选择(self, 事件=None):
        """处理技能项选择"""
        选中项 = self.技能列表树.selection()
        if not 选中项 or not self.当前NPCID:
            return
        
        技能项索引 = self.技能列表树.item(选中项[0], "tags")[0]
        self.当前技能项 = int(技能项索引)
        
        当前技能列表 = self.NPC技能数据.get(self.当前NPCID, [])
        if self.当前技能项 >= len(当前技能列表):
            self.清空编辑面板()
            self.显示提示("技能项数据不存在", 成功=False)
            return
        
        技能项 = 当前技能列表[self.当前技能项]
        技能ID = 技能项["技能"]
        
        # 填充技能选择框
        技能显示文本 = f"{self.技能列表.get(技能ID, '未知技能')} (ID: {技能ID})"
        self.选中技能变量.set(技能显示文本)
        
        # 填充动态属性（包含几率）
        self.属性编辑树.delete(*self.属性编辑树.get_children())
        for 属性名, 属性值 in 技能项.items():
            if 属性名 != "技能":  # 排除技能ID，其他属性（包括几率）都显示
                self.属性编辑树.insert("", tk.END, values=(属性名, str(属性值)))
    
    def 添加技能到NPC(self):
        """添加技能到NPC"""
        if not self.当前NPCID:
            messagebox.showwarning("选择NPC", "请先从左侧选择一个NPC")
            return
        
        if not self.技能列表:
            messagebox.showwarning("无技能数据", "未加载到任何技能数据")
            return
        
        选中技能文本 = self.选中技能变量.get()
        if not 选中技能文本:
            messagebox.showwarning("选择技能", "请从下拉框选择一个技能")
            return
        
        # 提取技能ID
        匹配 = re.search(r'ID: (\d+)', 选中技能文本)
        if not 匹配:
            messagebox.showwarning("技能格式错误", "无法识别选中的技能ID")
            return
        技能ID = 匹配.group(1)
        
        # 创建新技能项（默认包含几率属性）
        新技能项 = {"技能": 技能ID, "几率": 1.0}
        
        # 添加到当前NPC的技能列表
        if self.当前NPCID not in self.NPC技能数据:
            self.NPC技能数据[self.当前NPCID] = []
        self.NPC技能数据[self.当前NPCID].append(新技能项)
        
        # 刷新技能列表
        self.刷新技能列表()
        self.显示提示(f"已添加技能【{self.技能列表.get(技能ID)}】到NPC【{self.NPC列表.get(self.当前NPCID)}】",)
    
    def 从NPC移除技能(self):
        """从NPC移除技能"""
        if not self.当前NPCID:
            messagebox.showwarning("选择NPC", "请先从左侧选择一个NPC")
            return
        
        选中项 = self.技能列表树.selection()
        if not 选中项:
            messagebox.showwarning("选择技能", "请从中间列表选择要移除的技能")
            return
        
        if not messagebox.askyesno("确认移除", "确定要从当前NPC移除该技能吗？"):
            return
        
        技能项索引 = int(self.技能列表树.item(选中项[0], "tags")[0])
        当前技能列表 = self.NPC技能数据.get(self.当前NPCID, [])
        if 技能项索引 < len(当前技能列表):
            被删技能ID = 当前技能列表[技能项索引]["技能"]
            被删技能名称 = self.技能列表.get(被删技能ID, f"未知技能_{被删技能ID}")
            del 当前技能列表[技能项索引]
            self.NPC技能数据[self.当前NPCID] = 当前技能列表
            
            self.刷新技能列表()
            self.显示提示(f"已从NPC【{self.NPC列表.get(self.当前NPCID)}】移除技能【{被删技能名称}】")
    
    def 添加动态属性(self):
        """添加动态属性（默认值1.0）"""
        if not self.当前NPCID or self.当前技能项 is None:
            messagebox.showwarning("选择技能项", "请先选中一个NPC的技能项")
            return
        
        # 获取属性名
        属性名 = simpledialog.askstring("添加动态属性", "请输入新属性的名称（不可重复）：")
        if not 属性名 or 属性名.strip() == "":
            return
        属性名 = 属性名.strip()
        
        # 检查属性名是否重复
        当前技能列表 = self.NPC技能数据.get(self.当前NPCID, [])
        技能项 = 当前技能列表[self.当前技能项]
        if 属性名 in 技能项.keys() or 属性名 == "技能":
            messagebox.showwarning("属性重复", f"属性名“{属性名}”已存在或为系统保留名")
            return
        
        # 默认值1.0
        属性值 = 1.0
        
        # 更新技能项数据
        技能项[属性名] = 属性值
        当前技能列表[self.当前技能项] = 技能项
        self.NPC技能数据[self.当前NPCID] = 当前技能列表
        
        # 刷新技能列表并保留选中
        self.刷新技能列表并保留选中()
        self.显示提示(f"已添加动态属性：{属性名} = {属性值}", 显示弹窗=False)
    
    def 删除动态属性(self):
        """删除动态属性"""
        if not self.当前NPCID or self.当前技能项 is None:
            messagebox.showwarning("选择技能项", "请先选中一个NPC的技能项")
            return
        
        选中属性项 = self.属性编辑树.selection()
        if not 选中属性项:
            messagebox.showwarning("选择属性", "请从属性列表中选择要删除的属性")
            return
        
        属性名 = self.属性编辑树.item(选中属性项[0], "values")[0]
        
        if not messagebox.askyesno("确认删除", f"确定要删除属性“{属性名}”吗？"):
            return
        
        # 从技能项中删除属性
        当前技能列表 = self.NPC技能数据.get(self.当前NPCID, [])
        技能项 = 当前技能列表[self.当前技能项]
        if 属性名 in 技能项 and 属性名 != "技能":
            del 技能项[属性名]
            当前技能列表[self.当前技能项] = 技能项
            self.NPC技能数据[self.当前NPCID] = 当前技能列表
            
            self.属性编辑树.delete(选中属性项[0])
            # 刷新技能列表并保留选中
            self.刷新技能列表并保留选中()
            self.显示提示(f"已删除动态属性：{属性名}", 显示弹窗=False)
    
    def 处理属性双击编辑(self, 事件):
        """双击编辑属性名或值"""
        if not self.当前NPCID or self.当前技能项 is None:
            return
        
        self.关闭活跃编辑框()
        
        区域 = self.属性编辑树.identify_region(事件.x, 事件.y)
        if 区域 != "cell":
            return
        
        列 = self.属性编辑树.identify_column(事件.x)
        选中项 = self.属性编辑树.identify_row(事件.y)
        if not 选中项:
            return
        
        # 获取当前属性
        属性名, 属性值文本 = self.属性编辑树.item(选中项, "values")
        x, y, 宽度, 高度 = self.属性编辑树.bbox(选中项, 列)
        
        # 创建编辑框
        self.活跃编辑框 = ttk.Entry(self.属性编辑树)
        self.活跃编辑框.place(x=x, y=y, width=宽度, height=高度)
        
        # 根据列设置初始值
        if 列 == "#1":  # 属性名列
            self.活跃编辑框.insert(0, 属性名)
            编辑类型 = "名称"
        else:  # 属性值列
            self.活跃编辑框.insert(0, 属性值文本)
            编辑类型 = "值"
        
        self.活跃编辑框.focus()
        
        # 保存编辑结果
        def 保存编辑结果(事件=None):
            新值 = self.活跃编辑框.get().strip()
            if not 新值:
                self.关闭活跃编辑框()
                return
            
            当前技能列表 = self.NPC技能数据.get(self.当前NPCID, [])
            技能项 = 当前技能列表[self.当前技能项]
            
            if 编辑类型 == "名称":
                # 处理属性名修改
                if 新值 in 技能项 and 新值 != 属性名:
                    self.显示提示(f"属性名“{新值}”已存在", 成功=False)
                    return
                
                # 保存旧值并修改属性名
                属性值 = 技能项[属性名]
                del 技能项[属性名]
                技能项[新值] = 属性值
                self.属性编辑树.item(选中项, values=(新值, str(属性值)))
                self.状态变量.set(f"已修改属性名：{属性名} → {新值}")
            else:
                # 处理属性值修改
                try:
                    新属性值 = float(新值)
                except ValueError:
                    新属性值 = 新值  # 文本格式
                
                技能项[属性名] = 新属性值
                self.属性编辑树.item(选中项, values=(属性名, str(新属性值)))
                self.状态变量.set(f"已更新属性值：{属性名} = {新属性值}")
            
            # 更新数据
            当前技能列表[self.当前技能项] = 技能项
            self.NPC技能数据[self.当前NPCID] = 当前技能列表
            
            # 刷新技能列表并保留选中状态
            self.刷新技能列表并保留选中()
            self.关闭活跃编辑框()
        
        # 绑定事件
        self.活跃编辑框.bind("<FocusOut>", 保存编辑结果)
        self.活跃编辑框.bind("<Return>", 保存编辑结果)
        self.活跃编辑框.bind("<Escape>", lambda e: self.关闭活跃编辑框())
    
    def 保存当前技能项(self):
        """保存当前技能项（内部使用，不显示按钮）"""
        if not self.当前NPCID or self.当前技能项 is None:
            return
        
        当前技能列表 = self.NPC技能数据.get(self.当前NPCID, [])
        if self.当前技能项 >= len(当前技能列表):
            return
        
        技能项 = 当前技能列表[self.当前技能项]
        
        # 更新技能选择
        选中技能文本 = self.选中技能变量.get()
        匹配 = re.search(r'ID: (\d+)', 选中技能文本)
        if 匹配:
            新技能ID = 匹配.group(1)
            技能项["技能"] = 新技能ID
        
        # 更新动态属性
        新属性字典 = {"技能": 技能项["技能"]}
        for 项 in self.属性编辑树.get_children():
            属性名, 属性值文本 = self.属性编辑树.item(项, "values")
            if 属性名 and 属性名 != "技能":
                try:
                    属性值 = float(属性值文本)
                except ValueError:
                    属性值 = 属性值文本
                新属性字典[属性名] = 属性值
        
        # 替换技能项数据
        当前技能列表[self.当前技能项] = 新属性字典
        self.NPC技能数据[self.当前NPCID] = 当前技能列表
    
    def 处理关闭(self):
        """关闭窗口时保存数据"""
        self.保存_NPC技能数据()
        self.主窗口.destroy()


if __name__ == "__main__":
    # 初始化主窗口
    if 支持拖放:
        根窗口 = Tk()
    else:
        根窗口 = tk.Tk()
    
    应用 = NPC技能列表编辑器(根窗口)
    根窗口.protocol("WM_DELETE_WINDOW", 应用.处理关闭)
    根窗口.mainloop()
    