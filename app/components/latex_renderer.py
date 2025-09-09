from PyQt5.QtWidgets import QWidget, QVBoxLayout, QSizePolicy
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import Qt, QUrl, QTimer
import os

class LaTeXRenderer(QWebEngineView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(60)
        self.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.MinimumExpanding
        )
        
        # 创建定时器用于检查内容高度
        self.heightCheckTimer = QTimer(self)
        self.heightCheckTimer.setInterval(100)  # 100ms 检查一次
        self.heightCheckTimer.timeout.connect(self.checkContentHeight)
        
        self.template = """
            <!DOCTYPE html>
            <html>
            <head>
                <script>
                    window.MathJax = {
                        tex: {
                            inlineMath: [['$', '$'], ['\\\\(', '\\\\)']],
                            displayMath: [['$$', '$$'], ['\\\\[', '\\\\]']]
                        },
                        svg: {
                            fontCache: 'local',
                            scale: 1.2,
                            minScale: 0.5,
                            mtextInheritFont: false,
                            merrorInheritFont: true,
                            mathmlSpacing: false,
                            skipAttributes: {},
                            exFactor: 0.5,
                            displayAlign: 'center',
                            displayIndent: '0'
                        },
                        startup: {
                            typeset: false,
                            ready: () => {
                                MathJax.startup.defaultReady();
                                MathJax.startup.promise.then(() => {
                                    // 渲染完成后调整高度
                                    setTimeout(() => {
                                        var height = document.body.scrollHeight;
                                        document.body.style.minHeight = height + 'px';
                                    }, 100);
                                });
                            }
                        }
                    };
                </script>
                <script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-svg.js"></script>
                <style>
                    body {
                        margin: 0;
                        padding: 10px;
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        min-height: 60px;
                        background: white;
                        font-family: 'Times New Roman', serif;
                    }
                    .math {
                        font-size: 18px;
                        line-height: 1.2;
                        text-align: center;
                        width: 100%;
                        opacity: 0;
                        transition: opacity 0.3s ease-in-out;
                    }
                    .math.loaded {
                        opacity: 1;
                    }
                    mjx-container {
                        margin: 0 !important;
                        padding: 0 !important;
                    }
                </style>
            </head>
            <body>
                <div class="math" id="mathContainer">$$__LATEX__$$</div>
                <script>
                    // 立即开始渲染
                    MathJax.typesetPromise().then(() => {
                        document.getElementById('mathContainer').classList.add('loaded');
                    }).catch((err) => {
                        console.log('MathJax rendering error:', err);
                        document.getElementById('mathContainer').classList.add('loaded');
                    });
                </script>
            </body>
            </html>
        """

    def render_latex(self, latex_str):
        """渲染LaTeX公式"""
        if not latex_str:
            self.setHtml("")
            self.heightCheckTimer.stop()
            return
            
        # HTML模板
        html = self.template.replace('__LATEX__', latex_str)
        self.setHtml(html)
        
        # 启动高度检查定时器
        self.heightCheckTimer.start()

    def checkContentHeight(self):
        """检查内容高度"""
        # 执行 JavaScript 来获取内容高度
        self.page().runJavaScript("""
            document.body.scrollHeight;
        """, self.updateHeight)

    def updateHeight(self, height):
        """更新高度"""
        if height and height > self.minimumHeight():
            # 添加一些边距
            self.setFixedHeight(height + 32)
            # 停止定时器
            self.heightCheckTimer.stop()

    def get_image(self):
        """获取渲染后的图像，裁剪掉多余的空白"""
        full = self.grab()
        # 获取非空白区域
        image = full.toImage()
        rect = image.rect()
        for x in range(rect.left(), rect.right()):
            for y in range(rect.top(), rect.bottom()):
                if image.pixelColor(x, y).alpha() > 0:
                    rect.setLeft(max(0, x - 5))  # 左边留5像素边距
                    break
            else:
                continue
            break
        
        for x in range(rect.right(), rect.left(), -1):
            for y in range(rect.top(), rect.bottom()):
                if image.pixelColor(x, y).alpha() > 0:
                    rect.setRight(min(image.width(), x + 5))  # 右边留5像素边距
                    break
            else:
                continue
            break
        
        return full.copy(rect) 