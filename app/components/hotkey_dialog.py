# coding: utf-8
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QKeyEvent
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from qfluentwidgets import MessageBoxBase, SubtitleLabel, LineEdit, InfoBar, InfoBarPosition, PushButton, PrimaryPushButton


class HotkeyLineEdit(LineEdit):
    """快捷键输入框"""
    
    hotkeyChanged = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)  # 设置为只读，只能通过按键输入
        self.setPlaceholderText("点击这里然后按下快捷键组合...")
        self.currentKeys = []
        self.recording = False
        
    def keyPressEvent(self, event: QKeyEvent):
        if not self.recording:
            return
            
        key = event.key()
        modifiers = event.modifiers()
        
        # 如果按下的是修饰键，暂存起来
        if key in [Qt.Key_Control, Qt.Key_Alt, Qt.Key_Shift, Qt.Key_Meta]:
            return
        
        # 构建快捷键字符串
        keys = []
        if modifiers & Qt.ControlModifier:
            keys.append("Ctrl")
        if modifiers & Qt.AltModifier:
            keys.append("Alt")
        if modifiers & Qt.ShiftModifier:
            keys.append("Shift")
        if modifiers & Qt.MetaModifier:
            keys.append("Win")
            
        # 获取按键名称
        key_name = self.getKeyName(key)
        if key_name:
            keys.append(key_name)
            
        # 生成快捷键字符串
        hotkey_str = "+".join(keys)
        self.setText(hotkey_str)
        self.recording = False
        self.hotkeyChanged.emit(hotkey_str)
        
    def getKeyName(self, key):
        """获取按键名称"""
        key_map = {
            Qt.Key_A: 'A', Qt.Key_B: 'B', Qt.Key_C: 'C', Qt.Key_D: 'D', Qt.Key_E: 'E',
            Qt.Key_F: 'F', Qt.Key_G: 'G', Qt.Key_H: 'H', Qt.Key_I: 'I', Qt.Key_J: 'J',
            Qt.Key_K: 'K', Qt.Key_L: 'L', Qt.Key_M: 'M', Qt.Key_N: 'N', Qt.Key_O: 'O',
            Qt.Key_P: 'P', Qt.Key_Q: 'Q', Qt.Key_R: 'R', Qt.Key_S: 'S', Qt.Key_T: 'T',
            Qt.Key_U: 'U', Qt.Key_V: 'V', Qt.Key_W: 'W', Qt.Key_X: 'X', Qt.Key_Y: 'Y',
            Qt.Key_Z: 'Z',
            Qt.Key_0: '0', Qt.Key_1: '1', Qt.Key_2: '2', Qt.Key_3: '3', Qt.Key_4: '4',
            Qt.Key_5: '5', Qt.Key_6: '6', Qt.Key_7: '7', Qt.Key_8: '8', Qt.Key_9: '9',
            Qt.Key_F1: 'F1', Qt.Key_F2: 'F2', Qt.Key_F3: 'F3', Qt.Key_F4: 'F4',
            Qt.Key_F5: 'F5', Qt.Key_F6: 'F6', Qt.Key_F7: 'F7', Qt.Key_F8: 'F8',
            Qt.Key_F9: 'F9', Qt.Key_F10: 'F10', Qt.Key_F11: 'F11', Qt.Key_F12: 'F12',
            Qt.Key_Space: 'Space', Qt.Key_Enter: 'Enter', Qt.Key_Return: 'Return',
            Qt.Key_Escape: 'Escape', Qt.Key_Tab: 'Tab', Qt.Key_Backspace: 'Backspace',
            Qt.Key_Delete: 'Delete', Qt.Key_Insert: 'Insert', Qt.Key_Home: 'Home',
            Qt.Key_End: 'End', Qt.Key_PageUp: 'PageUp', Qt.Key_PageDown: 'PageDown',
            Qt.Key_Up: 'Up', Qt.Key_Down: 'Down', Qt.Key_Left: 'Left', Qt.Key_Right: 'Right',
        }
        return key_map.get(key, None)
        
    def mousePressEvent(self, event):
        """点击时开始录制快捷键"""
        super().mousePressEvent(event)
        self.recording = True
        self.setText("")
        self.setPlaceholderText("正在录制快捷键，请按下组合键...")
        
    def focusOutEvent(self, event):
        """失去焦点时停止录制"""
        super().focusOutEvent(event)
        self.recording = False
        if not self.text():
            self.setPlaceholderText("点击这里然后按下快捷键组合...")


class HotkeySettingDialog(MessageBoxBase):
    """快捷键设置对话框"""
    
    def __init__(self, current_hotkey="", parent=None):
        super().__init__(parent)
        self.titleLabel = SubtitleLabel("设置截图快捷键", self)
        
        # 创建快捷键输入框
        self.hotkeyEdit = HotkeyLineEdit(self)
        if current_hotkey:
            self.hotkeyEdit.setText(current_hotkey)
            
        # 说明标签
        self.descLabel = QLabel("点击输入框，然后按下您想要设置的快捷键组合", self)
        self.descLabel.setStyleSheet("color: #666; font-size: 12px; margin-top: 5px;")
        
        # 预设快捷键按钮
        self.presetLayout = QHBoxLayout()
        self.preset1Btn = QPushButton("Ctrl+Alt+S")
        self.preset2Btn = QPushButton("Ctrl+Shift+S")
        self.preset3Btn = QPushButton("F9")
        
        self.preset1Btn.clicked.connect(lambda: self.setPresetHotkey("Ctrl+Alt+S"))
        self.preset2Btn.clicked.connect(lambda: self.setPresetHotkey("Ctrl+Shift+S"))
        self.preset3Btn.clicked.connect(lambda: self.setPresetHotkey("F9"))
        
        self.presetLayout.addWidget(QLabel("常用快捷键:"))
        self.presetLayout.addWidget(self.preset1Btn)
        self.presetLayout.addWidget(self.preset2Btn)
        self.presetLayout.addWidget(self.preset3Btn)
        self.presetLayout.addStretch()
        
        # 添加控件到布局
        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.addWidget(self.hotkeyEdit)
        self.viewLayout.addWidget(self.descLabel)
        self.viewLayout.addLayout(self.presetLayout)
        
        self.widget.setMinimumWidth(400)
        
    def setPresetHotkey(self, hotkey):
        """设置预设快捷键"""
        self.hotkeyEdit.setText(hotkey)
        
    def validate(self):
        """验证快捷键"""
        hotkey = self.hotkeyEdit.text().strip()
        if not hotkey:
            InfoBar.warning(
                title='提示',
                content='请设置快捷键',
                duration=2000,
                position=InfoBarPosition.TOP,
                parent=self
            )
            return False
        return True
        
    def getHotkey(self):
        """获取设置的快捷键"""
        return self.hotkeyEdit.text().strip()