from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLineEdit,
    QPushButton, QLabel, QScrollArea, QFrame, QSplitter
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QColor, QTextCursor

class MessageWidget(QFrame):
    """單個聊天消息組件 - 自適應高度"""
    
    def __init__(self, text, is_user=False, parent=None):
        """
        初始化消息組件
        
        Args:
            text: 消息文本
            is_user: 是否為用戶消息
            parent: 父組件
        """
        super().__init__(parent)
        self.is_user = is_user
        self.init_ui(text)
        
    def init_ui(self, text):
        """初始化UI"""
        layout = QHBoxLayout(self)
        
        # 消息氣泡的樣式 - 更寬的設計和更大的字體
        user_bubble_style = """
            background-color: #E0F7FA;
            border: 1px solid #B2EBF2;
            border-radius: 15px;
            padding: 15px;
            color: #00838F;
            font-size: 16px;
        """
        
        bot_bubble_style = """
            background-color: #FFF8E1;
            border: 1px solid #FFECB3;
            border-radius: 15px;
            padding: 15px;
            color: #FF6F00;
            font-size: 16px;
        """
        
        # 創建消息文本 - 完全自適應高度
        self.text_label = QTextEdit()
        self.text_label.setReadOnly(True)
        self.text_label.setStyleSheet(user_bubble_style if self.is_user else bot_bubble_style)
        
        # 使用 setPlainText 而不是 setText
        self.text_label.setPlainText(text)
        
        # 禁用滾動條，這樣 QTextEdit 會完全顯示其內容
        self.text_label.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.text_label.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # 設置文本編輯器為自動擴展
        self.text_label.document().documentLayout().documentSizeChanged.connect(self.adjust_height)
        self.text_label.setMinimumHeight(50)  # 設置最小高度
        
        # 調整初始高度
        self.adjust_height()
        
        # 可複製的文本
        self.text_label.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse | 
            Qt.TextInteractionFlag.TextSelectableByKeyboard
        )
        
        # 根據是用戶還是助手消息，調整佈局
        if self.is_user:
            layout.addStretch(1)
            layout.addWidget(self.text_label)
        else:
            layout.addWidget(self.text_label)
            layout.addStretch(1)
            
        # 設置更寬的寬度 - 增加最大寬度使對話框更寬
        self.text_label.setMinimumWidth(300)
        self.text_label.setMaximumWidth(600)  # 增加最大寬度
        
        layout.setContentsMargins(10, 5, 10, 5)
    
    def adjust_height(self):
        """調整高度以適應文本內容"""
        # 獲取文檔大小
        doc_size = self.text_label.document().size().toSize()
        # 計算所需高度，加上一些額外空間用於邊距
        content_height = doc_size.height() + 30  # 加上內邊距
        # 設置文本編輯器的高度
        self.text_label.setFixedHeight(int(content_height))

class AIChatWidget(QWidget):
    """AI助手聊天組件"""
    
    # 定義信號
    question_submitted = pyqtSignal(str, str)  # 問題, 當前字幕
    grammar_analysis_requested = pyqtSignal(str)  # 要分析的句子
    translation_requested = pyqtSignal(str)  # 要翻譯的文本
    
    def __init__(self, parent=None):
        """初始化AI聊天組件"""
        super().__init__(parent)
        self.current_subtitle = ""
        self.init_ui()
        
    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        
        # 聊天標題 - 更加可愛的風格
        title_frame = QFrame()
        title_frame.setStyleSheet("""
            QFrame {
                background-color: #FFF8E1;
                border: 2px solid #FFECB3;
                border-radius: 10px;
                margin-bottom: 10px;
            }
        """)
        title_layout = QHBoxLayout(title_frame)
        
        title_label = QLabel("小瑤 AI 日語學習助手 (っ●ω●)っ♡")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #FF6F00;
            padding: 8px;
        """)
        
        title_layout.addWidget(title_label)
        
        # 創建聊天消息區域
        chat_frame = QFrame()
        chat_frame.setStyleSheet("""
            QFrame {
                background-color: #FAFAFA;
                border: 2px solid #E0E0E0;
                border-radius: 10px;
            }
        """)
        chat_layout = QVBoxLayout(chat_frame)
        
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                border: none;
                background: #F5F5F5;
                width: 10px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: #BDBDBD;
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }
        """)
        
        # 聊天消息容器 - 設置更大的間距和更寬的內容區域
        self.chat_container = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_container)
        self.chat_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.chat_layout.setContentsMargins(15, 15, 15, 15)  # 增加邊距
        self.chat_layout.setSpacing(20)  # 增加間距
        
        self.scroll_area.setWidget(self.chat_container)
        chat_layout.addWidget(self.scroll_area)
        
        # 機器人初始問候消息
        self.add_bot_message("你好呀～我是小瑤！(ﾉ◕ヮ◕)ﾉ*:･ﾟ✧\n\n我是你的日語學習小幫手！有什麼關於日語學習的問題，或是想瞭解當前視頻內容，都可以問我喔～")
        
        # 輸入區域 - 美化版本，更大的字體
        input_frame = QFrame()
        input_frame.setStyleSheet("""
            QFrame {
                background-color: #FFF8E1;
                border: 2px solid #FFECB3;
                border-radius: 10px;
                padding: 8px;
            }
        """)
        input_layout = QHBoxLayout(input_frame)
        
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("輸入問題或指令...")
        self.input_field.setStyleSheet("""
            QLineEdit {
                border: 1px solid #FFD54F;
                border-radius: 8px;
                padding: 12px;
                background-color: white;
                font-size: 16px;  /* 增加字體大小 */
            }
        """)
        self.input_field.setMinimumHeight(45)  # 增加輸入框高度
        self.input_field.returnPressed.connect(self.submit_question)
        
        self.send_button = QPushButton("發送")
        self.send_button.setStyleSheet("""
            QPushButton {
                background-color: #FFC107;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 20px;  /* 增加按鈕內邊距 */
                font-weight: bold;
                font-size: 16px;  /* 增加字體大小 */
            }
            QPushButton:hover {
                background-color: #FFB300;
            }
        """)
        self.send_button.setMinimumHeight(45)  # 增加按鈕高度
        self.send_button.clicked.connect(self.submit_question)
        
        input_layout.addWidget(self.input_field)
        input_layout.addWidget(self.send_button)
        
        # 功能按鈕 - 更漂亮的版本，更大的字體
        button_frame = QFrame()
        button_frame.setStyleSheet("""
            QFrame {
                background-color: #F9FBE7;
                border: 2px solid #DCEDC8;
                border-radius: 10px;
                padding: 8px;
                margin-top: 8px;
            }
        """)
        button_layout = QHBoxLayout(button_frame)
        
        self.analyze_button = QPushButton("✧ 分析當前字幕 ✧")
        self.analyze_button.setStyleSheet("""
            QPushButton {
                background-color: #C5E1A5;
                color: #33691E;
                border: none;
                border-radius: 8px;
                padding: 12px 20px;  /* 增加按鈕內邊距 */
                font-weight: bold;
                font-size: 16px;  /* 增加字體大小 */
            }
            QPushButton:hover {
                background-color: #AED581;
            }
        """)
        self.analyze_button.setMinimumHeight(45)  # 增加按鈕高度
        self.analyze_button.clicked.connect(self.request_subtitle_analysis)
        
        self.translate_button = QPushButton("✧ 翻譯當前字幕 ✧")
        self.translate_button.setStyleSheet("""
            QPushButton {
                background-color: #C5E1A5;
                color: #33691E;
                border: none;
                border-radius: 8px;
                padding: 12px 20px;  /* 增加按鈕內邊距 */
                font-weight: bold;
                font-size: 16px;  /* 增加字體大小 */
            }
            QPushButton:hover {
                background-color: #AED581;
            }
        """)
        self.translate_button.setMinimumHeight(45)  # 增加按鈕高度
        self.translate_button.clicked.connect(self.request_subtitle_translation)
        
        button_layout.addWidget(self.analyze_button)
        button_layout.addWidget(self.translate_button)
        
        # 添加到主佈局
        layout.addWidget(title_frame)
        layout.addWidget(chat_frame)
        layout.addWidget(input_frame)
        layout.addWidget(button_frame)
        
    
    def add_user_message(self, message):
        """添加用戶消息"""
        if not message.strip():
            return
            
        print(f"添加用戶訊息: {message}")  # 調試輸出
        message_widget = MessageWidget(message, is_user=True)
        self.chat_layout.addWidget(message_widget)
        self.scroll_to_bottom()
        
    def add_bot_message(self, message):
        """添加機器人消息"""
        if not message.strip():
            return
            
        print(f"添加機器人訊息: {message}")  # 調試輸出
        message_widget = MessageWidget(message, is_user=False)
        self.chat_layout.addWidget(message_widget)
        self.scroll_to_bottom()
        
    
    def submit_question(self):
        """提交問題"""
        question = self.input_field.text().strip()
        if not question:
            return
            
        # 添加用戶問題到聊天區
        self.add_user_message(question)
        
        # 清空輸入框
        self.input_field.clear()
        
        # 顯示"正在思考"消息 - 小瑤風格版本
        thinking_message = MessageWidget("小瑤正在思考中... (｡･ω･｡)", is_user=False)
        thinking_message.text_label.setStyleSheet("""
            background-color: #FFF8E1;
            border: 1px solid #FFECB3;
            border-radius: 15px;
            padding: 15px;
            color: #FF6F00;
            font-size: 16px;
            font-style: italic;
        """)
        self.chat_layout.addWidget(thinking_message)
        self.scroll_to_bottom()
        
        # 發射問題提交信號，包含當前字幕作為上下文
        self.question_submitted.emit(question, self.current_subtitle)
        
        # 保存thinking_message的引用，以便稍後移除
        self.thinking_message = thinking_message
        
    def remove_thinking_message(self):
        """移除正在思考消息"""
        if hasattr(self, 'thinking_message'):
            self.chat_layout.removeWidget(self.thinking_message)
            self.thinking_message.deleteLater()
            delattr(self, 'thinking_message')
            
    def handle_ai_response(self, response):
        """處理AI回覆"""
        # 先移除"正在思考"消息
        self.remove_thinking_message()
        
        # 添加AI回覆
        self.add_bot_message(response)
        
    def set_current_subtitle(self, subtitle_text):
        """設置當前字幕，用於上下文"""
        self.current_subtitle = subtitle_text
        
    def request_subtitle_analysis(self):
        """請求分析當前字幕"""
        if not self.current_subtitle:
            self.add_bot_message("目前沒有顯示的字幕呢～ (>_<) 請等待視頻播放到有字幕的部分喔！")
            return
            
        # 添加用戶請求到聊天區
        self.add_user_message(f"請分析這個句子: {self.current_subtitle}")
        
        # 顯示"正在分析"消息 - 小瑤風格版本
        thinking_message = MessageWidget("小瑤正在仔細分析這個句子... (・∀・)ノ", is_user=False)
        thinking_message.text_label.setStyleSheet("""
            background-color: #FFF8E1;
            border: 1px solid #FFECB3;
            border-radius: 15px;
            padding: 15px;
            color: #FF6F00;
            font-size: 16px;
            font-style: italic;
        """)
        self.chat_layout.addWidget(thinking_message)
        self.scroll_to_bottom()
        
        # 發射分析請求信號
        self.grammar_analysis_requested.emit(self.current_subtitle)
        
        # 保存thinking_message的引用
        self.thinking_message = thinking_message
        
    def request_subtitle_translation(self):
        """請求翻譯當前字幕"""
        if not self.current_subtitle:
            self.add_bot_message("目前沒有顯示的字幕呢～ (＞﹏＜) 請等待視頻播放到有字幕的部分喔！")
            return
            
        # 添加用戶請求到聊天區
        self.add_user_message(f"請翻譯: {self.current_subtitle}")
        
        # 顯示"正在翻譯"消息 - 小瑤風格版本
        thinking_message = MessageWidget("小瑤正在翻譯中... (￣▽￣)ノ", is_user=False)
        thinking_message.text_label.setStyleSheet("""
            background-color: #FFF8E1;
            border: 1px solid #FFECB3;
            border-radius: 15px;
            padding: 15px;
            color: #FF6F00;
            font-size: 16px;
            font-style: italic;
        """)
        self.chat_layout.addWidget(thinking_message)
        self.scroll_to_bottom()
        
        # 發射翻譯請求信號
        self.translation_requested.emit(self.current_subtitle)
        
        # 保存thinking_message的引用
        self.thinking_message = thinking_message
    
    def handle_error(self, error_message):
        """處理錯誤"""
        # 移除"正在思考"消息
        self.remove_thinking_message()
        
        # 添加錯誤消息 - 小瑤風格版本
        error_widget = MessageWidget(f"哎呀～出了點問題呢 (>ω<)： {error_message}\n\n小瑤會繼續努力的！請稍後再試喔～", is_user=False)
        error_widget.text_label.setStyleSheet("""
            background-color: #FFEBEE;
            border: 1px solid #FFCDD2;
            border-radius: 15px;
            padding: 15px;
            color: #C62828;
            font-size: 16px;
        """)
        self.chat_layout.addWidget(error_widget)
        self.scroll_to_bottom()
    
    def scroll_to_bottom(self):
        """滾動到底部"""
        # 使用定時器確保在UI更新後滾動
        QTimer.singleShot(50, lambda: self.scroll_area.verticalScrollBar().setValue(
            self.scroll_area.verticalScrollBar().maximum()
        ))