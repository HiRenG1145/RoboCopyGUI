"""预设管理对话框 — Fluent 风格 Dialog + ListWidget。"""

from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget
from qfluentwidgets import (
    Dialog,
    InfoBar,
    InfoBarPosition,
    ListWidget,
    MessageBox,
    PushButton,
)

from Core.preset_manager import PresetManager


class PresetDialog(Dialog):
    """Fluent 风格预设管理弹窗。"""

    def __init__(
        self, preset_manager: PresetManager, parent: QWidget | None = None
    ) -> None:
        super().__init__("管理预设方案", "选择一个预设来加载或删除", parent)
        self._pm = preset_manager
        self.setMinimumSize(420, 320)

        # 内容区域不能直接用 self.textLayout，需要新布局
        # Dialog 的 content 区域在 contentLabel 中，我们用自定义 widget

        # 左侧：预设列表
        self._list_widget = ListWidget()
        self._refresh_list()

        # 右侧：操作按钮
        load_btn = PushButton("加载")
        load_btn.clicked.connect(self._load)
        delete_btn = PushButton("删除")
        delete_btn.clicked.connect(self._delete)

        btn_layout = QVBoxLayout()
        btn_layout.addWidget(load_btn)
        btn_layout.addWidget(delete_btn)
        btn_layout.addStretch()

        main_layout = QHBoxLayout()
        main_layout.addWidget(self._list_widget, stretch=1)
        main_layout.addLayout(btn_layout)

        # 将自定义布局注入 Dialog 的 textLayout
        self.textLayout.addLayout(main_layout)

        # 按需调整按钮
        self.yesButton.setText("关闭")
        self.cancelButton.hide()

        self.yesSignal.connect(self._on_close)

    # ── 内部 ──────────────────────────────────────────────────────

    def _refresh_list(self) -> None:
        self._list_widget.clear()
        for name in self._pm.list_presets():
            self._list_widget.addItem(name)

    def _current_name(self) -> str | None:
        items = self._list_widget.selectedItems()
        return items[0].text() if items else None

    @property
    def selected_name(self) -> str | None:
        """用户选中的预设名称（仅在 Accepted 后有效）。"""
        return getattr(self, "_selected_name", None)

    @property
    def selected_data(self) -> dict | None:
        """用户选中的预设数据（仅在 Accepted 后有效）。"""
        return getattr(self, "_selected_data", None)

    def _load(self) -> None:
        name = self._current_name()
        if not name:
            InfoBar.warning(
                "提示", "请先选择一个预设。", position=InfoBarPosition.TOP, parent=self
            ).show()
            return
        data = self._pm.load_preset(name)
        if data:
            self._selected_name = name
            self._selected_data = data
            self.accept()
        else:
            InfoBar.error(
                "错误", f"无法加载预设「{name}」", position=InfoBarPosition.TOP, parent=self
            ).show()

    def _delete(self) -> None:
        name = self._current_name()
        if not name:
            InfoBar.warning(
                "提示", "请先选择一个预设。", position=InfoBarPosition.TOP, parent=self
            ).show()
            return
        box = MessageBox("确认删除", f"确定要删除预设「{name}」吗？", self)
        if box.exec():
            self._pm.delete_preset(name)
            self._refresh_list()

    def _on_close(self) -> None:
        self.accept()
