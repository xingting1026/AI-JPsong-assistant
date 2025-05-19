import os
import json
import threading
from PyQt6.QtCore import QObject, pyqtSignal
from paths import get_download_path, get_dictionary_path
from yt_dlp import YoutubeDL

class DataManager(QObject):
    """數據管理器，處理視頻、字幕和詞典數據"""
    
    # 定義信號
    video_downloaded = pyqtSignal(str, object)  # 視頻路徑, 字幕路徑（可以是字符串或字典）
    download_progress = pyqtSignal(str, float)  # 文件名, 進度百分比
    download_error = pyqtSignal(str)  # 錯誤信息
    
    def __init__(self):
        """初始化數據管理器"""
        super().__init__()
        self.current_video_path = ""
        self.current_subtitle_path = ""
        self.recent_videos = self._load_recent_videos()
    
    def _load_recent_videos(self):
        """加載最近播放的視頻列表"""
        recent_file = get_download_path("recent.json")
        if os.path.exists(recent_file):
            try:
                with open(recent_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def _save_recent_videos(self):
        """保存最近播放的視頻列表"""
        recent_file = get_download_path("recent.json")
        try:
            with open(recent_file, 'w', encoding='utf-8') as f:
                json.dump(self.recent_videos, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存最近視頻列表失敗: {e}")
    
    def download_from_youtube(self, url, language="ja"):
        """從YouTube下載視頻和字幕"""
        if not url:
            self.download_error.emit("請輸入有效的YouTube網址")
            return
            
        save_path = get_download_path()
        
        # 修改這裡，只下載官方字幕，不下載自動生成的字幕
        ydl_opts = {
            'outtmpl': os.path.join(save_path, '%(title)s.%(ext)s'),
            'writesubtitles': True,
            'writeautomaticsub': False,  # 設為False，禁用自動生成字幕
            'subtitleslangs': [language, 'zh-Hant', 'zh-TW', 'zh'],  # 添加更多可能的繁體中文字幕代碼
            'format': 'bestvideo[height<=720]+bestaudio/best[height<=720]',
            'merge_output_format': 'mp4',
            'progress_hooks': [self._download_progress_hook],
            'skip_download': False,  # 確保下載視頻
            'verbose': True  # 開啟詳細日誌
        }
        
        def download_thread():
            """下載線程"""
            try:
                with YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    video_path = os.path.join(save_path, f"{info['title']}.mp4")
                    
                    # 打印可用字幕信息
                    if 'requested_subtitles' in info:
                        print(f"可用字幕: {list(info['requested_subtitles'].keys())}")
                    
                    # 獲取日文字幕路徑
                    jp_subtitle_path = None
                    if os.path.exists(os.path.join(save_path, f"{info['title']}.{language}.vtt")):
                        jp_subtitle_path = os.path.join(save_path, f"{info['title']}.{language}.vtt")
                    
                    # 獲取繁體中文字幕路徑 (嘗試多種可能的後綴)
                    zh_subtitle_path = None
                    possible_zh_suffixes = ['zh-Hant.vtt', 'zh-TW.vtt', 'zh.vtt']
                    for suffix in possible_zh_suffixes:
                        path = os.path.join(save_path, f"{info['title']}.{suffix}")
                        if os.path.exists(path):
                            zh_subtitle_path = path
                            print(f"找到繁體中文字幕: {path}")
                            break
                    
                    # 將字幕路徑作為字典傳遞
                    subtitle_paths = {
                        'jp': jp_subtitle_path,
                        'zh': zh_subtitle_path
                    }
                    
                    # 添加到最近視頻列表
                    self._add_to_recent(video_path, subtitle_paths, info['title'], url)
                    
                    # 發射下載完成信號
                    self.video_downloaded.emit(video_path, subtitle_paths)
            except Exception as e:
                self.download_error.emit(f"下載失敗: {str(e)}")
        
        # 啟動下載線程
        threading.Thread(target=download_thread, daemon=True).start()
    
    def _download_progress_hook(self, progress):
        """下載進度回調"""
        if progress['status'] == 'downloading':
            filename = os.path.basename(progress['filename'])
            percent = progress.get('_percent_str', '0%').strip()
            try:
                percent_float = float(percent.replace('%', ''))
                self.download_progress.emit(filename, percent_float)
            except:
                pass
    
    def _add_to_recent(self, video_path, subtitle_path, title, url):
        """添加到最近視頻列表"""
        # 創建記錄
        record = {
            'title': title,
            'video_path': video_path,
            'subtitle_path': subtitle_path,  # 這可以是字典或字符串
            'url': url,
            'timestamp': import_time()
        }
        
        # 檢查是否已存在，如果存在則移除舊記錄
        self.recent_videos = [v for v in self.recent_videos if v.get('video_path') != video_path]
        
        # 添加到列表頂部
        self.recent_videos.insert(0, record)
        
        # 限制列表大小為10
        if len(self.recent_videos) > 10:
            self.recent_videos = self.recent_videos[:10]
            
        # 保存列表
        self._save_recent_videos()
    
    def get_recent_videos(self):
        """獲取最近播放的視頻列表"""
        return self.recent_videos
        
    def set_current_video(self, video_path, subtitle_path=None):
        """設置當前視頻和字幕"""
        self.current_video_path = video_path
        
        # 如果未提供字幕路徑，嘗試猜測
        if subtitle_path is None and video_path:
            base_path = os.path.splitext(video_path)[0]
            
            # 初始化字幕路徑字典
            subtitle_paths = {'jp': None, 'zh': None}
            
            # 尋找日文字幕
            possible_jp_subtitles = [
                f"{base_path}.ja.vtt",
                f"{base_path}.jp.vtt",
                f"{base_path}.jpn.vtt"
            ]
            for path in possible_jp_subtitles:
                if os.path.exists(path):
                    subtitle_paths['jp'] = path
                    break
            
            # 尋找繁體中文字幕
            possible_zh_subtitles = [
                f"{base_path}.zh-Hant.vtt",
                f"{base_path}.zh-TW.vtt",
                f"{base_path}.zh.vtt"
            ]
            for path in possible_zh_subtitles:
                if os.path.exists(path):
                    subtitle_paths['zh'] = path
                    break
            
            # 如果至少找到一種字幕，設置字幕路徑
            if subtitle_paths['jp'] or subtitle_paths['zh']:
                self.current_subtitle_path = subtitle_paths
            else:
                # 檢查是否有通用字幕文件
                if os.path.exists(f"{base_path}.vtt"):
                    self.current_subtitle_path = f"{base_path}.vtt"
                else:
                    self.current_subtitle_path = None
        else:
            self.current_subtitle_path = subtitle_path
        
        # 返回設置的路徑
        return self.current_video_path, self.current_subtitle_path

# 獲取當前時間戳
def import_time():
    """導入時間模塊並獲取當前時間戳"""
    from datetime import datetime
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')