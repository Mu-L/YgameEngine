# cython: language_level=3
# cython: c_string_encoding=utf-8
import os
import hashlib
import json
import tkinter as tk
from tkinter import filedialog
import threading
import time
import re

# 直接将原PCKUpdateGenerator重命名为PCK补丁编辑器（符合类名匹配规则）
class PCK补丁编辑器:
    def __natural_sort_key(self, s):
        """自然排序的键生成函数，用于正确排序版本号格式的文件名"""
        return [int(text) if text.isdigit() else text.lower() for text in re.split(r'([0-9]+)', s)]
    
    def __init__(self, root):
        # 主窗口配置
        self.root = root  # 接收外部传入的root（包装后的框架）
        # 注意：这里不再设置title/geometry（由外部框架包装器处理）
        
        # 配置文件路径（改为json格式）
        self.config_path = os.path.join(os.getcwd(), "pck_tool_config.json")
        # 全局变量
        self.target_dir = tk.StringVar()  # 选中的目录
        self.result_list = []  # 存储PCK文件信息
        self.sort_option = tk.StringVar(value="name")  # 排序选项："time"、"name"，默认文件名排序

        # 先创建UI组件，再加载配置
        self._create_widgets()
        self._load_config()
    
    def _create_widgets(self):
        # 目录选择区域
        frame_dir = tk.Frame(self.root, padx=10, pady=10)
        frame_dir.pack(fill=tk.X)
        
        lbl_dir = tk.Label(frame_dir, text="补丁目录：", font=("微软雅黑", 10))
        lbl_dir.pack(side=tk.LEFT, padx=5)
        
        entry_dir = tk.Entry(frame_dir, textvariable=self.target_dir, width=60, font=("微软雅黑", 10))
        entry_dir.pack(side=tk.LEFT, padx=5)
        
        btn_select = tk.Button(frame_dir, text="选择目录", command=self._select_directory, 
                               font=("微软雅黑", 10), bg="#409EFF", fg="white", width=10)
        btn_select.pack(side=tk.LEFT, padx=5)
        
        # 功能按钮区域
        frame_btn = tk.Frame(self.root, padx=10, pady=5)
        frame_btn.pack(fill=tk.X)
        
        btn_scan = tk.Button(frame_btn, text="扫描PCK文件并生成JSON", command=self._scan_pck_thread,
                             font=("微软雅黑", 10), bg="#67C23A", fg="white", width=20)
        btn_scan.pack(side=tk.LEFT, padx=5)
        
        btn_clear = tk.Button(frame_btn, text="清空日志", command=self._clear_log,
                              font=("微软雅黑", 10), bg="#E6A23C", fg="white", width=10)
        btn_clear.pack(side=tk.LEFT, padx=5)
        
        # 添加排序选项（单选按钮）
        rbtn_sort_time = tk.Radiobutton(frame_btn, text="按创建时间排序", variable=self.sort_option, value="time",
                                       font=("微软雅黑", 10), command=self._save_config)
        rbtn_sort_time.pack(side=tk.LEFT, padx=5)
        
        rbtn_sort_name = tk.Radiobutton(frame_btn, text="按文件名排序", variable=self.sort_option, value="name",
                                       font=("微软雅黑", 10), command=self._save_config)
        rbtn_sort_name.pack(side=tk.LEFT, padx=5)
        
        # 日志显示区域（原生Text+Scrollbar）
        frame_log = tk.Frame(self.root, padx=10, pady=5)
        frame_log.pack(fill=tk.BOTH, expand=True)
        
        lbl_log = tk.Label(frame_log, text="操作日志：", font=("微软雅黑", 10))
        lbl_log.pack(anchor=tk.W)
        
        scrollbar = tk.Scrollbar(frame_log)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.log_text = tk.Text(frame_log, font=("Consolas", 9), wrap=tk.WORD, yscrollcommand=scrollbar.set)
        self.log_text.pack(fill=tk.BOTH, expand=True, pady=5)
        scrollbar.config(command=self.log_text.yview)
        self.log_text.config(state=tk.DISABLED)
    
    def _log(self, msg):
        """添加日志到文本框"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] {msg}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
    
    def _load_config(self):
        """加载上次保存的目录和排序选项（JSON格式）"""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # 加载目录配置
                    last_dir = config.get("last_dir", "")
                    if last_dir and os.path.exists(last_dir):
                        self.target_dir.set(last_dir)
                        self._log(f"加载上次保存的目录：{last_dir}")
                    # 加载排序选项配置
                    sort_option = config.get("sort_option", "name")  # 默认文件名排序
                    self.sort_option.set(sort_option)
                    self._log(f"加载上次保存的排序选项：{'按创建时间排序' if sort_option == 'time' else '按文件名排序'}")
            except Exception as e:
                self._log(f"加载配置失败：{str(e)}")
    
    def _save_config(self):
        """保存当前目录和排序选项到JSON配置文件"""
        current_dir = self.target_dir.get().strip()
        try:
            config_data = {}
            # 保存目录配置（如果有效）
            if current_dir and os.path.exists(current_dir):
                config_data["last_dir"] = current_dir
            # 保存排序选项配置
            config_data["sort_option"] = self.sort_option.get()
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=4, ensure_ascii=False)
            
            self._log(f"已保存配置：目录={current_dir if current_dir else '未设置'}，排序={'按创建时间' if config_data['sort_option'] == 'time' else '按文件名'}")
        except Exception as e:
            self._log(f"保存配置失败：{str(e)}")
    
    def _select_directory(self):
        """选择目标目录"""
        dir_path = filedialog.askdirectory(title="选择包含PCK补丁文件的目录")
        if dir_path:
            self.target_dir.set(dir_path)
            self._save_config()
            self._log(f"已选择目录：{dir_path}")
        else:
            self._log("未选择任何目录")
    
    def _clear_log(self):
        """清空日志"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)
    
    def _calculate_md5(self, file_path):
        """计算单个文件的MD5值"""
        try:
            md5_hash = hashlib.md5()
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    md5_hash.update(chunk)
            return md5_hash.hexdigest()
        except Exception as e:
            self._log(f"计算MD5失败 [{os.path.basename(file_path)}]：{str(e)}")
            return None
    
    def _scan_pck(self):
        """扫描PCK文件并生成JSON"""
        target_dir = self.target_dir.get().strip()
        if not target_dir or not os.path.exists(target_dir):
            self._log("警告：请选择有效的目录！")
            return
        
        self._log("开始扫描PCK文件...")
        self.result_list.clear()
        
        # 1. 先收集所有PCK文件及其创建时间
        pck_files_with_time = []
        for item in os.listdir(target_dir):
            item_path = os.path.join(target_dir, item)
            if os.path.isfile(item_path) and item.lower().endswith(".pck"):
                # 获取文件创建时间
                creation_time = os.path.getctime(item_path)
                pck_files_with_time.append((item, item_path, creation_time))
        
        if not pck_files_with_time:
            self._log("警告：所选目录中未找到有效的.pck文件")
            return
        
        pck_count = len(pck_files_with_time)
        self._log(f"共发现 {pck_count} 个PCK文件")
        
        # 2. 根据单选按钮状态决定排序方式
        sort_option = self.sort_option.get()
        if sort_option == "time":
            pck_files_with_time.sort(key=lambda x: x[2])
            self._log("按文件创建时间排序完成")
        else:  # 默认按文件名排序
            # 使用自然排序按文件名排序
            pck_files_with_time.sort(key=lambda x: self.__natural_sort_key(x[0]))
            self._log("按文件名自然排序完成")
        
        # 3. 处理每个文件并添加到补丁信息中
        for item, item_path, creation_time in pck_files_with_time:
            self._log(f"正在处理文件：{item}")
            
            # 转换为可读格式
            creation_time_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(creation_time))
            
            md5_value = self._calculate_md5(item_path)
            if md5_value:
                # 只添加filename和md5，不添加create_time
                self.result_list.append({
                    "filename": item,
                    "md5": md5_value
                })
                self._log(f"MD5计算完成 [{item}]：{md5_value}")
        
        if self.result_list:
            json_path = os.path.join(target_dir, "update.json")
            try:
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump(self.result_list, f, indent=4, ensure_ascii=False)
                self._log(f"成功生成update.json：{json_path}")
                self._log(f"共处理 {pck_count} 个PCK文件，有效记录 {len(self.result_list)} 条")
                sort_option = self.sort_option.get()
                if sort_option == "time":
                    self._log("文件已按创建时间升序排序")
                elif sort_option == "name":
                    self._log("文件已按文件名自然排序")
            except Exception as e:
                self._log(f"错误：生成update.json失败：{str(e)}")
        else:
            self._log("警告：所有PCK文件的MD5计算均失败")
    
    def _scan_pck_thread(self):
        """启动线程执行扫描"""
        # 禁用按钮
        for widget in self.root.winfo_children():
            if isinstance(widget, tk.Frame):
                for btn in widget.winfo_children():
                    if isinstance(btn, tk.Button) and btn["text"] == "扫描PCK文件并生成JSON":
                        btn.config(state=tk.DISABLED)
        
        thread = threading.Thread(target=self._scan_pck)
        thread.daemon = True
        thread.start()
        
        # 恢复按钮
        def check_thread():
            if thread.is_alive():
                self.root.after(100, check_thread)
            else:
                for widget in self.root.winfo_children():
                    if isinstance(widget, tk.Frame):
                        for btn in widget.winfo_children():
                            if isinstance(btn, tk.Button) and btn["text"] == "扫描PCK文件并生成JSON":
                                btn.config(state=tk.NORMAL)
        self.root.after(100, check_thread)


# 独立运行时的代码（移到类外部）
if __name__ == "__main__":
    # 解决tkinter中文乱码
    import locale
    try:
        locale.setlocale(locale.LC_ALL, '')
    except:
        pass
    
    root = tk.Tk()
    app = PCK补丁编辑器(root)
    root.title("Godot PCK补丁MD5生成工具")  # 独立运行时设置标题
    root.geometry("700x500")
    root.resizable(False, False)
    root.mainloop()