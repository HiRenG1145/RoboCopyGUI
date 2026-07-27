"""应用入口 — 创建 QApplication、配置 Fluent 主题、启动主窗口。"""

import sys

from PySide6.QtWidgets import QApplication
from qfluentwidgets import setTheme, Theme


def main() -> None:
    app = QApplication(sys.argv)

    # Fluent Design 主题（自动跟随系统明暗模式）
    setTheme(Theme.AUTO)

    from main_window import MainWindow

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
