import webvtt
import os
from PyQt6.QtCore import QObject, pyqtSignal
import fugashi
import requests
import json
from pathlib import Path

class SubtitleProcessor(QObject):
    """字幕處理器，支持讀取、解析和翻譯字幕"""
    
    # 定義信號
    subtitles_loaded = pyqtSignal(dict)  # 字幕字典 {'jp': [...], 'zh': [...]}
    translation_finished = pyqtSignal(list)  # 翻譯後的字幕列表 - 保留以維持兼容性
    word_analyzed = pyqtSignal(dict)  # 單詞分析結果
    
    def __init__(self):
        """初始化字幕處理器"""
        super().__init__()
        self.subtitles = {'jp': [], 'zh': []}
        self.translated_subtitles = []  # 保留以維持兼容性
        
        # 初始化日語分詞器 (暫時跳過)
        self.tagger = None
        print("注意: 日語分詞器未啟用，單詞分析功能將不可用")
        
        # 加載緩存的翻譯
        self.translation_cache = {}
        self.load_translation_cache()
    
    def load_subtitles(self, subtitle_paths):
        """加載字幕文件
           subtitle_paths 可以是字符串(單個字幕文件)或字典{'jp': path1, 'zh': path2}
        """
        # 重置字幕
        self.subtitles = {'jp': [], 'zh': []}
        
        # 處理不同的輸入類型
        if isinstance(subtitle_paths, str):
            # 如果是單個字符串，假定它是日文字幕
            jp_path = subtitle_paths
            zh_path = None
        elif isinstance(subtitle_paths, dict):
            # 如果是字典，提取日文和中文字幕路徑
            jp_path = subtitle_paths.get('jp')
            zh_path = subtitle_paths.get('zh')
        else:
            # 無效輸入
            self.subtitles_loaded.emit(self.subtitles)
            return self.subtitles
        
        # 加載日文字幕
        if jp_path and os.path.exists(jp_path):
            try:
                jp_subtitles = []
                for caption in webvtt.read(jp_path):
                    jp_subtitles.append({
                        'start': caption.start,
                        'end': caption.end,
                        'start_seconds': caption.start_in_seconds,
                        'end_seconds': caption.end_in_seconds,
                        'text': caption.text
                    })
                self.subtitles['jp'] = jp_subtitles
                print(f"成功加載日文字幕，共 {len(jp_subtitles)} 條")
            except Exception as e:
                print(f"加載日文字幕失敗: {e}")
        
        # 加載繁體中文字幕
        if zh_path and os.path.exists(zh_path):
            try:
                zh_subtitles = []
                for caption in webvtt.read(zh_path):
                    zh_subtitles.append({
                        'start': caption.start,
                        'end': caption.end,
                        'start_seconds': caption.start_in_seconds,
                        'end_seconds': caption.end_in_seconds,
                        'text': caption.text
                    })
                self.subtitles['zh'] = zh_subtitles
                print(f"成功加載繁體中文字幕，共 {len(zh_subtitles)} 條")
                
                # 如果日文和中文字幕時間軸不一致，嘗試同步
                if self.subtitles['jp'] and len(self.subtitles['jp']) != len(zh_subtitles):
                    print("檢測到日文和中文字幕時間不同步，嘗試同步...")
                    self.subtitles['zh'] = self.align_subtitle_timing(
                        self.subtitles['jp'], 
                        zh_subtitles
                    )
            except Exception as e:
                print(f"加載繁體中文字幕失敗: {e}")
        
        # 為保持兼容性，設置translated_subtitles
        if self.subtitles['zh']:
            self.translated_subtitles = self.subtitles['zh']
        
        # 發射信號
        self.subtitles_loaded.emit(self.subtitles)
        return self.subtitles
    
    def align_subtitle_timing(self, jp_subtitles, zh_subtitles):
        """改進的字幕同步方法，處理中文字幕提前顯示的情況"""
        if not jp_subtitles or not zh_subtitles:
            return zh_subtitles
                
        print(f"字幕同步: 日文字幕 {len(jp_subtitles)} 條, 中文字幕 {len(zh_subtitles)} 條")
        
        aligned_zh_subtitles = []
        
        # 針對問題的解決方案：分割過長的中文字幕
        # 首先處理一些中文字幕可能包含多句內容的情況
        processed_zh_subtitles = []
        for sub in zh_subtitles:
            text = sub['text']
            # 檢查文本是否包含可能的分句標記（如句號、換行等）
            if '\n' in text or '。' in text or '. ' in text:
                parts = text.replace('\n', '。').replace('. ', '。').split('。')
                parts = [p for p in parts if p.strip()]  # 過濾空字符串
                
                if len(parts) > 1:
                    # 將一條字幕分成多條
                    duration = sub['end_seconds'] - sub['start_seconds']
                    part_duration = duration / len(parts)
                    
                    for i, part in enumerate(parts):
                        new_start = sub['start_seconds'] + i * part_duration
                        new_end = new_start + part_duration
                        
                        processed_zh_subtitles.append({
                            'start': sub['start'],  # 保持原始格式
                            'end': sub['end'],      # 保持原始格式
                            'start_seconds': new_start,
                            'end_seconds': new_end,
                            'text': part.strip()
                        })
                else:
                    processed_zh_subtitles.append(sub)
            else:
                processed_zh_subtitles.append(sub)
        
        # 對日文字幕逐一配對中文字幕
        for jp_sub in jp_subtitles:
            jp_start = jp_sub['start_seconds']
            jp_end = jp_sub['end_seconds']
            jp_text = jp_sub['text']
            
            # 嘗試找到時間重疊的中文字幕
            matching_zh_subs = []
            for zh_sub in processed_zh_subtitles:
                zh_start = zh_sub['start_seconds']
                zh_end = zh_sub['end_seconds']
                
                # 檢查時間重疊
                if (zh_start <= jp_end and zh_end >= jp_start):
                    matching_zh_subs.append(zh_sub)
            
            # 如果找到多條匹配的中文字幕，選擇時間重疊最多的
            best_zh_sub = None
            max_overlap = 0
            
            for zh_sub in matching_zh_subs:
                zh_start = zh_sub['start_seconds']
                zh_end = zh_sub['end_seconds']
                
                # 計算重疊時間
                overlap_start = max(jp_start, zh_start)
                overlap_end = min(jp_end, zh_end)
                overlap = max(0, overlap_end - overlap_start)
                
                if overlap > max_overlap:
                    max_overlap = overlap
                    best_zh_sub = zh_sub
            
            # 創建新的中文字幕條目，使用日文字幕的時間軸
            if best_zh_sub:
                aligned_zh_sub = {
                    'start': jp_sub['start'],
                    'end': jp_sub['end'],
                    'start_seconds': jp_sub['start_seconds'],
                    'end_seconds': jp_sub['end_seconds'],
                    'text': best_zh_sub['text']
                }
            else:
                # 如果找不到對應的中文字幕，創建一個空的
                aligned_zh_sub = {
                    'start': jp_sub['start'],
                    'end': jp_sub['end'],
                    'start_seconds': jp_sub['start_seconds'],
                    'end_seconds': jp_sub['end_seconds'],
                    'text': ""  # 空字幕
                }
            
            aligned_zh_subtitles.append(aligned_zh_sub)
        
        print(f"字幕同步完成，生成 {len(aligned_zh_subtitles)} 條同步中文字幕")
        return aligned_zh_subtitles
    
    def translate_subtitles(self, target_language="zh-TW"):
        """翻譯字幕
           注意：如果已經有繁體中文字幕，這個方法什麼也不做
        """
        # 如果已經有繁體中文字幕，直接返回
        if self.subtitles['zh']:
            self.translation_finished.emit(self.subtitles['zh'])
            return self.subtitles['zh']
            
        # 如果沒有日文字幕或中文字幕，則無法進行翻譯
        if not self.subtitles['jp']:
            print("沒有日文字幕可翻譯")
            return []
            
        print("未找到官方中文字幕，建議使用專業翻譯服務API進行翻譯")
        return []
    
    def analyze_word(self, word):
        """分析日語單詞"""
        if not word or not self.tagger:
            # 返回基本信息
            word_info = {
                'surface': word,
                'lemma': word,
                'pos': '未知',
                'pronunciation': word,
            }
            self.word_analyzed.emit(word_info)
            return word_info
            
        try:
            # 使用fugashi進行形態素分析
            words = self.tagger.parse(word)
            
            if not words:
                return None
                
            # 提取第一個單詞的信息
            word_obj = words[0]
            
            # 構建單詞信息
            word_info = {
                'surface': word_obj.surface,  # 單詞表面形式
                'lemma': word_obj.feature.lemma or word_obj.surface,  # 詞根形式
                'pos': word_obj.feature.pos,  # 詞性
                'pronunciation': word_obj.feature.pronunciation,  # 發音
            }
            
            # 發射信號
            self.word_analyzed.emit(word_info)
            
            return word_info
        except Exception as e:
            print(f"分析單詞失敗: {e}")
            
            # 返回基本信息
            word_info = {
                'surface': word,
                'lemma': word,
                'pos': '未知',
                'pronunciation': word,
            }
            self.word_analyzed.emit(word_info)
            return word_info
    
    def load_translation_cache(self):
        """加載翻譯緩存"""
        cache_path = Path('downloads/translation_cache.json')
        if cache_path.exists():
            try:
                with open(cache_path, 'r', encoding='utf-8') as f:
                    self.translation_cache = json.load(f)
            except Exception as e:
                print(f"加載翻譯緩存失敗: {e}")
                self.translation_cache = {}
    
    def save_translation_cache(self):
        """保存翻譯緩存"""
        cache_path = Path('downloads/translation_cache.json')
        try:
            cache_path.parent.mkdir(exist_ok=True)
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(self.translation_cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存翻譯緩存失敗: {e}")
    
    def get_current_subtitle(self, current_time):
        """根據當前時間獲取字幕"""
        result = {'jp': None, 'zh': None}
        
        # 查找當前時間對應的日文字幕
        for subtitle in self.subtitles['jp']:
            start_time = subtitle['start_seconds']
            end_time = subtitle.get('end_seconds', start_time + 5)  # 假設每條字幕顯示5秒
            
            if start_time <= current_time <= end_time:
                result['jp'] = subtitle
                break
        
        # 查找當前時間對應的中文字幕
        for subtitle in self.subtitles['zh']:
            start_time = subtitle['start_seconds']
            end_time = subtitle.get('end_seconds', start_time + 5)  # 假設每條字幕顯示5秒
            
            if start_time <= current_time <= end_time:
                result['zh'] = subtitle
                break
        
        return result