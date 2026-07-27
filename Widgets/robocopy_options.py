"""RoboCopy 选项面板 — Fluent 风格 CardWidget + CheckBox + SpinBox。"""

from dataclasses import asdict, dataclass

from PySide6.QtWidgets import QFormLayout, QHBoxLayout, QVBoxLayout, QWidget
from qfluentwidgets import CardWidget, CheckBox, SpinBox, StrongBodyLabel, TitleLabel


@dataclass
class RoboCopyOptionsData:
    """可序列化的选项数据，用于预设存取。"""

    mirror: bool = False
    empty_dirs: bool = True
    copy_all: bool = False       # 默认关闭——需要管理员权限
    restartable: bool = False
    threads: int = 8
    retries: int = 3
    wait: int = 5


class RoboCopyOptions(CardWidget):
    """Fluent 风格 RoboCopy 选项卡片。"""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        # —— 标题 ——
        self._title = TitleLabel("RoboCopy 选项")

        # —— 复选框 ——
        self._mirror_cb = CheckBox("镜像模式 /MIR")
        self._mirror_cb.setToolTip("目标将与源完全一致（会删除目标中源不存在的文件）")
        self._empty_cb = CheckBox("包含空子目录 /E")
        self._empty_cb.setChecked(True)
        self._copyall_cb = CheckBox("复制所有文件信息 /COPYALL（需管理员权限）")
        self._copyall_cb.setToolTip(
            "包含 NTFS 安全/审核/所有者信息，需要管理员权限，否则会报错"
        )
        self._restartable_cb = CheckBox("可重启模式 /Z")

        # —— 数字选项 ——
        self._threads_sb = SpinBox()
        self._threads_sb.setRange(1, 128)
        self._threads_sb.setValue(8)
        self._threads_sb.setToolTip("多线程数 /MT:N")

        self._retries_sb = SpinBox()
        self._retries_sb.setRange(0, 99)
        self._retries_sb.setValue(3)
        self._retries_sb.setToolTip("失败重试次数 /R:N（0 = 不重试）")

        self._wait_sb = SpinBox()
        self._wait_sb.setRange(0, 999)
        self._wait_sb.setValue(5)
        self._wait_sb.setToolTip("重试等待间隔 /W:N 秒")

        # —— 布局 ——
        checks_row = QHBoxLayout()
        checks_row.setSpacing(16)
        checks_row.addWidget(self._mirror_cb)
        checks_row.addWidget(self._empty_cb)
        checks_row.addWidget(self._copyall_cb)
        checks_row.addWidget(self._restartable_cb)
        checks_row.addStretch()

        form = QFormLayout()
        form.setSpacing(8)
        form.addRow(StrongBodyLabel("多线程 /MT:"), self._threads_sb)
        form.addRow(StrongBodyLabel("重试次数 /R:"), self._retries_sb)
        form.addRow(StrongBodyLabel("等待间隔 /W:"), self._wait_sb)

        root = QVBoxLayout()
        root.setContentsMargins(16, 12, 16, 12)
        root.setSpacing(12)
        root.addWidget(self._title)
        root.addLayout(checks_row)
        root.addLayout(form)
        self.setLayout(root)

    # ── API ──────────────────────────────────────────────────────

    def to_dict(self) -> dict:
        """导出 UI 状态为字典。"""
        data = RoboCopyOptionsData(
            mirror=self._mirror_cb.isChecked(),
            empty_dirs=self._empty_cb.isChecked(),
            copy_all=self._copyall_cb.isChecked(),
            restartable=self._restartable_cb.isChecked(),
            threads=self._threads_sb.value(),
            retries=self._retries_sb.value(),
            wait=self._wait_sb.value(),
        )
        return asdict(data)

    def from_dict(self, d: dict) -> None:
        """从字典恢复 UI 状态。"""
        self._mirror_cb.setChecked(d.get("mirror", False))
        self._empty_cb.setChecked(d.get("empty_dirs", True))
        self._copyall_cb.setChecked(d.get("copy_all", False))
        self._restartable_cb.setChecked(d.get("restartable", False))
        self._threads_sb.setValue(d.get("threads", 8))
        self._retries_sb.setValue(d.get("retries", 3))
        self._wait_sb.setValue(d.get("wait", 5))
