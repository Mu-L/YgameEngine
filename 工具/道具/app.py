# cython: language_level=3
# cython: c_string_encoding=utf-8
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog, colorchooser
import json
import os
import sys
from PIL import Image, ImageTk
import uuid
import shutil
from pathlib import Path
import re
import pandas as pd
from datetime import datetime

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

class 道具编辑器:
    def __init__(self, 主窗口):
        self.主窗口 = 主窗口
        self.主窗口.title("Godot道具库编辑器 ver1.3 (支持底色+品质颜色自定义)")
        self.主窗口.geometry("1300x750")
        self.主窗口.minsize(800, 600)
        
        # 初始化状态变量
        self.状态变量 = tk.StringVar(value="就绪 (按Ctrl+S保存)")
        # 计算路径
        self.计算项目路径()
        # ------------------------------
        self.类型属性记录文件 = os.path.join(self.系统文件夹, "item_typecode.json")
        self.类型属性记录 = {}  # 存储结构：{"类型名": [{"属性名": "初始值"}, ...]}
        self.加载类型属性记录()  # 加载历史记录（永不初始化覆盖）
        
        # 新增：列表底色配置初始化（在颜色配置前）
        self.列表底色 = "white"  # 默认底色
        self.是否启用自定义底色 = tk.BooleanVar(value=True)  # 底色启用开关
        # 初始化品质颜色配置（含底色）
        self.初始化颜色配置路径()
        self.加载品质颜色配置()
        # 数据存储
        self.道具列表 = {}
        self.当前道具ID = None
        self.已复制效果 = []  # 用于存储复制的效果
        self.活跃编辑框 = None  # 跟踪当前活跃的编辑框
        self.类型列表 = ["装备", "消耗品", "其他"]
        self.子类型列表 = {
            "装备": ["剑", "法杖", "盔甲"],
            "消耗品": ["药水", "食物"],
            "其他": ["货币", "材料"]
        }
        # 效果类型历史列表
        self.效果类型历史 = []  # 存储历史效果类型，用于复用
        
        # 配置文件路径
        self.图片目录 = os.path.join(self.系统文件夹, "item_icons")  # 存储源图片的目录
        self.系统文件 = os.path.join(self.系统文件夹, "itemsystem.json")
        self.类型文件 = os.path.join(self.系统文件夹, "item_types.json")
        self.颜色配置文件 = os.path.join(self.系统文件夹, "item_color.json")  # 品质+底色配置文件
        self.效果历史文件 = os.path.join(self.系统文件夹, "item_att.json")  # 存储效果类型历史
        
        # 配置提示选项
        self.显示成功弹窗 = True  # 是否显示成功提示弹窗
        
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

    # ------------------------------
    # 新增：类型属性记录（item_typecode.json）相关方法
    # ------------------------------
    def 加载类型属性记录(self):
        """加载item_typecode.json，无文件时创建空文件（不初始化默认值）"""
        try:
            if os.path.exists(self.类型属性记录文件):
                with open(self.类型属性记录文件, 'r', encoding='utf-8') as f:
                    self.类型属性记录 = json.load(f)
                    # 格式校验：确保是{"类型": [{"属性名": "初始值"}, ...]}结构
                    for 类型名, 属性列表 in self.类型属性记录.items():
                        if not isinstance(属性列表, list):
                            self.类型属性记录[类型名] = []
                        else:
                            # 过滤无效属性（必须是字典且含1个键值对）
                            有效属性 = []
                            for 属性 in 属性列表:
                                if isinstance(属性, dict) and len(属性) == 1:
                                    有效属性.append(属性)
                            self.类型属性记录[类型名] = 有效属性
                self.显示提示(f"已加载类型属性记录：{len(self.类型属性记录)}种类型", 显示弹窗=False)
            else:
                # 首次启动：创建空文件（不写默认值，避免覆盖后续记录）
                with open(self.类型属性记录文件, 'w', encoding='utf-8') as f:
                    json.dump({}, f, ensure_ascii=False, indent=2)
                self.类型属性记录 = {}
                self.显示提示(f"已创建空类型属性记录：{self.类型属性记录文件}", 显示弹窗=False)
        except Exception as e:
            messagebox.showerror("记录加载错误", f"加载item_typecode.json失败：{str(e)}\n将创建新空文件")
            # 修复损坏文件：创建空文件
            with open(self.类型属性记录文件, 'w', encoding='utf-8') as f:
                json.dump({}, f, ensure_ascii=False, indent=2)
            self.类型属性记录 = {}

    def 保存类型属性记录(self):
        """保存类型属性记录到item_typecode.json"""
        try:
            with open(self.类型属性记录文件, 'w', encoding='utf-8') as f:
                json.dump(self.类型属性记录, f, ensure_ascii=False, indent=2)
            self.显示提示("类型属性记录已保存", 显示弹窗=False)
        except Exception as e:
            messagebox.showerror("记录保存错误", f"保存item_typecode.json失败：{str(e)}")

    def 自动记录类型属性(self, 道具类型, 属性名, 初始值):
        """
        自动记录新属性到对应类型下
        :param 道具类型: 当前道具的类型（如"武器"）
        :param 属性名: 新添加的效果属性名（如"攻击力"）
        :param 初始值: 该属性的初始值（如"10.0"）
        """
        if not 道具类型 or not 属性名:
            return
        
        # 1. 确保类型在记录中存在
        if 道具类型 not in self.类型属性记录:
            self.类型属性记录[道具类型] = []
        
        # 2. 检查该属性是否已存在（避免重复记录）
        属性已存在 = any(
            属性.get(属性名) is not None 
            for 属性 in self.类型属性记录[道具类型]
        )
        if 属性已存在:
            return
        
        # 3. 新增属性记录（保留初始值）
        self.类型属性记录[道具类型].append({属性名: 初始值})
        # 4. 立即保存记录
        self.保存类型属性记录()
        self.显示提示(f"已记录属性：{道具类型}→{属性名}（初始值：{初始值}）", 显示弹窗=False)
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
            self.项目根目录 = 项目根目录  # 保存项目根目录，用于后续路径计算
            
            # 确保系统文件夹存在
            self.确保目录存在(self.系统文件夹)
            
            # 显示路径信息（调试用）
            print(f"当前执行路径: {当前路径}")
            print(f"项目根目录: {项目根目录}")
            print(f"系统文件夹: {self.系统文件夹}")
            
        except Exception as e:
            messagebox.showerror("路径计算错误", f"无法计算项目路径: {str(e)}")
            # fallback到当前目录
            self.项目根目录 = os.getcwd()
            self.系统文件夹 = os.path.join(self.项目根目录, "系统")
            self.确保目录存在(self.系统文件夹)
    
    # ------------------------------
    # 品质颜色+底色配置相关方法（新增品质颜色编辑逻辑）
    # ------------------------------
    def 初始化颜色配置路径(self):
        """初始化品质颜色+底色配置文件路径"""
        self.颜色配置文件 = os.path.join(self.系统文件夹, "item_color.json")
        self.品质颜色映射 = {}  # 存储：{品质值(float): 文本颜色值(str)}
        self.默认列表颜色 = "black"  # 无匹配品质时的默认文本色
        self.默认列表底色 = "white"  # 无配置时的默认底色

    def 加载品质颜色配置(self):
        """加载品质-文本颜色映射 + 默认底色配置"""
        默认颜色配置 = {
            "说明": "品质值对应文本颜色+列表底色配置（支持RGB格式如'#00FF00'或英文如'green'）",
            "默认颜色": "black",       # 文本默认色
            "默认底色": "white",       # 列表项默认底色
            "品质颜色映射": {
                "1.0": "#00FF00",    # 品质1.0 → 绿色文本
                "2.0": "#0000FF",    # 品质2.0 → 蓝色文本
                "3.0": "#FF00FF",    # 品质3.0 → 紫色文本
                "4.0": "#FFFF00",    # 品质4.0 → 黄色文本
                "5.0": "#FF8C00",    # 品质5.0 → 橙色文本
                "6.0": "#FF0000"     # 品质6.0 → 红色文本
            }
        }

        try:
            if os.path.exists(self.颜色配置文件):
                with open(self.颜色配置文件, 'r', encoding='utf-8') as f:
                    配置数据 = json.load(f)
                    self.默认列表颜色 = 配置数据.get("默认颜色", "black")
                    self.列表底色 = 配置数据.get("默认底色", "white")  # 加载底色
                    映射数据 = 配置数据.get("品质颜色映射", {})
                    for 品质_str, 颜色 in 映射数据.items():
                        try:
                            品质_float = float(品质_str)  # 统一转换为浮点数键
                            self.品质颜色映射[品质_float] = 颜色
                        except ValueError:
                            print(f"警告：品质值'{品质_str}'不是有效数字，跳过该配置")
                self.显示提示(f"已加载配置：{len(self.品质颜色映射)}组文本颜色规则 + 底色{self.列表底色}", 显示弹窗=False)
            else:
                # 创建默认配置文件（含底色）
                with open(self.颜色配置文件, 'w', encoding='utf-8') as f:
                    json.dump(默认颜色配置, f, ensure_ascii=False, indent=2)
                self.默认列表颜色 = 默认颜色配置["默认颜色"]
                self.列表底色 = 默认颜色配置["默认底色"]  # 初始化默认底色
                # 初始化默认文本颜色映射
                for 品质_str, 颜色 in 默认颜色配置["品质颜色映射"].items():
                    self.品质颜色映射[float(品质_str)] = 颜色
                self.显示提示(f"已创建默认配置：{self.颜色配置文件}", 显示弹窗=False)
            # 加载品质颜色到列表（新增）
            self.更新品质颜色列表()
        except Exception as e:
            messagebox.showerror("配置加载错误", f"加载item_color.json失败：{str(e)}")
            # 加载失败时用硬编码默认值
            self.默认列表颜色 = "black"
            self.列表底色 = "white"
            self.品质颜色映射 = {1.0: "#00FF00", 2.0: "#0000FF", 3.0: "#FF00FF"}
            self.更新品质颜色列表()
    
    def 保存颜色配置(self):
        """保存文本颜色+底色配置到文件"""
        try:
            配置数据 = {
                "说明": "品质值对应文本颜色+列表底色配置（支持RGB格式如'#00FF00'或英文如'green'）",
                "默认颜色": self.默认列表颜色,
                "默认底色": self.列表底色,  # 保存当前底色
                "品质颜色映射": {str(k): v for k, v in self.品质颜色映射.items()}  # 浮点数键转字符串（JSON兼容）
            }
            with open(self.颜色配置文件, 'w', encoding='utf-8') as f:
                json.dump(配置数据, f, ensure_ascii=False, indent=2)
            self.显示提示(f"配置已保存（文本默认色：{self.默认列表颜色}，底色：{self.列表底色}）", 显示弹窗=False)
        except Exception as e:
            messagebox.showerror("配置保存错误", f"保存颜色/底色配置失败：{str(e)}")
    
    # ------------------------------
    # 列表底色配置方法（原有逻辑保留）
    # ------------------------------
    def 选择列表底色(self):
        """打开颜色选择器，自定义列表项底色"""
        选择结果 = tk.colorchooser.askcolor(
            title="选择列表项底色",
            initialcolor=self.列表底色  # 初始颜色为当前底色
        )
        if 选择结果[1]:  # 十六进制字符串不为空表示有效选择
            self.列表底色 = 选择结果[1]
            # 更新底色选择按钮文本
            for 组件 in self.底色配置框架.winfo_children():
                if isinstance(组件, ttk.Button) and "选择底色" in 组件["text"]:
                    组件["text"] = f"选择底色（当前：{self.列表底色}）"
                    break
            self.保存颜色配置()
            self.刷新道具列表()
    
    def 重置列表底色(self):
        """重置列表底色为默认白色"""
        self.列表底色 = "white"
        # 更新按钮文本
        for 组件 in self.底色配置框架.winfo_children():
            if isinstance(组件, ttk.Button) and "选择底色" in 组件["text"]:
                组件["text"] = f"选择底色（当前：{self.列表底色}）"
                break
        self.保存颜色配置()
        self.刷新道具列表()
        self.显示提示("列表底色已重置为默认白色", 显示弹窗=False)
    
    # ------------------------------
    # 新增：品质颜色映射编辑方法
    # ------------------------------
    def 更新品质颜色列表(self):
        """更新品质颜色列表框的显示（显示品质值+颜色）"""
        if hasattr(self, "品质颜色列表框"):
            self.品质颜色列表框.delete(0, tk.END)  # 清空列表
            # 按品质值从小到大排序
            排序后的映射 = sorted(self.品质颜色映射.items(), key=lambda x: x[0])
            for 品质值, 颜色 in 排序后的映射:
                # 显示格式："品质1.0 → #00FF00（绿色）"
                颜色名称 = self.获取颜色名称(颜色)
                列表文本 = f"品质{品质值} → {颜色}（{颜色名称}）"
                self.品质颜色列表框.insert(tk.END, 列表文本)
                # 设置列表项文本颜色为对应颜色
                最后索引 = self.品质颜色列表框.size() - 1
                self.品质颜色列表框.itemconfig(最后索引, foreground=颜色)
    
    def 获取颜色名称(self, 颜色值):
        """根据颜色值（如#00FF00）返回简单颜色名称（用于显示）"""
        颜色映射 = {
            "#00FF00": "绿色", "#0000FF": "蓝色", "#FF00FF": "紫色",
            "#FFFF00": "黄色", "#FF8C00": "橙色", "#FF0000": "红色",
            "black": "黑色", "white": "白色", "gray": "灰色", "#808080": "灰色"
        }
        return 颜色映射.get(颜色值.lower(), "自定义色")
    
    def 添加品质值(self):
        """添加新的品质值（如7.0），用于自定义颜色"""
        # 让用户输入品质值（浮点数）
        品质文本 = simpledialog.askstring("添加品质值", "请输入品质值（如1.0、2.5，需为数字）：")
        if not 品质文本:
            return
        # 验证品质值是否为有效数字
        try:
            品质值 = float(品质文本)
        except ValueError:
            messagebox.showwarning("输入错误", "请输入有效的数字（如1.0、3.5）！")
            return
        # 验证品质值是否已存在
        if 品质值 in self.品质颜色映射:
            messagebox.showinfo("提示", f"品质值{品质值}已存在，无需重复添加！")
            return
        # 默认颜色设为黑色，后续用户可修改
        self.品质颜色映射[品质值] = "black"
        # 保存配置并更新列表
        self.保存颜色配置()
        self.更新品质颜色列表()
        self.显示提示(f"已添加品质值：{品质值}（默认颜色：黑色）", 显示弹窗=False)
    
    def 选择品质颜色(self):
        """为选中的品质值选择自定义颜色"""
        # 获取选中的列表项
        选中索引 = self.品质颜色列表框.curselection()
        if not 选中索引:
            messagebox.showinfo("提示", "请先选择一个品质值！")
            return
        # 解析选中的品质值
        选中文本 = self.品质颜色列表框.get(选中索引[0])
        匹配 = re.search(r"品质(\d+\.?\d*)", 选中文本)
        if not 匹配:
            messagebox.showwarning("解析错误", "无法识别选中的品质值！")
            return
        品质值 = float(匹配.group(1))
        # 打开颜色选择器（初始颜色为当前颜色）
        当前颜色 = self.品质颜色映射.get(品质值, "black")
        选择结果 = tk.colorchooser.askcolor(
            title=f"为品质{品质值}选择文本颜色",
            initialcolor=当前颜色
        )
        if 选择结果[1]:  # 选中有效颜色
            新颜色 = 选择结果[1]
            self.品质颜色映射[品质值] = 新颜色
            # 保存配置、更新列表、刷新道具列表
            self.保存颜色配置()
            self.更新品质颜色列表()
            self.刷新道具列表()
            self.显示提示(f"已更新品质{品质值}的颜色为：{新颜色}", 显示弹窗=False)
    
    def 删除品质值(self):
        """删除选中的品质值（保留默认6个品质值，避免空映射）"""
        # 限制：至少保留1个品质值
        if len(self.品质颜色映射) <= 1:
            messagebox.showwarning("限制", "至少需保留1个品质值，无法继续删除！")
            return
        # 获取选中的品质值
        选中索引 = self.品质颜色列表框.curselection()
        if not 选中索引:
            messagebox.showinfo("提示", "请先选择一个品质值！")
            return
        选中文本 = self.品质颜色列表框.get(选中索引[0])
        匹配 = re.search(r"品质(\d+\.?\d*)", 选中文本)
        if not 匹配:
            messagebox.showwarning("解析错误", "无法识别选中的品质值！")
            return
        品质值 = float(匹配.group(1))
        # 确认删除
        if messagebox.askyesno("确认删除", f"确定要删除品质值{品质值}吗？\n删除后该品质的道具将使用默认文本色！"):
            del self.品质颜色映射[品质值]
            # 保存配置并更新列表
            self.保存颜色配置()
            self.更新品质颜色列表()
            self.刷新道具列表()
            self.显示提示(f"已删除品质值：{品质值}", 显示弹窗=False)
    
    def 重置品质颜色(self):
        """重置品质颜色映射为默认配置（6个品质值+对应颜色）"""
        默认品质映射 = {
            1.0: "#00FF00", 2.0: "#0000FF", 3.0: "#FF00FF",
            4.0: "#FFFF00", 5.0: "#FF8C00", 6.0: "#FF0000"
        }
        if messagebox.askyesno("确认重置", "确定要恢复默认品质颜色配置吗？\n（将恢复1.0-6.0品质的默认颜色，自定义品质值会被删除）"):
            self.品质颜色映射 = 默认品质映射
            # 保存配置、更新列表、刷新道具列表
            self.保存颜色配置()
            self.更新品质颜色列表()
            self.刷新道具列表()
            self.显示提示("已重置品质颜色为默认配置（1.0-6.0品质）", 显示弹窗=False)
    
    # ------------------------------
    # 路径转换工具方法（原有逻辑保留）
    # ------------------------------
    def 获取_res路径(self, 相对路径):
        """根据相对项目根目录的路径，生成Godot的res://路径"""
        if not 相对路径:
            return ""
        return f"res://{相对路径.replace(os.sep, '/')}"

    def 获取_绝对路径(self, 相对路径):
        """根据相对项目根目录的路径，生成系统绝对路径"""
        if not 相对路径:
            return ""
        return os.path.join(self.项目根目录, 相对路径)
    
    # ------------------------------
    # 道具复制粘贴相关（原有逻辑保留）
    # ------------------------------
    def 复制道具(self):
        """复制当前选中的多个道具"""
        选中索引 = self.道具列表框.curselection()
        if not 选中索引:
            messagebox.showinfo("提示", "请先选择一个或多个道具")
            return
                
        self.保存当前道具()
        self.已复制道具列表 = []  # 存储多个复制的道具
        
        for idx in 选中索引:
            选中文本 = self.道具列表框.get(idx)
            匹配 = re.search(r'ID: (\d+)', 选中文本)
            if 匹配:
                道具ID = 匹配.group(1)
                if 道具ID in self.道具列表:
                    self.已复制道具列表.append(self.道具列表[道具ID].copy())
        
        if self.已复制道具列表:
            self.显示提示(f"已复制 {len(self.已复制道具列表)} 个道具信息")
        else:
            messagebox.showinfo("提示", "未找到可复制的道具")

    def 快捷键复制道具(self, event=None):
        """快捷键复制选中的多个道具"""
        选中索引 = self.道具列表框.curselection()
        if not 选中索引:
            messagebox.showinfo("提示", "请先选择一个或多个道具")
            return
        self.复制道具()

    def 快捷键粘贴道具(self, event=None):
        if not hasattr(self, '已复制道具列表') or not self.已复制道具列表:
            messagebox.showinfo("提示", "没有可粘贴的道具，请先复制道具")
            return
        
        复制数量 = len(self.已复制道具列表)
        if 复制数量 == 0:
            return
        
        选中索引 = self.道具列表框.curselection()
        if not 选中索引:
            messagebox.showinfo("提示", "请先选择一个要开始粘贴的道具")
            return
        
        # 保存滚动位置
        滚动状态 = self.保存滚动位置()
        
        起始索引 = 选中索引[0]
        起始文本 = self.道具列表框.get(起始索引)
        起始匹配 = re.search(r'ID: (\d+)', 起始文本)
        if not 起始匹配:
            messagebox.showinfo("提示", "选中的道具无效")
            return
        
        起始ID = 起始匹配.group(1)
        if 起始ID not in self.道具列表:
            messagebox.showinfo("提示", "选中的道具不存在")
            return
        
        所有道具ID = sorted([int(id) for id in self.道具列表.keys()])
        起始位置 = 所有道具ID.index(int(起始ID))
        
        需要的数量 = 复制数量
        目标道具ID列表 = []
        
        for i in range(需要的数量):
            目标位置 = 起始位置 + i
            if 目标位置 < len(所有道具ID):
                目标道具ID列表.append(str(所有道具ID[目标位置]))
            else:
                messagebox.showinfo(
                    "提示", 
                    f"只能找到 {i} 个可用目标道具，无法完成 {需要的数量} 个道具的粘贴"
                )
                return
        
        for i, 目标ID in enumerate(目标道具ID列表):
            self.道具列表[目标ID] = self.已复制道具列表[i].copy()
        
        # 恢复滚动位置
        self.更新道具列表(滚动状态)
        self.加载道具(起始ID)
        
        for 目标ID in 目标道具ID列表:
            for idx, 道具文本 in enumerate(self.道具列表框.get(0, tk.END)):
                if f"ID: {目标ID}" in 道具文本:
                    self.道具列表框.selection_set(idx)
                    break
        
        self.显示提示(f"已按ID顺序粘贴 {复制数量} 个道具（从ID: {起始ID} 开始）")
    
    # ------------------------------
    # 快捷键设置（原有逻辑保留）
    # ------------------------------
    def 设置快捷键(self):
        """设置快捷键"""
        # 保存
        self.主窗口.bind("<Control-s>", self.保存数据快捷键)
        self.主窗口.bind("<Control-S>", self.保存数据快捷键)
        # 复制道具
        self.道具列表框.bind("<Control-c>", self.快捷键复制道具)
        self.道具列表框.bind("<Control-C>", self.快捷键复制道具)
        # 粘贴道具
        self.道具列表框.bind("<Control-v>", self.快捷键粘贴道具)
        self.道具列表框.bind("<Control-V>", self.快捷键粘贴道具)
        # 绑定到主框架
        self.主框架.bind("<Control-s>", self.保存数据快捷键)
        self.主框架.bind("<Control-S>", self.保存数据快捷键)
    
    def 保存数据快捷键(self, 事件=None):
        """快捷键触发的保存功能"""
        self.保存数据()
        return "break"
    
    # ------------------------------
    # 基础工具方法（原有逻辑保留）
    # ------------------------------
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
        """初始化默认的配置文件，添加等级/品质默认值"""
        # 初始化itemsystem.json（含等级/品质）
        if not os.path.exists(self.系统文件):
            默认道具 = {
                "1001": {
                    "名称": "精铁剑",
                    "类型": "装备",
                    "子类型": "剑",
                    "价格": 3.0,
                    "等级": 0.0,  # 新增
                    "品质": 1.0,  # 新增（对应绿色文本）
                    "描述": "以精铁锻造的长剑，适合初学者使用",
                    "相对图标路径": "",
                    "效果": {
                        "攻击力": 10.0,
                        "防御力": 5.0
                    }
                },
                "1002": {
                    "名称": "治疗药水",
                    "类型": "消耗品",
                    "子类型": "药水",
                    "价格": 50.0,
                    "等级": 0.0,  # 新增
                    "品质": 2.0,  # 新增（对应蓝色文本）
                    "描述": "可以回复少量生命值的药水",
                    "相对图标路径": "",
                    "效果": {
                        "生命值": 50.0
                    }
                },
                "1003": {
                    "名称": "金币",
                    "类型": "其他",
                    "子类型": "货币",
                    "价格": 0.0,
                    "等级": 0.0,  # 新增
                    "品质": 0.0,  # 新增（默认文本色）
                    "描述": "游戏中的通用货币",
                    "相对图标路径": "",
                    "效果": {}
                }
            }
            
            try:
                with open(self.系统文件, 'w', encoding='utf-8') as f:
                    json.dump(默认道具, f, ensure_ascii=False, indent=2)
                self.显示提示(f"已创建默认道具数据: {self.系统文件}")
            except Exception as e:
                messagebox.showerror("初始化错误", f"无法创建{self.系统文件}：{str(e)}")
        
        # 初始化item_types.json
        if not os.path.exists(self.类型文件):
            默认类型 = {
                "types": ["装备", "消耗品", "其他"],
                "subtypes": {
                    "装备": ["剑", "法杖", "盔甲", "锤"],
                    "消耗品": ["药水", "食物"],
                    "其他": ["货币", "材料"]
                }
            }
            
            try:
                with open(self.类型文件, 'w', encoding='utf-8') as f:
                    json.dump(默认类型, f, ensure_ascii=False, indent=2)
                self.显示提示(f"已创建默认类型数据: {self.类型文件}")
            except Exception as e:
                messagebox.showerror("初始化错误", f"无法创建{self.类型文件}：{str(e)}")
        
        # 初始化item_att.json（存储效果类型历史）
        if not os.path.exists(self.效果历史文件):
            默认效果历史 = {
                "effect_types": [
                    "攻击力",
                    "防御力",
                    "生命值"
                ]
            }
            
            try:
                with open(self.效果历史文件, 'w', encoding='utf-8') as f:
                    json.dump(默认效果历史, f, ensure_ascii=False, indent=2)
                self.显示提示(f"已创建默认效果历史数据: {self.效果历史文件}")
            except Exception as e:
                messagebox.showerror("初始化错误", f"无法创建{self.效果历史文件}：{str(e)}")
    
    # ------------------------------
    # 拖放功能（原有逻辑保留）
    # ------------------------------
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
        if not self.当前道具ID:
            messagebox.showinfo("提示", "请先选择一个道具再设置图标")
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
    
    # ------------------------------
    # 数据加载与保存（原有逻辑保留）
    # ------------------------------
    def 加载数据(self):
        """加载道具数据，兼容旧数据补全等级/品质"""
        if os.path.exists(self.系统文件):
            try:
                with open(self.系统文件, 'r', encoding='utf-8') as f:
                    原始数据 = json.load(f)
                
                self.道具列表 = {}
                for 道具ID, 道具数据 in 原始数据.items():
                    新道具数据 = 道具数据.copy()
                    
                    # 补全等级字段（兼容旧数据）
                    if "等级" not in 新道具数据:
                        新道具数据["等级"] = 0.0
                    else:
                        try:
                            新道具数据["等级"] = float(新道具数据["等级"])
                        except ValueError:
                            新道具数据["等级"] = 0.0
                            self.显示提示(f"道具ID:{道具ID}的等级值无效，已重置为0.0", 成功=False, 显示弹窗=False)
                    
                    # 补全品质字段（兼容旧数据）
                    if "品质" not in 新道具数据:
                        新道具数据["品质"] = 0.0
                    else:
                        try:
                            新道具数据["品质"] = float(新道具数据["品质"])
                        except ValueError:
                            新道具数据["品质"] = 0.0
                            self.显示提示(f"道具ID:{道具ID}的品质值无效，已重置为0.0", 成功=False, 显示弹窗=False)
                    
                    # 路径转换逻辑
                    if "相对图标路径" in 新道具数据 and 新道具数据["相对图标路径"]:
                        pass
                    elif "源图片路径" in 新道具数据 and 新道具数据["源图片路径"]:
                        try:
                            绝对路径 = Path(新道具数据["源图片路径"]).resolve()
                            相对路径 = 绝对路径.relative_to(self.项目根目录)
                            新道具数据["相对图标路径"] = str(相对路径)
                        except ValueError:
                            新道具数据["相对图标路径"] = 新道具数据["源图片路径"]
                    elif "图标路径" in 新道具数据 and 新道具数据["图标路径"].startswith("res://"):
                        相对路径 = 新道具数据["图标路径"][6:].replace('/', os.sep)
                        新道具数据["相对图标路径"] = 相对路径
                    else:
                        新道具数据["相对图标路径"] = ""
                    
                    # 删除冗余字段
                    for 旧字段 in ["图标路径", "源图片路径"]:
                        if 旧字段 in 新道具数据:
                            del 新道具数据[旧字段]
                    
                    self.道具列表[道具ID] = 新道具数据
                
                self.显示提示(f"已加载道具数据: {len(self.道具列表)}个道具", 显示弹窗=False)
            except Exception as e:
                messagebox.showerror("加载错误", f"无法加载{self.系统文件}：{str(e)}")
                self.道具列表 = {}
        else:
            self.保存数据()
    
    def 保存数据(self):
        """保存道具数据，包含等级/品质"""
        self.保存当前道具()
        
        try:
            待保存数据 = {}
            for 道具ID, 道具数据 in self.道具列表.items():
                待保存数据[道具ID] = {
                    "名称": 道具数据.get("名称", ""),
                    "类型": 道具数据.get("类型", ""),
                    "子类型": 道具数据.get("子类型", ""),
                    "价格": 道具数据.get("价格", 0.0),
                    "等级": 道具数据.get("等级", 0.0),  # 新增
                    "品质": 道具数据.get("品质", 0.0),  # 新增
                    "描述": 道具数据.get("描述", ""),
                    "相对图标路径": 道具数据.get("相对图标路径", ""),
                    "效果": 道具数据.get("效果", {})
                }
            
            with open(self.系统文件, 'w', encoding='utf-8') as f:
                json.dump(待保存数据, f, ensure_ascii=False, indent=2)
            self.显示提示(f"已成功保存到 {self.系统文件} (Ctrl+S)", 显示弹窗=False)
            self.刷新道具列表()
        except Exception as e:
            messagebox.showerror("保存错误", f"无法保存{self.系统文件}：{str(e)}")
    
    def 保存当前道具(self):
        """保存当前编辑的道具，包含等级/品质"""
        if not self.当前道具ID or self.当前道具ID not in self.道具列表:
            return
        
        # 处理价格
        价格文本 = self.价格变量.get().strip()
        价格值 = 0.0
        if 价格文本:
            try:
                价格值 = float(价格文本)
            except ValueError:
                价格值 = 价格文本
                self.显示提示(f"价格 '{价格文本}' 不是有效数字，已按文本保存", 成功=False, 显示弹窗=True)
        
        # 处理等级
        等级文本 = self.等级变量.get().strip()
        等级值 = 0.0
        if 等级文本:
            try:
                等级值 = float(等级文本)
            except ValueError:
                等级值 = 等级文本
                self.显示提示(f"等级 '{等级文本}' 不是有效数字，已按文本保存", 成功=False, 显示弹窗=True)
        
        # 处理品质
        品质文本 = self.品质变量.get().strip()
        品质值 = 0.0
        if 品质文本:
            try:
                品质值 = float(品质文本)
            except ValueError:
                品质值 = 品质文本
                self.显示提示(f"品质 '{品质文本}' 不是有效数字，已按文本保存", 成功=False, 显示弹窗=True)
        
        # 收集表单数据
        self.道具列表[self.当前道具ID] = {
            "名称": self.名称变量.get(),
            "类型": self.类型变量.get(),
            "子类型": self.子类型变量.get(),
            "价格": 价格值,
            "等级": 等级值,  # 新增
            "品质": 品质值,  # 新增
            "描述": self.描述文本框.get(1.0, tk.END).strip(),
            "相对图标路径": self.图标路径变量.get(),
            "效果": self.获取效果数据()
        }
    
    def 获取效果数据(self):
        """从效果列表获取数据，效果值优先转换为浮点数"""
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
    
    # ------------------------------
    # 类型数据处理（原有逻辑保留）
    # ------------------------------
    def 加载类型数据(self):
        """加载类型和子类型数据"""
        if os.path.exists(self.类型文件):
            try:
                with open(self.类型文件, 'r', encoding='utf-8') as f:
                    数据 = json.load(f)
                    if "types" in 数据:
                        self.类型列表 = 数据["types"]
                    if "subtypes" in 数据:
                        self.子类型列表 = 数据["subtypes"]
                self.显示提示(f"已加载类型数据: {len(self.类型列表)}种类型", 显示弹窗=False)
            except Exception as e:
                messagebox.showerror("加载错误", f"无法加载类型数据：{str(e)}")
        else:
            self.保存类型数据()
    
    def 保存类型数据(self):
        """保存类型和子类型数据"""
        try:
            with open(self.类型文件, 'w', encoding='utf-8') as f:
                json.dump({
                    "types": self.类型列表,
                    "subtypes": self.子类型列表
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
    
    # ------------------------------
    # UI创建与更新（新增品质颜色配置框架）
    # ------------------------------
    def 创建界面组件(self):
        """创建UI组件，含等级/品质输入框+底色配置+品质颜色配置"""
        # 主框架
        self.主框架 = ttk.Frame(self.主窗口, padding="10")
        self.主框架.pack(fill=tk.BOTH, expand=True)
        
        # 左侧道具列表
        左侧框架 = ttk.LabelFrame(self.主框架, text="道具列表", padding="5")
        左侧框架.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=(0, 10))
        
        # 道具列表框（原有：已设置粗体字体）
        self.道具列表框 = tk.Listbox(左侧框架, width=30, height=30, selectmode=tk.EXTENDED,font=("SimHei", 12,"bold"))
        self.道具列表框.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        self.道具列表框.bind('<<ListboxSelect>>', self.处理道具选择)
        
        # 滚动条
        滚动条 = ttk.Scrollbar(左侧框架, orient=tk.VERTICAL, command=self.道具列表框.yview)
        滚动条.pack(side=tk.RIGHT, fill=tk.Y)
        self.道具列表框.config(yscrollcommand=滚动条.set)
        
        # 按钮框架（原有：添加/拷贝/删除道具等）
        按钮框架 = ttk.Frame(左侧框架, padding="5")
        按钮框架.pack(fill=tk.X)
        
        ttk.Button(按钮框架, text="添加道具", command=self.添加道具).pack(fill=tk.X, pady=1)
        ttk.Button(按钮框架, text="拷贝道具", command=self.拷贝道具).pack(fill=tk.X, pady=1)
        ttk.Button(按钮框架, text="删除道具", command=self.删除道具).pack(fill=tk.X, pady=1)
        ttk.Button(按钮框架, text="废弃道具", command=self.废弃道具).pack(fill=tk.X, pady=1)
        ttk.Button(按钮框架, text="刷新列表", command=self.刷新道具列表).pack(fill=tk.X, pady=1)
        ttk.Button(按钮框架, text="保存所有 (Ctrl+S)", command=self.保存数据).pack(fill=tk.X, pady=1)
        ttk.Button(按钮框架, text="导出到Excel", command=self.导出到Excel).pack(fill=tk.X, pady=1)
        ttk.Button(按钮框架, text="从Excel导入", command=self.从Excel导入).pack(fill=tk.X, pady=1)
        # 提示设置（原有）
        设置框架 = ttk.LabelFrame(左侧框架, text="提示设置", padding="5")
        设置框架.pack(fill=tk.X, pady=3)
        
        self.弹窗变量 = tk.BooleanVar(value=self.显示成功弹窗)
        ttk.Checkbutton(
            设置框架, 
            text="显示成功提示弹窗", 
            variable=self.弹窗变量,
            command=self.切换弹窗显示
        ).pack(anchor=tk.W)
        
        # 列表底色配置框架（原有）
        self.底色配置框架 = ttk.LabelFrame(左侧框架, text="列表底色配置", padding="5")
        self.底色配置框架.pack(fill=tk.X, pady=5)
        ttk.Checkbutton(
            self.底色配置框架,
            text="启用自定义底色",
            variable=self.是否启用自定义底色,
            command=self.刷新道具列表
        ).pack(anchor=tk.W, pady=2)
        ttk.Button(
            self.底色配置框架,
            text=f"选择底色（当前：{self.列表底色}）",
            command=self.选择列表底色
        ).pack(fill=tk.X, pady=2)
        ttk.Button(
            self.底色配置框架,
            text="重置为默认底色（白色）",
            command=self.重置列表底色
        ).pack(fill=tk.X, pady=2)
        
        # ------------------------------
        # 新增：品质颜色配置框架（核心修改）
        # ------------------------------
        self.品质颜色配置框架 = ttk.LabelFrame(左侧框架, text="品质颜色配置", padding="5")
        self.品质颜色配置框架.pack(fill=tk.X, pady=5)
        
        # 1. 品质颜色列表显示（带滚动条）
        品质列表框架 = ttk.Frame(self.品质颜色配置框架)
        品质列表框架.pack(fill=tk.X, pady=2)
        
        self.品质颜色列表框 = tk.Listbox(品质列表框架, width=40, height=6, selectmode=tk.SINGLE)
        self.品质颜色列表框.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        品质滚动条 = ttk.Scrollbar(品质列表框架, orient=tk.VERTICAL, command=self.品质颜色列表框.yview)
        品质滚动条.pack(side=tk.RIGHT, fill=tk.Y)
        self.品质颜色列表框.config(yscrollcommand=品质滚动条.set)
        
        # 2. 品质颜色操作按钮
        品质按钮框架 = ttk.Frame(self.品质颜色配置框架)
        品质按钮框架.pack(fill=tk.X, pady=2)
        
        ttk.Button(品质按钮框架, text="添加品质值", command=self.添加品质值).pack(side=tk.TOP, fill=tk.X, expand=True, padx=1)
        ttk.Button(品质按钮框架, text="选择颜色", command=self.选择品质颜色).pack(side=tk.TOP, fill=tk.X, expand=True, padx=1)
        ttk.Button(品质按钮框架, text="删除品质值", command=self.删除品质值).pack(side=tk.TOP, fill=tk.X, expand=True, padx=1)
        ttk.Button(品质按钮框架, text="重置默认", command=self.重置品质颜色).pack(side=tk.TOP, fill=tk.X, expand=True, padx=1)
        
        # 右侧编辑区域（原有逻辑保留）
        右侧框架 = ttk.Frame(self.主框架)
        右侧框架.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # 上半部分：基本信息 + 图标
        右上框架 = ttk.Frame(右侧框架)
        右上框架.pack(side=tk.TOP, fill=tk.X, expand=False)
        
        # 道具基本信息（含等级/品质）
        基本信息框架 = ttk.LabelFrame(右上框架, text="基本信息", padding="10")
        基本信息框架.pack(side=tk.LEFT, fill=tk.X, expand=True, pady=(0, 10), padx=(0, 10))
        
        # 表单网格
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
        
        # 类型
        ttk.Label(表单网格, text="类型:").grid(row=2, column=0, sticky=tk.W, pady=5, padx=5)
        self.类型变量 = tk.StringVar()
        类型框架 = ttk.Frame(表单网格)
        类型框架.grid(row=2, column=1, sticky=tk.W, pady=5)
        ttk.Combobox(类型框架, textvariable=self.类型变量, values=self.类型列表, width=20).pack(side=tk.LEFT)
        ttk.Button(类型框架, text="添加类型", command=self.添加类型).pack(side=tk.LEFT, padx=5)
        
        # 子类型
        ttk.Label(表单网格, text="子类型:").grid(row=3, column=0, sticky=tk.W, pady=5, padx=5)
        self.子类型变量 = tk.StringVar()
        子类型框架 = ttk.Frame(表单网格)
        子类型框架.grid(row=3, column=1, sticky=tk.W, pady=5)
        self.子类型下拉框 = ttk.Combobox(子类型框架, textvariable=self.子类型变量, width=20)
        self.子类型下拉框.pack(side=tk.LEFT)
        ttk.Button(子类型框架, text="添加子类型", command=self.添加子类型).pack(side=tk.LEFT, padx=5)
        
        # 价格
        ttk.Label(表单网格, text="价格:").grid(row=4, column=0, sticky=tk.W, pady=5, padx=5)
        self.价格变量 = tk.StringVar()
        价格框架 = ttk.Frame(表单网格)
        价格框架.grid(row=4, column=1, sticky=tk.W, pady=5)
        ttk.Entry(价格框架, textvariable=self.价格变量, width=20).pack(side=tk.LEFT)
        ttk.Label(价格框架, text="(支持数字，如3.5)").pack(side=tk.LEFT, padx=5, fill=tk.Y, anchor=tk.CENTER)
        
        # 等级（新增）
        ttk.Label(表单网格, text="等级:").grid(row=5, column=0, sticky=tk.W, pady=5, padx=5)
        self.等级变量 = tk.StringVar()
        等级框架 = ttk.Frame(表单网格)
        等级框架.grid(row=5, column=1, sticky=tk.W, pady=5)
        ttk.Entry(等级框架, textvariable=self.等级变量, width=20).pack(side=tk.LEFT)
        ttk.Label(等级框架, text="(默认0.0，支持数字)").pack(side=tk.LEFT, padx=5, fill=tk.Y, anchor=tk.CENTER)
        
        # 品质（新增）
        ttk.Label(表单网格, text="品质:").grid(row=6, column=0, sticky=tk.W, pady=5, padx=5)
        self.品质变量 = tk.StringVar()
        品质框架 = ttk.Frame(表单网格)
        品质框架.grid(row=6, column=1, sticky=tk.W, pady=5)
        ttk.Entry(品质框架, textvariable=self.品质变量, width=20).pack(side=tk.LEFT)
        ttk.Label(品质框架, text="(对应文本颜色，如1.0=绿色)").pack(side=tk.LEFT, padx=5, fill=tk.Y, anchor=tk.CENTER)
        
        self.更新品质颜色列表()
        # 描述
        ttk.Label(基本信息框架, text="描述:").pack(anchor=tk.W, pady=(10, 5))
        self.描述文本框 = tk.Text(基本信息框架, height=4, width=60)
        self.描述文本框.pack(fill=tk.X, pady=(0, 10))
        
        # 图标框架
        图标框架 = ttk.LabelFrame(右上框架, text="图标", padding="5")
        图标框架.pack(side=tk.RIGHT, fill=tk.Y, anchor=tk.NE, pady=(0, 10))
        
        图标网格 = ttk.Frame(图标框架)
        图标网格.pack(fill=tk.X)
        
        # 图标路径显示
        ttk.Label(图标网格, text="图标路径:").grid(row=0, column=0, sticky=tk.W, pady=5, padx=5)
        self.图标路径变量 = tk.StringVar()
        ttk.Entry(图标网格, textvariable=self.图标路径变量, width=40, state="readonly").grid(row=0, column=1, sticky=tk.W, pady=5)
        
        # 图标预览
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
        
        # 效果列表
        效果框架 = ttk.LabelFrame(右侧框架, text="效果列表 (值支持数字，如10.5)", padding="10")
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
        
        # 效果树
        列 = ("key", "value")
        self.效果树 = ttk.Treeview(效果框架, columns=列, show="headings", height=10, selectmode=tk.EXTENDED)
        
        self.效果树.heading("key", text="属性")
        self.效果树.heading("value", text="值 (支持数字)")
        
        self.效果树.column("key", width=200, anchor=tk.W)
        self.效果树.column("value", width=200, anchor=tk.W)
        
        # 效果滚动条
        效果滚动条 = ttk.Scrollbar(效果框架, orient=tk.VERTICAL, command=self.效果树.yview)
        self.效果树.configure(yscrollcommand=效果滚动条.set)
        
        self.效果树.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        效果滚动条.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 效果树绑定事件
        self.效果树.bind("<Double-1>", self.处理效果双击)
        self.效果树.bind("<<TreeviewSelect>>", self.处理效果选择)
        self.效果树.bind("<Control-c>", self.复制效果)
        self.效果树.bind("<Control-v>", self.粘贴效果)
        
        # 状态栏
        状态栏 = ttk.Label(self.主窗口, textvariable=self.状态变量, relief=tk.SUNKEN, anchor=tk.W)
        状态栏.pack(side=tk.BOTTOM, fill=tk.X)
        
        # 更新道具列表
        self.更新道具列表()
        
        # 绑定类型变化事件
        self.类型变量.trace_add("write", self.处理类型变化)
        
        # 绑定文本变化事件
        self.名称变量.trace_add("write", lambda *args: self.状态变量.set("有未保存的更改 (按Ctrl+S保存)"))
        self.类型变量.trace_add("write", lambda *args: self.状态变量.set("有未保存的更改 (按Ctrl+S保存)"))
        self.子类型变量.trace_add("write", lambda *args: self.状态变量.set("有未保存的更改 (按Ctrl+S保存)"))
        self.价格变量.trace_add("write", lambda *args: self.状态变量.set("有未保存的更改 (按Ctrl+S保存)"))
        self.等级变量.trace_add("write", lambda *args: self.状态变量.set("有未保存的更改 (按Ctrl+S保存)"))  # 新增
        self.品质变量.trace_add("write", lambda *args: self.状态变量.set("有未保存的更改 (按Ctrl+S保存)"))  # 新增
        self.描述文本框.bind("<<Modified>>", lambda e: self.状态变量.set("有未保存的更改 (按Ctrl+S保存)") or self.描述文本框.edit_modified(False))
        
        # 窗口关闭事件
        self.主窗口.protocol("WM_DELETE_WINDOW", self.处理关闭)
    
    # ------------------------------
    # 道具操作相关（原有逻辑保留）
    # ------------------------------
    def 废弃道具(self):
        """将选中的道具标记为废弃，并保留滚动位置"""
        选中索引 = self.道具列表框.curselection()
        if not 选中索引:
            messagebox.showinfo("提示", "请先选择一个或多个道具")
            return
            
        self.保存当前道具()
        
        # 保存当前滚动位置
        滚动状态 = self.保存滚动位置()
        
        废弃数量 = 0
        选中的道具ID列表 = []  # 存储被废弃的道具ID
        
        for idx in 选中索引:
            选中文本 = self.道具列表框.get(idx)
            匹配 = re.search(r'ID: (\d+)', 选中文本)
            if 匹配:
                道具ID = 匹配.group(1)
                选中的道具ID列表.append(道具ID)
                if 道具ID in self.道具列表:
                    # 在名称前添加"废弃_"标记
                    self.道具列表[道具ID]["名称"] = f"废弃_{self.道具列表[道具ID]['名称']}"
                    废弃数量 += 1
        
        # 更新列表时恢复滚动位置
        self.更新道具列表(滚动状态)
        
        # 恢复选中状态并重新加载当前道具
        if self.当前道具ID and self.当前道具ID in 选中的道具ID列表:
            self.加载道具(self.当前道具ID)
        
        self.显示提示(f"已将 {废弃数量} 个道具标记为废弃")
    
    def 同步效果到同类型(self):
        """将当前道具的效果同步到所有同类型道具"""
        if not self.当前道具ID or self.当前道具ID not in self.道具列表:
            messagebox.showinfo("提示", "请先选择一个道具")
            return
            
        self.保存当前道具()
        当前道具 = self.道具列表[self.当前道具ID]
        当前类型 = 当前道具.get("类型")
        当前效果 = 当前道具.get("效果", {})
        
        if not 当前类型:
            messagebox.showinfo("提示", "当前道具没有设置类型")
            return
        
        同类型道具 = [
            道具ID for 道具ID, 道具数据 in self.道具列表.items()
            if 道具数据.get("类型") == 当前类型 and 道具ID != self.当前道具ID
        ]
        
        if not 同类型道具:
            messagebox.showinfo("提示", f"没有找到其他 '{当前类型}' 类型的道具")
            return
        
        初始化窗口 = tk.Toplevel(self.主窗口)
        初始化窗口.title("选择初始化值")
        初始化窗口.geometry("350x200")
        初始化窗口.resizable(False, False)
        初始化窗口.transient(self.主窗口)
        初始化窗口.grab_set()
        
        初始化窗口.update_idletasks()
        宽度 = 初始化窗口.winfo_width()
        高度 = 初始化窗口.winfo_height()
        x = (self.主窗口.winfo_width() // 2) - (宽度 // 2) + self.主窗口.winfo_x()
        y = (self.主窗口.winfo_height() // 2) - (高度 // 2) + self.主窗口.winfo_y()
        初始化窗口.geometry('{}x{}+{}+{}'.format(宽度, 高度, x, y))
        
        主框架 = ttk.Frame(初始化窗口, padding=15)
        主框架.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(主框架, text="请选择新属性的初始化值:").pack(anchor=tk.W, pady=(0, 15))
        
        初始化值变量 = tk.StringVar(value="0.0")
        选项框架 = ttk.Frame(主框架)
        选项框架.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Radiobutton(选项框架, text="0.0 (浮点数)", variable=初始化值变量, value="0.0").pack(anchor=tk.W, pady=2)
        ttk.Radiobutton(选项框架, text="空字符串", variable=初始化值变量, value="").pack(anchor=tk.W, pady=2)
        
        按钮框架 = ttk.Frame(主框架)
        按钮框架.pack(fill=tk.X, pady=(0, 10))
        
        结果 = [None]
        def 确认():
            结果[0] = 初始化值变量.get()
            初始化窗口.destroy()
        
        确认按钮 = ttk.Button(按钮框架, text="确认", command=确认)
        确认按钮.pack(fill=tk.X, padx=50)
        
        self.主窗口.wait_window(初始化窗口)
        if 结果[0] is None:
            return
        
        try:
            初始化值 = float(结果[0]) if 结果[0] == "0.0" else 结果[0]
        except:
            初始化值 = 结果[0]
        
        值描述 = "0.0 (浮点数)" if 结果[0] == "0.0" else "空字符串"
        if not messagebox.askyesno(
            "确认同步", 
            f"将为所有 {len(同类型道具)} 个 '{当前类型}' 类型的道具\n"
            f"添加缺失的属性并设置默认值为 {值描述}，是否继续？"
        ):
            return
        
        总添加数 = 0
        for 道具ID in 同类型道具:
            道具 = self.道具列表[道具ID]
            道具效果 = 道具.get("效果", {})
            
            for 效果名称 in 当前效果:
                if 效果名称 not in 道具效果:
                    道具效果[效果名称] = 初始化值
                    总添加数 += 1
            
            道具["效果"] = 道具效果
        
        self.加载效果(当前效果)
        self.显示提示(
            f"已完成同步，共为 {len(同类型道具)} 个 '{当前类型}' 类型道具\n"
            f"添加了 {总添加数} 个属性（默认值: {值描述}）"
        )
        # 1. 新增：保存和恢复滚动位置的通用方法
    def 保存滚动位置(self):
        """保存当前列表的滚动状态"""
        return self.道具列表框.yview()  # 返回滚动状态元组 (start, end)

    def 恢复滚动位置(self, 滚动状态):
        """恢复列表的滚动状态"""
        if 滚动状态:
            self.道具列表框.yview_moveto(滚动状态[0])  # 使用原始滚动位置
    def 刷新道具列表(self):
        """手动刷新道具列表（保留滚动位置）"""
        self.保存当前道具()
        
        # 保存当前滚动状态（使用原生方法）
        滚动状态 = self.保存滚动位置()
        
        self.加载数据()
        
        # 关键修复：使用正确的参数名称传递滚动状态
        self.更新道具列表(滚动状态)
        
        # 恢复当前道具的选中状态
        if self.当前道具ID and self.当前道具ID in self.道具列表:
            for i, 道具文本 in enumerate(self.道具列表框.get(0, tk.END)):
                if f"ID: {self.当前道具ID}" in 道具文本:
                    self.道具列表框.selection_set(i)
                    self.道具列表框.see(i)
                    break
        self.显示提示("道具列表已刷新",显示弹窗=False)
    
    def 切换弹窗显示(self):
        """切换是否显示成功提示弹窗"""
        self.显示成功提示弹窗 = self.弹窗变量.get()
        状态 = "已启用" if self.显示成功提示弹窗 else "已禁用"
        self.显示提示(f"成功提示弹窗{状态}", 显示弹窗=False)
    
    def 拷贝道具(self):
        """复制当前选中的道具，完全继承等级/品质"""
        选中索引 = self.道具列表框.curselection()
        if not 选中索引:
            messagebox.showinfo("提示", "请先选择一个或多个道具")
            return
            
        self.保存当前道具()
        复制数量 = 0
        for idx in 选中索引:
            选中文本 = self.道具列表框.get(idx)
            匹配 = re.search(r'ID: (\d+)', 选中文本)
            if 匹配:
                道具ID = 匹配.group(1)
                if 道具ID in self.道具列表:
                    当前道具 = self.道具列表[道具ID]
                    
                    # 生成新ID
                    新ID = 1001
                    while str(新ID) in self.道具列表:
                        新ID += 1
                    新ID = str(新ID)
                    
                    # 完全复制原道具数据（含等级/品质）
                    新名称 = f"{当前道具['名称']}"
                    新道具 = 当前道具.copy()
                    新道具["名称"] = 新名称
                    
                    # 继承图标路径
                    原相对路径 = 当前道具.get("相对图标路径")
                    if 原相对路径:
                        新道具["相对图标路径"] = 原相对路径
                    
                    # 添加新道具
                    self.道具列表[新ID] = 新道具
                    复制数量 += 1
        
        self.更新道具列表()
        self.显示提示(f"已复制 {复制数量} 个道具（仅ID不同，其他信息完全一致）", 显示弹窗=False)
        
    def 处理关闭(self):
        """窗口关闭时保存数据"""
        self.保存数据()
        self.主窗口.destroy()
    
    def 更新道具列表(self, 滚动状态=None):
        """更新道具列表，支持文本颜色+自定义底色 + 精确滚动位置保留"""
        # 记录当前选中的道具ID（更新后重新选中）
        选中ID列表 = []
        for 选中索引 in self.道具列表框.curselection():
            选中文本 = self.道具列表框.get(选中索引)
            匹配 = re.search(r'ID: (\d+)', 选中文本)
            if 匹配:
                选中ID列表.append(匹配.group(1))
        
        self.道具列表框.delete(0, tk.END)  # 清空列表
        
        # 遍历道具列表，逐个插入并设置样式
        for 道具索引, (道具ID, 道具数据) in enumerate(self.道具列表.items()):
            道具名称 = 道具数据.get("名称", "未命名")
            列表文本 = f"{道具名称} (ID: {道具ID})"
            
            self.道具列表框.insert(tk.END, 列表文本)
            当前项索引 = 道具索引
            
            # 文本颜色设置（保持不变）
            品质值 = 道具数据.get("品质", 0.0)
            文本颜色 = self.品质颜色映射.get(品质值, self.默认列表颜色)
            
            try:
                if self.是否启用自定义底色.get():
                    self.道具列表框.itemconfig(当前项索引, foreground=文本颜色, background=self.列表底色)
                else:
                    self.道具列表框.itemconfig(当前项索引, foreground=文本颜色)
            except tk.TclError:
                pass  # 保持原有错误处理
        
        # 恢复滚动位置（使用原生滚动状态）
        if 滚动状态:
            self.恢复滚动位置(滚动状态)
        
        # 恢复选中状态
        for 索引, 道具文本 in enumerate(self.道具列表框.get(0, tk.END)):
            for 选中ID in 选中ID列表:
                if f"ID: {选中ID}" in 道具文本:
                    self.道具列表框.selection_set(索引)
                    break
        
        self.显示提示(f"道具列表已更新，共 {len(self.道具列表)} 个道具", 显示弹窗=False)
        
    def 关闭活跃编辑框(self):
        """关闭当前活跃的编辑框"""
        if self.活跃编辑框:
            try:
                self.活跃编辑框.destroy()
            except:
                pass
            self.活跃编辑框 = None
    
    def 处理道具选择(self, 事件):
        """处理道具选择事件"""
        self.关闭活跃编辑框()
        self.保存当前道具()
        
        选中项 = self.道具列表框.curselection()
        if not 选中项:
            return
            
        选中文本 = self.道具列表框.get(选中项[0])
        匹配 = re.search(r'ID: (\d+)', 选中文本)
        if 匹配:
            道具ID = 匹配.group(1)
            self.加载道具(道具ID)
            道具名称 = self.道具列表[道具ID].get("名称", "未命名")
            self.显示提示(f"已选择道具: {道具名称} (ID: {道具ID})", 显示弹窗=False)
    
    def 加载道具(self, 道具ID):
        """加载道具数据到表单，含等级/品质"""
        if 道具ID not in self.道具列表:
            return
            
        self.当前道具ID = 道具ID
        道具 = self.道具列表[道具ID]
        
        # 加载基本信息
        self.ID变量.set(道具ID)
        self.名称变量.set(道具.get("名称", ""))
        self.类型变量.set(道具.get("类型", ""))
        self.子类型变量.set(道具.get("子类型", ""))
        self.价格变量.set(str(道具.get("价格", 0.0)))
        self.等级变量.set(str(道具.get("等级", 0.0)))  # 新增
        self.品质变量.set(str(道具.get("品质", 0.0)))  # 新增
        self.描述文本框.delete(1.0, tk.END)
        self.描述文本框.insert(tk.END, 道具.get("描述", ""))
        
        # 加载子类型列表
        self.处理类型变化()
        
        # 加载图标
        self.图标路径变量.set(道具.get("相对图标路径", ""))
        self.显示图标预览()
        
        # 加载效果
        self.加载效果(道具.get("效果", {}))
    
    def 加载效果(self, 效果数据):
        """加载效果数据到效果树"""
        # 清空现有效果
        for 项 in self.效果树.get_children():
            self.效果树.delete(项)
        
        # 添加新效果
        for 键, 值 in 效果数据.items():
            self.效果树.insert('', tk.END, values=(键, str(值)))
    
    def 处理类型变化(self, *args):
        """处理类型变化，更新子类型列表"""
        当前类型 = self.类型变量.get()
        if 当前类型 in self.子类型列表:
            self.子类型下拉框['values'] = self.子类型列表[当前类型]
    
    def 添加类型(self):
        """添加新的道具类型"""
        新类型 = simpledialog.askstring("添加类型", "请输入新类型名称:")
        if 新类型 and 新类型.strip():
            新类型 = 新类型.strip()
            if 新类型 not in self.类型列表:
                self.类型列表.append(新类型)
                self.类型列表.sort()
                self.类型变量.set(新类型)
                self.子类型列表[新类型] = []
                self.保存类型数据()
                self.处理类型变化()
            else:
                messagebox.showinfo("提示", f"类型 '{新类型}' 已存在")
    
    def 添加子类型(self):
        """添加新的子类型"""
        当前类型 = self.类型变量.get()
        if not 当前类型:
            messagebox.showinfo("提示", "请先选择一个类型")
            return
            
        新子类型 = simpledialog.askstring("添加子类型", f"请为类型 '{当前类型}' 输入新子类型名称:")
        if 新子类型 and 新子类型.strip():
            新子类型 = 新子类型.strip()
            if 当前类型 not in self.子类型列表:
                self.子类型列表[当前类型] = []
            
            if 新子类型 not in self.子类型列表[当前类型]:
                self.子类型列表[当前类型].append(新子类型)
                self.子类型列表[当前类型].sort()
                self.子类型变量.set(新子类型)
                self.保存类型数据()
            else:
                messagebox.showinfo("提示", f"子类型 '{新子类型}' 已存在")
    
    def 添加道具(self):
        """添加新道具，包含等级/品质默认值"""
        self.保存当前道具()
        
        # 生成新ID
        新ID = 1001
        while str(新ID) in self.道具列表:
            新ID += 1
        新ID = str(新ID)
        
        # 创建新道具（含等级/品质默认值）
        self.道具列表[新ID] = {
            "名称": "",
            "类型": "",
            "子类型": "",
            "价格": 0.0,
            "等级": 0.0,  # 新增
            "品质": 0.0,  # 新增
            "描述": "",
            "相对图标路径": "",
            "效果": {}
        }
        
        self.更新道具列表()
        self.加载道具(新ID)
        
        # 选中新添加的道具
        for i, 道具文本 in enumerate(self.道具列表框.get(0, tk.END)):
            if f"ID: {新ID}" in 道具文本:
                self.道具列表框.selection_set(i)
                self.道具列表框.see(i)
                break
        
        #self.显示提示(f"已添加新道具 (ID: {新ID})")
    
    def 删除道具(self):
        选中索引 = self.道具列表框.curselection()
        if not 选中索引:
            messagebox.showinfo("提示", "请先选择一个或多个道具")
            return
            
        要重置的ID = []
        for idx in 选中索引:
            选中文本 = self.道具列表框.get(idx)
            匹配 = re.search(r'ID: (\d+)', 选中文本)
            if 匹配:
                道具ID = 匹配.group(1)
                if 道具ID in self.道具列表:
                    要重置的ID.append(道具ID)
        
        if not 要重置的ID:
            messagebox.showinfo("提示", "未找到可操作的道具")
            return
            
        if messagebox.askyesno("确认清空", f"确定要清空这 {len(要重置的ID)} 个道具的信息吗？"):
            if self.当前道具ID in 要重置的ID:
                self.当前道具ID = None
            
            # 保存滚动位置
            滚动状态 = self.保存滚动位置()
            
            # 执行删除操作
            for 道具ID in 要重置的ID:
                if 道具ID in self.道具列表:
                    self.道具列表[道具ID] = {
                        "名称": "", "类型": "", "子类型": "", "价格": 0.0,
                        "等级": 0.0, "品质": 0.0, "描述": "", 
                        "相对图标路径": "", "效果": {}
                    }
            
            # 恢复滚动位置更新列表
            self.更新道具列表(滚动状态)
            if 要重置的ID:
                self.加载道具(要重置的ID[0])
            
            self.显示提示(f"已清空 {len(要重置的ID)} 个道具的信息")
    
    def 选择图标(self):
        """选择图标并复制到项目目录"""
        if not self.当前道具ID:
            messagebox.showinfo("提示", "请先选择一个道具")
            return
            
        文件路径 = filedialog.askopenfilename(
            title="选择图标",
            filetypes=[
                ("图片文件", "*.png;*.jpg;*.jpeg;*.gif;*.bmp;*.tiff"),
                ("所有文件", "*.*")
            ]
        )
        
        if 文件路径:
            self.处理图标(文件路径)
    
    def 处理图标(self, 文件路径):
        """处理图标文件，复制到项目目录并更新路径"""
        try:
            # 确保图片目录存在
            self.确保目录存在(self.图片目录)
            
            # 生成新文件名（保留原扩展名）
            文件名 = os.path.basename(文件路径)
            名称, 扩展名 = os.path.splitext(文件名)
            新文件名 = f"{uuid.uuid4().hex}{扩展名}"
            目标路径 = os.path.join(self.图片目录, 新文件名)
            
            # 复制文件
            shutil.copy2(文件路径, 目标路径)
            
            # 计算相对路径
            目标绝对路径 = Path(目标路径).resolve()
            相对路径 = 目标绝对路径.relative_to(self.项目根目录)
            
            # 更新道具图标路径
            self.图标路径变量.set(str(相对路径))
            self.显示图标预览()
            
            # 保存当前道具
            self.保存当前道具()
            
            self.显示提示(f"图标已更新: {str(相对路径)}", 显示弹窗=False)
            self.保存数据()
        except Exception as e:
            messagebox.showerror("图标处理错误", f"无法处理图标: {str(e)}")
    
    def 显示图标预览(self):
        
        """显示图标预览"""
        相对路径 = self.图标路径变量.get()
         # 1. 先强制清空之前的图片缓存和文本（核心修复）
        self.图标预览.config(image="", text="")
        if hasattr(self.图标预览, "image"):
            del self.图标预览.image  # 彻底删除图片引用，避免残留
        if not 相对路径:
            self.图标预览.config(text="无图标")
            return
        
        try:
            绝对路径 = self.获取_绝对路径(相对路径)
            if os.path.exists(绝对路径):
                # 打开并缩放图片
                图片 = Image.open(绝对路径)
                图片.thumbnail((80, 80))  # 缩放到最大80x80
                tk图片 = ImageTk.PhotoImage(图片)
                
                # 显示图片
                self.图标预览.config(image=tk图片, text="")
                self.图标预览.image = tk图片  # 保持引用
            else:
                self.图标预览.config(text=f"图片不存在:\n{相对路径}")
        except Exception as e:
            self.图标预览.config(text=f"无法显示图片:\n{str(e)}")
            print(e)
    
    def 移除图标(self):
        """移除当前道具的图标"""
        if not self.当前道具ID:
            return
            
        self.图标路径变量.set("")
        self.图标预览.config(text="无图标", image="")
        self.保存当前道具()
        self.显示提示("已移除图标")
    
    # ------------------------------
    # 效果操作相关（原有逻辑保留）
    # ------------------------------
    def 添加效果(self):
        """添加新效果（简化版：直接插入）"""
        self.效果树.insert("", tk.END, values=("效果名", "1.0"))
        self.显示提示("已添加新效果", 显示弹窗=False)
    
    def 从历史添加效果(self):
        if not self.当前道具ID:
            messagebox.showinfo("提示", "请先选择一个道具")
            return
        
        当前道具类型 = self.类型变量.get()
        该类型属性列表 = self.类型属性记录.get(当前道具类型, [])
        已存在属性 = [self.效果树.item(项, "values")[0] for 项 in self.效果树.get_children()]
        
        # 初始化状态变量（手动维护选中项，确保不丢失）
        最后选中索引 = None
        已选中项 = set()
        
        # 1. 创建主弹窗
        多选窗口 = tk.Toplevel(self.主窗口)
        多选窗口.title(f"添加效果（{当前道具类型 if 当前道具类型 else '无类型'}）")
        多选窗口.geometry("500x420")  # 微调高度，适配按钮位置
        多选窗口.resizable(False, False)
        多选窗口.transient(self.主窗口)
        多选窗口.grab_set()
        
        # 窗口居中
        多选窗口.update_idletasks()
        窗宽 = 多选窗口.winfo_width()
        窗高 = 多选窗口.winfo_height()
        主窗x = self.主窗口.winfo_x()
        主窗y = self.主窗口.winfo_y()
        主窗宽 = self.主窗口.winfo_width()
        主窗高 = self.主窗口.winfo_height()
        目标x = 主窗x + (主窗宽 - 窗宽) // 2
        目标y = 主窗y + (主窗高 - 窗高) // 2
        多选窗口.geometry(f"{窗宽}x{窗高}+{目标x}+{目标y}")
        
        # 2. 标题标签（操作说明）
        标题标签 = ttk.Label(
            多选窗口, 
            text=f"当前类型：{当前道具类型 if 当前道具类型 else '未选择类型'}\n"
                f"操作方式：\n"
                f"- 左键单击：累加选中（跨行支持，一次必中）\n"
                f"- Shift+左键：选中连续范围\n"
                f"- 右键单击：取消单个选中项\n"
                f"- 全选/清除：快速批量操作"
        )
        标题标签.pack(pady=8, padx=10, anchor=tk.W)
        
        # 3. 历史属性列表框（核心选择区）
        历史属性框架 = ttk.LabelFrame(多选窗口, text="历史属性列表")
        历史属性框架.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # 3.1 列表框（禁用默认选择，手动控制）
        属性列表框 = tk.Listbox(
            历史属性框架, 
            selectmode=tk.NONE,
            font=("SimHei", 10),
            height=8
        )
        属性列表框.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # 3.2 滚动条
        列表滚动条 = ttk.Scrollbar(历史属性框架, orient=tk.VERTICAL, command=属性列表框.yview)
        列表滚动条.pack(side=tk.RIGHT, fill=tk.Y)
        属性列表框.config(yscrollcommand=列表滚动条.set)
        
        # 3.3 填充历史属性数据
        if 该类型属性列表:
            for 属性字典 in 该类型属性列表:
                for 属性名, 初始值 in 属性字典.items():
                    列表文本 = f"{属性名} (初始值：{初始值})"
                    属性列表框.insert(tk.END, 列表文本)
        else:
            属性列表框.insert(tk.END, "暂无该类型的历史属性记录")
            属性列表框.config(state=tk.DISABLED)
        
        # 4. 核心选择逻辑（左键选中+右键取消）
        def 处理左键点击(event):
            nonlocal 最后选中索引, 已选中项
            
            # 多重保障获取点击索引
            try:
                当前索引 = 属性列表框.index(f"@{event.x},{event.y}")
            except:
                try:
                    当前索引 = 属性列表框.nearest(event.y)
                except:
                    return
            
            if not (0 <= 当前索引 < 属性列表框.size()) or 属性列表框["state"] == tk.DISABLED:
                return
            
            # Shift键判断
            shift_pressed = event.state & 0x10
            
            # 4.1 Shift+左键：连续范围选中
            if shift_pressed and 最后选中索引 is not None:
                起始 = min(最后选中索引, 当前索引)
                结束 = max(最后选中索引, 当前索引)
                for i in range(起始, 结束 + 1):
                    已选中项.add(i)
            # 4.2 普通左键：累加选中
            else:
                已选中项.add(当前索引)
            
            # 同步更新列表框显示
            属性列表框.selection_clear(0, tk.END)
            for i in 已选中项:
                属性列表框.selection_set(i)
            
            最后选中索引 = 当前索引
        
        def 处理右键点击(event):
            nonlocal 已选中项
            
            try:
                当前索引 = 属性列表框.index(f"@{event.x},{event.y}")
            except:
                try:
                    当前索引 = 属性列表框.nearest(event.y)
                except:
                    return
            
            if 0 <= 当前索引 < 属性列表框.size() and 当前索引 in 已选中项:
                已选中项.remove(当前索引)
                # 同步更新显示
                属性列表框.selection_clear(0, tk.END)
                for i in 已选中项:
                    属性列表框.selection_set(i)
        
        # 绑定点击事件
        属性列表框.bind('<ButtonPress-1>', 处理左键点击)
        属性列表框.bind('<ButtonPress-3>', 处理右键点击)
        
        # 5. 自定义属性框架（含添加按钮）
        自定义属性框架 = ttk.LabelFrame(多选窗口, text="自定义属性添加")
        自定义属性框架.pack(fill=tk.X, padx=10, pady=5)
        
        # 5.1 网格布局配置（4列，支持按钮跨列）
        自定义属性框架.grid_columnconfigure(1, weight=1)
        自定义属性框架.grid_columnconfigure(3, weight=1)
        
        # 5.2 属性名输入（row=0，列0-1）
        ttk.Label(自定义属性框架, text="属性名：").grid(row=0, column=0, sticky=tk.W, pady=8, padx=5)
        自定义属性名变量 = tk.StringVar()
        自定义属性名输入框 = ttk.Entry(
            自定义属性框架, 
            textvariable=自定义属性名变量, 
            font=("SimHei", 10)
        )
        自定义属性名输入框.grid(row=0, column=1, sticky=tk.EW, pady=8, padx=5)
        
        # 5.3 初始值输入（row=0，列2-3）
        ttk.Label(自定义属性框架, text="初始值：").grid(row=0, column=2, sticky=tk.W, pady=8, padx=5)
        自定义初始值变量 = tk.StringVar(value="0.0")
        自定义初始值输入框 = ttk.Entry(
            自定义属性框架, 
            textvariable=自定义初始值变量, 
            font=("SimHei", 10)
        )
        自定义初始值输入框.grid(row=0, column=3, sticky=tk.EW, pady=8, padx=5)
        
        # 5.4 【关键】添加自定义属性按钮（移入框架内，row=1，跨4列）
        def 添加自定义属性():
            属性名 = 自定义属性名变量.get().strip()
            初始值 = 自定义初始值变量.get().strip()
            
            if not 属性名:
                messagebox.showwarning("输入错误", "自定义属性名不能为空！")
                自定义属性名输入框.focus()
                return
            if 属性名 in 已存在属性:
                messagebox.showinfo("提示", f"属性 '{属性名}' 已存在于当前效果列表")
                自定义属性名变量.set("")
                自定义属性名输入框.focus()
                return
            
            # 添加到效果列表
            self.效果树.insert('', tk.END, values=(属性名, 初始值))
            已存在属性.append(属性名)
            
            # 自动记录到类型属性
            if 当前道具类型:
                self.自动记录类型属性(当前道具类型, 属性名, 初始值)
            
            # 反馈与重置
            self.状态变量.set("有未保存的更改 (按Ctrl+S保存)")
            self.显示提示(f"已添加自定义属性：{属性名}（初始值：{初始值}）", 显示弹窗=False)
            自定义属性名变量.set("")
            自定义初始值变量.set("0.0")
            自定义属性名输入框.focus()
        
        # 按钮放在输入框下方，跨4列对齐
        ttk.Button(
            自定义属性框架, 
            text="添加自定义属性", 
            command=添加自定义属性
        ).grid(row=1, column=0, columnspan=4, sticky=tk.EW, pady=5, padx=5)
        
        # 6. 底部功能按钮区（保留历史属性相关操作）
        按钮框架 = ttk.Frame(多选窗口)
        按钮框架.pack(fill=tk.X, pady=10, padx=10)
        
        # 6.1 全选按钮
        def 全选属性():
            nonlocal 已选中项
            if 属性列表框["state"] == tk.DISABLED or 属性列表框.size() == 0:
                return
            已选中项 = set(range(属性列表框.size()))
            属性列表框.selection_set(0, tk.END)
        
        # 6.2 清除选择按钮
        def 清除选择():
            nonlocal 已选中项
            已选中项 = set()
            属性列表框.selection_clear(0, tk.END)
        
        # 6.3 插入选中属性按钮
        def 插入选中属性():
            if 属性列表框["state"] == tk.DISABLED or not 已选中项:
                messagebox.showinfo("提示", "请先在历史属性列表中选择至少一个属性")
                return
            
            插入数量 = 0
            for 索引 in 已选中项:
                列表文本 = 属性列表框.get(索引)
                匹配 = re.search(r'^(.+?) \(初始值：(.+?)\)$', 列表文本)
                if 匹配:
                    属性名 = 匹配.group(1)
                    初始值 = 匹配.group(2)
                    
                    if 属性名 not in 已存在属性:
                        self.效果树.insert('', tk.END, values=(属性名, 初始值))
                        已存在属性.append(属性名)
                        插入数量 += 1
            
            if 插入数量 > 0:
                self.状态变量.set("有未保存的更改 (按Ctrl+S保存)")
                self.显示提示(f"已插入 {插入数量} 个历史属性", 显示弹窗=False)
            else:
                messagebox.showinfo("提示", "选中的属性已全部存在，无需重复插入")
        
        # 6.4 底部按钮布局（无"添加自定义属性"按钮）
        ttk.Button(按钮框架, text="全选", command=全选属性).pack(
            side=tk.LEFT, fill=tk.X, expand=True, padx=2
        )
        ttk.Button(按钮框架, text="清除选择", command=清除选择).pack(
            side=tk.LEFT, fill=tk.X, expand=True, padx=2
        )
        ttk.Button(按钮框架, text="插入选中属性", command=插入选中属性).pack(
            side=tk.LEFT, fill=tk.X, expand=True, padx=2
        )
        ttk.Button(按钮框架, text="取消", command=多选窗口.destroy).pack(
            side=tk.LEFT, fill=tk.X, expand=True, padx=2
        )
        
        # 7. 快捷键支持
        多选窗口.bind("<Return>", lambda e: 添加自定义属性())  # 回车触发添加
        多选窗口.bind("<Escape>", lambda e: 多选窗口.destroy())  # ESC关闭
        自定义属性名输入框.focus()  # 初始聚焦输入框
        

    
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
    
    def 删除选中效果(self):
        """删除选中的效果"""
        选中项 = self.效果树.selection()
        if not 选中项:
            messagebox.showinfo("提示", "请先选择一个或多个效果")
            return
            
        for 项 in 选中项:
            self.效果树.delete(项)
        self.状态变量.set("有未保存的更改 (按Ctrl+S保存)")
    
    def 处理效果双击(self, 事件):
        """处理效果双击事件，允许编辑"""
        self.关闭活跃编辑框()
        
        区域 = self.效果树.identify_region(事件.x, 事件.y)
        项 = self.效果树.identify_row(事件.y)
        列 = self.效果树.identify_column(事件.x)
        
        if 区域 == "cell" and 项 and 列:
            列索引 = int(列.replace('#', '')) - 1  # 转换为0-based索引
            x, y, width, height = self.效果树.bbox(项, 列)
            
            # 获取当前值
            当前值 = self.效果树.item(项, "values")[列索引]
            
            # 创建编辑框
            self.活跃编辑框 = ttk.Entry(self.效果树)
            self.活跃编辑框.insert(0, 当前值)
            self.活跃编辑框.place(x=x, y=y, width=width, height=height)
            self.活跃编辑框.focus_set()
            
            # 保存编辑的项和列
            self.编辑项 = 项
            self.编辑列 = 列索引
            
            # 绑定事件
            self.活跃编辑框.bind("<FocusOut>", self.结束效果编辑)
            self.活跃编辑框.bind("<Return>", self.结束效果编辑)
            self.活跃编辑框.bind("<Escape>", lambda e: self.关闭活跃编辑框())
    
    def 结束效果编辑(self, 事件=None):
        """结束效果编辑（新增：自动记录新属性到类型记录）"""
        if self.活跃编辑框 and hasattr(self, '编辑项') and hasattr(self, '编辑列'):
            新值 = self.活跃编辑框.get()
            旧值列表 = list(self.效果树.item(self.编辑项, "values"))
            编辑的属性名 = 旧值列表[0]  # 第0列是属性名，第1列是值
            编辑的列索引 = self.编辑列
            
            # ------------------------------
            # 新增：判断是否为「新属性」（需记录）
            # 条件：1. 编辑的是属性值列（第1列）；2. 该属性是首次添加（旧值为空或"0.0"且新值非默认）
            # ------------------------------
            if 编辑的列索引 == 1:  # 只有编辑「值」时才可能是新属性（属性名在添加时已确定）
                当前道具类型 = self.类型变量.get()  # 获取当前道具的类型
                旧值 = 旧值列表[1] if len(旧值列表) > 1 else ""
                
                # 判断是否为「新添加的属性」：旧值是默认的"0.0"，且新值已修改（或旧值为空）
                if (旧值 == "0.0" and 新值 != "0.0") or (not 旧值 and 新值):
                    # 自动记录该属性到当前类型下
                    self.自动记录类型属性(当前道具类型, 编辑的属性名, 新值)
            
            # 原有逻辑：更新效果树值
            旧值列表[编辑的列索引] = 新值
            self.效果树.item(self.编辑项, values=旧值列表)
            
            # 如果是属性名列，添加到历史记录
            if 编辑的列索引 == 0 and 新值:
                self.添加效果类型到历史(新值)
            
            self.状态变量.set("有未保存的更改 (按Ctrl+S保存)")
        
        self.关闭活跃编辑框()
    
    def 处理效果选择(self, 事件):
        """处理效果选择事件"""
        self.关闭活跃编辑框()
    
    def 复制效果(self, 事件=None):
        """复制选中的效果"""
        选中项 = self.效果树.selection()
        if not 选中项:
            messagebox.showinfo("提示", "请先选择一个或多个效果")
            return
            
        self.已复制效果 = []
        for 项 in 选中项:
            self.已复制效果.append(self.效果树.item(项, "values"))
        
        self.显示提示(f"已复制 {len(self.已复制效果)} 个效果", 显示弹窗=False)
    
    def 粘贴效果(self, 事件=None):
        """粘贴效果"""
        if not self.已复制效果:
            messagebox.showinfo("提示", "没有可粘贴的效果，请先复制效果")
            return
            
        已存在的键 = [self.效果树.item(项, "values")[0] for 项 in self.效果树.get_children()]
        粘贴数量 = 0
        
        for 效果 in self.已复制效果:
            键, 值 = 效果
            # 检查是否已存在相同的键
            if 键 in 已存在的键:
                新键 = f"{键}_副本"
                计数 = 1
                while 新键 in 已存在的键:
                    计数 += 1
                    新键 = f"{键}_副本{计数}"
                键 = 新键
                已存在的键.append(键)
            
            self.效果树.insert('', tk.END, values=(键, 值))
            粘贴数量 += 1
        
        self.状态变量.set("有未保存的更改 (按Ctrl+S保存)")
        self.显示提示(f"已粘贴 {粘贴数量} 个效果", 显示弹窗=False)

    def 导出到Excel(self):
    #"""将所有道具数据导出到Excel（确保效果属性完整）"""
        if not self.道具列表:
            messagebox.showinfo("提示", "没有可导出的道具数据")
            return
            
        self.保存当前道具()
        导出数据 = []
        
        for 道具ID, 道具数据 in self.道具列表.items():
            # 基础信息
            行数据 = {
                "ID": 道具ID,
                "名称": 道具数据.get("名称", ""),
                "类型": 道具数据.get("类型", ""),
                "子类型": 道具数据.get("子类型", ""),
                "价格": 道具数据.get("价格", 0.0),
                "等级": 道具数据.get("等级", 0.0),
                "品质": 道具数据.get("品质", 0.0),
                "描述": 道具数据.get("描述", ""),
                "图标路径": 道具数据.get("相对图标路径", "")
            }
            
            # 处理效果数据（确保所有效果都被导出）
            效果数据 = 道具数据.get("效果", {})
            for 效果名, 效果值 in 效果数据.items():
                行数据[f"效果_{效果名}"] = 效果值
                
            导出数据.append(行数据)
        
        # 创建DataFrame并确保列顺序合理
        df = pd.DataFrame(导出数据)
        # 固定基础列在前，效果列在后
        基础列 = ["ID", "名称", "类型", "子类型", "价格", "等级", "品质", "描述", "图标路径"]
        效果列 = [col for col in df.columns if col not in 基础列]
        df = df[基础列 + 效果列]  # 重排列顺序
        
        # 保存文件
        当前时间 = datetime.now().strftime("%Y%m%d_%H%M%S")
        默认文件名 = f"道具数据导出_{当前时间}.xlsx"
        文件路径 = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel文件", "*.xlsx"), ("所有文件", "*.*")],
            initialfile=默认文件名
        )
        
        if 文件路径:
            try:
                with pd.ExcelWriter(文件路径, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False, sheet_name='道具数据')
                self.显示提示(f"成功导出 {len(导出数据)} 个道具（含效果）到 {文件路径}")
            except Exception as e:
                messagebox.showerror("导出错误", f"导出失败: {str(e)}")


    def 从Excel导入(self):
        文件路径 = filedialog.askopenfilename(
            title="选择Excel文件",
            filetypes=[("Excel文件", "*.xlsx")]
        )
        if not 文件路径:
            return
            
        try:
            # 读取时禁用空值自动转为nan，统一处理
            df = pd.read_excel(文件路径, na_filter=False)
            df = df.replace("", None)  # 空字符串转为None，避免干扰
            
            if df.empty:
                messagebox.showinfo("提示", "文件无数据")
                return
            
            self.保存当前道具()
            滚动状态 = self.保存滚动位置()
            导入数量 = 0
            效果列 = [col for col in df.columns if col.startswith("效果_")]
            
            for _, 行 in df.iterrows():
                # 处理道具ID
                原始ID = 行.get("ID")
                道具ID = str(int(原始ID)) if isinstance(原始ID, (int, float)) else str(原始ID).strip() if 原始ID is not None else None
                if not 道具ID:
                    新ID = 1001
                    while str(新ID) in self.道具列表:
                        新ID += 1
                    道具ID = str(新ID)
                
                # 基础属性（强制数值为浮点数）
                道具数据 = {
                    "名称": str(行["名称"]).strip() if 行["名称"] is not None else "",
                    "类型": str(行["类型"]).strip() if 行["类型"] is not None else "",
                    "子类型": str(行["子类型"]).strip() if 行["子类型"] is not None else "",
                    # 价格/等级/品质强制为浮点数（空值默认为0.0）
                    "价格": float(行["价格"]) if (行["价格"] is not None and str(行["价格"]).strip() != "") else 0.0,
                    "等级": float(行["等级"]) if (行["等级"] is not None and str(行["等级"]).strip() != "") else 0.0,
                    "品质": float(行["品质"]) if (行["品质"] is not None and str(行["品质"]).strip() != "") else 0.0,
                    "描述": str(行["描述"]).strip() if 行["描述"] is not None else "",
                    "相对图标路径": str(行["图标路径"]).strip() if 行["图标路径"] is not None else "",
                    "效果": {}
                }
                
                # 效果值处理（强制数值为浮点数，文本为字符串）
                道具效果 = {}
                for 列 in 效果列:
                    效果名 = 列[3:]
                    效果值 = 行[列]
                    
                    # 过滤空值和无效值
                    if 效果值 is None:
                        continue
                    效果值_str = str(效果值).strip()
                    if 效果值_str == "":
                        continue
                    
                    # 核心逻辑：优先转为浮点数，失败则保留字符串
                    try:
                        # 无论是否带小数点，统一转为浮点数（如"10"→10.0，"10.5"→10.5）
                        转换后的值 = float(效果值_str)
                        道具效果[效果名] = 转换后的值
                    except (ValueError, TypeError):
                        # 无法转为浮点数的视为文本（如"中毒效果"、"持续3秒"）
                        道具效果[效果名] = 效果值_str
                
                道具数据["效果"] = 道具效果
                self.道具列表[道具ID] = 道具数据
                导入数量 += 1
            
            self.更新道具列表(滚动状态)
            # 导入后：为避免当前表单（可能尚未刷新）在用户随后手动保存时
            # 覆盖刚导入的数据，重置当前选择并清空编辑表单。
            self.道具列表框.selection_clear(0, tk.END)
            self.当前道具ID = None
            # 清空表单显示，确保不会在后续保存时把旧数据写回
            try:
                self.ID变量.set("")
                self.名称变量.set("")
                self.类型变量.set("")
                self.子类型变量.set("")
                self.价格变量.set("")
                self.等级变量.set("")
                self.品质变量.set("")
                self.描述文本框.delete(1.0, tk.END)
                self.图标路径变量.set("")
                self.加载效果({})
            except Exception:
                pass

            # 自动保存导入结果到系统文件，避免丢失（同时不会触发覆盖，因为当前道具已清空）
            try:
                self.保存数据()
            except Exception:
                # 保存失败时仍显示导入成功信息，具体错误会在保存中弹出
                pass

            总效果数 = sum(len(v["效果"]) for v in self.道具列表.values())
            messagebox.showinfo("成功", 
                f"导入 {导入数量} 个道具，{总效果数} 个有效效果\n"
                f"数值已统一转为浮点数，文本保留为字符串"
            )
            
        except Exception as e:
            messagebox.showerror("导入错误", f"失败原因: {str(e)}")
if __name__ == "__main__":
    if 支持拖放:
        主窗口 = Tk()
    else:
        主窗口 = tk.Tk()
    
    # 设置中文字体支持
    主窗口.option_add("*Font", "SimHei 10")
    
    应用 = 道具编辑器(主窗口)
    主窗口.mainloop()
    
