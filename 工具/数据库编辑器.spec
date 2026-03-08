# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('Buff', 'Buff'), ('NPC', 'NPC'), ('NPC技能', 'NPC技能'), ('技能', '技能'), ('掉落', '掉落'), ('效果buff', '效果buff'), ('道具', '道具'), ('技能系统', '技能系统'), ('补丁', '补丁')],
    hiddenimports=['PIL', 'PIL.Image', 'PIL.ImageTk', 'tkinter.colorchooser', 'tkinter.filedialog', 'tkinter.messagebox', 'tkinter.simpledialog', 'pathlib', 'datetime', 'uuid', 'shutil', 're', 'pandas', 'numpy'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='数据库编辑器',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
