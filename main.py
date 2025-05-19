import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFontDatabase, QFont, QPalette, QColor, QIcon
from PyQt6.QtCore import Qt
from app_UI import JapaneseAssistantUI
from paths import get_font_path

def setup_application_style():
    """設置應用程序樣式"""
    app = QApplication.instance()
    app.setStyle('Fusion')  # 使用Fusion風格獲得更現代的外觀
    
    # 設置應用程序級別的調色板 - 更柔和的色調
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(250, 250, 250))  # 淺灰白背景
    palette.setColor(QPalette.ColorRole.WindowText, QColor(80, 80, 80))  # 深灰文字
    palette.setColor(QPalette.ColorRole.Base, QColor(255, 255, 255))    # 白色背景
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(245, 245, 245))
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor(80, 80, 80))
    palette.setColor(QPalette.ColorRole.Text, QColor(80, 80, 80))
    palette.setColor(QPalette.ColorRole.Button, QColor(250, 250, 250))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(80, 80, 80))
    
    # 更新強調色為暖色調
    palette.setColor(QPalette.ColorRole.Link, QColor(255, 152, 0))      # 橙色鏈接
    palette.setColor(QPalette.ColorRole.Highlight, QColor(255, 193, 7)) # 琥珀色強調
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
    
    app.setPalette(palette)
    
    # 添加全局樣式表
    app.setStyleSheet("""
    QMainWindow {
        background-color: #FAFAFA;
    }
    
    QWidget {
        font-family: 'Microsoft JhengHei UI', 'PingFang TC', sans-serif;
    }
    
    QToolTip {
        border: 1px solid #FFECB3;
        background-color: #FFF8E1;
        color: #FF6F00;
        padding: 5px;
        border-radius: 3px;
    }
    
    QTabWidget::pane {
        border: 2px solid #FFECB3;
        border-radius: 6px;
        top: -2px;
    }
    
    QTabBar::tab {
        background: #FFF8E1;
        border: 1px solid #FFECB3;
        padding: 6px 12px;
        margin-right: 2px;
        border-top-left-radius: 4px;
        border-top-right-radius: 4px;
    }
    
    QTabBar::tab:selected {
        background: #FFD54F;
        border-bottom: none;
        color: #FF6F00;
        font-weight: bold;
    }
    
    QTabBar::tab:!selected {
        margin-top: 2px;
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
    
    QPushButton {
        background-color: #FFECB3;
        border: 1px solid #FFD54F;
        border-radius: 5px;
        padding: 5px 10px;
        color: #FF6F00;
        font-weight: bold;
    }
    
    QPushButton:hover {
        background-color: #FFD54F;
    }
    
    QPushButton:pressed {
        background-color: #FFC107;
    }
    
    QFrame {
        border-radius: 6px;
    }
    
    QLineEdit {
        border: 1px solid #E0E0E0;
        border-radius: 4px;
        padding: 5px;
        background-color: white;
    }
    
    QStatusBar {
        background-color: #FFF8E1;
        color: #FF6F00;
        border-top: 1px solid #FFECB3;
    }
    """)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    # 設置應用程序樣式
    setup_application_style()
    
    # 創建並顯示主窗口
    window = JapaneseAssistantUI()
    window.show()
    
    # 添加歡迎提示
    window.status_bar.showMessage("小瑤已就緒! (ﾉ◕ヮ◕)ﾉ*:･ﾟ✧ 歡迎使用日語學習助手～")
    
    sys.exit(app.exec())