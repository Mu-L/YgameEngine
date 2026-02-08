import os
import json
import shutil
import urllib.request
import zipfile
from pathlib import Path

# ========== 【仅需修改这里的配置】 ==========
# 服务器基础域名（结尾不要加/）
DOMAIN = "https://0dcszgip.cn-nb1.rainapp.top/godot_YgameEngine"
# 本地版本记录文件
LOCAL_VERSION_FILE = "local_version.txt"
# 临时下载目录
TEMP_DIR = "update_temp"
# 补丁解压目标目录（当前目录）
TARGET_DIR = "."
# 初始版本号（首次安装时的版本）
INIT_VERSION = "v1.0"

# ========== 工具函数：下载文件（带进度提示） ==========
def download_file(url: str, save_path: str) -> bool:
    """
    下载文件，返回是否成功
    :param url: 下载URL
    :param save_path: 保存路径
    """
    print(f"\n[↓] 开始下载：{url}")
    print(f"[→] 保存到：{save_path}")
    
    # 创建保存目录
    save_dir = os.path.dirname(save_path)
    if save_dir and not os.path.exists(save_dir):
        os.makedirs(save_dir)
    
    try:
        # 添加User-Agent，避免被服务器拦截
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        req = urllib.request.Request(url, headers=headers)
        
        # 下载文件
        with urllib.request.urlopen(req) as response, open(save_path, "wb") as f:
            # 显示简单进度
            total_size = int(response.headers.get("Content-Length", 0))
            downloaded_size = 0
            chunk_size = 8192
            
            while True:
                chunk = response.read(chunk_size)
                if not chunk:
                    break
                downloaded_size += len(chunk)
                f.write(chunk)
                
                # 打印进度（可选）
                if total_size > 0:
                    progress = (downloaded_size / total_size) * 100
                    print(f"\r[进度] {progress:.1f}%", end="", flush=True)
        
        print("\n[√] 下载完成！")
        return True
    except Exception as e:
        print(f"\n[×] 下载失败：{str(e)}")
        return False

# ========== 工具函数：解压补丁（支持zip/patch后缀） ==========
def unzip_file(zip_path: str, target_dir: str) -> bool:
    """
    解压zip格式的补丁文件
    :param zip_path: 补丁文件路径
    :param target_dir: 解压目标目录
    """
    print(f"\n[📦] 开始解压补丁：{zip_path}")
    print(f"[→] 解压到：{target_dir}")
    
    try:
        # 兼容.zip和.patch后缀（本质都是zip）
        with zipfile.ZipFile(zip_path, "r") as zf:
            # 解压所有文件（覆盖已有文件）
            zf.extractall(target_dir)
        print("[√] 解压完成！（已自动覆盖local_version.txt）")
        return True
    except zipfile.BadZipFile:
        print("[×] 解压失败：补丁文件不是有效的ZIP格式！")
        return False
    except Exception as e:
        print(f"[×] 解压失败：{str(e)}")
        return False

# ========== 工具函数：读取版本文件 ==========
def read_version_file(file_path: str) -> str:
    """读取版本文件，返回版本号（无则返回空）"""
    if not os.path.exists(file_path):
        return ""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read().strip()
    except Exception:
        return ""

# ========== 工具函数：初始化版本文件（仅首次） ==========
def init_version_file(file_path: str, init_version: str) -> str:
    """首次初始化版本文件，返回初始版本号"""
    print(f"\n[*] 未检测到本地版本文件，初始化版本为：{init_version}")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(init_version.strip())
    return init_version

# ========== 核心函数：逐级更新（依赖补丁自动覆盖版本号） ==========
def update_step_by_step(current_version: str, server_version: str, version_map: dict) -> bool:
    """
    逐级更新版本（如v1.0→v1.1→v1.2），版本号由补丁中的local_version.txt自动覆盖
    :param current_version: 当前本地版本
    :param server_version: 服务器最新版本
    :param version_map: 版本-补丁映射字典
    :return: 是否更新成功
    """
    print(f"\n[📌] 开始逐级更新：{current_version} → {server_version}")
    
    # 循环更新，直到当前版本等于服务器版本
    while current_version != server_version:
        # 检查当前版本是否有对应的补丁
        if current_version not in version_map:
            print(f"[×] 更新失败：未找到{current_version}对应的增量补丁！")
            return False
        
        # 获取当前版本的补丁文件名
        patch_file_name = version_map[current_version]
        print(f"\n[🔍] 准备更新 {current_version} → 下一个版本，补丁：{patch_file_name}")
        
        # 下载补丁
        patch_url = f"{DOMAIN}/patch/{patch_file_name}"
        patch_path = os.path.join(TEMP_DIR, patch_file_name)
        if not download_file(patch_url, patch_path):
            print(f"[×] 补丁{patch_file_name}下载失败！")
            return False
        
        # 解压补丁（自动覆盖local_version.txt）
        if not unzip_file(patch_path, TARGET_DIR):
            print(f"[×] 补丁{patch_file_name}解压失败！")
            return False
        
        # 重新读取本地版本号（关键：从补丁覆盖后的文件中读取）
        new_version = read_version_file(LOCAL_VERSION_FILE)
        if not new_version or new_version == current_version:
            print(f"[×] 补丁{patch_file_name}未正确更新版本号！")
            return False
        
        print(f"[📝] 本地版本已自动更新为：{new_version}（来自补丁中的local_version.txt）")
        # 更新当前版本，继续循环
        current_version = new_version
    
    return True

# ========== 主更新逻辑 ==========
def main():
    print("=" * 50)
    print("YgameEngine 增量更新工具")
    print("=" * 50)
    
    # 1. 读取/初始化本地版本文件
    local_version = read_version_file(LOCAL_VERSION_FILE)
    if not local_version:
        local_version = init_version_file(LOCAL_VERSION_FILE, INIT_VERSION)
    print(f"[🔍] 本地当前版本：{local_version}")
    
    # 2. 创建临时目录
    if os.path.exists(TEMP_DIR):
        shutil.rmtree(TEMP_DIR)
    os.makedirs(TEMP_DIR, exist_ok=True)
    
    try:
        # 3. 下载服务器版本信息
        print("\n[📡] 获取服务器版本信息...")
        # 下载最新版本号
        latest_version_url = f"{DOMAIN}/latest_version.txt"
        latest_version_path = os.path.join(TEMP_DIR, "latest_version.txt")
        if not download_file(latest_version_url, latest_version_path):
            raise Exception("无法下载服务器最新版本信息！")
        
        # 下载版本-补丁映射
        version_map_url = f"{DOMAIN}/version_map.json"
        version_map_path = os.path.join(TEMP_DIR, "version_map.json")
        if not download_file(version_map_url, version_map_path):
            raise Exception("无法下载版本-补丁映射文件！")
        
        # 4. 解析服务器版本信息
        server_version = read_version_file(latest_version_path)
        if not server_version:
            raise Exception("服务器版本文件为空！")
        print(f"[🔍] 服务器最新版本：{server_version}")
        
        # 5. 判断是否需要更新
        if local_version == server_version:
            print("\n[✅] 当前已是最新版本，无需更新！")
            return
        
        # 6. 读取版本-补丁映射
        with open(version_map_path, "r", encoding="utf-8") as f:
            version_map = json.load(f)
        
        # 7. 核心：逐级更新（版本号由补丁自动覆盖）
        if update_step_by_step(local_version, server_version, version_map):
            # 最终验证版本号
            final_version = read_version_file(LOCAL_VERSION_FILE)
            print(f"\n[✅] 最终版本验证：{final_version}（与服务器版本{server_version}一致）")
            print("\n[🎉] 增量更新完成！可直接运行游戏程序～")
        else:
            raise Exception("逐级更新失败！")
    
    except Exception as e:
        print(f"\n[×] 更新失败：{str(e)}")
    finally:
        # 清理临时目录
        print("\n[🧹] 清理临时文件...")
        if os.path.exists(TEMP_DIR):
            shutil.rmtree(TEMP_DIR)
        print("\n按Enter键退出...")
        input()

if __name__ == "__main__":
    # 设置控制台编码（解决中文乱码）
    if os.name == "nt":
        os.system("chcp 65001 >nul")
    main()