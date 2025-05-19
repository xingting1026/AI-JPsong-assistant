import os

# 獲取項目根目錄
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

# 常用目錄
ASSETS_DIR = os.path.join(PROJECT_ROOT, "assets")
DOWNLOADS_DIR = os.path.join(PROJECT_ROOT, "downloads")
DICTIONARY_DIR = os.path.join(PROJECT_ROOT, "dictionary")

# 確保目錄存在
os.makedirs(ASSETS_DIR, exist_ok=True)
os.makedirs(DOWNLOADS_DIR, exist_ok=True)
os.makedirs(DICTIONARY_DIR, exist_ok=True)

# 輔助函數
def get_asset_path(asset_name):
    """獲取資源文件路徑"""
    return os.path.join(ASSETS_DIR, asset_name)

def get_font_path(font_name):
    """獲取字體文件路徑"""
    return os.path.join(ASSETS_DIR, "fonts", font_name)

def get_download_path(filename=None):
    """獲取下載文件夾路徑"""
    if filename:
        return os.path.join(DOWNLOADS_DIR, filename)
    return DOWNLOADS_DIR

def get_dictionary_path(filename=None):
    """獲取字典文件路徑"""
    if filename:
        return os.path.join(DICTIONARY_DIR, filename)
    return DICTIONARY_DIR
