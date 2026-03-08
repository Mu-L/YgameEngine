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

class 技能编辑器:
    def __init__(self, 主窗口):
        self.主窗口 = 主窗口
        self.主窗口.title("Godot 技能编辑器 ver1.3 (快捷键+保留ID)")
        self.主窗口.geometry("1000x700")
        self.主窗口.minsize(800, 600)
        
        # 初始化状态变量
        self.状态变量 = tk.StringVar(value="就绪 (Ctrl+S保存 | Ctrl+C复制 | Ctrl+V粘贴)")
        # 计算路径
        self.计算项目路径()
        # 数据存储
        self.技能列表 = {}
        self.当前技能ID = None
        self.已复制效果 = []
        self.活跃编辑框 = None
        self.已复制技能列表 = []  # 存储复制的技能数据（无ID）
        
        # 固定选项
        self.伤害类型列表 = ["物理", "魔法"]
        self.技能类型列表 = ["主动", "被动"]
        # 效果类型历史列表
        self.效果类型历史 = []  # 存储历史效果类型，用于复用
        
        # 配置文件路径
        self.图片目录 = os.path.join(self.系统文件夹, "skill_icons")
        self.系统文件 = os.path.join(self.系统文件夹, "skillsystem.json")
        self.类型文件 = os.path.join(self.系统文件夹, "skill_types.json")
        self.效果历史文件 = os.path.join(self.系统文件夹, "skill_att.json")  # 存储效果类型历史
        
        # 配置提示选项
        self.显示成功弹窗 = True
        
        # 确保图片目录存在
        self.确保目录存在(self.图片目录)
        
        # 初始化并加载数据
        self.初始化默认文件()
        self.加载数据()
        self.加载类型数据()
        self.加载效果类型历史()
        
        # 创建UI
        self.创建界面组件()
        
        # 配置拖拽功能
        self.设置拖放功能()
        
        # 绑定快捷键
        self.设置快捷键()
    
    def 计算项目路径(self):
        """计算项目根目录和系统文件夹路径"""
        try:
            if getattr(sys, 'frozen', False):
                当前路径 = os.path.dirname(sys.executable)
            else:
                当前路径 = os.path.dirname(os.path.abspath(__file__))
            
            self.项目根目录 = os.path.abspath(os.path.join(当前路径, "..", "..", "..", ".."))
            self.系统文件夹 = os.path.join(self.项目根目录, "系统")
            self.确保目录存在(self.系统文件夹)
            
            print(f"当前执行路径: {当前路径}")
            print(f"项目根目录: {self.项目根目录}")
            print(f"系统文件夹: {self.系统文件夹}")
            
        except Exception as e:
            messagebox.showerror("路径计算错误", f"无法计算项目路径: {str(e)}")
            self.项目根目录 = os.getcwd()
            self.系统文件夹 = os.path.join(self.项目根目录, "系统")
            self.确保目录存在(self.系统文件夹)
    
    def 设置快捷键(self):
        """设置快捷键（新增技能列表复制粘贴）"""
        # 保存快捷键
        self.主窗口.bind("<Control-s>", self.保存数据快捷键)
        self.主窗口.bind("<Control-S>", self.保存数据快捷键)
        self.主框架.bind("<Control-s>", self.保存数据快捷键)
        self.主框架.bind("<Control-S>", self.保存数据快捷键)
        
        # 技能列表复制粘贴快捷键
        self.技能列表框.bind("<Control-c>", self.快捷键复制技能)
        self.技能列表框.bind("<Control-C>", self.快捷键复制技能)
        self.技能列表框.bind("<Control-v>", self.快捷键粘贴技能)
        self.技能列表框.bind("<Control-V>", self.快捷键粘贴技能)
    
    def 保存数据快捷键(self, 事件=None):
        """快捷键触发的保存功能"""
        self.保存数据()
        return "break"
    
    # 新增：快捷键复制技能（参考道具编辑器逻辑）
    def 快捷键复制技能(self, event=None):
        """复制选中的技能数据（不含ID），支持Ctrl+C"""
        self.已复制技能列表 = []
        选中索引 = self.技能列表框.curselection()
        
        if not 选中索引:
            self.状态变量.set("未选择任何技能进行复制")
            return "break"
        
        # 保存当前编辑的技能
        self.保存当前技能()
        
        # 收集选中的技能数据（按选择顺序，不含ID）
        for idx in 选中索引:
            选中文本 = self.技能列表框.get(idx)
            匹配 = re.search(r'ID: (\d+)', 选中文本)
            if 匹配:
                技能ID = 匹配.group(1)
                if 技能ID in self.技能列表:
                    # 复制技能数据（排除ID，深拷贝避免引用问题）
                    技能数据 = self.技能列表[技能ID].copy()
                    self.已复制技能列表.append(技能数据)
        
        if self.已复制技能列表:
            self.显示提示(f"已复制 {len(self.已复制技能列表)} 个技能 (Ctrl+C)", 显示弹窗=False)
        
        return "break"
    
    # 新增：快捷键粘贴技能（参考道具编辑器逻辑）
    def 快捷键粘贴技能(self, event=None):
        """按ID顺序粘贴技能到连续目标，覆盖原有数据，支持Ctrl+V"""
        # 检查是否有复制的技能
        if not self.已复制技能列表:
            messagebox.showinfo("提示", "没有可粘贴的技能，请先复制技能")
            return "break"
        
        复制数量 = len(self.已复制技能列表)
        if 复制数量 == 0:
            messagebox.showinfo("提示", "没有可粘贴的技能，请先复制技能")
            return "break"
        
        # 获取选中的起始技能
        选中索引 = self.技能列表框.curselection()
        if not 选中索引:
            messagebox.showinfo("提示", "请先选择一个要开始粘贴的技能")
            return "break"
        
        # 获取起始技能ID
        起始索引 = 选中索引[0]
        起始文本 = self.技能列表框.get(起始索引)
        起始匹配 = re.search(r'ID: (\d+)', 起始文本)
        if not 起始匹配:
            messagebox.showinfo("提示", "选中的技能无效")
            return "break"
        
        起始ID = 起始匹配.group(1)
        if 起始ID not in self.技能列表:
            messagebox.showinfo("提示", "选中的技能不存在")
            return "break"
        
        # 获取所有技能ID并按数字排序
        所有技能ID = sorted([int(id) for id in self.技能列表.keys()])
        起始位置 = 所有技能ID.index(int(起始ID))
        
        # 计算目标技能数量（与复制数量一致）
        需要的数量 = 复制数量
        目标技能ID列表 = []
        
        # 从起始位置选取连续目标技能
        for i in range(需要的数量):
            目标位置 = 起始位置 + i
            if 目标位置 < len(所有技能ID):
                目标技能ID列表.append(str(所有技能ID[目标位置]))
            else:
                messagebox.showinfo(
                    "提示", 
                    f"只能找到 {i} 个可用目标技能，无法完成 {需要的数量} 个技能的粘贴"
                )
                return "break"
        
        # 执行粘贴（覆盖目标技能数据，保留目标ID）
        for i, 目标ID in enumerate(目标技能ID列表):
            # 复制技能数据，保留目标ID
            新技能数据 = self.已复制技能列表[i].copy()
            
            # 处理图标：复制新图标文件，避免原图标被多技能引用
            旧图标相对路径 = 新技能数据.get("图标相对路径", "")
            if 旧图标相对路径:
                try:
                    旧图标绝对路径 = os.path.join(self.项目根目录, 旧图标相对路径)
                    if os.path.exists(旧图标绝对路径):
                        # 生成新图标文件名
                        扩展名 = os.path.splitext(旧图标绝对路径)[1].lower()
                        新文件名 = f"skill_icon_{uuid.uuid4().hex}{扩展名}"
                        新图标绝对路径 = os.path.join(self.图片目录, 新文件名)
                        
                        # 复制图标文件
                        shutil.copy2(旧图标绝对路径, 新图标绝对路径)
                        
                        # 计算新的相对路径
                        新图标相对路径 = os.path.relpath(新图标绝对路径, self.项目根目录)
                        新图标相对路径 = 新图标相对路径.replace('/', '\\')
                        
                        # 更新图标路径
                        新技能数据["图标相对路径"] = 新图标相对路径
                except Exception as e:
                    messagebox.showwarning("警告", f"复制图标时出错：{str(e)}\n将使用原图标路径")
            
            # 覆盖目标技能数据（保留目标ID）
            self.技能列表[目标ID] = 新技能数据
        
        # 更新界面
        self.更新技能列表()
        # 重新加载起始技能
        self.加载技能(起始ID)
        
        # 选中所有粘贴后的技能
        for 目标ID in 目标技能ID列表:
            for idx, 技能文本 in enumerate(self.技能列表框.get(0, tk.END)):
                if f"ID: {目标ID}" in 技能文本:
                    self.技能列表框.selection_set(idx)
                    break
        
        self.显示提示(f"已按ID顺序粘贴 {复制数量} 个技能（从ID: {起始ID} 开始）")
        return "break"
    
    def 显示提示(self, 消息, 成功=True, 显示弹窗=False):
        """显示操作提示"""
        self.状态变量.set(消息)
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
        """初始化默认配置文件"""
        if not os.path.exists(self.系统文件):
            默认技能 = {
                "2001": {
                    "名称": "普通攻击",
                    "图标相对路径": "",
                    "伤害": 5.0,
                    "消耗": 0.0,
                    "伤害类型": "物理",
                    "目标": 1.0,
                    "射程": 1.0,
                    "效果": {"伤害": 5.0},
                    "伤害倍率": 1.0,
                    "描述": "基础物理攻击，对单个目标造成伤害",
                    "类型": "主动"
                },
                "2002": {
                    "名称": "火球术",
                    "图标相对路径": "",
                    "伤害": 8.0,
                    "消耗": 3.0,
                    "伤害类型": "魔法",
                    "目标": 1.0,
                    "射程": 3.0,
                    "效果": {"火焰伤害": 8.0},
                    "伤害倍率": 1.2,
                    "描述": "释放火球攻击单个目标，造成魔法伤害",
                    "类型": "主动"
                },
                "2003": {
                    "名称": "生命恢复",
                    "图标相对路径": "",
                    "伤害": 0.0,
                    "消耗": 5.0,
                    "伤害类型": "魔法",
                    "目标": 1.0,
                    "射程": 2.0,
                    "效果": {"恢复": 10.0},
                    "伤害倍率": 1.0,
                    "描述": "恢复目标一定量的生命值",
                    "类型": "主动"
                }
            }
            try:
                with open(self.系统文件, 'w', encoding='utf-8') as f:
                    json.dump(默认技能, f, ensure_ascii=False, indent=2)
                self.显示提示(f"已创建默认技能数据: {self.系统文件}")
            except Exception as e:
                messagebox.showerror("初始化错误", f"无法创建{self.系统文件}：{str(e)}")
        
        if not os.path.exists(self.类型文件):
            默认类型 = {
                "damage_types": self.伤害类型列表,
                "skill_types": self.技能类型列表
            }
            try:
                with open(self.类型文件, 'w', encoding='utf-8') as f:
                    json.dump(默认类型, f, ensure_ascii=False, indent=2)
                self.显示提示(f"已创建默认类型数据: {self.类型文件}")
            except Exception as e:
                messagebox.showerror("初始化错误", f"无法创建{self.类型文件}：{str(e)}")
        
        # 初始化skill_att.json（存储效果类型历史）
        if not os.path.exists(self.效果历史文件):
            默认效果历史 = {
                "effect_types": [
                    "伤害",
                    "恢复",
                    "火焰伤害"
                ]
            }
            
            try:
                with open(self.效果历史文件, 'w', encoding='utf-8') as f:
                    json.dump(默认效果历史, f, ensure_ascii=False, indent=2)
                self.显示提示(f"已创建默认效果历史数据: {self.效果历史文件}")
            except Exception as e:
                messagebox.showerror("初始化错误", f"无法创建{self.效果历史文件}：{str(e)}")
    
    def 设置拖放功能(self):
        """配置窗口接受图片拖拽"""
        if not 支持拖放:
            self.图标预览.config(text="请先安装tkinterdnd2以支持拖拽\n或点击下方按钮选择图片")
            return
            
        self.主窗口.drop_target_register(DND_FILES)
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
        if not self.当前技能ID:
            messagebox.showinfo("提示", "请先选择一个技能再设置图标")
            return
            
        文件列表 = self.主窗口.tk.splitlist(事件.data)
        for 文件 in 文件列表:
            if self.是图片文件(文件):
                self.处理图标(文件)
                break
    
    def 是图片文件(self, 文件路径):
        """检查文件是否为图片"""
        图片扩展名 = ('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff')
        return 文件路径.lower().endswith(图片扩展名)
    
    def 加载数据(self):
        """加载技能数据（兼容旧数据）"""
        if os.path.exists(self.系统文件):
            try:
                with open(self.系统文件, 'r', encoding='utf-8') as f:
                    self.技能列表 = json.load(f)
                
                补充射程数量 = 0
                转换路径数量 = 0
                
                for 技能ID, 技能数据 in self.技能列表.items():
                    # 补充射程字段
                    if "射程" not in 技能数据:
                        技能数据["射程"] = 1.0
                        补充射程数量 += 1
                    
                    # 转换旧图标路径
                    图标相对路径 = ""
                    if "源图片路径" in 技能数据 and 技能数据["源图片路径"]:
                        try:
                            源绝对路径 = 技能数据["源图片路径"]
                            if os.path.exists(源绝对路径):
                                图标相对路径 = str(Path(源绝对路径).relative_to(self.项目根目录))
                                图标相对路径 = 图标相对路径.replace('/', '\\')
                                转换路径数量 += 1
                        except Exception as e:
                            print(f"转换源图片路径失败（ID:{技能ID}）: {str(e)}")
                    elif "图标路径" in 技能数据 and 技能数据["图标路径"].startswith("res://"):
                        try:
                            图标相对路径 = 技能数据["图标路径"][5:]
                            图标相对路径 = 图标相对路径.replace('/', '\\')
                            验证绝对路径 = os.path.join(self.项目根目录, 图标相对路径)
                            if os.path.exists(验证绝对路径):
                                转换路径数量 += 1
                            else:
                                图标相对路径 = ""
                        except Exception as e:
                            print(f"转换res路径失败（ID:{技能ID}）: {str(e)}")
                    
                    # 更新路径并删除旧键
                    if 图标相对路径:
                        技能数据["图标相对路径"] = 图标相对路径
                    for 旧键 in ["图标路径", "源图片路径"]:
                        if 旧键 in 技能数据:
                            del 技能数据[旧键]
                
                # 保存兼容后的数据
                if 补充射程数量 > 0 or 转换路径数量 > 0:
                    with open(self.系统文件, 'w', encoding='utf-8') as f:
                        json.dump(self.技能列表, f, ensure_ascii=False, indent=2)
                    提示 = []
                    if 补充射程数量 > 0:
                        提示.append(f"补充{补充射程数量}个技能射程")
                    if 转换路径数量 > 0:
                        提示.append(f"转换{转换路径数量}个技能图标路径")
                    self.显示提示(" | ".join(提示), 显示弹窗=False)
                
                self.显示提示(f"已加载{len(self.技能列表)}个技能", 显示弹窗=False)
            except Exception as e:
                messagebox.showerror("加载错误", f"无法加载{self.系统文件}：{str(e)}")
                self.技能列表 = {}
        else:
            self.保存数据()
    
    def 保存数据(self):
        """保存技能数据"""
        self.保存当前技能()
        try:
            with open(self.系统文件, 'w', encoding='utf-8') as f:
                json.dump(self.技能列表, f, ensure_ascii=False, indent=2)
            self.显示提示(f"已保存到 {self.系统文件} (Ctrl+S)",显示弹窗=False)
        except Exception as e:
            messagebox.showerror("保存错误", f"无法保存{self.系统文件}：{str(e)}")
        self.刷新技能列表()
    def 保存当前技能(self):
        """保存当前编辑的技能"""
        if not self.当前技能ID or self.当前技能ID not in self.技能列表:
            return
        
        # 数值转换为浮点数（失败则保留文本）
        def 转换为浮点数(文本, 字段名):
            if 文本.strip() == "":
                return 0.0 if 字段名 != "射程" else 1.0
            try:
                return float(文本)
            except ValueError:
                self.显示提示(f"{字段名}'{文本}'不是有效数字，按文本保存", 成功=False)
                return 文本
        
        # 收集数据（仅保留图标相对路径）
        self.技能列表[self.当前技能ID] = {
            "名称": self.名称变量.get(),
            "图标相对路径": self.图标相对路径变量.get(),
            "伤害": 转换为浮点数(self.伤害变量.get(), "伤害"),
            "消耗": 转换为浮点数(self.消耗变量.get(), "消耗"),
            "伤害类型": self.伤害类型变量.get(),
            "目标": 转换为浮点数(self.目标变量.get(), "目标"),
            "射程": 转换为浮点数(self.射程变量.get(), "射程"),
            "效果": self.获取效果数据(),
            "伤害倍率": 转换为浮点数(self.伤害倍率变量.get(), "伤害倍率"),
            "描述": self.描述文本框.get(1.0, tk.END).strip(),
            "类型": self.技能类型变量.get()
        }
    
    def 获取效果数据(self):
        """从效果列表获取数据（优先浮点数）"""
        效果 = {}
        for 项 in self.效果树.get_children():
            数值 = self.效果树.item(项, "values")
            if len(数值) >= 2 and 数值[0]:
                键 = 数值[0]
                值文本 = 数值[1].strip()
                try:
                    效果[键] = float(值文本)
                except ValueError:
                    效果[键] = 值文本
        return 效果
    
    def 加载类型数据(self):
        """加载伤害类型和技能类型数据"""
        if os.path.exists(self.类型文件):
            try:
                with open(self.类型文件, 'r', encoding='utf-8') as f:
                    数据 = json.load(f)
                    if "damage_types" in 数据:
                        self.伤害类型列表 = 数据["damage_types"]
                    if "skill_types" in 数据:
                        self.技能类型列表 = 数据["skill_types"]
                self.显示提示(f"已加载类型数据", 显示弹窗=False)
            except Exception as e:
                messagebox.showerror("加载错误", f"无法加载类型数据：{str(e)}")
        else:
            self.保存类型数据()
    
    def 保存类型数据(self):
        """保存类型数据"""
        try:
            with open(self.类型文件, 'w', encoding='utf-8') as f:
                json.dump({
                    "damage_types": self.伤害类型列表,
                    "skill_types": self.技能类型列表
                }, f, ensure_ascii=False, indent=2)
            self.显示提示("类型数据已更新")
        except Exception as e:
            messagebox.showerror("保存错误", f"无法保存类型数据：{str(e)}")
    
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
    
    def 添加效果类型到历史(self, 类型名称):
        """添加效果类型到历史记录（去重）"""
        if 类型名称 and 类型名称 not in self.效果类型历史:
            self.效果类型历史.append(类型名称)
            self.保存效果类型历史()
    
    def 创建界面组件(self):
        """创建UI（更新列表标题提示快捷键）"""
        # 主框架
        self.主框架 = ttk.Frame(self.主窗口, padding="10")
        self.主框架.pack(fill=tk.BOTH, expand=True)
        
        # 左侧技能列表（更新标题提示快捷键）
        左侧框架 = ttk.LabelFrame(self.主框架, text="技能列表 (Ctrl+C复制 | Ctrl+V粘贴)", padding="5")
        左侧框架.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=(0, 10))
        
        self.技能列表框 = tk.Listbox(左侧框架, width=30, height=30, selectmode=tk.EXTENDED)
        self.技能列表框.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        self.技能列表框.bind('<<ListboxSelect>>', self.处理技能选择)
        
        滚动条 = ttk.Scrollbar(左侧框架, orient=tk.VERTICAL, command=self.技能列表框.yview)
        滚动条.pack(side=tk.RIGHT, fill=tk.Y)
        self.技能列表框.config(yscrollcommand=滚动条.set)
        
        # 左侧按钮（保持不变）
        按钮框架 = ttk.Frame(左侧框架, padding="5")
        按钮框架.pack(fill=tk.X)
        ttk.Button(按钮框架, text="添加技能", command=self.添加技能).pack(fill=tk.X, pady=2)
        ttk.Button(按钮框架, text="拷贝技能", command=self.拷贝技能).pack(fill=tk.X, pady=2)
        ttk.Button(按钮框架, text="删除技能", command=self.删除技能).pack(fill=tk.X, pady=2)  # 更新按钮文本
        ttk.Button(按钮框架, text="废弃技能", command=self.废弃技能).pack(fill=tk.X, pady=2)
        ttk.Button(按钮框架, text="刷新列表", command=self.刷新技能列表).pack(fill=tk.X, pady=2)
        ttk.Button(按钮框架, text="保存所有 (Ctrl+S)", command=self.保存数据).pack(fill=tk.X, pady=2)
        
        # 提示设置（保持不变）
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
        
        # 上半部分：基本信息 + 图标
        右上框架 = ttk.Frame(右侧框架)
        右上框架.pack(side=tk.TOP, fill=tk.X, expand=False)
        
        # 技能基本信息（保持不变）
        基本信息框架 = ttk.LabelFrame(右上框架, text="基本信息（含射程）", padding="10")
        基本信息框架.pack(side=tk.LEFT, fill=tk.X, expand=True, pady=(0, 10), padx=(0, 10))
        
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
        
        # 伤害
        ttk.Label(表单网格, text="伤害:").grid(row=2, column=0, sticky=tk.W, pady=5, padx=5)
        self.伤害变量 = tk.StringVar()
        伤害框架 = ttk.Frame(表单网格)
        伤害框架.grid(row=2, column=1, sticky=tk.W, pady=5)
        ttk.Entry(伤害框架, textvariable=self.伤害变量, width=20).pack(side=tk.LEFT)
        ttk.Label(伤害框架, text="(浮点数，如5.0)").pack(side=tk.LEFT, padx=5, fill=tk.Y, anchor=tk.CENTER)
        
        # 消耗
        ttk.Label(表单网格, text="消耗:").grid(row=3, column=0, sticky=tk.W, pady=5, padx=5)
        self.消耗变量 = tk.StringVar()
        消耗框架 = ttk.Frame(表单网格)
        消耗框架.grid(row=3, column=1, sticky=tk.W, pady=5)
        ttk.Entry(消耗框架, textvariable=self.消耗变量, width=20).pack(side=tk.LEFT)
        ttk.Label(消耗框架, text="(浮点数，如3.0)").pack(side=tk.LEFT, padx=5, fill=tk.Y, anchor=tk.CENTER)
        
        # 伤害类型
        ttk.Label(表单网格, text="伤害类型:").grid(row=4, column=0, sticky=tk.W, pady=5, padx=5)
        self.伤害类型变量 = tk.StringVar()
        伤害类型框架 = ttk.Frame(表单网格)
        伤害类型框架.grid(row=4, column=1, sticky=tk.W, pady=5)
        ttk.Combobox(伤害类型框架, textvariable=self.伤害类型变量, values=self.伤害类型列表, width=20).pack(side=tk.LEFT)
        ttk.Button(伤害类型框架, text="添加类型", command=self.添加伤害类型).pack(side=tk.LEFT, padx=5)
        
        # 目标
        ttk.Label(表单网格, text="目标:").grid(row=5, column=0, sticky=tk.W, pady=5, padx=5)
        self.目标变量 = tk.StringVar()
        目标框架 = ttk.Frame(表单网格)
        目标框架.grid(row=5, column=1, sticky=tk.W, pady=5)
        ttk.Entry(目标框架, textvariable=self.目标变量, width=20).pack(side=tk.LEFT)
        ttk.Label(目标框架, text="(浮点数，如1.0)").pack(side=tk.LEFT, padx=5, fill=tk.Y, anchor=tk.CENTER)
        
        # 射程
        ttk.Label(表单网格, text="射程:").grid(row=6, column=0, sticky=tk.W, pady=5, padx=5)
        self.射程变量 = tk.StringVar()
        射程框架 = ttk.Frame(表单网格)
        射程框架.grid(row=6, column=1, sticky=tk.W, pady=5)
        ttk.Entry(射程框架, textvariable=self.射程变量, width=20).pack(side=tk.LEFT)
        ttk.Label(射程框架, text="(浮点数，通用默认1.0)").pack(side=tk.LEFT, padx=5, fill=tk.Y, anchor=tk.CENTER)
        
        # 伤害倍率
        ttk.Label(表单网格, text="伤害倍率:").grid(row=7, column=0, sticky=tk.W, pady=5, padx=5)
        self.伤害倍率变量 = tk.StringVar()
        倍率框架 = ttk.Frame(表单网格)
        倍率框架.grid(row=7, column=1, sticky=tk.W, pady=5)
        ttk.Entry(倍率框架, textvariable=self.伤害倍率变量, width=20).pack(side=tk.LEFT)
        ttk.Label(倍率框架, text="(浮点数，如1.2)").pack(side=tk.LEFT, padx=5, fill=tk.Y, anchor=tk.CENTER)
        
        # 技能类型
        ttk.Label(表单网格, text="类型:").grid(row=8, column=0, sticky=tk.W, pady=5, padx=5)
        self.技能类型变量 = tk.StringVar()
        ttk.Combobox(表单网格, textvariable=self.技能类型变量, values=self.技能类型列表, width=20).grid(row=8, column=1, sticky=tk.W, pady=5)
        
        # 描述
        ttk.Label(基本信息框架, text="描述:").pack(anchor=tk.W, pady=(10, 5))
        self.描述文本框 = tk.Text(基本信息框架, height=4, width=60)
        self.描述文本框.pack(fill=tk.X, pady=(0, 10))
        
        # 图标区域（保持不变）
        图标框架 = ttk.LabelFrame(右上框架, text="图标", padding="5")
        图标框架.pack(side=tk.RIGHT, fill=tk.Y, anchor=tk.NE, pady=(0, 10))
        
        图标网格 = ttk.Frame(图标框架)
        图标网格.pack(fill=tk.X)
        
        ttk.Label(图标网格, text="图标相对路径:").grid(row=0, column=0, sticky=tk.W, pady=5, padx=5)
        self.图标相对路径变量 = tk.StringVar()
        ttk.Entry(图标网格, textvariable=self.图标相对路径变量, width=30, state="readonly").grid(row=0, column=1, sticky=tk.W, pady=5)
        
        # 图标预览和按钮
        图标预览框架 = ttk.Frame(图标框架)
        图标预览框架.pack(fill=tk.X, pady=10)
        
        预览容器 = ttk.Frame(图标预览框架, width=240, height=80)
        预览容器.pack_propagate(False)
        预览容器.pack(side=tk.LEFT, padx=10)
        
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
        
        # 效果列表（下方，保持不变）
        效果框架 = ttk.LabelFrame(右侧框架, text="效果列表 (值优先浮点数，如10.0)", padding="10")
        效果框架.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        
        # 效果按钮
        效果按钮框架 = ttk.Frame(效果框架)
        效果按钮框架.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(效果按钮框架, text="添加效果", command=self.添加效果).pack(side=tk.LEFT, padx=2)
        ttk.Button(效果按钮框架, text="从历史添加", command=self.从历史添加效果).pack(side=tk.LEFT, padx=2)
        ttk.Button(效果按钮框架, text="删除选中", command=self.删除选中效果).pack(side=tk.LEFT, padx=2)
        ttk.Button(效果按钮框架, text="同步到同类型", command=self.同步效果到同类型).pack(side=tk.LEFT, padx=2)
        ttk.Button(效果按钮框架, text="复制选中", command=self.复制效果).pack(side=tk.LEFT, padx=2)
        ttk.Button(效果按钮框架, text="粘贴", command=self.粘贴效果).pack(side=tk.LEFT, padx=2)
        
        # 效果列表 - 启用多选模式
        列 = ("key", "value")
        self.效果树 = ttk.Treeview(效果框架, columns=列, show="headings", height=10, selectmode=tk.EXTENDED)
        
        self.效果树.heading("key", text="效果")
        self.效果树.heading("value", text="值 (优先浮点数，如10.0)")
        
        self.效果树.column("key", width=200, anchor=tk.W)
        self.效果树.column("value", width=200, anchor=tk.W)
        
        效果滚动条 = ttk.Scrollbar(效果框架, orient=tk.VERTICAL, command=self.效果树.yview)
        self.效果树.configure(yscrollcommand=效果滚动条.set)
        
        self.效果树.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        效果滚动条.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 双击编辑
        self.效果树.bind("<Double-1>", self.处理效果双击)
        self.效果树.bind("<<TreeviewSelect>>", self.处理效果选择)
        
        # 快捷键
        self.效果树.bind("<Control-c>", self.复制效果)
        self.效果树.bind("<Control-v>", self.粘贴效果)
        
        # 状态栏
        状态栏 = ttk.Label(self.主窗口, textvariable=self.状态变量, relief=tk.SUNKEN, anchor=tk.W)
        状态栏.pack(side=tk.BOTTOM, fill=tk.X)
        
        # 更新技能列表
        self.更新技能列表()
        
        # 绑定编辑框内容变化事件
        self.名称变量.trace_add("write", lambda *args: self.状态变量.set("有未保存的更改 (按Ctrl+S保存)"))
        self.伤害变量.trace_add("write", lambda *args: self.状态变量.set("有未保存的更改 (按Ctrl+S保存)"))
        self.消耗变量.trace_add("write", lambda *args: self.状态变量.set("有未保存的更改 (按Ctrl+S保存)"))
        self.伤害类型变量.trace_add("write", lambda *args: self.状态变量.set("有未保存的更改 (按Ctrl+S保存)"))
        self.目标变量.trace_add("write", lambda *args: self.状态变量.set("有未保存的更改 (按Ctrl+S保存)"))
        self.射程变量.trace_add("write", lambda *args: self.状态变量.set("有未保存的更改 (按Ctrl+S保存)"))
        self.伤害倍率变量.trace_add("write", lambda *args: self.状态变量.set("有未保存的更改 (按Ctrl+S保存)"))
        self.技能类型变量.trace_add("write", lambda *args: self.状态变量.set("有未保存的更改 (按Ctrl+S保存)"))
        self.描述文本框.bind("<<Modified>>", lambda e: self.状态变量.set("有未保存的更改 (按Ctrl+S保存)") or self.描述文本框.edit_modified(False))
        
        # 窗口关闭事件
        self.主窗口.protocol("WM_DELETE_WINDOW", self.处理关闭)
    
    def 废弃技能(self):
        """将选中的技能标记为废弃，修改名称并保留ID"""
        选中索引 = self.技能列表框.curselection()
        if not 选中索引:
            messagebox.showinfo("提示", "请先选择一个或多个技能")
            return
            
        # 保存当前编辑的技能
        self.保存当前技能()
        
        # 处理每个选中的技能
        废弃数量 = 0
        for idx in 选中索引:
            选中文本 = self.技能列表框.get(idx)
            匹配 = re.search(r'ID: (\d+)', 选中文本)
            if 匹配:
                技能ID = 匹配.group(1)
                if 技能ID in self.技能列表:
                    # 修改技能名称为"废弃"并保留ID
                    self.技能列表[技能ID]["名称"] = f"废弃_{self.技能列表[技能ID]['名称']}"
                    废弃数量 += 1
        
        # 更新列表显示
        self.更新技能列表()
        
        # 如果当前编辑的技能被废弃，更新显示
        if self.当前技能ID and self.当前技能ID in [re.search(r'ID: (\d+)', self.技能列表框.get(idx)).group(1) for idx in 选中索引 if re.search(r'ID: (\d+)', self.技能列表框.get(idx))]:
            self.加载技能(self.当前技能ID)
        
        self.显示提示(f"已将 {废弃数量} 个技能标记为废弃")
    
    def 同步效果到同类型(self):
        """将当前技能的效果同步到所有同类型技能"""
        if not self.当前技能ID or self.当前技能ID not in self.技能列表:
            messagebox.showinfo("提示", "请先选择一个技能")
            return
            
        # 保存当前编辑的效果
        self.保存当前技能()
        
        # 获取当前技能的类型和效果
        当前技能 = self.技能列表[self.当前技能ID]
        当前类型 = 当前技能.get("类型")
        当前效果 = 当前技能.get("效果", {})
        
        if not 当前类型:
            messagebox.showinfo("提示", "当前技能没有设置类型")
            return
        
        # 查找所有同类型的技能
        同类型技能 = [
            技能ID for 技能ID, 技能数据 in self.技能列表.items()
            if 技能数据.get("类型") == 当前类型 and 技能ID != self.当前技能ID
        ]
        
        if not 同类型技能:
            messagebox.showinfo("提示", f"没有找到其他 '{当前类型}' 类型的技能")
            return
        
        # 创建一个对话框让用户选择初始化值类型
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
        ttk.Label(主框架, text="请选择新效果的初始化值:").pack(anchor=tk.W, pady=(0, 15))
        
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
            f"将为所有 {len(同类型技能)} 个 '{当前类型}' 类型的技能\n"
            f"添加缺失的效果并设置默认值为 {值描述}，是否继续？"
        ):
            return
        
        # 记录新增的效果数量
        总添加数 = 0
        
        # 为每个同类型技能添加缺失的效果
        for 技能ID in 同类型技能:
            技能 = self.技能列表[技能ID]
            技能效果 = 技能.get("效果", {})
            
            # 检查并添加缺失的效果
            for 效果名称 in 当前效果:
                if 效果名称 not in 技能效果:
                    技能效果[效果名称] = 初始化值  # 设置用户选择的默认值
                    总添加数 += 1
            
            # 更新技能效果
            技能["效果"] = 技能效果
        
        # 刷新当前技能的效果列表
        self.加载效果(当前效果)
        
        self.显示提示(
            f"已完成同步，共为 {len(同类型技能)} 个 '{当前类型}' 类型技能\n"
            f"添加了 {总添加数} 个效果（默认值: {值描述}）"
        )
    
    def 刷新技能列表(self):
        """手动刷新技能列表"""
        # 保存当前编辑的内容
        self.保存当前技能()
        # 重新加载数据
        self.加载数据()
        # 更新列表显示
        self.更新技能列表()
        # 保持当前选中项
        if self.当前技能ID and self.当前技能ID in self.技能列表:
            for i, 技能文本 in enumerate(self.技能列表框.get(0, tk.END)):
                if f"ID: {self.当前技能ID}" in 技能文本:
                    self.技能列表框.selection_set(i)
                    self.技能列表框.see(i)
                    break
        self.显示提示("技能列表已刷新",显示弹窗=False)
    
    def 切换弹窗显示(self):
        """切换是否显示成功提示弹窗"""
        self.显示成功提示弹窗 = self.弹窗变量.get()
        状态 = "已启用" if self.显示成功提示弹窗 else "已禁用"
        self.显示提示(f"成功提示弹窗{状态}", 显示弹窗=False)
    
    def 拷贝技能(self):
        """复制当前选中的技能（保留浮点数属性，含射程）"""
        # 获取所有选中的技能
        选中索引 = self.技能列表框.curselection()
        if not 选中索引:
            messagebox.showinfo("提示", "请先选择一个或多个技能")
            return
            
        # 保存当前编辑的技能
        self.保存当前技能()
        
        # 复制每个选中的技能
        复制数量 = 0
        for idx in 选中索引:
            选中文本 = self.技能列表框.get(idx)
            匹配 = re.search(r'ID: (\d+)', 选中文本)
            if 匹配:
                技能ID = 匹配.group(1)
                if 技能ID in self.技能列表:
                    # 获取当前技能数据
                    当前技能 = self.技能列表[技能ID]
                    
                    # 生成新ID
                    新ID = 2001
                    while str(新ID) in self.技能列表:
                        新ID += 1
                    新ID = str(新ID)
                    
                    # 复制技能数据
                    新名称 = f"{当前技能['名称']}"
                    新技能 = 当前技能.copy()
                    新技能["名称"] = 新名称
                    
                    # 如果有图标，创建图标的副本
                    if 当前技能.get("图标相对路径"):
                        try:
                            原始绝对路径 = os.path.join(self.项目根目录, 当前技能["图标相对路径"])
                            if os.path.exists(原始绝对路径):
                                扩展名 = os.path.splitext(原始绝对路径)[1].lower()
                                新文件名 = f"{os.path.splitext(os.path.basename(原始绝对路径))[0]}_copy{uuid.uuid4().hex[:6]}{扩展名}"
                                新绝对路径 = os.path.join(self.图片目录, 新文件名)
                                
                                # 复制文件
                                shutil.copy2(原始绝对路径, 新绝对路径)
                                
                                # 计算新的相对路径
                                新相对路径 = os.path.relpath(新绝对路径, self.项目根目录)
                                新相对路径 = 新相对路径.replace('/', '\\')
                                
                                # 更新图标路径
                                新技能["图标相对路径"] = 新相对路径
                        except Exception as e:
                            messagebox.showwarning("警告", f"复制图片时出错：{str(e)}\n将使用原技能的图片")
                    
                    # 添加新技能
                    self.技能列表[新ID] = 新技能
                    复制数量 += 1
        
        # 更新列表
        self.更新技能列表()
        self.显示提示(f"已复制 {复制数量} 个技能（含射程）")
    
    def 处理关闭(self):
        """窗口关闭时保存数据"""
        self.保存数据()
        self.主窗口.destroy()
    
    def 更新技能列表(self):
        """更新技能列表"""
        self.技能列表框.delete(0, tk.END)
        for 技能ID, 技能数据 in self.技能列表.items():
            self.技能列表框.insert(tk.END, f"{技能数据.get('名称', '未命名')} (ID: {技能ID})")
        self.显示提示(f"技能列表已更新，共 {len(self.技能列表)} 个技能(含射程)", 显示弹窗=False)
    
    def 关闭活跃编辑框(self):
        """关闭当前活跃的编辑框"""
        if self.活跃编辑框:
            try:
                self.活跃编辑框.destroy()
            except:
                pass
            self.活跃编辑框 = None
    
    def 处理技能选择(self, 事件):
        """处理技能选择事件"""
        self.关闭活跃编辑框()
        self.保存当前技能()
        
        选中项 = self.技能列表框.curselection()
        if not 选中项:
            return
            
        # 如果选择了多个，只加载第一个
        选中文本 = self.技能列表框.get(选中项[0])
        匹配 = re.search(r'ID: (\d+)', 选中文本)
        if 匹配:
            技能ID = 匹配.group(1)
            self.加载技能(技能ID)
            技能名称 = self.技能列表[技能ID].get("名称", "未命名")
            self.显示提示(f"已选择技能: {技能名称} (ID: {技能ID}) (含射程)", 显示弹窗=False)
    
    def 加载技能(self, 技能ID):
        """加载技能数据到表单"""
        if 技能ID not in self.技能列表:
            return
            
        self.当前技能ID = 技能ID
        技能 = self.技能列表[技能ID]
        
        # 填充表单
        self.ID变量.set(技能ID)
        self.名称变量.set(技能.get("名称", ""))
        
        # 数值字段显示
        self.伤害变量.set(str(技能.get("伤害", 0.0)) if isinstance(技能.get("伤害", 0.0), (int, float)) else 技能.get("伤害", ""))
        self.消耗变量.set(str(技能.get("消耗", 0.0)) if isinstance(技能.get("消耗", 0.0), (int, float)) else 技能.get("消耗", ""))
        
        self.伤害类型变量.set(技能.get("伤害类型", ""))
        
        self.目标变量.set(str(技能.get("目标", 1.0)) if isinstance(技能.get("目标", 1.0), (int, float)) else 技能.get("目标", ""))
        self.射程变量.set(str(技能.get("射程", 1.0)) if isinstance(技能.get("射程", 1.0), (int, float)) else 技能.get("射程", ""))
        self.伤害倍率变量.set(str(技能.get("伤害倍率", 1.0)) if isinstance(技能.get("伤害倍率", 1.0), (int, float)) else 技能.get("伤害倍率", ""))
        
        self.技能类型变量.set(技能.get("类型", ""))
        self.描述文本框.delete(1.0, tk.END)
        self.描述文本框.insert(tk.END, 技能.get("描述", ""))
        
        # 图标相对路径
        图标相对路径 = 技能.get("图标相对路径", "")
        self.图标相对路径变量.set(图标相对路径)
        
        # 加载图标预览
        图标绝对路径 = os.path.join(self.项目根目录, 图标相对路径) if 图标相对路径 else ""
        self.加载图标预览(图标绝对路径)
        
        # 加载效果列表
        self.加载效果(技能.get("效果", {}))
    
    def 加载效果(self, 效果):
        """加载效果列表"""
        # 清空现有项
        for 项 in self.效果树.get_children():
            self.效果树.delete(项)
        
        # 添加效果
        for 键, 值 in 效果.items():
            显示值 = str(值) if isinstance(值, (int, float)) else 值
            self.效果树.insert("", tk.END, values=(键, 显示值))
        
        self.显示提示(f"已加载 {len(效果)} 个效果", 显示弹窗=False)
    
    def 加载图标预览(self, 图片绝对路径):
        """加载图标预览"""
        # 清除之前的图片引用
        if hasattr(self.图标预览, 'image'):
            delattr(self.图标预览, 'image')
        
        # 检查路径是否有效
        if not 图片绝对路径 or not isinstance(图片绝对路径, str):
            默认文本 = "点击下方按钮选择图片\n或直接拖拽图片到窗口"
            无拖放文本 = "请先安装tkinterdnd2以支持拖拽\n或点击下方按钮选择图片"
            self.图标预览.config(
                text=默认文本 if 支持拖放 else 无拖放文本, 
                image=""
            )
            return
            
        # 检查文件是否存在
        if not os.path.exists(图片绝对路径) or not os.path.isfile(图片绝对路径):
            self.图标预览.config(text=f"图片文件不存在\n{图片绝对路径}", image="")
            return
            
        try:
            # 尝试打开并显示图片
            图片 = Image.open(图片绝对路径)
            图片.thumbnail((100, 100))
            照片 = ImageTk.PhotoImage(图片)
            self.图标预览.config(image=照片, text="")
            self.图标预览.image = 照片
            self.显示提示(f"已加载图标: {os.path.basename(图片绝对路径)}", 显示弹窗=False)
        except Exception as e:
            self.图标预览.config(text=f"无法加载图片\n{str(e)}", image="")
    
    def 添加技能(self):
        """添加新技能"""
        # 关闭任何活跃的编辑框
        self.关闭活跃编辑框()
        
        # 生成新ID
        新ID = 2001
        while str(新ID) in self.技能列表:
            新ID += 1
        新ID = str(新ID)
        
        # 创建新技能
        self.技能列表[新ID] = {
            "名称": "",
            "图标相对路径": "",
            "伤害": 0.0,
            "消耗": 0.0,
            "伤害类型": "",
            "目标": 1.0,
            "射程": 1.0,
            "效果": {},
            "伤害倍率": 1.0,
            "描述": "",
            "类型": ""
        }
        
        # 更新列表并选中新技能
        self.更新技能列表()
        
        # 选中新技能
        for i, 技能文本 in enumerate(self.技能列表框.get(0, tk.END)):
            if f"ID: {新ID}" in 技能文本:
                self.技能列表框.selection_set(i)
                self.技能列表框.see(i)
                self.处理技能选择(None)
                break
    
    # 修改：删除技能改为保留ID清空信息
    def 删除技能(self):
        """保留ID，仅清空技能内容（不删除ID）"""
        # 关闭任何活跃的编辑框
        self.关闭活跃编辑框()
        
        选中索引 = self.技能列表框.curselection()
        if not 选中索引:
            messagebox.showinfo("提示", "请先选择一个或多个技能")
            return
        
        # 获取选中的技能ID
        选中ID = []
        for idx in 选中索引:
            选中文本 = self.技能列表框.get(idx)
            匹配 = re.search(r'ID: (\d+)', 选中文本)
            if 匹配:
                选中ID.append(匹配.group(1))
        
        if not 选中ID:
            messagebox.showinfo("提示", "未找到选中的技能 ID")
            return
            
        # 确认清空
        if messagebox.askyesno("确认清空", f"确定要清空这 {len(选中ID)} 个技能的内容吗？\nID将会被保留，但所有数据会被清空。"):
            # 记录清空的技能名称
            清空名称 = []
            
            # 逐个清空内容，保留ID
            for 技能ID in 选中ID:
                if 技能ID in self.技能列表:
                    # 记录原名称
                    原名称 = self.技能列表[技能ID].get("名称", "未命名")
                    清空名称.append(原名称)
                    
                    # 删除图标文件
                    self.按ID删除图标文件(技能ID)
                    
                    # 保留ID，清空内容（设置默认空值）
                    self.技能列表[技能ID] = {
                        "名称": f"",  # 标记为已清空
                        "图标相对路径": "",          # 清空图标路径
                        "伤害": 0.0,                # 默认浮点数
                        "消耗": 0.0,                # 默认浮点数
                        "伤害类型": "",             # 清空类型
                        "目标": 1.0,                # 默认目标数
                        "射程": 1.0,                # 默认射程
                        "效果": {},                 # 清空效果
                        "伤害倍率": 1.0,            # 默认倍率
                        "描述": "", # 标记描述
                        "类型": ""                  # 清空类型
                    }
            
            # 如果当前编辑的技能被清空，重新加载显示
            if self.当前技能ID in 选中ID:
                self.加载技能(self.当前技能ID)
        
        # 更新列表
        self.更新技能列表()
        self.显示提示(f"已清空 {len(清空名称)} 个技能的内容，ID已保留")
    
    def 按ID删除图标文件(self, 技能ID):
        """通过技能ID删除图标文件"""
        if 技能ID in self.技能列表:
            图标相对路径 = self.技能列表[技能ID].get("图标相对路径", "")
            if 图标相对路径:
                图标绝对路径 = os.path.join(self.项目根目录, 图标相对路径)
                if os.path.exists(图标绝对路径) and os.path.isfile(图标绝对路径):
                    try:
                        # 检查文件是否在图片目录中，防止误删
                        if str(Path(图标绝对路径).parent) == str(Path(self.图片目录).resolve()):
                            os.remove(图标绝对路径)
                            self.状态变量.set(f"已删除图标: {os.path.basename(图标绝对路径)}")
                    except Exception as e:
                        messagebox.showwarning("警告", f"删除图标时出错：{str(e)}")
    
    def 清空表单(self):
        """清空表单"""
        self.ID变量.set("")
        self.名称变量.set("")
        self.伤害变量.set("")
        self.消耗变量.set("")
        self.伤害类型变量.set("")
        self.目标变量.set("")
        self.射程变量.set("")
        self.伤害倍率变量.set("")
        self.技能类型变量.set("")
        self.描述文本框.delete(1.0, tk.END)
        self.图标相对路径变量.set("")
        
        # 清除图片预览
        if hasattr(self.图标预览, 'image'):
            delattr(self.图标预览, 'image')
        默认文本 = "点击下方按钮选择图片\n或直接拖拽图片到窗口"
        无拖放文本 = "请先安装tkinterdnd2以支持拖拽\n或点击下方按钮选择图片"
        self.图标预览.config(
            text=默认文本 if 支持拖放 else 无拖放文本, 
            image=""
        )
        
        # 清空效果列表
        for 项 in self.效果树.get_children():
            self.效果树.delete(项)
    
    def 添加伤害类型(self):
        """添加新伤害类型"""
        新类型 = simpledialog.askstring("添加伤害类型", "请输入新伤害类型名称:")
        if 新类型 and 新类型 not in self.伤害类型列表:
            self.伤害类型列表.append(新类型)
            self.伤害类型变量.set(新类型)
            self.保存类型数据()
            # 更新伤害类型下拉框
            下拉框 = self.主窗口.nametowidget(self.伤害类型变量._w).master.winfo_children()[0]
            下拉框['values'] = self.伤害类型列表
            self.显示提示(f"已添加新伤害类型: {新类型}")
    
    def 选择图标(self):
        """选择图标文件"""
        if not self.当前技能ID:
            messagebox.showinfo("提示", "请先选择或创建一个技能")
            return
            
        文件路径 = filedialog.askopenfilename(
            title="选择图标",
            filetypes=[("图片文件", "*.png;*.jpg;*.jpeg;*.gif;*.bmp")]
        )
        
        if 文件路径:
            self.处理图标(文件路径)
    
    def 处理图标(self, 文件路径):
        """处理图标文件，复制到项目目录并生成相对路径"""
        try:
            # 验证源文件
            if not os.path.exists(文件路径) or not os.path.isfile(文件路径):
                raise Exception(f"源文件不存在或不是有效文件: {文件路径}")
            
            # 确保图片目录存在
            if not self.确保目录存在(self.图片目录):
                return
            
            # 先删除旧图标
            self.删除图标文件()
            
            # 生成新文件名
            扩展名 = os.path.splitext(文件路径)[1].lower()
            新文件名 = f"skill_icon_{uuid.uuid4().hex}{扩展名}"
            
            # 构建目标路径
            目标绝对路径 = Path(self.图片目录) / 新文件名
            目标绝对路径 = str(目标绝对路径.resolve())
            
            # 复制文件
            shutil.copy2(文件路径, 目标绝对路径)
            
            # 验证复制结果
            if not os.path.exists(目标绝对路径):
                raise Exception(f"文件复制后验证失败: {目标绝对路径}")
            
            # 计算相对路径
            图标相对路径 = os.path.relpath(目标绝对路径, self.项目根目录)
            图标相对路径 = 图标相对路径.replace('/', '\\')
            
            # 更新UI
            self.图标相对路径变量.set(图标相对路径)
            self.加载图标预览(目标绝对路径)
            
            self.显示提示(f"图片已成功添加: {os.path.basename(目标绝对路径)}", 显示弹窗=False)
            self.保存数据()
        except Exception as e:
            messagebox.showerror("图片处理错误", f"处理图片时出错: {str(e)}")
            self.图标相对路径变量.set("")
    
    def 删除图标文件(self):
        """删除当前技能的图标文件"""
        if not self.当前技能ID:
            return
            
        当前图标相对路径 = self.图标相对路径变量.get()
        if 当前图标相对路径:
            当前图标绝对路径 = os.path.join(self.项目根目录, 当前图标相对路径)
            if os.path.exists(当前图标绝对路径) and os.path.isfile(当前图标绝对路径):
                try:
                    if str(Path(当前图标绝对路径).parent) == str(Path(self.图片目录).resolve()):
                        os.remove(当前图标绝对路径)
                        self.显示提示(f"已删除旧图标: {os.path.basename(当前图标绝对路径)}", 显示弹窗=False)
                    else:
                        self.状态变量.set(f"未删除旧图标（不在图片目录中）: {os.path.basename(当前图标绝对路径)}")
                except Exception as e:
                    messagebox.showwarning("警告", f"删除旧图标时出错：{str(e)}")
    
    def 移除图标(self):
        """移除当前技能的图标"""
        if not self.当前技能ID:
            messagebox.showinfo("提示", "请先选择一个技能")
            return
            
        if not self.图标相对路径变量.get():
            messagebox.showinfo("提示", "当前技能没有图标")
            return
            
        if messagebox.askyesno("确认移除", "确定要移除当前技能的图标吗？\n相关图片文件也将被删除。"):
            # 删除图标文件
            self.删除图标文件()
            
            # 清空路径
            self.图标相对路径变量.set("")
            
            # 更新预览
            self.加载图标预览("")
            
            self.显示提示("已移除图标")
    
    def 添加效果(self):
        """添加新效果"""
        self.效果树.insert("", tk.END, values=("效果名", "1.0"))
        self.显示提示("已添加新效果", 显示弹窗=False)
    
    def 从历史添加效果(self):
        """从历史类型中选择添加效果"""
        if not self.效果类型历史:
            messagebox.showinfo("提示", "暂无历史效果类型")
            return
            
        # 创建选择对话框
        选择窗口 = tk.Toplevel(self.主窗口)
        选择窗口.title("选择效果类型")
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
                messagebox.showinfo("提示", "请先选择要删除的效果类型")
                return
            
            类型名称 = 列表框.get(选中项[0])
            if messagebox.askyesno("确认删除", f"确定要删除历史效果类型 '{类型名称}' 吗？"):
                self.效果类型历史.remove(类型名称)
                self.保存效果类型历史()
                # 重新加载列表
                列表框.delete(0, tk.END)
                for 类型 in self.效果类型历史:
                    列表框.insert(tk.END, 类型)
                self.显示提示(f"已删除历史效果类型: {类型名称}", 显示弹窗=False)
        
        # 提示标签
        提示标签 = ttk.Label(选择窗口, text="双击可删除选中的效果类型", font=("微软雅黑", 9))
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
                self.效果树.insert("", tk.END, values=(类型名称, "1.0"))
                self.显示提示(f"已添加效果: {类型名称}", 显示弹窗=False)
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
                菜单.add_command(label="删除此效果类型", command=删除选中历史)
                菜单.post(事件.x_root, 事件.y_root)
        
        列表框.bind("<Double-1>", 双击删除)
        列表框.bind("<Button-3>", 显示右键菜单)
    
    def 处理效果选择(self, 事件):
        """处理效果选中事件"""
        pass
    
    def 删除选中效果(self):
        """删除选中的效果"""
        self.关闭活跃编辑框()
        
        选中项 = self.效果树.selection()
        if not 选中项:
            messagebox.showinfo("提示", "请先选择要删除的效果")
            return
            
        数量 = len(选中项)
        for 项 in 选中项:
            self.效果树.delete(项)
            
        self.显示提示(f"已删除 {数量} 个选中的效果")
    
    def 复制效果(self, 事件=None):
        """复制选中的效果"""
        self.已复制效果 = []
        for 项 in self.效果树.selection():
            数值 = self.效果树.item(项, "values")
            self.已复制效果.append((数值[0], 数值[1]))
        
        if self.已复制效果:
            self.显示提示(f"已复制 {len(self.已复制效果)} 个效果 (Ctrl+C)", 显示弹窗=False)
        
        return "break"
    
    def 粘贴效果(self, 事件=None):
        """粘贴效果"""
        if not self.已复制效果:
            self.状态变量.set("没有可粘贴的效果")
            return "break"
            
        # 获取当前选中位置
        选中项 = self.效果树.selection()
        插入位置 = ""
        
        if 选中项:
            插入位置 = 选中项[-1]
        
        for 效果 in self.已复制效果:
            if 插入位置:
                self.效果树.insert("", tk.AFTER, 插入位置, values=效果)
                插入位置 = self.效果树.get_children()[-1]
            else:
                self.效果树.insert("", tk.END, values=效果)
        
        self.显示提示(f"已粘贴 {len(self.已复制效果)} 个效果 (Ctrl+V)")
        
        return "break"
    
    def 处理效果双击(self, 事件):
        """双击编辑效果项（优先浮点数）"""
        # 关闭任何已存在的编辑框
        self.关闭活跃编辑框()
        
        区域 = self.效果树.identify_region(事件.x, 事件.y)
        if 区域 != "cell":
            return
            
        # 解析列索引
        列字符串 = self.效果树.identify_column(事件.x)
        列 = int(列字符串.replace('#', '')) - 1  # 转换为0-based索引
        
        项 = self.效果树.identify_row(事件.y)
        
        # 获取单元格位置和当前值
        x, y, 宽度, 高度 = self.效果树.bbox(项, 列)
        值 = self.效果树.item(项, "values")[列]
        
        # 创建编辑框
        输入框 = ttk.Entry(self.效果树)
        输入框.place(x=x, y=y, width=宽度, height=高度)
        输入框.insert(0, 值)
        输入框.focus()
        
        # 保存当前编辑框引用
        self.活跃编辑框 = 输入框
        
        # 保存编辑结果（自动转换为浮点数）
        def 保存编辑(事件=None):
            # 检查项目是否仍然存在
            if 项 not in self.效果树.get_children():
                输入框.destroy()
                self.活跃编辑框 = None
                return
                
            新值 = 输入框.get()
            数值列表 = list(self.效果树.item(项, "values"))
            数值列表[列] = 新值
            self.效果树.item(项, values=数值列表)
            
            # 如果是效果名列，添加到历史记录
            if 列 == 0 and 新值:
                self.添加效果类型到历史(新值)
            
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
        
    应用 = 技能编辑器(根窗口)
    根窗口.mainloop()
