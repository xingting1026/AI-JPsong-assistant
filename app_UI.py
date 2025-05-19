from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QLabel, QSplitter, QFileDialog, QProgressBar, QComboBox,
    QFrame, QLineEdit, QStatusBar, QMessageBox, QTabWidget
)
from PyQt6.QtCore import Qt, QSize,QTimer
from PyQt6.QtGui import QIcon, QFont

from media_player import MediaPlayer
from dictionary_widget import DictionaryWidget
from ai_assistant import AIAssistant
from ai_chat_widget import AIChatWidget
from data_manager import DataManager
from subtitle_processor import SubtitleProcessor
from paths import get_download_path, get_asset_path

class SubtitleDisplayWidget(QWidget):
    """字幕顯示小工具"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        
        # 創建裝飾框架
        subtitle_frame = QFrame()
        subtitle_frame.setFrameShape(QFrame.Shape.StyledPanel)
        subtitle_frame.setStyleSheet("""
            QFrame {
                background-color: #F9FBE7;
                border: 2px solid #DCEDC8;
                border-radius: 10px;
                padding: 5px;
            }
        """)
        
        subtitle_layout = QVBoxLayout(subtitle_frame)
        
        # 日文字幕
        self.japanese_subtitle = QLabel()
        self.japanese_subtitle.setWordWrap(True)
        self.japanese_subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.japanese_subtitle.setFont(QFont("Yu Gothic UI", 16))
        self.japanese_subtitle.setStyleSheet("""
            background-color: rgba(0, 0, 0, 0.7);
            color: white;
            padding: 15px;
            border-radius: 10px;
            margin: 5px;
        """)
        # 啟用文本選擇功能
        self.japanese_subtitle.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse | 
            Qt.TextInteractionFlag.TextSelectableByKeyboard
        )
        
        # 中文翻譯
        self.chinese_subtitle = QLabel()
        self.chinese_subtitle.setWordWrap(True)
        self.chinese_subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.chinese_subtitle.setFont(QFont("Microsoft JhengHei UI", 14))
        self.chinese_subtitle.setStyleSheet("""
            background-color: rgba(0, 0, 0, 0.5);
            color: #FFEB3B;
            padding: 12px;
            border-radius: 10px;
            margin: 5px;
        """)
        # 啟用文本選擇功能
        self.chinese_subtitle.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse | 
            Qt.TextInteractionFlag.TextSelectableByKeyboard
        )
        
        # 添加到佈局
        subtitle_layout.addWidget(self.japanese_subtitle)
        subtitle_layout.addWidget(self.chinese_subtitle)
        
        layout.addWidget(subtitle_frame)
        layout.addStretch(1)  # 底部留白
        
    def update_subtitle(self, japanese_text, chinese_text=""):
        """更新字幕文本"""
        self.japanese_subtitle.setText(japanese_text)
        self.chinese_subtitle.setText(chinese_text)
        
    def clear_subtitle(self):
        """清除字幕"""
        self.japanese_subtitle.clear()
        self.chinese_subtitle.clear()
        
        # 額外設置一些佔位文本，使字幕區域保持可見
        self.japanese_subtitle.setText("")
        self.chinese_subtitle.setText("")

class JapaneseAssistantUI(QMainWindow):
    """日語學習助手主界面"""
    def __init__(self):
        super().__init__()
        
        # 設置窗口屬性
        self.setWindowTitle("AI 日語學習助手")
        self.resize(1200, 800)
        
        # 初始化組件
        self.data_manager = DataManager()
        self.subtitle_processor = SubtitleProcessor()
        self.ai_assistant = AIAssistant()  # 初始化AI助手
        
        # 添加這一行來初始化字幕跟蹤變量
        self._last_subtitle = (None, None)
        self._current_jp_subtitle = ""  # 當前日文字幕
        
        # 初始化UI
        self.init_ui()
        
        # 連接數據管理器的信號
        self.connect_signals()
        
        # 顯示歡迎信息
        self.status_bar.showMessage("歡迎使用 AI 日語學習助手")
        
    def init_ui(self):
        """初始化用戶界面"""
        # 創建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主佈局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # 頂部工具欄
        toolbar_frame = self.create_toolbar()
        
        # 創建分割器
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # 左側：視頻播放區
        video_widget = QWidget()
        video_layout = QVBoxLayout(video_widget)
        video_layout.setContentsMargins(0, 0, 0, 0)
        
        # 視頻播放器
        self.media_player = MediaPlayer()
        
        # 字幕顯示區
        self.subtitle_display = SubtitleDisplayWidget()
        
        video_layout.addWidget(self.media_player)
        video_layout.addWidget(self.subtitle_display)
        
        # 右側：選項卡容器（字典和AI助手）
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        # 創建選項卡小工具
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #C5CAE9;
                border-radius: 3px;
            }
            QTabBar::tab {
                background: #E8EAF6;
                border: 1px solid #C5CAE9;
                padding: 5px 10px;
                border-top-left-radius: 3px;
                border-top-right-radius: 3px;
            }
            QTabBar::tab:selected {
                background: #5C6BC0;
                color: white;
            }
            QTabBar::tab:!selected {
                margin-top: 2px;
            }
        """)
        
        # 字典小工具
        self.dictionary = DictionaryWidget()
        
        # AI助手聊天小工具
        self.ai_chat = AIChatWidget()
        
        # 添加到選項卡
        self.tab_widget.addTab(self.dictionary, "字典查詢")
        self.tab_widget.addTab(self.ai_chat, "AI助手")
        
        right_layout.addWidget(self.tab_widget)
        
        # 添加到分割器
        splitter.addWidget(video_widget)
        splitter.addWidget(right_widget)
        
        # 設置分割器初始大小
        splitter.setSizes([int(self.width() * 0.7), int(self.width() * 0.3)])
        
        # 狀態欄
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # 添加到主佈局
        main_layout.addWidget(toolbar_frame)
        main_layout.addWidget(splitter)
        
    def create_toolbar(self):
        """創建頂部工具欄"""
        toolbar_frame = QFrame()
        toolbar_frame.setFrameShape(QFrame.Shape.StyledPanel)
        toolbar_frame.setMaximumHeight(60)
        toolbar_frame.setStyleSheet("""
            QFrame {
                background-color: #F5F5F5;
                border: 1px solid #E0E0E0;
                border-radius: 4px;
            }
        """)
        
        toolbar_layout = QHBoxLayout(toolbar_frame)
        toolbar_layout.setContentsMargins(5, 5, 5, 5)
        
        # YouTube 網址輸入框
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("輸入 YouTube 網址...")
        
        # 語言選擇下拉框
        self.language_combo = QComboBox()
        self.language_combo.addItems(["日語 (ja)", "英語 (en)", "韓語 (ko)"])
        
        # 下載按鈕
        self.download_button = QPushButton("下載視頻+字幕")
        self.download_button.clicked.connect(self.download_video)
        
        # 打開本地文件按鈕
        self.open_button = QPushButton("打開本地文件")
        self.open_button.clicked.connect(self.open_local_file)
        
        # 進度條
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumWidth(200)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setVisible(False)  # 初始隱藏
        
        # 添加到工具欄佈局
        toolbar_layout.addWidget(self.url_input)
        toolbar_layout.addWidget(self.language_combo)
        toolbar_layout.addWidget(self.download_button)
        toolbar_layout.addWidget(self.open_button)
        toolbar_layout.addWidget(self.progress_bar)
        
        return toolbar_frame
    
    def connect_signals(self):
        """連接信號到槽"""
        # 數據管理器信號
        self.data_manager.video_downloaded.connect(self.on_video_downloaded)
        self.data_manager.download_progress.connect(self.on_download_progress)
        self.data_manager.download_error.connect(self.on_download_error)
        
        # 媒體播放器信號
        self.media_player.position_changed.connect(self.on_position_changed)
        
        # 字幕處理器信號
        self.subtitle_processor.word_analyzed.connect(self.dictionary.display_word_info)
        
        # 字典小工具信號
        self.dictionary.word_selected.connect(self.on_word_selected)
        
        # AI助手信號
        self.ai_assistant.response_ready.connect(self.on_ai_response)
        self.ai_assistant.translation_ready.connect(self.on_translation_ready)
        self.ai_assistant.error_occurred.connect(self.on_ai_error)
        
        # AI聊天小工具信號
        self.ai_chat.question_submitted.connect(self.on_question_submitted)
        self.ai_chat.grammar_analysis_requested.connect(self.on_grammar_analysis_requested)
        self.ai_chat.translation_requested.connect(self.on_translation_requested)
    
    
    def download_video(self):
        """下載 YouTube 視頻"""
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "錯誤", "請輸入有效的 YouTube 網址")
            return
        
        # 獲取選中的語言代碼
        language = self.language_combo.currentText()
        lang_code = language.split("(")[1].strip(")")
        
        # 顯示進度條
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)
        
        # 更新狀態欄
        self.status_bar.showMessage(f"正在下載視頻和{language}字幕...")
        
        # 禁用下載按鈕和打開文件按鈕，防止重複操作
        self.download_button.setEnabled(False)
        self.open_button.setEnabled(False)
        
        # 開始下載
        self.data_manager.download_from_youtube(url, lang_code)
    
    def open_local_file(self):
        """打開本地視頻文件"""
        options = QFileDialog.Option.ReadOnly
        file_path, _ = QFileDialog.getOpenFileName(
            self, "打開視頻文件", get_download_path(),
            "視頻文件 (*.mp4 *.mkv *.avi *.mov);;所有文件 (*)", options=options
        )
        
        if not file_path:
            return
            
        # 設置當前視頻
        video_path, subtitle_path = self.data_manager.set_current_video(file_path)
        
        # 加載視頻
        if video_path:
            self.load_media(video_path, subtitle_path)
    
    def load_media(self, video_path, subtitle_paths=None):
        """加載媒體和字幕"""
        # 先停止當前正在播放的媒體
        self.media_player.stop()
        
        # 清空當前字幕顯示
        self.subtitle_display.clear_subtitle()
        
        # 重置字幕處理器
        self.subtitle_processor.subtitles = {'jp': [], 'zh': []}
        
        # 重置當前字幕追踪變量
        self._last_subtitle = (None, None)
        self._current_jp_subtitle = ""
        self.ai_chat.set_current_subtitle("")
        
        # 短暫延遲，確保媒體播放器已經停止
        QTimer.singleShot(100, lambda: self._complete_media_loading(video_path, subtitle_paths))

    def _complete_media_loading(self, video_path, subtitle_paths=None):
        """完成媒體加載的第二部分"""
        # 加載視頻
        if self.media_player.load_media(video_path):
            # 加載字幕（如果有）
            if subtitle_paths:
                subtitles = self.subtitle_processor.load_subtitles(subtitle_paths)
                if subtitles and (subtitles['jp'] or subtitles['zh']):
                    # 更新狀態欄
                    jp_status = "有日文字幕" if subtitles['jp'] else "無日文字幕"
                    zh_status = "有繁體中文字幕" if subtitles['zh'] else "無繁體中文字幕"
                    self.status_bar.showMessage(f"已加載視頻({jp_status}, {zh_status}): {video_path}")
                else:
                    self.status_bar.showMessage(f"已加載視頻（無字幕）: {video_path}")
            else:
                self.status_bar.showMessage(f"已加載視頻（無字幕）: {video_path}")
                
            # 開始播放新視頻
            self.media_player.play()
    
    def on_video_downloaded(self, video_path, subtitle_paths):
        """視頻下載完成回調"""
        # 隱藏進度條
        self.progress_bar.setVisible(False)
        
        # 加載視頻和字幕 - 使用修正後的方法
        self.load_media(video_path, subtitle_paths)
        
        # 更新狀態欄
        self.status_bar.showMessage(f"視頻下載完成: {video_path}")
        
        # 重新啟用下載按鈕和打開文件按鈕
        self.download_button.setEnabled(True)
        self.open_button.setEnabled(True)
    
    def on_download_progress(self, filename, percent):
        """下載進度回調"""
        self.progress_bar.setValue(int(percent))
        self.status_bar.showMessage(f"正在下載: {filename} - {percent:.1f}%")
    
    def on_download_error(self, error_message):
        """下載錯誤回調"""
        self.progress_bar.setVisible(False)
        self.status_bar.showMessage(f"下載失敗: {error_message}")
        QMessageBox.warning(self, "下載錯誤", error_message)
        
        # 重新啟用下載按鈕和打開文件按鈕
        self.download_button.setEnabled(True)
        self.open_button.setEnabled(True)
    
    def on_position_changed(self, position):
        """播放位置變化回調"""
        # 獲取當前時間點的字幕
        current_time_seconds = position / 1000.0
        subtitles = self.subtitle_processor.get_current_subtitle(current_time_seconds)
        
        jp_subtitle = subtitles.get('jp')
        zh_subtitle = subtitles.get('zh')
        
        # 決定要顯示什麼字幕
        jp_text = jp_subtitle['text'] if jp_subtitle else ""
        zh_text = zh_subtitle['text'] if zh_subtitle else ""
        
        # 更新當前日文字幕 (用於AI助手上下文)
        if jp_text:
            self._current_jp_subtitle = jp_text
            self.ai_chat.set_current_subtitle(jp_text)
        
        # 調試輸出，查看中文字幕和日文字幕是否對應
        if (jp_text or zh_text) and self._last_subtitle != (jp_text, zh_text):
            self._last_subtitle = (jp_text, zh_text)
            print(f"時間: {current_time_seconds:.2f}")
            print(f"日文: {jp_text}")
            print(f"中文: {zh_text}")
            print("-" * 50)
        
        if jp_text or zh_text:
            # 更新字幕顯示
            self.subtitle_display.update_subtitle(jp_text, zh_text)
        else:
            # 清除字幕顯示
            self.subtitle_display.clear_subtitle()
    
    def on_word_selected(self, word):
        """當單詞被選中時的回調"""
        # 分析單詞
        word_info = self.subtitle_processor.analyze_word(word)
        
        # 更新狀態欄
        if word_info:
            self.status_bar.showMessage(f"已查詢單詞: {word}")
        else:
            self.status_bar.showMessage(f"無法解析單詞: {word}")
    
    def on_ai_response(self, response):
        """AI回覆回調"""
        self.ai_chat.handle_ai_response(response)
    
    def on_translation_ready(self, original_text, translated_text):
        """翻譯完成回調"""
        # 移除"正在翻譯"消息
        self.ai_chat.remove_thinking_message()
        
        # 添加翻譯結果
        self.ai_chat.add_bot_message(f"原文: {original_text}\n\n{translated_text}")
    
    def on_ai_error(self, error_message):
        """AI錯誤回調"""
        self.ai_chat.handle_error(error_message)
    
    def on_question_submitted(self, question, context):
        """問題提交回調"""
        self.ai_assistant.ask_question(question, context)
    
    def on_grammar_analysis_requested(self, sentence):
        """語法分析請求回調"""
        self.ai_assistant.analyze_grammar(sentence)
    
    def on_translation_requested(self, text):
        """翻譯請求回調"""
        self.ai_assistant.translate_text(text)
    
    def closeEvent(self, event):
        """窗口關閉事件回調"""
        # 停止媒體播放
        self.media_player.cleanup()
        
        # 調用父類的關閉事件處理
        super().closeEvent(event)