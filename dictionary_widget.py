from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTextEdit, QLineEdit, 
    QPushButton, QHBoxLayout, QTabWidget, QScrollArea,
    QMessageBox, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal, pyqtSlot, QObject
from PyQt6.QtGui import QFont
import requests
import json
import threading
import time

class JishoWorker(QObject):
    """Worker object to perform Jisho API requests in a separate thread"""
    
    # Define signals
    result_ready = pyqtSignal(list)  # Signal emitted when results are ready
    no_results = pyqtSignal(str)     # Signal emitted when no results found
    error_occurred = pyqtSignal(str) # Signal emitted when error occurs
    
    def search_word(self, word):
        """Search for a word using Jisho API"""
        try:
            # Use Jisho API to search
            url = f"https://jisho.org/api/v1/search/words?keyword={word}"
            response = requests.get(url)
            response.raise_for_status()  # Check for errors
            
            data = response.json()
            
            # Check if there are results
            if data['meta']['status'] == 200 and len(data['data']) > 0:
                self.result_ready.emit(data['data'])
            else:
                # No results
                self.no_results.emit(word)
                
        except Exception as e:
            print(f"Dictionary lookup error: {e}")
            self.error_occurred.emit(str(e))


class DictionaryWidget(QWidget):
    """日語字典查詢小工具"""
    
    # Define signals
    word_selected = pyqtSignal(str)  # Word selected signal
    
    def __init__(self, parent=None):
        """Initialize dictionary widget"""
        super().__init__(parent)
        
        # Set font
        self.japanese_font = QFont("Yu Gothic UI", 14)
        
        # Create worker object (stays in main thread)
        self.jisho_worker = JishoWorker()
        self.jisho_worker.result_ready.connect(self._display_jisho_result)
        self.jisho_worker.no_results.connect(self._show_no_results)
        self.jisho_worker.error_occurred.connect(self._show_error)
        
        # Initialize UI
        self.init_ui()
        
    def init_ui(self):
        """Initialize user interface"""
        layout = QVBoxLayout(self)
        
        # Top title
        title_frame = QFrame()
        title_frame.setFrameShape(QFrame.Shape.StyledPanel)
        title_frame.setStyleSheet("""
            QFrame {
                background-color: #FFF8E1;
                border: 2px solid #FFECB3;
                border-radius: 10px;
                margin-bottom: 10px;
            }
        """)
        title_layout = QHBoxLayout(title_frame)
        
        title_label = QLabel("✿ 日語詞典查詢 ✿")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #FF6F00;
            padding: 8px;
        """)
        
        title_layout.addWidget(title_label)
        
        # Top search bar - stylized
        search_frame = QFrame()
        search_frame.setFrameShape(QFrame.Shape.StyledPanel)
        search_frame.setStyleSheet("""
            QFrame {
                background-color: #F9FBE7;
                border: 2px solid #DCEDC8;
                border-radius: 10px;
                padding: 5px;
                margin-bottom: 10px;
            }
        """)
        search_layout = QHBoxLayout(search_frame)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("輸入日語單詞...")
        self.search_input.setFont(self.japanese_font)
        self.search_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #AED581;
                border-radius: 5px;
                padding: 8px;
                background-color: white;
                font-size: 14px;
            }
        """)
        self.search_input.returnPressed.connect(self.search_word)
        
        self.search_button = QPushButton("查詢")
        self.search_button.setStyleSheet("""
            QPushButton {
                background-color: #8BC34A;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7CB342;
            }
        """)
        self.search_button.clicked.connect(self.search_word)
        
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_button)
        
        # Results tabs container frame
        results_frame = QFrame()
        results_frame.setFrameShape(QFrame.Shape.StyledPanel)
        results_frame.setStyleSheet("""
            QFrame {
                background-color: #FAFAFA;
                border: 2px solid #E0E0E0;
                border-radius: 10px;
                padding: 5px;
            }
        """)
        results_layout = QVBoxLayout(results_frame)
        
        # Results tabs
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.TabPosition.North)
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 2px solid #DCEDC8;
                border-radius: 8px;
                background-color: white;
            }
            QTabBar::tab {
                background: #F9FBE7;
                border: 1px solid #DCEDC8;
                padding: 8px 15px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background: #8BC34A;
                color: white;
                font-weight: bold;
            }
            QTabBar::tab:!selected {
                margin-top: 2px;
            }
        """)
        
        # Basic info tab
        self.basic_tab = QWidget()
        basic_layout = QVBoxLayout(self.basic_tab)
        basic_layout.setContentsMargins(10, 10, 10, 10)
        
        # Word title frame
        title_container = QFrame()
        title_container.setFrameShape(QFrame.Shape.StyledPanel)
        title_container.setStyleSheet("""
            QFrame {
                background-color: #E8F5E9;
                border: 2px solid #C8E6C9;
                border-radius: 10px;
                margin-bottom: 10px;
            }
        """)
        title_container_layout = QVBoxLayout(title_container)
        
        self.word_title = QLabel("單詞")
        self.word_title.setFont(QFont("Yu Gothic UI", 20, QFont.Weight.Bold))
        self.word_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.word_title.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            color: #2E7D32;
            padding: 10px;
        """)
        
        self.pronunciation_label = QLabel("讀音: ")
        self.pronunciation_label.setFont(QFont("Yu Gothic UI", 14))
        self.pronunciation_label.setStyleSheet("""
            font-size: 14px;
            color: #558B2F;
            padding: 5px;
        """)
        
        title_container_layout.addWidget(self.word_title)
        title_container_layout.addWidget(self.pronunciation_label)
        
        # Meaning text frame
        meaning_container = QFrame()
        meaning_container.setFrameShape(QFrame.Shape.StyledPanel)
        meaning_container.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 2px solid #E0E0E0;
                border-radius: 10px;
            }
        """)
        meaning_container_layout = QVBoxLayout(meaning_container)
        
        # Meaning text with better styling
        self.meaning_text = QTextEdit()
        self.meaning_text.setReadOnly(True)
        self.meaning_text.setFont(QFont("Microsoft JhengHei UI", 14))
        self.meaning_text.setStyleSheet("""
            QTextEdit {
                background-color: transparent;
                border: none;
                color: #424242;
            }
        """)
        
        meaning_container_layout.addWidget(self.meaning_text)
        
        basic_layout.addWidget(title_container)
        basic_layout.addWidget(meaning_container)
        
        # Examples tab
        self.examples_tab = QWidget()
        examples_layout = QVBoxLayout(self.examples_tab)
        examples_layout.setContentsMargins(10, 10, 10, 10)
        
        # Examples title frame
        examples_title_frame = QFrame()
        examples_title_frame.setFrameShape(QFrame.Shape.StyledPanel)
        examples_title_frame.setStyleSheet("""
            QFrame {
                background-color: #F1F8E9;
                border: 2px solid #DCEDC8;
                border-radius: 10px;
                margin-bottom: 10px;
            }
        """)
        examples_title_layout = QVBoxLayout(examples_title_frame)
        
        # Adding decorative elements
        examples_title = QLabel("✧ 例句展示 ✧")
        examples_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        examples_title.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #558B2F;
            padding: 8px;
        """)
        
        examples_title_layout.addWidget(examples_title)
        
        # Examples content frame
        examples_container = QFrame()
        examples_container.setFrameShape(QFrame.Shape.StyledPanel)
        examples_container.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 2px solid #E0E0E0;
                border-radius: 10px;
            }
        """)
        examples_container_layout = QVBoxLayout(examples_container)
        
        self.examples_text = QTextEdit()
        self.examples_text.setReadOnly(True)
        self.examples_text.setFont(QFont("Microsoft JhengHei UI", 14))
        self.examples_text.setStyleSheet("""
            QTextEdit {
                background-color: transparent;
                border: none;
                color: #424242;
            }
        """)
        
        examples_container_layout.addWidget(self.examples_text)
        
        examples_layout.addWidget(examples_title_frame)
        examples_layout.addWidget(examples_container)
        
        # Add tabs
        self.tab_widget.addTab(self.basic_tab, "詞義")
        self.tab_widget.addTab(self.examples_tab, "例句")
        
        results_layout.addWidget(self.tab_widget)
        
        # Add to main layout
        layout.addWidget(title_frame)
        layout.addWidget(search_frame)
        layout.addWidget(results_frame)
    
    def search_word(self):
        """Search for a word"""
        word = self.search_input.text().strip()
        if not word:
            return
        
        # Emit word selected signal
        self.word_selected.emit(word)
        
        # Show searching status
        self.word_title.setText(f"{word} - 查詢中...")
        self.pronunciation_label.setText("讀音: 載入中...")
        self.meaning_text.setHtml("<p>正在查詢，請稍候...</p>")
        self.examples_text.setHtml("<p>載入中...</p>")
        
        # Use a thread-safe way to perform the search
        # Create a new thread for the worker
        search_thread = threading.Thread(
            target=self.jisho_worker.search_word,
            args=(word,),
            daemon=True
        )
        search_thread.start()
    
    @pyqtSlot(list)
    def _display_jisho_result(self, data):
        """Display Jisho API query results"""
        if not data:
            return
            
        # Take the first result
        first_result = data[0]
        
        # Extract word information
        word = first_result.get('japanese', [{}])[0].get('word', '')
        reading = first_result.get('japanese', [{}])[0].get('reading', '')
        
        # Set word title
        self.word_title.setText(word or reading)
        
        # Set pronunciation
        self.pronunciation_label.setText(f"讀音: [{reading}]")
        
        # Prepare meaning HTML - with better styling
        senses = first_result.get('senses', [])
        meaning_html = f"<h2 style='color:#2E7D32;'>單詞：{word or reading}</h2>"
        
        # Part of speech (if available)
        pos_list = []
        for sense in senses:
            if 'parts_of_speech' in sense:
                pos_list.extend(sense['parts_of_speech'])
        
        if pos_list:
            meaning_html += f"<p style='color:#558B2F;'><b>詞性：</b> {', '.join(pos_list)}</p>"
        
        # Add all definitions with better formatting
        meaning_html += "<h3 style='color:#558B2F; background-color:#F1F8E9; padding:5px; border-radius:5px;'>詞義：</h3><ul style='color:#424242;'>"
        for i, sense in enumerate(senses, 1):
            english_def = ', '.join(sense.get('english_definitions', []))
            meaning_html += f"<li><b style='color:#2E7D32;'>{i}.</b> {english_def}</li>"
            
            # Add examples, tags, restrictions, etc.
            if 'tags' in sense and sense['tags']:
                meaning_html += f"<p style='color:#7B8D42; margin-left:20px;'><i>標籤: {', '.join(sense['tags'])}</i></p>"
            
            if 'restrictions' in sense and sense['restrictions']:
                meaning_html += f"<p style='color:#7B8D42; margin-left:20px;'><i>限制: {', '.join(sense['restrictions'])}</i></p>"
                
        meaning_html += "</ul>"
        
        # Set meaning HTML
        self.meaning_text.setHtml(meaning_html)
        
        # Prepare examples HTML - with better styling
        examples_html = "<h2 style='color:#2E7D32; text-align:center;'>例句</h2>"
        
        # Here should be real examples, but Jisho API doesn't provide them
        # You could use Tatoeba API or other resources to get examples
        examples_html += "<div style='background-color:#F1F8E9; padding:10px; border-radius:8px; text-align:center;'>"
        examples_html += "<p style='color:#7B8D42;'>Jisho API沒有提供例句。</p>"
        examples_html += "<p style='color:#558B2F;'>可以考慮使用其他資源如Tatoeba查詢例句～</p>"
        examples_html += "</div>"
        
        # Set examples HTML
        self.examples_text.setHtml(examples_html)
        
        # Switch to meaning tab
        self.tab_widget.setCurrentIndex(0)
    
    @pyqtSlot(str)
    def _show_no_results(self, word):
        """Show no results message - with better styling"""
        self.word_title.setText(word)
        self.pronunciation_label.setText("讀音: 未知")
        
        # Set meaning HTML - with friendly message
        no_results_html = f"""
        <div style='text-align:center; padding:20px;'>
            <h3 style='color:#FF8F00;'>找不到單詞 「{word}」 的結果</h3>
            <p style='color:#757575;'>請確認拼寫是否正確，或嘗試其他相關單詞～</p>
            <div style='font-size:24px; margin:20px;'>( ´・ω・` )</div>
        </div>
        """
        self.meaning_text.setHtml(no_results_html)
        
        # Set examples HTML
        self.examples_text.setHtml("<p style='text-align:center; color:#757575; padding:20px;'>沒有例句。</p>")
    
    @pyqtSlot(str)    
    def _show_error(self, error_msg):
        """Show error message - with better styling"""
        self.word_title.setText("查詢錯誤")
        self.pronunciation_label.setText("讀音: --")
        
        # Set meaning HTML - with friendly error
        error_html = f"""
        <div style='text-align:center; padding:20px;'>
            <h3 style='color:#F44336;'>查詢時出現錯誤</h3>
            <p style='color:#757575;'>{error_msg}</p>
            <p style='color:#757575;'>請稍後再試～</p>
            <div style='font-size:24px; margin:20px;'>( >﹏<。)</div>
        </div>
        """
        self.meaning_text.setHtml(error_html)
        
        # Set examples HTML
        self.examples_text.setHtml("<p style='text-align:center; color:#757575; padding:20px;'>無法獲取例句。</p>")
    
    @pyqtSlot(dict)
    def display_word_info(self, word_info):
        """Display word analysis results"""
        if not word_info:
            return
        
        # Set word title
        self.word_title.setText(word_info.get('surface', ''))
        
        # Set pronunciation
        pronunciation = word_info.get('pronunciation', '')
        self.pronunciation_label.setText(f"讀音: [{pronunciation}]")
        
        # Set meaning
        lemma = word_info.get('lemma', '')
        pos = word_info.get('pos', '')
        
        meaning_html = f"""
        <h2 style='color:#2E7D32;'>單詞分析</h2>
        <div style='background-color:#F1F8E9; padding:10px; border-radius:8px;'>
            <p><b style='color:#2E7D32;'>單詞：</b> {word_info.get('surface', '')}</p>
            <p><b style='color:#2E7D32;'>詞性：</b> {pos}</p>
            <p><b style='color:#2E7D32;'>詞根形式：</b> {lemma}</p>
            <p><b style='color:#2E7D32;'>讀音：</b> {pronunciation}</p>
        </div>
        """
        self.meaning_text.setHtml(meaning_html)
        
        # Set focus to basic tab
        self.tab_widget.setCurrentIndex(0)