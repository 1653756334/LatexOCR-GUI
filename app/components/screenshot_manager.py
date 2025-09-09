# coding: utf-8
import sys
import os
import tempfile
from datetime import datetime
from PyQt5.QtCore import Qt, QRect, pyqtSignal, QPoint, QTimer
from PyQt5.QtGui import QPixmap, QPainter, QPen, QColor, QCursor, QKeySequence
from PyQt5.QtWidgets import QWidget, QApplication, QDesktopWidget, QRubberBand, QLabel


class ScreenshotWidget(QWidget):
    """截图选择窗口"""
    
    screenshotSelected = pyqtSignal(QPixmap)
    
    def __init__(self):
        super().__init__()
        self.initUI()
        self.rubberBand = None
        self.origin = QPoint()
        
    def initUI(self):
        try:
            # 设置窗口属性
            self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
            self.setAttribute(Qt.WA_TranslucentBackground)
            
            # 获取屏幕信息
            app = QApplication.instance()
            desktop = app.desktop()
            screen_geometry = desktop.screenGeometry()
            
            # 设置窗口覆盖整个屏幕
            self.setGeometry(screen_geometry)
            
            # 获取屏幕截图
            screen = app.primaryScreen()
            if screen:
                # 获取完整屏幕截图
                self.screen = screen.grabWindow(0)
                
                # 如果截图大小与屏幕几何不匹配，进行缩放
                if self.screen.size() != screen_geometry.size():
                    self.screen = self.screen.scaled(
                        screen_geometry.size(),
                        Qt.KeepAspectRatio,
                        Qt.SmoothTransformation
                    )
            else:
                raise Exception("无法获取屏幕")
            
            # 设置光标
            self.setCursor(QCursor(Qt.CrossCursor))
            
            # 创建说明标签
            self.tipLabel = QLabel('拖拽选择截图区域，按ESC退出', self)
            self.tipLabel.setStyleSheet("""
                QLabel {
                    background-color: rgba(0, 0, 0, 180);
                    color: white;
                    padding: 10px;
                    border-radius: 5px;
                    font-size: 14px;
                }
            """)
            self.tipLabel.adjustSize()
            self.tipLabel.move(20, 20)
            
        except Exception as e:
            print(f"初始化截图界面UI出错: {e}")
            raise e
        
    def paintEvent(self, event):
        painter = QPainter(self)
        
        # 绘制截图作为背景
        if hasattr(self, 'screen') and not self.screen.isNull():
            # 将截图绘制到整个窗口
            painter.drawPixmap(self.rect(), self.screen)
        
        # 绘制半透明遮罩
        painter.fillRect(self.rect(), QColor(0, 0, 0, 100))
        
        # 如果有选择区域，绘制原始图像的该部分（不带遮罩）
        if self.rubberBand and self.rubberBand.isVisible():
            rect = self.rubberBand.geometry()
            if hasattr(self, 'screen') and not self.screen.isNull():
                # 绘制选择区域的原始截图（无遮罩）
                painter.drawPixmap(rect, self.screen, rect)
                
                # 绘制选择框边框
                pen = QPen(QColor(0, 150, 255), 2)  # 蓝色边框
                painter.setPen(pen)
                painter.drawRect(rect)
            
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.origin = event.pos()
            if not self.rubberBand:
                self.rubberBand = QRubberBand(QRubberBand.Rectangle, self)
            self.rubberBand.setGeometry(QRect(self.origin, event.pos()).normalized())
            self.rubberBand.show()
            
    def mouseMoveEvent(self, event):
        if self.rubberBand:
            self.rubberBand.setGeometry(QRect(self.origin, event.pos()).normalized())
            self.update()
            
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.rubberBand:
            # 获取选择的区域
            rect = self.rubberBand.geometry()
            if rect.width() > 10 and rect.height() > 10:  # 确保选择区域足够大
                # 截取选择的区域
                screenshot = self.screen.copy(rect)
                self.screenshotSelected.emit(screenshot)
                self.close()
            
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()
        super().keyPressEvent(event)


class ScreenshotManager:
    """截图管理器"""
    
    def __init__(self, parent=None):
        self.parent = parent
        self.screenshot_widget = None
        
    def take_screenshot(self):
        """开始截图"""
        try:
            # 隐藏主窗口（如果存在）
            if self.parent:
                self.parent.hide()
                
            # 延迟一下让窗口完全隐藏
            QTimer.singleShot(200, self._show_screenshot_widget)
            
        except Exception as e:
            print(f"截图流程出错: {e}")
            if self.parent:
                self.parent.show()
        
    def _show_screenshot_widget(self):
        """显示截图选择窗口"""
        try:
            # 如果之前的截图窗口还存在，先关闭它
            if self.screenshot_widget:
                self.screenshot_widget.close()
                self.screenshot_widget = None
                
            self.screenshot_widget = ScreenshotWidget()
            self.screenshot_widget.screenshotSelected.connect(self._on_screenshot_selected)
            self.screenshot_widget.show()
            
        except Exception as e:
            print(f"显示截图窗口出错: {e}")
            if self.parent:
                self.parent.show()
        
    def _on_screenshot_selected(self, pixmap):
        """处理截图选择完成"""
        try:
            # 先关闭截图窗口
            if self.screenshot_widget:
                self.screenshot_widget.close()
                self.screenshot_widget = None
            
            # 保存截图到临时文件
            temp_dir = tempfile.gettempdir()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            temp_file = os.path.join(temp_dir, f"screenshot_{timestamp}.png")
            
            if pixmap.save(temp_file, "PNG"):
                # 先显示主窗口，再发送截图完成信号
                self._show_main_window()
                
                # 延迟一下再发送信号，确保主窗口已经显示
                QTimer.singleShot(100, lambda: self._emit_screenshot_signal(temp_file))
            else:
                self._show_main_window()
                
        except Exception as e:
            print(f"处理截图选择出错: {e}")
            if self.parent:
                self.parent.show()
                
    def _emit_screenshot_signal(self, temp_file):
        """发送截图完成信号"""
        try:
            from ..common.signal_bus import signalBus
            signalBus.screenshotTaken.emit(temp_file)
        except Exception as e:
            print(f"发送截图信号出错: {e}")
            
    def _show_main_window(self):
        """显示主窗口"""
        try:
            if self.parent:
                self.parent.show()
                self.parent.raise_()
                self.parent.activateWindow()
                # 确保窗口在最前面
                self.parent.setWindowState(self.parent.windowState() & ~Qt.WindowMinimized | Qt.WindowActive)
        except Exception as e:
            print(f"显示主窗口出错: {e}")