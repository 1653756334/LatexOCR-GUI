# coding: utf-8
import sys
from PyQt5.QtCore import QObject, pyqtSignal, QTimer
from PyQt5.QtWidgets import QApplication


class GlobalHotkeyManager(QObject):
    """全局快捷键管理器"""
    
    hotkeyPressed = pyqtSignal(str)  # 快捷键按下信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.registered_hotkeys = {}
        self.pynput_available = False
        
        # 尝试导入pynput
        try:
            import pynput
            from pynput import keyboard
            self.pynput_available = True
            self.keyboard = keyboard
            self.listener = None
            self.current_keys = set()
            self.hotkey_combinations = {}
            
            # 连接信号到主线程处理
            self.hotkeyPressed.connect(self._handle_hotkey_in_main_thread)
        except ImportError:
            print("警告: pynput未安装，全局快捷键功能不可用")
            print("请运行: pip install pynput")
            
    def _handle_hotkey_in_main_thread(self, hotkey_str):
        """在主线程中处理快捷键"""
        callback = self.registered_hotkeys.get(hotkey_str)
        if callback:
            callback()
            
    def register_hotkey(self, hotkey_str, callback=None):
        """注册全局快捷键"""
        if not self.pynput_available:
            return False
            
        try:
            # 解析快捷键字符串
            keys = self._parse_hotkey_string(hotkey_str)
            if keys:
                self.hotkey_combinations[frozenset(keys)] = hotkey_str
                self.registered_hotkeys[hotkey_str] = callback
                
                # 启动键盘监听器
                if not self.listener or not self.listener.running:
                    self._start_listener()
                    
                print(f"成功注册快捷键: {hotkey_str}")
                return True
        except Exception as e:
            print(f"注册快捷键失败: {e}")
            
        return False
        
    def unregister_hotkey(self, hotkey_str):
        """注销全局快捷键"""
        if hotkey_str in self.registered_hotkeys:
            del self.registered_hotkeys[hotkey_str]
            
            # 从组合键中移除
            keys = self._parse_hotkey_string(hotkey_str)
            if keys:
                key_set = frozenset(keys)
                if key_set in self.hotkey_combinations:
                    del self.hotkey_combinations[key_set]
                    
    def _parse_hotkey_string(self, hotkey_str):
        """解析快捷键字符串"""
        if not self.pynput_available:
            return None
            
        keys = []
        parts = hotkey_str.split('+')
        
        for part in parts:
            part = part.strip().lower()
            
            if part == 'ctrl':
                keys.append(self.keyboard.Key.ctrl_l)
            elif part == 'alt':
                keys.append(self.keyboard.Key.alt_l)
            elif part == 'shift':
                keys.append(self.keyboard.Key.shift_l)
            elif part == 'win':
                keys.append(self.keyboard.Key.cmd)
            elif len(part) == 1 and part.isalpha():
                keys.append(self.keyboard.KeyCode.from_char(part))
            elif part.startswith('f') and len(part) <= 3 and part[1:].isdigit():
                # F1-F12 功能键
                f_num = int(part[1:])
                if 1 <= f_num <= 12:
                    keys.append(getattr(self.keyboard.Key, f'f{f_num}'))
            elif part.isdigit():
                keys.append(self.keyboard.KeyCode.from_char(part))
            elif part == 'space':
                keys.append(self.keyboard.Key.space)
            elif part == 'enter':
                keys.append(self.keyboard.Key.enter)
            elif part == 'escape':
                keys.append(self.keyboard.Key.esc)
            elif part == 'tab':
                keys.append(self.keyboard.Key.tab)
            elif part == 'backspace':
                keys.append(self.keyboard.Key.backspace)
                
        return keys
        
    def _start_listener(self):
        """启动键盘监听器"""
        if not self.pynput_available:
            return
            
        try:
            if self.listener:
                self.listener.stop()
                
            self.listener = self.keyboard.Listener(
                on_press=self._on_key_press,
                on_release=self._on_key_release
            )
            self.listener.start()
        except Exception as e:
            print(f"启动键盘监听器失败: {e}")
            
    def _on_key_press(self, key):
        """按键按下事件"""
        # 标准化按键格式
        normalized_key = self._normalize_key(key)
        self.current_keys.add(normalized_key)
        self._check_hotkey_combination()
        
    def _on_key_release(self, key):
        """按键释放事件"""
        normalized_key = self._normalize_key(key)
        if normalized_key in self.current_keys:
            self.current_keys.remove(normalized_key)
            
    def _normalize_key(self, key):
        """标准化按键格式"""
        # 如果是字符按键，统一转换为小写字符
        if hasattr(key, 'char') and key.char:
            return self.keyboard.KeyCode.from_char(key.char.lower())
        elif hasattr(key, 'vk') and 65 <= key.vk <= 90:  # A-Z的虚拟键码
            return self.keyboard.KeyCode.from_char(chr(key.vk + 32))  # 转换为小写
        elif hasattr(key, 'vk') and 48 <= key.vk <= 57:  # 0-9的虚拟键码
            return self.keyboard.KeyCode.from_char(chr(key.vk))
        else:
            return key
            
    def _check_hotkey_combination(self):
        """检查是否匹配已注册的快捷键组合"""
        current_set = frozenset(self.current_keys)
        
        for key_set, hotkey_str in self.hotkey_combinations.items():
            # 检查是否完全匹配
            if key_set == current_set:
                # 匹配到快捷键组合，通过信号发送到主线程
                self.hotkeyPressed.emit(hotkey_str)
                break
                
    def stop(self):
        """停止快捷键监听"""
        if self.pynput_available and self.listener:
            self.listener.stop()


# 全局单例
global_hotkey_manager = GlobalHotkeyManager()