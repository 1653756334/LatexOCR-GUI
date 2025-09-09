# coding: utf-8
from PyQt5.QtCore import QObject, pyqtSignal


class SignalBus(QObject):
    """ Signal bus """

    switchToSampleCard = pyqtSignal(str, int)
    micaEnableChanged = pyqtSignal(bool)
    supportSignal = pyqtSignal()
    screenshotHotkeyChanged = pyqtSignal(str)  # 快捷键更新信号
    screenshotTaken = pyqtSignal(str)  # 截图完成信号，参数为图片路径


signalBus = SignalBus()