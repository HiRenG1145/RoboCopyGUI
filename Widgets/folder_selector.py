"""文件夹选择器 — Fluent 风格：标签 + LineEdit + 浏览按钮。"""

from PySide6.QtWidgets import QFileDialog, QHBoxLayout, QWidget
from qfluentwidgets import BodyLabel, FluentIcon, LineEdit, PushButton


class FolderSelector(QWidget):
    """一行水平布局：标签 | 路径输入框 | 浏览按钮。"""

    def __init__(self, label: str = "文件夹", parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._label = BodyLabel(label)
        self._label.setFixedWidth(56)

        self._edit = LineEdit()
        self._edit.setPlaceholderText("选择文件夹...")
        self._edit.setReadOnly(True)
        self._edit.setClearButtonEnabled(True)

        self._btn = PushButton(FluentIcon.FOLDER, "浏览...")
        self._btn.clicked.connect(self._browse)

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        layout.addWidget(self._label)
        layout.addWidget(self._edit, stretch=1)
        layout.addWidget(self._btn)
        self.setLayout(layout)

    # ── API ───────────────────────────────────────────────────────

    def path(self) -> str:
        """返回当前路径。"""
        return self._edit.text()

    def set_path(self, path: str) -> None:
        """设置路径。"""
        self._edit.setText(path)

    # ── 内部 ───────────────────────────────────────────────────────

    def _browse(self) -> None:
        folder = QFileDialog.getExistingDirectory(self, "选择文件夹", self._edit.text())
        if folder:
            self._edit.setText(folder)
