# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

datas = [('config.json', '.'), ('web_crawler.py', '.'), ('tor_file_downloader.py', '.'), ('file_downloader.py', '.'), ('link_detector.py', '.')]
binaries = []
hiddenimports = ['requests', 'aiohttp', 'aiofiles', 'beautifulsoup4', 'lxml', 'tqdm', 'validators', 'stemquests', 'stem', 'psutil', 'PySocks', 'web_crawler', 'tor_file_downloader', 'file_downloader', 'link_detector']
tmp_ret = collect_all('stemquests')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('stem')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]


a = Analysis(
    ['/home/ctec/webcrawler/main.py'],
    pathex=['/home/ctec/webcrawler'],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter'],
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
    name='webcrawler',
    debug=False,
    bootloader_ignore_signals=False,
    strip=True,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
