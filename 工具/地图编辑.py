import json
import os
import sys
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Timer

# ========== 核心配置：保存到上级三级的「系统」文件夹 ==========
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_3_dir = os.path.abspath(os.path.join(script_dir, '../../..'))
system_dir = os.path.join(parent_3_dir, '系统')
if not os.path.exists(system_dir):
    os.makedirs(system_dir)
DEFAULT_FILE = os.path.join(system_dir, 'Maptxt.json')
PORT = 8080
# 强制UTF-8，解决乱码问题
sys.stdout.reconfigure(encoding='utf-8')
sys.stdin.reconfigure(encoding='utf-8')

# 初始化默认地图文件（含默认大地图，支持多区域）
def init_default_file():
    default_data = {
        "大地图": {
            "1,1": "种子森林1",
            "1,2": "种子森林2",
            "1,3": "种子森林3",
            "2,1": "矿洞1"
        }
    }
    if not os.path.exists(DEFAULT_FILE):
        with open(DEFAULT_FILE, 'w', encoding='utf-8') as f:
            json.dump(default_data, f, ensure_ascii=False, indent=4)
    print(f"✅ 数据文件: {os.path.abspath(DEFAULT_FILE)}")
    print(f"📌 上级三级目录: {parent_3_dir}")
    print(f"📌 系统文件夹路径: {system_dir}")

# 自动打开浏览器（延迟1秒，确保服务启动完成）
def open_browser():
    url = f"http://localhost:{PORT}"
    webbrowser.open_new(url)
    print(f"🌐 已自动打开浏览器: {url}")

# 前端：多区域管理列表+Excel二维表格（核心修改：三重防重复校验）
HTML_CONTENT = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>多区域地图编辑器 | 全局点位名称唯一</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: "微软雅黑", 宋体, Arial, sans-serif;
            font-size: 14px;
        }
        body {
            background: #f5f5f5;
            padding: 20px;
        }
        .container {
            max-width: 1600px;
            margin: 0 auto;
            background: #fff;
            padding: 25px;
            border: 1px solid #e6e6e6;
            border-radius: 3px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
            display: flex;
            gap: 20px;
            flex-wrap: wrap;
        }
        .area-wrap {
            width: 280px;
            min-width: 280px;
            display: flex;
            flex-direction: column;
            gap: 15px;
        }
        .area-title {
            font-size: 16px;
            font-weight: bold;
            color: #333;
            padding-bottom: 10px;
            border-bottom: 1px solid #e6e6e6;
        }
        .area-add {
            display: flex;
            gap: 10px;
        }
        .area-input {
            flex: 1;
            padding: 6px 10px;
            border: 1px solid #ccc;
            border-radius: 3px;
            outline: none;
        }
        .area-input:focus {
            border-color: #1890ff;
        }
        .area-list {
            border: 1px solid #ccc;
            border-radius: 3px;
            overflow: hidden;
            flex: 1;
            min-height: 400px;
        }
        .area-item {
            padding: 12px 15px;
            border-bottom: 1px solid #eee;
            display: flex;
            justify-content: space-between;
            align-items: center;
            cursor: pointer;
            transition: all 0.2s;
        }
        .area-item:last-child {
            border-bottom: none;
        }
        .area-item:hover {
            background: #f5f5f5;
        }
        .area-item.active {
            background: #e6e6ff;
            color: #1890ff;
            font-weight: 500;
        }
        .area-del {
            color: #ff4d4f;
            cursor: pointer;
            padding: 4px 8px;
            border-radius: 2px;
            transition: all 0.2s;
        }
        .area-del:hover {
            background: #fff2f2;
        }
        .excel-wrap {
            flex: 1;
            min-width: 600px;
            display: flex;
            flex-direction: column;
            gap: 15px;
        }
        .excel-title {
            font-size: 16px;
            font-weight: bold;
            color: #333;
            padding-bottom: 10px;
            border-bottom: 1px solid #e6e6e6;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .excel-title span {
            color: #1890ff;
            font-size: 16px;
        }
        .btn {
            padding: 6px 18px;
            border: none;
            border-radius: 3px;
            cursor: pointer;
            transition: all 0.2s;
        }
        .btn:hover {
            opacity: 0.9;
        }
        .btn-primary {
            background: #1890ff;
            color: #fff;
        }
        .btn-success {
            background: #52c41a;
            color: #fff;
        }
        .btn-warning {
            background: #faad14;
            color: #fff;
        }
        .btn-danger {
            background: #ff4d4f;
            color: #fff;
        }
        .btn-group {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }
        .excel-table-wrap {
            overflow: auto;
            border: 1px solid #ccc;
            flex: 1;
            min-height: 400px;
        }
        .excel-table {
            border-collapse: collapse;
            table-layout: fixed;
        }
        .excel-th {
            background: #f2f2f2;
            border: 1px solid #ccc;
            padding: 8px 12px;
            text-align: center;
            font-weight: bold;
            user-select: none;
            min-width: 120px;
            height: 32px;
            line-height: 32px;
        }
        .excel-idx {
            background: #f2f2f2;
            border: 1px solid #ccc;
            padding: 0 12px;
            text-align: center;
            font-weight: bold;
            user-select: none;
            width: 60px;
        }
        .excel-cell {
            border: 1px solid #ccc;
            padding: 4px 8px;
            min-width: 120px;
            height: 32px;
            line-height: 24px;
            vertical-align: middle;
            cursor: cell;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        .excel-cell[contenteditable="true"]:focus {
            outline: 2px solid #1890ff;
            outline-offset: -1px;
            background: #e6e6ff;
            border-color: transparent;
        }
        .excel-cell.duplicate {
            background: #ffcccc;
            color: #ff4d4f;
            font-weight: 500;
        }
        .excel-tr:hover .excel-cell {
            background: #f9f9f9;
        }
        .excel-tr:hover .excel-cell.duplicate {
            background: #ffbbbb;
        }
        .empty-tip {
            text-align: center;
            padding: 50px 0;
            color: #999;
            font-style: italic;
        }
        .status {
            margin-top: 10px;
            padding: 10px 15px;
            border-radius: 3px;
            display: none;
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 999;
        }
        .status.show {
            display: block;
            animation: fade 3s linear;
        }
        .status-success {
            background: #f0f9eb;
            color: #52c41a;
            border: 1px solid #b7eb8f;
        }
        .status-error {
            background: #fff2f2;
            color: #ff4d4f;
            border: 1px solid #ffccc7;
        }
        @keyframes fade {
            0% {opacity: 0;}
            10% {opacity: 1;}
            90% {opacity: 1;}
            100% {opacity: 0;}
        }
        .modal-mask {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.5);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 9999;
            display: none;
        }
        .modal-mask.show {
            display: flex;
        }
        .modal-box {
            background: #fff;
            padding: 30px;
            border-radius: 8px;
            width: 500px;
        }
        .modal-title {
            font-size: 18px;
            font-weight: bold;
            color: #ff4d4f;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .modal-content {
            color: #666;
            line-height: 1.6;
            margin-bottom: 20px;
            max-height: 400px;
            overflow-y: auto;
            padding-right: 10px;
        }
        .modal-content p {
            margin: 5px 0;
        }
        .modal-btn-group {
            display: flex;
            justify-content: flex-end;
            gap: 10px;
        }
        .del-modal .modal-title {
            color: #333;
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- 左侧：地图区域管理 -->
        <div class="area-wrap">
            <div class="area-title">地图区域管理</div>
            <div class="area-add">
                <input type="text" class="area-input" id="areaInput" placeholder="输入区域名称，如：新手村">
                <button class="btn btn-primary" id="addAreaBtn">添加区域</button>
            </div>
            <div class="area-list" id="areaList">
                <div class="empty-tip">加载区域中...</div>
            </div>
        </div>

        <!-- 右侧：Excel编辑区 -->
        <div class="excel-wrap">
            <div class="excel-title">
                地图编辑区 - 选中区域：<span id="currentArea">未选中</span>
            </div>
            <div class="btn-group">
                <button class="btn btn-primary" id="refreshBtn">🔄 刷新表格</button>
                <button class="btn btn-success" id="saveBtn">💾 保存当前区域</button>
                <button class="btn btn-warning" id="addRowBtn">➕ 新增一行（X+1）</button>
                <button class="btn btn-warning" id="addColBtn">➡️ 新增一列（Y+1）</button>
            </div>
            <div class="excel-table-wrap" id="excelTableWrap">
                <table class="excel-table" id="mapTable">
                    <thead id="tableHead"></thead>
                    <tbody id="tableBody"></tbody>
                </table>
            </div>
        </div>
    </div>

    <!-- 状态提示框 -->
    <div class="status" id="status"></div>

    <!-- 重复数据提示弹窗 -->
    <div class="modal-mask" id="duplicateModal">
        <div class="modal-box">
            <div class="modal-title">⚠️ 检测到重复点位名称</div>
            <div class="modal-content" id="duplicateContent"></div>
            <div class="modal-btn-group">
                <button class="btn btn-primary" id="closeDuplicateModal">知道了，立即修改</button>
            </div>
        </div>
    </div>

    <!-- 删除区域确认弹窗 -->
    <div class="modal-mask del-modal" id="delModal">
        <div class="modal-box">
            <div class="modal-title" id="modalTitle">确定要删除「大地图」区域吗？</div>
            <div>删除后该区域所有地图数据将永久消失，无法恢复！</div>
            <div class="modal-btn-group">
                <button class="btn btn-danger" id="confirmDelBtn">确认删除</button>
                <button class="btn btn-primary" id="cancelDelBtn">取消</button>
            </div>
        </div>
    </div>

    <script>
        // DOM元素获取
        const areaInput = document.getElementById('areaInput');
        const addAreaBtn = document.getElementById('addAreaBtn');
        const areaList = document.getElementById('areaList');
        const currentArea = document.getElementById('currentArea');
        const refreshBtn = document.getElementById('refreshBtn');
        const saveBtn = document.getElementById('saveBtn');
        const addRowBtn = document.getElementById('addRowBtn');
        const addColBtn = document.getElementById('addColBtn');
        const tableHead = document.getElementById('tableHead');
        const tableBody = document.getElementById('tableBody');
        const status = document.getElementById('status');
        const delModal = document.getElementById('delModal');
        const modalTitle = document.getElementById('modalTitle');
        const confirmDelBtn = document.getElementById('confirmDelBtn');
        const cancelDelBtn = document.getElementById('cancelDelBtn');
        const duplicateModal = document.getElementById('duplicateModal');
        const duplicateContent = document.getElementById('duplicateContent');
        const closeDuplicateModal = document.getElementById('closeDuplicateModal');

        // 全局状态
        let allAreaData = {};
        let currentAreaName = '';
        let rowCount = 3;
        let colCount = 3;
        let delAreaName = '';

        // 显示提示框
        function showTip(text, isSuccess = true) {
            status.className = `status ${isSuccess ? 'status-success' : 'status-error'}`;
            status.textContent = text;
            status.classList.add('show');
            setTimeout(() => status.classList.remove('show'), 3000);
        }

        // ========== 核心1：全局点位名称查重（返回所有重复信息） ==========
        function findAllDuplicateNames() {
            const nameMap = new Map(); // 存储{名称: [{区域, 坐标}]}
            const duplicates = [];     // 最终重复数据

            // 遍历所有区域，构建名称映射
            for (const areaName in allAreaData) {
                const areaData = allAreaData[areaName];
                for (const coord in areaData) {
                    const name = areaData[coord].trim();
                    if (!name) continue; // 跳过空名称
                    if (!nameMap.has(name)) {
                        nameMap.set(name, []);
                    }
                    nameMap.get(name).push({ area: areaName, coord: coord });
                }
            }

            // 筛选出出现次数>1的名称
            for (const [name, positions] of nameMap) {
                if (positions.length > 1) {
                    duplicates.push({ name, positions });
                }
            }
            return duplicates;
        }

        // ========== 核心2：单个名称唯一性校验（编辑时用） ==========
        function checkNameUnique(newName, excludeArea, excludeCoord) {
            if (!newName) return { isUnique: true };
            const duplicates = findAllDuplicateNames();
            for (const item of duplicates) {
                if (item.name === newName) {
                    // 排除当前编辑的坐标，判断是否还有其他重复
                    const otherPositions = item.positions.filter(p => 
                        p.area !== excludeArea || p.coord !== excludeCoord
                    );
                    if (otherPositions.length > 0) {
                        return {
                            isUnique: false,
                            message: `「${newName}」已存在于「${otherPositions[0].area}」的${otherPositions[0].coord}坐标！`
                        };
                    }
                }
            }
            return { isUnique: true };
        }

        // ========== 核心3：标红重复单元格 ==========
        function markDuplicateCells() {
            // 先清除所有标红
            document.querySelectorAll('.excel-cell.duplicate').forEach(cell => {
                cell.classList.remove('duplicate');
            });
            // 找到所有重复名称
            const duplicates = findAllDuplicateNames();
            duplicates.forEach(item => {
                item.positions.forEach(pos => {
                    // 若当前选中的是该区域，才标红（避免跨区域DOM找不到）
                    if (pos.area === currentAreaName) {
                        const [x, y] = pos.coord.split(',').map(Number);
                        const cell = document.querySelector(`.excel-cell[data-x="${x}"][data-y="${y}"]`);
                        if (cell) cell.classList.add('duplicate');
                    }
                });
            });
        }

        // ========== 核心4：重复数据弹窗提示 ==========
        function showDuplicateModal() {
            const duplicates = findAllDuplicateNames();
            if (duplicates.length === 0) return false;

            // 拼接提示内容
            let html = '<p>以下点位名称存在重复，无法保存，请修改后再操作：</p>';
            duplicates.forEach((item, idx) => {
                html += `<p><b>${idx+1}. 名称「${item.name}」</b> 重复位置：</p>`;
                item.positions.forEach(p => {
                    html += `<p>&nbsp;&nbsp;→ 「${p.area}」-${p.coord} 坐标</p>`;
                });
            });
            duplicateContent.innerHTML = html;
            duplicateModal.classList.add('show');
            return true;
        }

        // 弹窗开关
        function openDelModal(areaName) {
            delAreaName = areaName;
            modalTitle.textContent = `确定要删除「${areaName}」区域吗？`;
            delModal.classList.add('show');
        }
        function closeDelModal() {
            delModal.classList.remove('show');
            delAreaName = '';
        }
        closeDuplicateModal.addEventListener('click', () => {
            duplicateModal.classList.remove('show');
        });

        // 加载所有区域数据（新增：加载后校验重复）
        async function loadAllAreaData() {
            try {
                const res = await fetch('/api/get-all');
                const data = await res.json();
                allAreaData = data || {};
                renderAreaList();
                // 加载完成后，立即检测重复并提示
                showDuplicateModal();
                // 默认选中第一个区域
                const firstArea = Object.keys(allAreaData)[0];
                if (firstArea) {
                    selectArea(firstArea);
                }
            } catch (err) {
                showTip('加载区域失败：' + err.message, false);
                areaList.innerHTML = '<div class="empty-tip">加载失败，请刷新</div>';
            }
        }

        // 渲染区域列表
        function renderAreaList() {
            if (Object.keys(allAreaData).length === 0) {
                areaList.innerHTML = '<div class="empty-tip">暂无地图区域，点击添加</div>';
                return;
            }
            areaList.innerHTML = '';
            Object.keys(allAreaData).forEach(areaName => {
                const div = document.createElement('div');
                div.className = `area-item ${areaName === currentAreaName ? 'active' : ''}`;
                div.innerHTML = `
                    <span class="area-name">${areaName}</span>
                    <span class="area-del" data-name="${areaName}">删除</span>
                `;
                div.addEventListener('click', (e) => {
                    if (e.target.className !== 'area-del') selectArea(areaName);
                });
                div.querySelector('.area-del').addEventListener('click', (e) => {
                    e.stopPropagation();
                    openDelModal(areaName);
                });
                areaList.appendChild(div);
            });
        }

        // 选中区域
        function selectArea(areaName) {
            currentAreaName = areaName;
            currentArea.textContent = areaName;
            document.querySelectorAll('.area-item').forEach(item => {
                item.classList.remove('active');
                if (item.querySelector('.area-name').textContent === areaName) {
                    item.classList.add('active');
                }
            });
            loadCurrentAreaTable();
        }

        // 添加区域（区域名唯一）
        async function addNewArea() {
            const areaName = areaInput.value.trim();
            if (!areaName) {
                showTip('请输入区域名称！', false);
                areaInput.focus();
                return;
            }
            if (allAreaData[areaName]) {
                showTip(`「${areaName}」区域名称已存在！`, false);
                areaInput.focus();
                return;
            }
            allAreaData[areaName] = {};
            await saveAllAreaData();
            renderAreaList();
            selectArea(areaName);
            areaInput.value = '';
            showTip(`「${areaName}」区域添加成功！`, true);
        }

        // 删除区域
        async function deleteArea() {
            if (!delAreaName) return;
            delete allAreaData[delAreaName];
            await saveAllAreaData();
            closeDelModal();
            renderAreaList();
            if (delAreaName === currentAreaName) {
                const firstArea = Object.keys(allAreaData)[0];
                if (firstArea) {
                    selectArea(firstArea);
                } else {
                    currentAreaName = '';
                    currentArea.textContent = '未选中';
                    tableHead.innerHTML = '';
                    tableBody.innerHTML = '<div class="empty-tip">暂无选中区域</div>';
                    rowCount = 3;
                    colCount = 3;
                }
            }
            showTip(`「${delAreaName}」区域删除成功！`, true);
        }

        // 加载当前区域表格
        function loadCurrentAreaTable() {
            const areaData = allAreaData[currentAreaName] || {};
            if (Object.keys(areaData).length > 0) {
                const coords = Object.keys(areaData).map(k => k.split(',').map(Number));
                rowCount = Math.max(...coords.map(c => c[0])) || 3;
                colCount = Math.max(...coords.map(c => c[1])) || 3;
            } else {
                rowCount = 3;
                colCount = 3;
            }
            renderExcelTable();
        }

        // 渲染Excel表格（新增：渲染后标红重复单元格）
        function renderExcelTable() {
            if (!currentAreaName) {
                tableHead.innerHTML = '';
                tableBody.innerHTML = '<tr><td class="empty-tip" colspan="100">请先选中左侧地图区域</td></tr>';
                return;
            }
            const areaData = allAreaData[currentAreaName] || {};
            // 渲染表头
            let headHtml = '<tr><th class="excel-idx"></th>';
            for (let y = 1; y <= colCount; y++) {
                headHtml += `<th class="excel-th">Y${y}</th>`;
            }
            headHtml += '</tr>';
            tableHead.innerHTML = headHtml;
            // 渲染表体
            let bodyHtml = '';
            for (let x = 1; x <= rowCount; x++) {
                bodyHtml += `<tr class="excel-tr" data-x="${x}">`;
                bodyHtml += `<td class="excel-idx">X${x}</td>`;
                for (let y = 1; y <= colCount; y++) {
                    const key = `${x},${y}`;
                    const name = areaData[key] || '';
                    bodyHtml += `<td class="excel-cell" contenteditable="true" data-x="${x}" data-y="${y}">${name}</td>`;
                }
                bodyHtml += '</tr>';
            }
            tableBody.innerHTML = bodyHtml;

            // 单元格编辑事件（实时校验）
            document.querySelectorAll('.excel-cell').forEach(cell => {
                let originalValue = cell.textContent.trim();
                cell.addEventListener('keydown', (e) => {
                    if (e.key === 'Enter') {
                        e.preventDefault();
                        cell.blur();
                    }
                });
                cell.addEventListener('focus', () => {
                    originalValue = cell.textContent.trim();
                });
                cell.addEventListener('blur', () => {
                    const x = cell.dataset.x;
                    const y = cell.dataset.y;
                    const newName = cell.textContent.trim();
                    const key = `${x},${y}`;
                    const areaData = allAreaData[currentAreaName] || {};

                    if (newName === originalValue) return;
                    // 空名称直接删除
                    if (!newName) {
                        if (areaData[key]) delete areaData[key];
                        allAreaData[currentAreaName] = areaData;
                        markDuplicateCells(); // 刷新标红
                        return;
                    }
                    // 唯一性校验
                    const checkResult = checkNameUnique(newName, currentAreaName, key);
                    if (!checkResult.isUnique) {
                        cell.textContent = originalValue;
                        showTip(checkResult.message, false);
                        return;
                    }
                    // 校验通过，保存数据
                    areaData[key] = newName;
                    allAreaData[currentAreaName] = areaData;
                    markDuplicateCells(); // 刷新标红
                });
            });

            // 渲染完成后，标红重复单元格
            markDuplicateCells();
        }

        // 新增行/列
        function addRow() {
            if (!currentAreaName) {
                showTip('请先选中地图区域！', false);
                return;
            }
            rowCount++;
            renderExcelTable();
            showTip(`已新增X${rowCount}行！`, true);
        }
        function addCol() {
            if (!currentAreaName) {
                showTip('请先选中地图区域！', false);
                return;
            }
            colCount++;
            renderExcelTable();
            showTip(`已新增Y${colCount}列！`, true);
        }

        // 保存所有数据（核心修改：保存前先校验，有重复则拦截）
        async function saveAllAreaData() {
            // 保存前先检测重复，有重复直接返回失败
            const hasDuplicate = showDuplicateModal();
            if (hasDuplicate) return false;

            try {
                const res = await fetch('/api/save-all', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json; charset=utf-8' },
                    body: JSON.stringify(allAreaData)
                });
                const data = await res.json();
                return data.success;
            } catch (err) {
                showTip('保存失败：服务器错误', false);
                return false;
            }
        }

        // 保存当前区域（拦截重复）
        async function saveCurrentArea() {
            if (!currentAreaName) {
                showTip('请先选中地图区域！', false);
                return;
            }
            const success = await saveAllAreaData();
            if (success) {
                showTip(`「${currentAreaName}」保存成功！`, true);
            } else {
                showTip(`「${currentAreaName}」保存失败，存在重复名称！`, false);
            }
        }

        // 绑定事件
        addAreaBtn.addEventListener('click', addNewArea);
        areaInput.addEventListener('keydown', (e) => e.key === 'Enter' && addNewArea());
        confirmDelBtn.addEventListener('click', deleteArea);
        cancelDelBtn.addEventListener('click', closeDelModal);
        refreshBtn.addEventListener('click', () => {
            loadCurrentAreaTable();
            showTip('表格刷新成功！', true);
        });
        saveBtn.addEventListener('click', saveCurrentArea);
        addRowBtn.addEventListener('click', addRow);
        addColBtn.addEventListener('click', addCol);

        // 页面初始化
        window.addEventListener('load', loadAllAreaData);
    </script>
</body>
</html>
"""

# 自定义请求处理器（无修改）
class MapAreaEditorHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        return
    def set_headers(self, content_type='application/json; charset=utf-8'):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Content-Type', content_type)
        self.end_headers()
    def do_OPTIONS(self):
        self.set_headers()
    def do_GET(self):
        if self.path == '/api/get-all':
            self.set_headers()
            with open(DEFAULT_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))
        elif self.path == '/' or self.path == '':
            self.set_headers('text/html; charset=utf-8')
            self.wfile.write(HTML_CONTENT.encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'404 Not Found')
    def do_POST(self):
        if self.path == '/api/save-all':
            self.set_headers()
            content_len = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_len).decode('utf-8')
            try:
                data = json.loads(post_data)
                with open(DEFAULT_FILE, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)
                self.wfile.write(json.dumps({'success': True}).encode('utf-8'))
            except Exception as e:
                self.wfile.write(json.dumps({'success': False, 'error': str(e)}).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

# 启动服务（无修改）
def run_server():
    init_default_file()
    server_address = ('', PORT)
    httpd = HTTPServer(server_address, MapAreaEditorHandler)
    Timer(1, open_browser).start()
    print("="*90)
    print("✅ 多区域地图编辑器已启动（全局点位名称唯一版）")
    print(f"📁 数据文件：{os.path.abspath(DEFAULT_FILE)}")
    print(f"🌐 访问地址：http://localhost:{PORT}（已自动打开浏览器）")
    print("📌 核心功能：三重防重复校验 + 重复单元格标红 + 保存拦截")
    print("⚠️  关闭服务：在命令行按 Ctrl+C 即可")
    print("="*90)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.server_close()
        print("\n🛑 服务已正常停止，所有数据已保存至「系统」文件夹的Maptxt.json")

# 程序入口（无修改）
if __name__ == '__main__':
    try:
        run_server()
    except Exception as e:
        print(f"\n❌ 运行出错：{str(e)}")
        print(f"📌 脚本所在目录：{script_dir}")
        print(f"📌 上级三级目录：{parent_3_dir}")
        print(f"📌 系统文件夹路径：{system_dir}")
    finally:
        input("\n🛑 按任意键关闭窗口...")