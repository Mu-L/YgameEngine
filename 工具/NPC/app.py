# cython: language_level=3
# cython: c_string_encoding=utf-8
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import json
import os
import sys
from PIL import Image, ImageTk
import uuid
import shutil
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

class NPC编辑器:
    def __init__(self, 主窗口):
        self.主窗口 = 主窗口
        self.主窗口.title("Godot NPC编辑器 ver1.4 (支持按顺序粘贴)")
        self.主窗口.geometry("1000x700")
        self.主窗口.minsize(800, 600)
        
        # 初始化状态变量
        self.状态变量 = tk.StringVar(value="就绪 (按Ctrl+S保存, Ctrl+C/V复制粘贴NPC)")
        # 计算路径
        self.计算项目路径()
        # 数据存储
        self.NPC列表 = {}
        self.当前NPCID = None
        self.已复制属性 = []  # 用于存储复制的属性
        self.活跃编辑框 = None  # 跟踪当前活跃的编辑框
        self.已复制NPC列表 = []  # 用于存储复制的NPC数据列表（与道具编辑器保持一致）
        
        # 固定阵营选项
        self.阵营列表 = ["友方", "中立", "敌方"]
        # 种族列表（可扩展）
        self.种族列表 = ["矿石", "动物", "人族", "精灵", "机械"]
        # 属性类型历史列表
        self.属性类型历史 = []  # 存储历史属性类型，用于复用
        
        # 配置文件路径
        self.图片目录 = os.path.join(self.系统文件夹, "npc_icons")  # 存储NPC图标的目录
        self.系统文件 = os.path.join(self.系统文件夹, "npcsystem.json")
        self.类型文件 = os.path.join(self.系统文件夹, "npc_types.json")
        self.属性历史文件 = os.path.join(self.系统文件夹, "npc_att.json")  # 存储属性类型历史
        
        # 配置提示选项
        self.显示成功弹窗 = True  # 是否显示成功提示弹窗
        
        # 确保图片目录存在
        self.确保目录存在(self.图片目录)
        
        # 初始化并加载数据
        self.初始化默认文件()
        self.加载数据()
        self.加载类型数据()
        self.加载属性类型历史()
        
        # 创建UI
        self.创建界面组件()
        
        # 配置拖拽功能
        self.设置拖放功能()
        
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
            
            # 计算项目根目录（系统文件夹的父目录，即res://对应的根目录）
            self.项目根目录 = os.path.abspath(os.path.join(当前路径, "..", "..", "..", ".."))
            
            # 系统文件夹路径
            self.系统文件夹 = os.path.join(self.项目根目录, "系统")
            
            # 确保系统文件夹存在
            self.确保目录存在(self.系统文件夹)
            
            # 显示路径信息（调试用）
            print(f"当前执行路径: {当前路径}")
            print(f"项目根目录: {self.项目根目录}")  # Godot的res://对应此目录
            print(f"系统文件夹: {self.系统文件夹}")
            
        except Exception as e:
            messagebox.showerror("路径计算错误", f"无法计算项目路径: {str(e)}")
            # fallback到当前目录
            self.项目根目录 = os.getcwd()
            self.系统文件夹 = os.path.join(self.项目根目录, "系统")
            self.确保目录存在(self.系统文件夹)
    
    def 设置快捷键(self):
        """设置快捷键"""
        # 绑定Ctrl+S保存所有
        self.主窗口.bind("<Control-s>", self.保存数据快捷键)
        self.主窗口.bind("<Control-S>", self.保存数据快捷键)
        # 绑定到主框架
        self.主框架.bind("<Control-s>", self.保存数据快捷键)
        self.主框架.bind("<Control-S>", self.保存数据快捷键)
        
        # 绑定Ctrl+C复制NPC列表项
        self.NPC列表框.bind("<Control-c>", self.复制列表项)
        self.NPC列表框.bind("<Control-C>", self.复制列表项)
        
        # 绑定Ctrl+V粘贴NPC列表项
        self.NPC列表框.bind("<Control-v>", self.快捷键粘贴NPC)
        self.NPC列表框.bind("<Control-V>", self.快捷键粘贴NPC)
    
    def 保存数据快捷键(self, 事件=None):
        """快捷键触发的保存功能"""
        self.保存数据()
        return "break"
    
    # 复制列表项 - 修改为与道具编辑器一致的存储方式
    def 复制列表项(self, 事件=None):
        """复制选中的NPC列表项 (支持Ctrl+C快捷键)"""
        self.已复制NPC列表 = []  # 清空之前的复制内容
        选中索引 = self.NPC列表框.curselection()
        
        if not 选中索引:
            self.状态变量.set("未选择任何NPC进行复制")
            return "break"
            
        # 保存当前编辑的NPC
        self.保存当前NPC()
        
        # 收集选中的NPC数据（按选择顺序）
        for idx in 选中索引:
            选中文本 = self.NPC列表框.get(idx)
            匹配 = re.search(r'ID: (\d+)', 选中文本)
            if 匹配:
                NPCID = 匹配.group(1)
                if NPCID in self.NPC列表:
                    # 复制NPC数据但不包含ID
                    NPC数据 = self.NPC列表[NPCID].copy()
                    self.已复制NPC列表.append(NPC数据)
        
        if self.已复制NPC列表:
            self.显示提示(f"已复制 {len(self.已复制NPC列表)} 个NPC (Ctrl+C)", 显示弹窗=False)
        
        # 返回'break'防止事件继续传播
        return "break"
    
    # 粘贴列表项 - 修改为与道具编辑器逻辑一致
    def 快捷键粘贴NPC(self, event=None):
        """将复制的NPC信息按ID顺序粘贴到连续的目标NPC（与道具编辑器逻辑一致）"""
        # 检查是否有复制的NPC
        if not self.已复制NPC列表:
            messagebox.showinfo("提示", "没有可粘贴的NPC，请先复制NPC")
            return "break"
        
        复制数量 = len(self.已复制NPC列表)
        if 复制数量 == 0:
            messagebox.showinfo("提示", "没有可粘贴的NPC，请先复制NPC")
            return "break"
        
        # 获取选中的目标NPC
        选中索引 = self.NPC列表框.curselection()
        if not 选中索引:
            messagebox.showinfo("提示", "请先选择一个要开始粘贴的NPC")
            return "break"
        
        # 获取选中的第一个NPC ID作为起始点
        起始索引 = 选中索引[0]
        起始文本 = self.NPC列表框.get(起始索引)
        起始匹配 = re.search(r'ID: (\d+)', 起始文本)
        if not 起始匹配:
            messagebox.showinfo("提示", "选中的NPC无效")
            return "break"
        
        起始ID = 起始匹配.group(1)
        if 起始ID not in self.NPC列表:
            messagebox.showinfo("提示", "选中的NPC不存在")
            return "break"
        
        # 获取所有NPC ID并按数字排序
        所有NPCID = sorted([int(id) for id in self.NPC列表.keys()])
        起始位置 = 所有NPCID.index(int(起始ID))
        
        # 计算需要的目标NPC数量（与复制数量相同）
        需要的数量 = 复制数量
        目标NPCID列表 = []
        
        # 从起始位置开始按顺序选取足够的目标NPC
        for i in range(需要的数量):
            目标位置 = 起始位置 + i
            if 目标位置 < len(所有NPCID):
                目标NPCID列表.append(str(所有NPCID[目标位置]))
            else:
                # 如果超出范围，提示无法找到足够的目标NPC
                messagebox.showinfo(
                    "提示", 
                    f"只能找到 {i} 个可用目标NPC，无法完成 {需要的数量} 个NPC的粘贴"
                )
                return "break"
        
        # 执行粘贴操作 - 覆盖目标NPC数据
        for i, 目标ID in enumerate(目标NPCID列表):
            # 复制NPC数据并保留目标ID
            新NPC数据 = self.已复制NPC列表[i].copy()
            
            # 如果有图标，创建图标的副本并更新路径
            旧图标路径 = 新NPC数据.get("图标路径", "")
            if 旧图标路径:
                # 转换为绝对路径
                旧绝对路径 = os.path.join(self.项目根目录, 旧图标路径)
                if os.path.exists(旧绝对路径) and os.path.isfile(旧绝对路径):
                    try:
                        # 生成新文件名
                        扩展名 = os.path.splitext(旧绝对路径)[1].lower()
                        新文件名 = f"icon_{uuid.uuid4().hex}{扩展名}"
                        新绝对路径 = os.path.join(self.图片目录, 新文件名)
                        
                        # 复制文件
                        shutil.copy2(旧绝对路径, 新绝对路径)
                        
                        # 生成新的相对路径（项目根目录下）
                        新相对路径 = os.path.relpath(新绝对路径, self.项目根目录)
                        新NPC数据["图标路径"] = 新相对路径  # 存储相对路径
                        
                    except Exception as e:
                        messagebox.showwarning("警告", f"复制图片时出错：{str(e)}\n将使用原NPC的图片路径")
            
            # 覆盖目标NPC数据
            self.NPC列表[目标ID] = 新NPC数据
        
        # 更新界面
        self.更新NPC列表()
        # 重新加载起始NPC
        self.加载NPC(起始ID)
        
        # 选中所有粘贴后的NPC
        for 目标ID in 目标NPCID列表:
            for idx, NPC文本 in enumerate(self.NPC列表框.get(0, tk.END)):
                if f"ID: {目标ID}" in NPC文本:
                    self.NPC列表框.selection_set(idx)
                    break
        
        self.显示提示(f"已按ID顺序粘贴 {复制数量} 个NPC（从ID: {起始ID} 开始）")
        return "break"
    
    def 显示提示(self, 消息, 成功=True, 显示弹窗=False):
        """显示操作提示"""
        # 更新状态栏
        self.状态变量.set(消息)
        
        # 显示弹窗（如果需要）
        if 显示弹窗 or (显示弹窗 is None and self.显示成功弹窗):
            if 成功:
                messagebox.showinfo("操作成功", 消息)
            else:
                messagebox.showwarning("操作提示", 消息)
    
    def 确保目录存在(self, 目录):
        """确保目录存在，如果不存在则创建"""
        try:
            Path(目录).mkdir(parents=True, exist_ok=True)
            self.显示提示(f"目录已准备就绪: {目录}", 显示弹窗=False)
            return True
        except Exception as e:
            messagebox.showerror("目录错误", f"无法创建目录 {目录}：{str(e)}")
            return False
    
    def 初始化默认文件(self):
        """初始化默认的配置文件，所有数值使用浮点数，仅保留一个图标路径"""
        # 初始化npcsystem.json（删除源图片路径，仅保留图标路径）
        if not os.path.exists(self.系统文件):
            默认NPC = {
                "1001": {
                    "名称": "石头",
                    "种族": "矿石",
                    "等级": 1.0,  # 浮点数
                    "经验值": 1.0,  # 浮点数
                    "阵营": "敌方",
                    "描述": "普通的石头怪，行动缓慢但防御力高",
                    "图标路径": "",  # 仅保留：相对项目根目录的路径（如系统/npc_icons/xxx.png）
                    "属性列表": {
                        "生命值": 10.0  # 浮点数
                    }
                },
                "1002": {
                    "名称": "青蛇",
                    "种族": "动物",
                    "等级": 3.0,  # 浮点数
                    "经验值": 1.0,  # 浮点数
                    "阵营": "敌方",
                    "描述": "带有微弱毒性的蛇类，行动敏捷",
                    "图标路径": "",
                    "属性列表": {
                        "生命值": 5.0,  # 浮点数
                        "攻击力": 3.0   # 浮点数
                    }
                },
                "1003": {
                    "名称": "小雨",
                    "种族": "人族",
                    "等级": 1.0,  # 浮点数
                    "经验值": 1.0,  # 浮点数
                    "阵营": "中立",
                    "描述": "在村庄附近徘徊的小女孩",
                    "图标路径": "",
                    "属性列表": {}
                }
            }
            
            try:
                with open(self.系统文件, 'w', encoding='utf-8') as f:
                    json.dump(默认NPC, f, ensure_ascii=False, indent=2)
                self.显示提示(f"已创建默认NPC数据: {self.系统文件}")
            except Exception as e:
                messagebox.showerror("初始化错误", f"无法创建{self.系统文件}：{str(e)}")
        
        # 初始化npc_types.json
            if not os.path.exists(self.类型文件):
                默认类型 = {
                    "races": self.种族列表,  # 种族列表
                    "camps": self.阵营列表   # 阵营列表（固定）
                }
                
                try:
                    with open(self.类型文件, 'w', encoding='utf-8') as f:
                        json.dump(默认类型, f, ensure_ascii=False, indent=2)
                    self.显示提示(f"已创建默认类型数据: {self.类型文件}")
                except Exception as e:
                    messagebox.showerror("初始化错误", f"无法创建{self.类型文件}：{str(e)}")
            
            # 初始化npc_att.json（存储属性类型历史）
            if not os.path.exists(self.属性历史文件):
                默认属性历史 = {
                    "attribute_types": [
                        "生命值",
                        "攻击力"
                    ]
                }
                
                try:
                    with open(self.属性历史文件, 'w', encoding='utf-8') as f:
                        json.dump(默认属性历史, f, ensure_ascii=False, indent=2)
                    self.显示提示(f"已创建默认属性历史数据: {self.属性历史文件}")
                except Exception as e:
                    messagebox.showerror("初始化错误", f"无法创建{self.属性历史文件}：{str(e)}")
    
    def 设置拖放功能(self):
        """配置窗口接受图片拖拽"""
        if not 支持拖放:
            self.图标预览.config(text="请先安装tkinterdnd2以支持拖拽\n或点击下方按钮选择图片")
            return
            
        # 允许窗口接受拖拽
        self.主窗口.drop_target_register(DND_FILES)
        
        # 绑定拖拽相关事件
        self.主窗口.dnd_bind('<<Drop>>', self.处理拖放)
        self.主窗口.dnd_bind('<<DragEnter>>', self.处理拖拽进入)
        self.主窗口.dnd_bind('<<DragOver>>', self.处理拖拽经过)
    
    def 处理拖拽进入(self, 事件):
        """拖拽进入窗口时的处理"""
        if 事件.data:
            文件列表 = self.主窗口.tk.splitlist(事件.data)
            for 文件 in 文件列表:
                if self.是图片文件(文件):
                    return 事件.action
        return 'dnd_ignore'
    
    def 处理拖拽经过(self, 事件):
        """拖拽经过窗口时的处理"""
        return self.处理拖拽进入(事件)
    
    def 处理拖放(self, 事件):
        """处理放置的文件"""
        if not self.当前NPCID:
            messagebox.showinfo("提示", "请先选择一个NPC再设置图标")
            return
            
        文件列表 = self.主窗口.tk.splitlist(事件.data)
        for 文件 in 文件列表:
            if self.是图片文件(文件):
                self.处理图标(文件)
                break  # 只处理第一个图片文件
    
    def 是图片文件(self, 文件路径):
        """检查文件是否为图片"""
        图片扩展名 = ('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff')
        return 文件路径.lower().endswith(图片扩展名)
    
    def 加载数据(self):
        """加载NPC数据，兼容旧数据（自动转换源图片路径为相对路径）"""
        if os.path.exists(self.系统文件):
            try:
                with open(self.系统文件, 'r', encoding='utf-8') as f:
                    原始数据 = json.load(f)
                
                # 兼容旧数据：删除源图片路径，转换图标路径为相对路径
                self.NPC列表 = {}
                for NPCID, NPC数据 in 原始数据.items():
                    # 移除源图片路径字段（如果存在）
                    if "源图片路径" in NPC数据:
                        del NPC数据["源图片路径"]
                    
                    # 转换旧图标路径（res://开头）为相对路径
                    旧图标路径 = NPC数据.get("图标路径", "")
                    if 旧图标路径.startswith("res://"):
                        NPC数据["图标路径"] = 旧图标路径[6:]  # 去掉res://前缀
                    
                    self.NPC列表[NPCID] = NPC数据
                
                self.显示提示(f"已加载NPC数据: {len(self.NPC列表)}个NPC", 显示弹窗=False)
            except Exception as e:
                messagebox.showerror("加载错误", f"无法加载{self.系统文件}：{str(e)}")
                self.NPC列表 = {}
        else:
            self.保存数据()
    
    def 保存数据(self):
        """保存NPC数据到JSON文件（仅存储相对路径的图标路径）"""
        # 先保存前确保当前编辑的NPC数据已更新
        self.保存当前NPC()
        
        try:
            with open(self.系统文件, 'w', encoding='utf-8') as f:
                json.dump(self.NPC列表, f, ensure_ascii=False, indent=2)
            self.显示提示(f"已成功保存到 {self.系统文件} (Ctrl+S)")
        except Exception as e:
            messagebox.showerror("保存错误", f"无法保存{self.系统文件}：{str(e)}")
        self.刷新NPC列表()
    def 保存当前NPC(self):
        """保存当前正在编辑的NPC数据（仅存储一个图标路径）"""
        if not self.当前NPCID or self.当前NPCID not in self.NPC列表:
            return
        
        # 处理等级：尝试转换为浮点数，失败则保留文本并提示
        等级文本 = self.等级变量.get().strip()
        等级值 = 1.0  # 默认浮点数
        if 等级文本:
            try:
                等级值 = float(等级文本)  # 等级优先浮点数
            except ValueError:
                等级值 = 等级文本
                self.显示提示(f"等级 '{等级文本}' 不是有效数字，已按文本保存", 
                              成功=False, 显示弹窗=True)
        
        # 处理经验值：尝试转换为浮点数，失败则保留文本并提示
        经验值文本 = self.经验值变量.get().strip()
        经验值 = 1.0  # 默认浮点数
        if 经验值文本:
            try:
                经验值 = float(经验值文本)  # 经验值优先浮点数
            except ValueError:
                经验值 = 经验值文本
                self.显示提示(f"经验值 '{经验值文本}' 不是有效数字，已按文本保存", 
                              成功=False, 显示弹窗=True)
        
        # 收集表单数据（仅保留图标路径）
        self.NPC列表[self.当前NPCID] = {
            "名称": self.名称变量.get(),
            "种族": self.种族变量.get(),
            "等级": 等级值,  # 存储为浮点数
            "经验值": 经验值,  # 存储为浮点数
            "阵营": self.阵营变量.get(),
            "描述": self.描述文本框.get(1.0, tk.END).strip(),
            "图标路径": self.图标路径变量.get(),  # 仅存储：相对项目根目录的路径
            "属性列表": self.获取属性数据()  # 获取属性列表数据（浮点数优先）
        }
    
    def 获取属性数据(self):
        """从属性列表获取数据（优先转换为浮点数）"""
        属性 = {}
        for 项 in self.属性树.get_children():
            数值 = self.属性树.item(项, "values")
            if len(数值) >= 2 and 数值[0]:  # 确保证属性名不为空
                键 = 数值[0]
                值文本 = 数值[1].strip()
                
                # 尝试转换为浮点数，失败则保留文本
                try:
                    属性[键] = float(值文本)  # 所有属性值优先浮点数
                except ValueError:
                    属性[键] = 值文本  # 转换失败则保留文本
        return 属性
    
    def 加载类型数据(self):
        """加载种族和阵营数据"""
        if os.path.exists(self.类型文件):
            try:
                with open(self.类型文件, 'r', encoding='utf-8') as f:
                    数据 = json.load(f)
                    if "races" in 数据:
                        self.种族列表 = 数据["races"]
                    if "camps" in 数据:
                        self.阵营列表 = 数据["camps"]
                self.显示提示(f"已加载类型数据: {len(self.种族列表)}个种族", 显示弹窗=False)
            except Exception as e:
                messagebox.showerror("加载错误", f"无法加载类型数据：{str(e)}")
        else:
            self.保存类型数据()
    
    def 保存类型数据(self):
        """保存种族和阵营数据"""
        try:
            with open(self.类型文件, 'w', encoding='utf-8') as f:
                json.dump({
                    "races": self.种族列表,
                    "camps": self.阵营列表
                }, f, ensure_ascii=False, indent=2)
            self.显示提示("类型数据已更新")
        except Exception as e:
            messagebox.showerror("保存错误", f"无法保存类型数据：{str(e)}")
    
    def 加载属性类型历史(self):
        """加载历史属性类型，用于复用"""
        if os.path.exists(self.属性历史文件):
            try:
                with open(self.属性历史文件, 'r', encoding='utf-8') as f:
                    数据 = json.load(f)
                    if "attribute_types" in 数据:
                        self.属性类型历史 = 数据["attribute_types"]
                self.显示提示(f"已加载属性类型历史: {len(self.属性类型历史)}种", 显示弹窗=False)
            except Exception as e:
                messagebox.showerror("加载错误", f"无法加载属性历史数据：{str(e)}")
                self.属性类型历史 = []
        else:
            self.保存属性类型历史()
    
    def 保存属性类型历史(self):
        """保存属性类型历史"""
        try:
            with open(self.属性历史文件, 'w', encoding='utf-8') as f:
                json.dump({
                    "attribute_types": self.属性类型历史
                }, f, ensure_ascii=False, indent=2)
            self.显示提示("属性类型历史已更新", 显示弹窗=False)
        except Exception as e:
            messagebox.showerror("保存错误", f"无法保存属性历史数据：{str(e)}")
    
    def 添加属性类型到历史(self, 类型名称):
        """添加属性类型到历史记录（去重）"""
        if 类型名称 and 类型名称 not in self.属性类型历史:
            self.属性类型历史.append(类型名称)
            self.保存属性类型历史()
    
    def 创建界面组件(self):
        """创建UI组件（删除源图片路径显示，仅保留图标路径）"""
        # 主框架
        self.主框架 = ttk.Frame(self.主窗口, padding="10")
        self.主框架.pack(fill=tk.BOTH, expand=True)
        
        # 左侧NPC列表
        左侧框架 = ttk.LabelFrame(self.主框架, text="NPC列表 (支持Ctrl+C/V按顺序粘贴覆盖)", padding="5")
        左侧框架.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=(0, 10))
        
        # NPC列表
        self.NPC列表框 = tk.Listbox(左侧框架, width=30, height=30, selectmode=tk.EXTENDED)
        self.NPC列表框.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        self.NPC列表框.bind('<<ListboxSelect>>', self.处理NPC选择)
        
        # 滚动条
        滚动条 = ttk.Scrollbar(左侧框架, orient=tk.VERTICAL, command=self.NPC列表框.yview)
        滚动条.pack(side=tk.RIGHT, fill=tk.Y)
        self.NPC列表框.config(yscrollcommand=滚动条.set)
        
        # 添加按钮
        按钮框架 = ttk.Frame(左侧框架, padding="5")
        按钮框架.pack(fill=tk.X)
        
        ttk.Button(按钮框架, text="添加NPC", command=self.添加NPC).pack(fill=tk.X, pady=2)
        ttk.Button(按钮框架, text="拷贝NPC", command=self.拷贝NPC).pack(fill=tk.X, pady=2)
        ttk.Button(按钮框架, text="删除NPC", command=self.删除NPC).pack(fill=tk.X, pady=2)
        ttk.Button(按钮框架, text="废弃NPC(标记)", command=self.废弃NPC).pack(fill=tk.X, pady=2)
        ttk.Button(按钮框架, text="刷新列表", command=self.刷新NPC列表).pack(fill=tk.X, pady=2)
        ttk.Button(按钮框架, text="保存所有 (Ctrl+S)", command=self.保存数据).pack(fill=tk.X, pady=2)
        
        # 提示设置
        设置框架 = ttk.LabelFrame(左侧框架, text="提示设置", padding="5")
        设置框架.pack(fill=tk.X, pady=5)
        
        self.弹窗变量 = tk.BooleanVar(value=self.显示成功弹窗)
        ttk.Checkbutton(
            设置框架, 
            text="显示成功提示弹窗", 
            variable=self.弹窗变量,
            command=self.切换弹窗显示
        ).pack(anchor=tk.W)
        
        # 右侧编辑区域
        右侧框架 = ttk.Frame(self.主框架)
        右侧框架.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # 上半部分：基本信息（左）+ 图标（右上）
        右上框架 = ttk.Frame(右侧框架)
        右上框架.pack(side=tk.TOP, fill=tk.X, expand=False)
        
        # NPC基本信息（左侧）
        基本信息框架 = ttk.LabelFrame(右上框架, text="基本信息", padding="10")
        基本信息框架.pack(side=tk.LEFT, fill=tk.X, expand=True, pady=(0, 10), padx=(0, 10))
        
        # 表单布局
        表单网格 = ttk.Frame(基本信息框架)
        表单网格.pack(fill=tk.X)
        
        # 名称
        ttk.Label(表单网格, text="名称:").grid(row=0, column=0, sticky=tk.W, pady=5, padx=5)
        self.名称变量 = tk.StringVar()
        ttk.Entry(表单网格, textvariable=self.名称变量, width=50).grid(row=0, column=1, sticky=tk.W, pady=5)
        
        # ID
        ttk.Label(表单网格, text="ID:").grid(row=1, column=0, sticky=tk.W, pady=5, padx=5)
        self.ID变量 = tk.StringVar()
        ttk.Entry(表单网格, textvariable=self.ID变量, width=20, state="readonly").grid(row=1, column=1, sticky=tk.W, pady=5)
        
        # 种族
        ttk.Label(表单网格, text="种族:").grid(row=2, column=0, sticky=tk.W, pady=5, padx=5)
        self.种族变量 = tk.StringVar()
        种族框架 = ttk.Frame(表单网格)
        种族框架.grid(row=2, column=1, sticky=tk.W, pady=5)
        ttk.Combobox(种族框架, textvariable=self.种族变量, values=self.种族列表, width=20).pack(side=tk.LEFT)
        ttk.Button(种族框架, text="添加种族", command=self.添加种族).pack(side=tk.LEFT, padx=5)
        
        # 等级（突出浮点数提示）
        ttk.Label(表单网格, text="等级:").grid(row=3, column=0, sticky=tk.W, pady=5, padx=5)
        self.等级变量 = tk.StringVar()
        等级框架 = ttk.Frame(表单网格)
        等级框架.grid(row=3, column=1, sticky=tk.W, pady=5)
        ttk.Entry(等级框架, textvariable=self.等级变量, width=20).pack(side=tk.LEFT)
        ttk.Label(等级框架, text="(优先浮点数，如3.0)").pack(side=tk.LEFT, padx=5, fill=tk.Y, anchor=tk.CENTER)
        
        # 经验值（突出浮点数提示）
        ttk.Label(表单网格, text="经验值:").grid(row=4, column=0, sticky=tk.W, pady=5, padx=5)
        self.经验值变量 = tk.StringVar()
        经验值框架 = ttk.Frame(表单网格)
        经验值框架.grid(row=4, column=1, sticky=tk.W, pady=5)
        ttk.Entry(经验值框架, textvariable=self.经验值变量, width=20).pack(side=tk.LEFT)
        ttk.Label(经验值框架, text="(优先浮点数，如1.0)").pack(side=tk.LEFT, padx=5, fill=tk.Y, anchor=tk.CENTER)
        
        # 阵营
        ttk.Label(表单网格, text="阵营:").grid(row=5, column=0, sticky=tk.W, pady=5, padx=5)
        self.阵营变量 = tk.StringVar()
        ttk.Combobox(表单网格, textvariable=self.阵营变量, values=self.阵营列表, width=20).grid(row=5, column=1, sticky=tk.W, pady=5)
        
        # 描述
        ttk.Label(基本信息框架, text="描述:").pack(anchor=tk.W, pady=(10, 5))
        self.描述文本框 = tk.Text(基本信息框架, height=4, width=60)
        self.描述文本框.pack(fill=tk.X, pady=(0, 10))
        
        # 图标区域（右上角）- 删除源图片路径显示
        图标框架 = ttk.LabelFrame(右上框架, text="图标", padding="5")
        图标框架.pack(side=tk.RIGHT, fill=tk.Y, anchor=tk.NE, pady=(0, 10))
        
        图标网格 = ttk.Frame(图标框架)
        图标网格.pack(fill=tk.X)
        
        # 仅保留：图标路径（相对项目根目录，Godot用res://+此路径）
        ttk.Label(图标网格, text="图标路径 (res://+此路径):").grid(row=0, column=0, sticky=tk.W, pady=5, padx=5)
        self.图标路径变量 = tk.StringVar()
        ttk.Entry(图标网格, textvariable=self.图标路径变量, width=30, state="readonly").grid(row=0, column=1, sticky=tk.W, pady=5)
        
        # 图标预览和按钮
        图标预览框架 = ttk.Frame(图标框架)
        图标预览框架.pack(fill=tk.X, pady=10)
        
        # 预览容器
        预览容器 = ttk.Frame(图标预览框架, width=240, height=80)
        预览容器.pack_propagate(False)
        预览容器.pack(side=tk.LEFT, padx=10)
        
        # 提示文字
        默认文本 = "点击下方按钮选择图片\n或直接拖拽图片到窗口"
        无拖放文本 = "请先安装tkinterdnd2以支持拖拽\n或点击下方按钮选择图片"
        
        self.图标预览 = ttk.Label(
            预览容器, 
            text=默认文本 if 支持拖放 else 无拖放文本, 
            borderwidth=2, 
            relief="groove", 
            width=30
        )
        self.图标预览.pack(fill=tk.BOTH, expand=True)
        
        ttk.Button(图标预览框架, text="选择图片", command=self.选择图标).pack(side=tk.LEFT, padx=10, pady=20)
        ttk.Button(图标预览框架, text="移除图标", command=self.移除图标).pack(side=tk.LEFT, padx=10, pady=20)
        
        # 属性列表（下方，强调浮点数）
        属性框架 = ttk.LabelFrame(右侧框架, text="属性列表 (值优先浮点数，如10.0)", padding="10")
        属性框架.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        
        # 属性按钮
        属性按钮框架 = ttk.Frame(属性框架)
        属性按钮框架.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(属性按钮框架, text="添加属性", command=self.添加属性).pack(side=tk.LEFT, padx=2)
        ttk.Button(属性按钮框架, text="从历史添加", command=self.从历史添加属性).pack(side=tk.LEFT, padx=2)
        ttk.Button(属性按钮框架, text="删除选中", command=self.删除选中属性).pack(side=tk.LEFT, padx=2)
        ttk.Button(属性按钮框架, text="同步到同种族", command=self.同步属性到同种族).pack(side=tk.LEFT, padx=2)
        ttk.Button(属性按钮框架, text="复制选中", command=self.复制属性).pack(side=tk.LEFT, padx=2)
        ttk.Button(属性按钮框架, text="粘贴", command=self.粘贴属性).pack(side=tk.LEFT, padx=2)
        
        # 属性列表 - 启用多选模式
        列 = ("key", "value")
        self.属性树 = ttk.Treeview(属性框架, columns=列, show="headings", height=10, selectmode=tk.EXTENDED)
        
        # 设置列（强调浮点数）
        self.属性树.heading("key", text="属性")
        self.属性树.heading("value", text="值 (优先浮点数，如10.0)")
        
        self.属性树.column("key", width=200, anchor=tk.W)
        self.属性树.column("value", width=200, anchor=tk.W)
        
        # 滚动条
        属性滚动条 = ttk.Scrollbar(属性框架, orient=tk.VERTICAL, command=self.属性树.yview)
        self.属性树.configure(yscrollcommand=属性滚动条.set)
        
        self.属性树.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        属性滚动条.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 双击编辑
        self.属性树.bind("<Double-1>", self.处理属性双击)
        self.属性树.bind("<<TreeviewSelect>>", self.处理属性选择)
        
        # 快捷键
        self.属性树.bind("<Control-c>", self.复制属性)
        self.属性树.bind("<Control-v>", self.粘贴属性)
        
        # 状态栏
        状态栏 = ttk.Label(self.主窗口, textvariable=self.状态变量, relief=tk.SUNKEN, anchor=tk.W)
        状态栏.pack(side=tk.BOTTOM, fill=tk.X)
        
        # 更新NPC列表
        self.更新NPC列表()
        
        # 绑定编辑框内容变化事件
        self.名称变量.trace_add("write", lambda *args: self.状态变量.set("有未保存的更改 (按Ctrl+S保存)"))
        self.种族变量.trace_add("write", lambda *args: self.状态变量.set("有未保存的更改 (按Ctrl+S保存)"))
        self.等级变量.trace_add("write", lambda *args: self.状态变量.set("有未保存的更改 (按Ctrl+S保存)"))
        self.经验值变量.trace_add("write", lambda *args: self.状态变量.set("有未保存的更改 (按Ctrl+S保存)"))
        self.阵营变量.trace_add("write", lambda *args: self.状态变量.set("有未保存的更改 (按Ctrl+S保存)"))
        self.描述文本框.bind("<<Modified>>", lambda e: self.状态变量.set("有未保存的更改 (按Ctrl+S保存)") or self.描述文本框.edit_modified(False))
        
        # 窗口关闭事件
        self.主窗口.protocol("WM_DELETE_WINDOW", self.处理关闭)
    
    def 废弃NPC(self):
        """将选中的NPC标记为废弃，修改名称并保留ID"""
        # 获取所有选中的NPC
        选中索引 = self.NPC列表框.curselection()
        if not 选中索引:
            messagebox.showinfo("提示", "请先选择一个或多个NPC")
            return
            
        # 保存当前编辑的NPC
        self.保存当前NPC()
        
        # 处理每个选中的NPC
        废弃数量 = 0
        for idx in 选中索引:
            选中文本 = self.NPC列表框.get(idx)
            匹配 = re.search(r'ID: (\d+)', 选中文本)
            if 匹配:
                NPCID = 匹配.group(1)
                if NPCID in self.NPC列表:
                    # 修改NPC名称为"废弃"并保留ID
                    self.NPC列表[NPCID]["名称"] = f"废弃_{self.NPC列表[NPCID]['名称']}"
                    废弃数量 += 1
        
        # 更新列表显示
        self.更新NPC列表()
        
        # 如果当前编辑的NPC被废弃，更新显示
        if self.当前NPCID and self.当前NPCID in [re.search(r'ID: (\d+)', self.NPC列表框.get(idx)).group(1) for idx in 选中索引 if re.search(r'ID: (\d+)', self.NPC列表框.get(idx))]:
            self.加载NPC(self.当前NPCID)
        
        self.显示提示(f"已将 {废弃数量} 个NPC标记为废弃")
    
    def 同步属性到同种族(self):
        """将当前NPC的属性同步到所有同种族NPC（默认值为浮点数）"""
        if not self.当前NPCID or self.当前NPCID not in self.NPC列表:
            messagebox.showinfo("提示", "请先选择一个NPC")
            return
            
        # 保存当前编辑的属性
        self.保存当前NPC()
        
        # 获取当前NPC的种族和属性
        当前NPC = self.NPC列表[self.当前NPCID]
        当前种族 = 当前NPC.get("种族")
        当前属性 = 当前NPC.get("属性列表", {})
        
        if not 当前种族:
            messagebox.showinfo("提示", "当前NPC没有设置种族")
            return
        
        # 查找所有同种族的NPC
        同种族NPC = [
            NPCID for NPCID, NPC数据 in self.NPC列表.items()
            if NPC数据.get("种族") == 当前种族 and NPCID != self.当前NPCID
        ]
        
        if not 同种族NPC:
            messagebox.showinfo("提示", f"没有找到其他 '{当前种族}' 种族的NPC")
            return
        
        # 创建一个对话框让用户选择初始化值类型（默认浮点数）
        初始化窗口 = tk.Toplevel(self.主窗口)
        初始化窗口.title("选择初始化值")
        初始化窗口.geometry("350x200")
        初始化窗口.resizable(False, False)
        初始化窗口.transient(self.主窗口)
        初始化窗口.grab_set()
        
        # 居中显示
        初始化窗口.update_idletasks()
        宽度 = 初始化窗口.winfo_width()
        高度 = 初始化窗口.winfo_height()
        x = (self.主窗口.winfo_width() // 2) - (宽度 // 2) + self.主窗口.winfo_x()
        y = (self.主窗口.winfo_height() // 2) - (高度 // 2) + self.主窗口.winfo_y()
        初始化窗口.geometry('{}x{}+{}+{}'.format(宽度, 高度, x, y))
        
        # 主框架
        主框架 = ttk.Frame(初始化窗口, padding=15)
        主框架.pack(fill=tk.BOTH, expand=True)
        
        # 提示文字
        ttk.Label(主框架, text="请选择新属性的初始化值:").pack(anchor=tk.W, pady=(0, 15))
        
        # 选项变量（默认浮点数0.0）
        初始化值变量 = tk.StringVar(value="0.0")
        
        # 选项
        选项框架 = ttk.Frame(主框架)
        选项框架.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Radiobutton(选项框架, text="0.0 (浮点数，推荐)", variable=初始化值变量, value="0.0").pack(anchor=tk.W, pady=2)
        ttk.Radiobutton(选项框架, text="0 (整数)", variable=初始化值变量, value="0").pack(anchor=tk.W, pady=2)
        ttk.Radiobutton(选项框架, text="空字符串", variable=初始化值变量, value="").pack(anchor=tk.W, pady=2)
        
        # 确认按钮区域
        按钮框架 = ttk.Frame(主框架)
        按钮框架.pack(fill=tk.X, pady=(0, 10))
        
        结果 = [None]
        
        def 确认():
            结果[0] = 初始化值变量.get()
            初始化窗口.destroy()
        
        确认按钮 = ttk.Button(按钮框架, text="确认", command=确认)
        确认按钮.pack(fill=tk.X, padx=50)
        
        # 等待用户选择
        self.主窗口.wait_window(初始化窗口)
        
        if 结果[0] is None:
            return
        
        # 确定初始化值（优先浮点数）
        try:
            if 结果[0] == "0.0":
                初始化值 = 0.0  # 浮点数
            elif 结果[0] == "0":
                初始化值 = 0
            else:
                初始化值 = 结果[0]
        except:
            初始化值 = 结果[0]
        
        # 询问用户是否确认同步
        值描述 = "0.0 (浮点数)" if 结果[0] == "0.0" else "0 (整数)" if 结果[0] == "0" else "空字符串"
        if not messagebox.askyesno(
            "确认同步", 
            f"将为所有 {len(同种族NPC)} 个 '{当前种族}' 种族的NPC\n"
            f"添加缺失的属性并设置默认值为 {值描述}，是否继续？"
        ):
            return
        
        # 记录新增的属性数量
        总添加数 = 0
        
        # 为每个同种族NPC添加缺失的属性
        for NPCID in 同种族NPC:
            NPC = self.NPC列表[NPCID]
            NPC属性 = NPC.get("属性列表", {})
            
            # 检查并添加缺失的属性
            for 属性名称 in 当前属性:
                if 属性名称 not in NPC属性:
                    NPC属性[属性名称] = 初始化值  # 设置用户选择的默认值
                    总添加数 += 1
            
            # 更新NPC属性
            NPC["属性列表"] = NPC属性
        
        # 刷新当前NPC的属性列表
        self.加载属性(当前属性)
        
        self.显示提示(
            f"已完成同步，共为 {len(同种族NPC)} 个 '{当前种族}' 种族NPC\n"
            f"添加了 {总添加数} 个属性（默认值: {值描述}）"
        )
    
    def 刷新NPC列表(self):
        """手动刷新NPC列表"""
        # 保存当前编辑的内容
        self.保存当前NPC()
        # 重新加载数据
        self.加载数据()
        # 更新列表显示
        self.更新NPC列表()
        # 保持当前选中项
        if self.当前NPCID and self.当前NPCID in self.NPC列表:
            for i, NPC文本 in enumerate(self.NPC列表框.get(0, tk.END)):
                if f"ID: {self.当前NPCID}" in NPC文本:
                    self.NPC列表框.selection_set(i)
                    self.NPC列表框.see(i)
                    break
        self.显示提示("NPC列表已刷新")
    
    def 切换弹窗显示(self):
        """切换是否显示成功提示弹窗"""
        self.显示成功提示弹窗 = self.弹窗变量.get()
        状态 = "已启用" if self.显示成功提示弹窗 else "已禁用"
        self.显示提示(f"成功提示弹窗{状态}", 显示弹窗=False)
    
    def 拷贝NPC(self):
        """复制当前选中的NPC（保留浮点数属性和简化图标路径）"""
        # 获取所有选中的NPC
        选中索引 = self.NPC列表框.curselection()
        if not 选中索引:
            messagebox.showinfo("提示", "请先选择一个或多个NPC")
            return
            
        # 保存当前编辑的NPC
        self.保存当前NPC()
        
        # 确定插入位置
        插入位置 = 0
        if 选中索引:
            插入位置 = max(选中索引) + 1
        else:
            插入位置 = self.NPC列表框.size()
        
        # 复制每个选中的NPC
        复制数量 = 0
        新ID列表 = []
        
        for idx in 选中索引:
            选中文本 = self.NPC列表框.get(idx)
            匹配 = re.search(r'ID: (\d+)', 选中文本)
            if 匹配:
                NPCID = 匹配.group(1)
                if NPCID in self.NPC列表:
                    # 获取当前NPC数据（包含浮点数属性和简化图标路径）
                    当前NPC = self.NPC列表[NPCID]
                    
                    # 生成新ID
                    新ID = 1001
                    while str(新ID) in self.NPC列表:
                        新ID += 1
                    新ID = str(新ID)
                    
                    # 复制NPC数据（保留浮点数格式和简化图标路径）
                    新名称 = f"{当前NPC['名称']}"
                    新NPC = 当前NPC.copy()
                    新NPC["名称"] = 新名称
                    
                    # 如果有图标，创建图标的副本并更新路径
                    旧图标路径 = 当前NPC.get("图标路径", "")
                    if 旧图标路径:
                        # 转换为绝对路径
                        旧绝对路径 = os.path.join(self.项目根目录, 旧图标路径)
                        if os.path.exists(旧绝对路径) and os.path.isfile(旧绝对路径):
                            try:
                                # 生成新文件名
                                扩展名 = os.path.splitext(旧绝对路径)[1].lower()
                                新文件名 = f"icon_{uuid.uuid4().hex}{扩展名}"
                                新绝对路径 = os.path.join(self.图片目录, 新文件名)
                                
                                # 复制文件
                                shutil.copy2(旧绝对路径, 新绝对路径)
                                
                                # 生成新的相对路径（项目根目录下）
                                新相对路径 = os.path.relpath(新绝对路径, self.项目根目录)
                                新NPC["图标路径"] = 新相对路径  # 存储相对路径
                                
                            except Exception as e:
                                messagebox.showwarning("警告", f"复制图片时出错：{str(e)}\n将使用原NPC的图片路径")
                    
                    # 添加新NPC
                    self.NPC列表[新ID] = 新NPC
                    新ID列表.append(新ID)
                    复制数量 += 1
                    插入位置 += 1
        
        # 更新列表
        self.更新NPC列表()
        
        # 选中新复制的NPC
        if 新ID列表:
            # 找到新ID在列表中的位置并选中
            列表长度 = self.NPC列表框.size()
            选中位置 = []
            
            for i in range(列表长度):
                列表项 = self.NPC列表框.get(i)
                for 新ID in 新ID列表:
                    if f"ID: {新ID}" in 列表项:
                        选中位置.append(i)
                        break
            
            if 选中位置:
                self.NPC列表框.selection_clear(0, tk.END)
                for pos in 选中位置:
                    self.NPC列表框.selection_set(pos)
                # 滚动到第一个选中项
                self.NPC列表框.see(选中位置[0])
        
        self.显示提示(f"已复制 {复制数量} 个NPC到指定位置")
    
    def 处理关闭(self):
        """窗口关闭时保存数据"""
        self.保存数据()
        self.主窗口.destroy()
    
    def 更新NPC列表(self):
        """更新NPC列表"""
        self.NPC列表框.delete(0, tk.END)
        for NPCID, NPC数据 in self.NPC列表.items():
            self.NPC列表框.insert(tk.END, f"{NPC数据.get('名称', '未命名')} (ID: {NPCID})")
        self.显示提示(f"NPC列表已更新，共 {len(self.NPC列表)} 个NPC", 显示弹窗=False)
    
    def 关闭活跃编辑框(self):
        """关闭当前活跃的编辑框"""
        if self.活跃编辑框:
            try:
                self.活跃编辑框.destroy()
            except:
                pass
            self.活跃编辑框 = None
    
    def 处理NPC选择(self, 事件):
        """处理NPC选择事件"""
        self.关闭活跃编辑框()
        self.保存当前NPC()
        
        选中项 = self.NPC列表框.curselection()
        if not 选中项:
            return
            
        # 如果选择了多个，只加载第一个
        选中文本 = self.NPC列表框.get(选中项[0])
        匹配 = re.search(r'ID: (\d+)', 选中文本)
        if 匹配:
            NPCID = 匹配.group(1)
            self.加载NPC(NPCID)
            NPC名称 = self.NPC列表[NPCID].get("名称", "未命名")
            self.显示提示(f"已选择NPC: {NPC名称} (ID: {NPCID})", 显示弹窗=False)
    
    def 加载NPC(self, NPCID):
        """加载NPC数据到表单（浮点数显示为带小数点的格式，图标路径为相对路径）"""
        if NPCID not in self.NPC列表:
            return
            
        self.当前NPCID = NPCID
        NPC = self.NPC列表[NPCID]
        
        # 填充表单（浮点数显示为字符串）
        self.ID变量.set(NPCID)
        self.名称变量.set(NPC.get("名称", ""))
        self.种族变量.set(NPC.get("种族", ""))
        
        # 等级显示：如果是数字，转换为字符串（保留浮点数格式）
        等级 = NPC.get("等级", 1.0)
        self.等级变量.set(str(等级) if isinstance(等级, (int, float)) else 等级)
        
        # 经验值显示：如果是数字，转换为字符串（保留浮点数格式）
        经验值 = NPC.get("经验值", 1.0)
        self.经验值变量.set(str(经验值) if isinstance(经验值, (int, float)) else 经验值)
        
        self.阵营变量.set(NPC.get("阵营", ""))
        self.描述文本框.delete(1.0, tk.END)
        self.描述文本框.insert(tk.END, NPC.get("描述", ""))
        
        # 加载图标路径（相对项目根目录）
        相对图标路径 = NPC.get("图标路径", "")
        self.图标路径变量.set(相对图标路径)
        
        # 加载图标预览（转换为绝对路径）
        绝对图标路径 = os.path.join(self.项目根目录, 相对图标路径) if 相对图标路径 else ""
        self.加载图标预览(绝对图标路径)
        
        # 加载属性列表（浮点数显示为带小数点的格式）
        self.加载属性(NPC.get("属性列表", {}))
    
    def 加载属性(self, 属性):
        """加载属性列表（浮点数显示为带小数点的格式）"""
        # 清空现有项
        for 项 in self.属性树.get_children():
            self.属性树.delete(项)
        
        # 添加属性（浮点数转换为字符串显示）
        for 键, 值 in 属性.items():
            # 显示时统一转换为字符串，浮点数会自动显示为10.0格式
            显示值 = str(值) if isinstance(值, (int, float)) else 值
            self.属性树.insert("", tk.END, values=(键, 显示值))
        
        self.显示提示(f"已加载 {len(属性)} 个属性", 显示弹窗=False)
    
    def 加载图标预览(self, 绝对图片路径):
        """加载图标预览（接收绝对路径）"""
        # 清除之前的图片引用
        if hasattr(self.图标预览, 'image'):
            delattr(self.图标预览, 'image')
        
        # 检查路径是否有效
        if not 绝对图片路径 or not isinstance(绝对图片路径, str) or not os.path.exists(绝对图片路径):
            默认文本 = "点击下方按钮选择图片\n或直接拖拽图片到窗口"
            无拖放文本 = "请先安装tkinterdnd2以支持拖拽\n或点击下方按钮选择图片"
            self.图标预览.config(
                text=默认文本 if 支持拖放 else 无拖放文本, 
                image=""
            )
            return
            
        try:
            # 尝试打开并显示图片
            图片 = Image.open(绝对图片路径)
            图片.thumbnail((100, 100))  # 缩小图片
            照片 = ImageTk.PhotoImage(图片)
            self.图标预览.config(image=照片, text="")
            self.图标预览.image = 照片  # 保持引用
            self.显示提示(f"已加载图标: {os.path.basename(绝对图片路径)}", 显示弹窗=False)
        except Exception as e:
            self.图标预览.config(text=f"无法加载图片\n{str(e)}", image="")
    
    def 添加NPC(self):
        """添加新NPC（默认等级为1.0浮点数，图标路径为空）"""
        # 关闭任何活跃的编辑框
        self.关闭活跃编辑框()
        
        # 生成新ID
        新ID = 1001
        while str(新ID) in self.NPC列表:
            新ID += 1
        新ID = str(新ID)
        
        # 创建新NPC（默认值为浮点数，仅保留图标路径）
        self.NPC列表[新ID] = {
            "名称": "",
            "种族": "",
            "等级": 1.0,  # 默认浮点数
            "经验值": 1.0,  # 默认浮点数
            "阵营": "",
            "描述": "",
            "图标路径": "",  # 仅存储相对路径
            "属性列表": {}
        }
        
        # 更新列表列表并选中新NPC
        self.更新NPC列表()
        
        # 选中新NPC
        for i, NPC文本 in enumerate(self.NPC列表框.get(0, tk.END)):
            if f"ID: {新ID}" in NPC文本:
                self.NPC列表框.selection_set(i)
                self.NPC列表框.see(i)
                self.处理NPC选择(None)
                break
    
    def 删除NPC(self):
        """保留ID，仅清空当前选中的NPC内容"""
        # 关闭任何活跃的编辑框
        self.关闭活跃编辑框()
        
        选中索引 = self.NPC列表框.curselection()
        if not 选中索引:
            messagebox.showinfo("提示", "请先选择一个或多个NPC")
            return
        
        # 获取选中的NPCID
        选中ID = []
        for idx in 选中索引:
            选中文本 = self.NPC列表框.get(idx)
            匹配 = re.search(r'ID: (\d+)', 选中文本)
            if 匹配:
                选中ID.append(匹配.group(1))
        
        if not 选中ID:
            messagebox.showinfo("提示", "未找到选中的NPC ID")
            return
            
        # 确认清空
        if messagebox.askyesno("确认清空", f"确定要清空这 {len(选中ID)} 个NPC的内容吗？\nID将会被保留，但所有数据会被清空。"):
            # 记录清空的NPC名称
            清空名称 = []
            
            # 逐个清空内容，保留ID
            for NPCID in 选中ID:
                if NPCID in self.NPC列表:
                    # 记录原名称
                    原名称 = self.NPC列表[NPCID].get("名称", "未命名")
                    清空名称.append(原名称)
                    
                    # 删除图标文件（通过相对路径转换为绝对路径）
                    self.按ID删除图标文件(NPCID)
                    
                    # 保留ID，清空内容（设置为默认空值）
                    self.NPC列表[NPCID] = {
                        "名称": f"",  # 标记为已清空
                        "种族": "",
                        "等级": 0.0,  # 保留浮点数类型
                        "经验值": 1.0,  # 保留经验值字段，默认浮点数
                        "阵营": "",
                        "描述": "此NPC内容已被清空",
                        "图标路径": "",  # 清空图标路径
                        "属性列表": {}  # 清空属性
                    }
            
            # 如果当前编辑的NPC被清空，重新加载以显示空内容
            if self.当前NPCID in 选中ID:
                self.加载NPC(self.当前NPCID)
            
            # 更新列表
            self.更新NPC列表()
            
            self.显示提示(f"已清空 {len(清空名称)} 个NPC的内容，ID已保留")
    
    
    def 按ID删除图标文件(self, NPCID):
        """通过NPCID删除图标文件（从相对路径转换为绝对路径）"""
        if NPCID in self.NPC列表:
            相对图标路径 = self.NPC列表[NPCID].get("图标路径", "")
            if 相对图标路径:
                绝对图标路径 = os.path.join(self.项目根目录, 相对图标路径)
                if os.path.exists(绝对图标路径) and os.path.isfile(绝对图标路径):
                    try:
                        # 检查文件是否在我们的图片目录中，防止误删其他文件
                        if str(Path(绝对图标路径).parent) == str(Path(self.图片目录).resolve()):
                            os.remove(绝对图标路径)
                            self.状态变量.set(f"已删除图标: {os.path.basename(绝对图标路径)}")
                    except Exception as e:
                        messagebox.showwarning("警告", f"删除图标时出错：{str(e)}")
    
    def 清空表单(self):
        """清空表单（仅清空一个图标路径）"""
        self.ID变量.set("")
        self.名称变量.set("")
        self.种族变量.set("")
        self.等级变量.set("")
        self.经验值变量.set("")
        self.阵营变量.set("")
        self.描述文本框.delete(1.0, tk.END)
        self.图标路径变量.set("")  # 仅清空一个图标路径
        
        # 清除图片预览
        if hasattr(self.图标预览, 'image'):
            delattr(self.图标预览, 'image')
        默认文本 = "点击下方按钮选择图片\n或直接拖拽图片到窗口"
        无拖放文本 = "请先安装tkinterdnd2以支持拖拽\n或点击下方按钮选择图片"
        self.图标预览.config(
            text=默认文本 if 支持拖放 else 无拖放文本, 
            image=""
        )
        
        # 清空属性列表
        for 项 in self.属性树.get_children():
            self.属性树.delete(项)
    
    def 添加种族(self):
        """添加新种族"""
        新种族 = simpledialog.askstring("添加种族", "请输入新种族名称:")
        if 新种族 and 新种族 not in self.种族列表:
            self.种族列表.append(新种族)
            self.种族变量.set(新种族)
            self.保存类型数据()
            # 更新种族下拉框
            下拉框 = self.主窗口.nametowidget(self.种族变量._w).master.winfo_children()[0]
            下拉框['values'] = self.种族列表
            self.显示提示(f"已添加新种族: {新种族}")
    
    def 选择图标(self):
        """选择图标文件"""
        if not self.当前NPCID:
            messagebox.showinfo("提示", "请先选择或创建一个NPC")
            return
            
        文件路径 = filedialog.askopenfilename(
            title="选择图标",
            filetypes=[("图片文件", "*.png;*.jpg;*.jpeg;*.gif;*.bmp")]
        )
        
        if 文件路径:
            self.处理图标(文件路径)
    
    def 处理图标(self, 文件路径):
        """处理图标文件：复制到项目目录，生成相对路径（仅存储一个路径）"""
        try:
            # 验证源文件是否存在
            if not os.path.exists(文件路径) or not os.path.isfile(文件路径):
                raise Exception(f"源文件不存在或不是有效文件: {文件路径}")
            
            # 确保图片目录存在
            if not self.确保目录存在(self.图片目录):
                return
            
            # 首先删除旧图标
            self.删除图标文件()
            
            # 生成新文件名
            扩展名 = os.path.splitext(文件路径)[1].lower()  # 统一扩展名小写
            新文件名 = f"icon_{uuid.uuid4().hex}{扩展名}"
            
            # 构建目标绝对路径
            目标绝对路径 = Path(self.图片目录) / 新文件名
            目标绝对路径 = str(目标绝对路径.resolve())
            
            # 复制文件
            try:
                shutil.copy2(文件路径, 目标绝对路径)
            except Exception as e:
                raise Exception(f"复制文件失败: {str(e)}\n源路径: {文件路径}\n目标路径: {目标绝对路径}")
            
            # 验证文件是否真的复制成功
            if not os.path.exists(目标绝对路径):
                raise Exception(f"文件复制后验证失败，目标文件不存在: {目标绝对路径}")
            
            # 生成相对项目根目录的路径（仅存储此路径）
            相对路径 = os.path.relpath(目标绝对路径, self.项目根目录)
            # 统一使用正斜杠（Godot兼容）
            相对路径 = 相对路径.replace("\\", "/")
            
            # 更新UI和数据
            self.图标路径变量.set(相对路径)
            self.加载图标预览(目标绝对路径)  # 预览用绝对路径
            
            self.显示提示(f"图片已成功添加\n路径: {相对路径}\nGodot使用: res://{相对路径}", 显示弹窗=False)
            self.保存数据()
        except Exception as e:
            messagebox.showerror("图片处理错误", f"处理图片时出错: {str(e)}")
            # 若复制失败，清空路径变量
            self.图标路径变量.set("")
    
    def 删除图标文件(self):
        """删除当前NPC的图标文件（从相对路径转换为绝对路径）"""
        if not self.当前NPCID:
            return
            
        # 获取当前相对图标路径
        相对图标路径 = self.图标路径变量.get()
        if not 相对图标路径:
            return
            
        # 转换为绝对路径
        绝对图标路径 = os.path.join(self.项目根目录, 相对图标路径)
        
        # 检查路径是否存在且是文件
        if os.path.exists(绝对图标路径) and os.path.isfile(绝对图标路径):
            try:
                # 检查文件是否在我们的图片目录中，防止误删其他文件
                if str(Path(绝对图标路径).parent) == str(Path(self.图片目录).resolve()):
                    os.remove(绝对图标路径)
                    self.显示提示(f"已删除旧图标: {os.path.basename(绝对图标路径)}", 显示弹窗=False)
                else:
                    self.状态变量.set(f"未删除旧图标（不在项目图片目录中）: {os.path.basename(绝对图标路径)}")
            except Exception as e:
                messagebox.showwarning("警告", f"删除旧图标时出错：{str(e)}")
    
    def 移除图标(self):
        """移除当前NPC的图标"""
        if not self.当前NPCID:
            messagebox.showinfo("提示", "请先选择一个NPC")
            return
            
        if not self.图标路径变量.get():
            messagebox.showinfo("提示", "当前NPC没有图标")
            return
            
        if messagebox.askyesno("确认移除", "确定要移除当前NPC的图标吗？\n相关图片文件也将被删除。"):
            # 删除图标文件
            self.删除图标文件()
            
            # 清空图标路径
            self.图标路径变量.set("")
            
            # 更新预览
            self.加载图标预览("")
            
            self.显示提示("已移除图标")
    
    def 添加属性(self):
        """添加新属性（默认值为1.0浮点数）"""
        self.属性树.insert("", tk.END, values=("属性名", "1.0"))  # 默认浮点数
        self.显示提示("已添加新属性", 显示弹窗=False)
    
    def 从历史添加属性(self):
        """从历史类型中选择添加属性"""
        if not self.属性类型历史:
            messagebox.showinfo("提示", "暂无历史属性类型")
            return
            
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
        
        # 提示标签
        提示标签 = ttk.Label(选择窗口, text="双击可删除选中的属性类型", font=("微软雅黑", 9))
        提示标签.pack(pady=(0, 2))
        
        # 列表框
        列表框 = tk.Listbox(选择窗口, selectmode=tk.SINGLE)
        列表框.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # 添加历史类型
        for 类型 in self.属性类型历史:
            列表框.insert(tk.END, 类型)
        
        # 滚动条
        滚动条 = ttk.Scrollbar(选择窗口, orient=tk.VERTICAL, command=列表框.yview)
        滚动条.pack(side=tk.RIGHT, fill=tk.Y)
        列表框.config(yscrollcommand=滚动条.set)
        
        def 确认选择():
            选中项 = 列表框.curselection()
            if 选中项:
                类型名称 = 列表框.get(选中项[0])
                self.属性树.insert("", tk.END, values=(类型名称, "1.0"))
                self.显示提示(f"已添加属性: {类型名称}", 显示弹窗=False)
            选择窗口.destroy()
        
        # 删除按钮函数
        def 删除选中历史():
            选中项 = 列表框.curselection()
            if not 选中项:
                messagebox.showinfo("提示", "请先选择要删除的属性类型")
                return
            
            类型名称 = 列表框.get(选中项[0])
            if messagebox.askyesno("确认删除", f"确定要删除历史属性类型 '{类型名称}' 吗？"):
                self.属性类型历史.remove(类型名称)
                self.保存属性类型历史()
                # 重新加载列表
                列表框.delete(0, tk.END)
                for 类型 in self.属性类型历史:
                    列表框.insert(tk.END, 类型)
                self.显示提示(f"已删除历史属性类型: {类型名称}", 显示弹窗=False)
        
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
                列表框.selection_set(列表框.nearest(事件.y))
                # 选中点击的项目
                菜单 = tk.Menu(选择窗口, tearoff=0)
                菜单.add_command(label="删除此属性类型", command=删除选中历史)
                菜单.post(事件.x_root, 事件.y_root)
        
        列表框.bind("<Double-1>", 双击删除)
        列表框.bind("<Button-3>", 显示右键菜单)
    
    def 处理属性选择(self, 事件):
        """处理属性选中事件"""
        pass  # 仅用于触发选中状态
    
    def 删除选中属性(self):
        """删除选中的属性"""
        # 关闭任何活跃的编辑框
        self.关闭活跃编辑框()
        
        # 获取所有选中的项
        选中项 = self.属性树.selection()
        if not 选中项:
            messagebox.showinfo("提示", "请先选择要删除的属性")
            return
            
        # 逐个删除选中项
        数量 = len(选中项)
        for 项 in 选中项:
            self.属性树.delete(项)
            
        self.显示提示(f"已删除 {数量} 个选中的属性")
    
    def 复制属性(self, 事件=None):
        """复制选中的属性 (支持Ctrl+C快捷键)"""
        self.已复制属性 = []
        for 项 in self.属性树.selection():
            数值 = self.属性树.item(项, "values")
            self.已复制属性.append((数值[0], 数值[1]))
        
        if self.已复制属性:
            self.显示提示(f"已复制 {len(self.已复制属性)} 个属性 (Ctrl+C)", 显示弹窗=False)
        
        # 返回'break'防止事件继续传播
        return "break"
    
    def 粘贴属性(self, 事件=None):
        """粘贴属性 (支持Ctrl+V快捷键)"""
        if not self.已复制属性:
            self.状态变量.set("没有可粘贴的属性")
            return "break"
            
        # 获取当前选中位置
        选中项 = self.属性树.selection()
        插入位置 = ""
        
        if 选中项:
            # 如果有选中项，在最后一个选中项的下方插入
            插入位置 = 选中项[-1]
        
        for 属性 in self.已复制属性:
            if 插入位置:
                self.属性树.insert("", tk.AFTER, 插入位置, values=属性)
                插入位置 = self.属性树.get_children()[-1]  # 更新插入位置为新添加的项
            else:
                self.属性树.insert("", tk.END, values=属性)
        
        self.显示提示(f"已粘贴 {len(self.已复制属性)} 个属性 (Ctrl+V)")
        
        # 返回'break'防止事件继续传播
        return "break"
    
    def 处理属性双击(self, 事件):
        """双击编辑属性项（优先浮点数）"""
        # 关闭任何已存在的编辑框
        self.关闭活跃编辑框()
        
        区域 = self.属性树.identify_region(事件.x, 事件.y)
        if 区域 != "cell":
            return
            
        # 解析列索引
        列字符串 = self.属性树.identify_column(事件.x)
        列 = int(列字符串.replace('#', '')) - 1  # 转换为0-based索引
        
        项 = self.属性树.identify_row(事件.y)
        
        # 获取单元格位置和当前值
        x, y, 宽度, 高度 = self.属性树.bbox(项, 列)
        值 = self.属性树.item(项, "values")[列]
        
        # 创建编辑框
        输入框 = ttk.Entry(self.属性树)
        输入框.place(x=x, y=y, width=宽度, height=高度)
        输入框.insert(0, 值)
        输入框.focus()
        
        # 保存当前编辑框引用
        self.活跃编辑框 = 输入框
        
        # 保存编辑结果（自动转换为浮点数）
        def 保存编辑(事件=None):
            # 检查项目是否仍然存在
            if 项 not in self.属性树.get_children():
                输入框.destroy()
                self.活跃编辑框 = None
                return
            
            新值 = 输入框.get()
            数值列表 = list(self.属性树.item(项, "values"))
            数值列表[列] = 新值
            self.属性树.item(项, values=数值列表)
            
            # 如果是属性名列，添加到历史记录
            if 列 == 0 and 新值:
                self.添加属性类型到历史(新值)
            
            输入框.destroy()
            self.活跃编辑框 = None
            self.状态变量.set("有未保存的更改 (按Ctrl+S保存)")
        
        输入框.bind("<FocusOut>", 保存编辑)
        输入框.bind("<Return>", 保存编辑)
        输入框.bind("<Escape>", lambda e: [输入框.destroy(), setattr(self, '活跃编辑框', None)])

if __name__ == "__main__":
    # 根据是否有dnd支持选择不同的根窗口类型
    if 支持拖放:
        根窗口 = Tk()  # 使用tkinterdnd2的Tk
    else:
        根窗口 = tk.Tk()  # 使用标准Tk
        
    应用 = NPC编辑器(根窗口)
    根窗口.mainloop()
    