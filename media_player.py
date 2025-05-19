import os
import platform
try:
    import vlc
except ImportError:
    print("警告: 無法導入vlc模組，請安裝python-vlc套件")
    print("安裝命令: pip install python-vlc")
    vlc = None
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QSlider, QStyle, QFrame
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QSize
from PyQt6.QtGui import QIcon

class MediaPlayer(QWidget):
    """媒體播放器組件"""
    
    # 定義信號
    position_changed = pyqtSignal(int)  # 播放位置變化（毫秒）
    media_loaded = pyqtSignal(bool)     # 媒體加載狀態
    play_state_changed = pyqtSignal(bool)  # 播放狀態變化（是否正在播放）
    
    def __init__(self, parent=None):
        """初始化媒體播放器"""
        super().__init__(parent)
        
        # VLC實例
        self.instance = vlc.Instance("--no-xlib")
        self.player = self.instance.media_player_new()
        
        # 播放狀態
        self.is_playing = False
        self.is_media_loaded = False
        
        # 初始化UI
        self.init_ui()
        
        # 設置更新計時器
        self.update_timer = QTimer(self)
        self.update_timer.setInterval(500)  # 每500毫秒更新一次
        self.update_timer.timeout.connect(self.update_position)
        self.update_timer.start()

    def init_ui(self):
        """初始化用戶界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 影片區域
        self.video_frame = QFrame()
        self.video_frame.setStyleSheet("background-color: black;")
        self.video_frame.setMinimumHeight(300)
        
        # 控制按鈕區域
        controls_layout = QHBoxLayout()
        controls_layout.setContentsMargins(5, 5, 5, 5)
        
        # 播放/暫停按鈕
        self.play_button = QPushButton()
        self.play_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
        self.play_button.setIconSize(QSize(24, 24))
        self.play_button.clicked.connect(self.toggle_play)
        
        # 停止按鈕
        self.stop_button = QPushButton()
        self.stop_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaStop))
        self.stop_button.setIconSize(QSize(24, 24))
        self.stop_button.clicked.connect(self.stop)
        
        # 快退按鈕
        self.rewind_button = QPushButton()
        self.rewind_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaSeekBackward))
        self.rewind_button.setIconSize(QSize(24, 24))
        self.rewind_button.clicked.connect(lambda: self.seek_relative(-10000))  # 後退10秒
        
        # 快進按鈕
        self.forward_button = QPushButton()
        self.forward_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaSeekForward))
        self.forward_button.setIconSize(QSize(24, 24))
        self.forward_button.clicked.connect(lambda: self.seek_relative(10000))  # 前進10秒
        
        # 時間標籤
        self.time_label = QLabel("00:00 / 00:00")
        
        # 進度條
        self.position_slider = QSlider(Qt.Orientation.Horizontal)
        self.position_slider.setRange(0, 1000)
        self.position_slider.sliderMoved.connect(self.set_position)
        self.position_slider.sliderPressed.connect(self.pause_update_timer)
        self.position_slider.sliderReleased.connect(self.resume_update_timer)
        
        # 音量標籤
        volume_label = QLabel("音量:")
        
        # 音量滑塊
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setMaximumWidth(100)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(50)
        self.volume_slider.valueChanged.connect(self.set_volume)
        
        # 添加控制元素到佈局
        controls_layout.addWidget(self.play_button)
        controls_layout.addWidget(self.stop_button)
        controls_layout.addWidget(self.rewind_button)
        controls_layout.addWidget(self.forward_button)
        controls_layout.addWidget(self.time_label)
        controls_layout.addWidget(self.position_slider)
        controls_layout.addWidget(volume_label)
        controls_layout.addWidget(self.volume_slider)
        
        # 將組件添加到主佈局
        layout.addWidget(self.video_frame, 1)
        layout.addLayout(controls_layout)
    
    def load_media(self, media_path):
        """加載媒體文件"""
        if not media_path or not os.path.exists(media_path):
            self.is_media_loaded = False
            self.media_loaded.emit(False)
            return False
        
        # 先停止任何正在播放的媒體
        self.player.stop()
        
        # 釋放當前媒體資源
        if self.player.get_media():
            self.player.get_media().release()
        
        # 創建新媒體
        media = self.instance.media_new(media_path)
        self.player.set_media(media)
        
        # 設置視頻輸出窗口
        if platform.system() == "Windows":
            self.player.set_hwnd(int(self.video_frame.winId()))
        elif platform.system() == "Darwin":  # macOS
            self.player.set_nsobject(int(self.video_frame.winId()))
        else:  # Linux
            self.player.set_xwindow(int(self.video_frame.winId()))
        
        # 設置音量（0-100）
        self.player.audio_set_volume(self.volume_slider.value())
        
        # 重置位置滑塊
        self.position_slider.setValue(0)
        
        # 更新時間標籤
        self.time_label.setText("00:00 / 00:00")
        
        # 媒體加載成功
        self.is_media_loaded = True
        self.media_loaded.emit(True)
        
        return True
        
    def play(self):
        """播放媒體"""
        if not self.is_media_loaded:
            return
            
        self.player.play()
        self.is_playing = True
        self.play_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPause))
        self.play_state_changed.emit(True)
        
    def pause(self):
        """暫停播放"""
        if not self.is_playing:
            return
            
        self.player.pause()
        self.is_playing = False
        self.play_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
        self.play_state_changed.emit(False)
        
    def stop(self):
        """停止播放"""
        self.player.stop()
        self.is_playing = False
        self.play_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
        self.play_state_changed.emit(False)
        
    def toggle_play(self):
        """切換播放/暫停狀態"""
        if not self.is_media_loaded:
            return
            
        if self.is_playing:
            self.pause()
        else:
            self.play()
    
    def set_volume(self, volume):
        """設置音量"""
        self.player.audio_set_volume(volume)
    
    def get_position_ms(self):
        """獲取當前播放位置（毫秒）"""
        if not self.is_media_loaded:
            return 0
        return self.player.get_time()
    
    def get_duration_ms(self):
        """獲取媒體總時長（毫秒）"""
        if not self.is_media_loaded:
            return 0
        return self.player.get_length()
    
    def set_position(self, position):
        """設置播放位置（滑塊位置0-1000）"""
        if not self.is_media_loaded:
            return
            
        # 轉換滑塊位置為百分比
        pos = position / 1000.0
        
        # 設置播放位置
        self.player.set_position(pos)
    
    def seek_relative(self, offset_ms):
        """相對尋找位置（毫秒）"""
        if not self.is_media_loaded:
            return
            
        current_time = self.player.get_time()
        new_time = max(0, current_time + offset_ms)
        max_time = self.player.get_length()
        
        if max_time > 0:
            new_time = min(new_time, max_time)
            
        self.player.set_time(new_time)
    
    def update_position(self):
        """更新位置信息"""
        if not self.is_media_loaded:
            return
            
        # 檢查是否正在拖動滑塊
        if self.position_slider.isSliderDown():
            return
            
        # 檢查是否有有效的時間長度
        length = self.player.get_length()
        if length <= 0:
            return
            
        # 獲取當前時間
        time = self.player.get_time()
        
        # 更新滑塊位置
        self.position_slider.setValue(int(1000 * time / length))
        
        # 更新時間標籤
        self.time_label.setText(f"{self.format_time(time)} / {self.format_time(length)}")
        
        # 發射位置變化信號
        self.position_changed.emit(time)
    
    def format_time(self, milliseconds):
        """格式化時間（毫秒轉為分:秒）"""
        seconds = int(milliseconds / 1000)
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes:02d}:{seconds:02d}"
    
    def pause_update_timer(self):
        """暫停更新計時器（當滑塊被按下時）"""
        self.update_timer.stop()
    
    def resume_update_timer(self):
        """恢復更新計時器（當滑塊被釋放時）"""
        self.update_timer.start()
        
    def cleanup(self):
        """清理資源"""
        self.update_timer.stop()
        self.player.stop()
        self.player.release()