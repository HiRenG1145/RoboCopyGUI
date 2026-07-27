"""主窗口 — FramelessMainWindow + 亚克力标题栏 + CardWidget 分区布局。"""

from PySide6.QtWidgets import QHBoxLayout, QInputDialog, QProgressBar, QVBoxLayout, QWidget
from qfluentwidgets import (
    CardWidget,
    FluentIcon,
    InfoBar,
    InfoBarPosition,
    PrimaryPushButton,
    PushButton,
    StrongBodyLabel,
    TitleLabel,
)
from qframelesswindow import FramelessMainWindow, StandardTitleBar

from Core.preset_manager import PresetManager
from Core.robocopy_runner import RoboCopyRunner
from Views.preset_dialog import PresetDialog
from Widgets.folder_selector import FolderSelector
from Widgets.log_viewer import LogViewer
from Widgets.robocopy_options import RoboCopyOptions


class MainWindow(FramelessMainWindow):
    """RoboCopy GUI 主窗口（Frameless + Fluent Design）。"""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("RoboCopy GUI")
        self.resize(760, 680)

        # —— 标题栏 ——
        self._title_bar = StandardTitleBar(self)
        self._title_bar.setTitle("RoboCopy GUI")
        self.setTitleBar(self._title_bar)

        # —— 核心对象 ——
        self._pm = PresetManager()
        self._runner = RoboCopyRunner(self)

        # —— 构建 UI ——
        self._build_ui()

        # —— 信号 ——
        self._runner.log_line.connect(self._log.append_log)
        self._runner.finished.connect(self._on_finished)

    # ── UI 构建 ──────────────────────────────────────────────────

    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)

        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # —— 标题栏放入布局顶层（占据真实高度，不再浮层覆盖） ——
        self._title_bar.setFixedHeight(40)
        root.addWidget(self._title_bar)

        # —— 内容区（CardWidget 分区 + 按钮） ——
        content = QVBoxLayout()
        content.setContentsMargins(24, 12, 24, 16)
        content.setSpacing(12)

        # ============================================================
        # 卡片 1：文件夹选择
        # ============================================================
        folder_card = CardWidget()
        folder_card_layout = QVBoxLayout(folder_card)
        folder_card_layout.setContentsMargins(16, 12, 16, 12)
        folder_card_layout.setSpacing(10)
        folder_card_layout.addWidget(TitleLabel("文件夹选择"))

        self._src_folder = FolderSelector("源文件夹")
        self._dest_folder = FolderSelector("目标文件夹")
        folder_card_layout.addWidget(self._src_folder)
        folder_card_layout.addWidget(self._dest_folder)

        content.addWidget(folder_card)

        # ============================================================
        # 卡片 2：RoboCopy 选项
        # ============================================================
        self._options = RoboCopyOptions()
        content.addWidget(self._options)

        # ============================================================
        # 进度条（运行中显示忙碌动画）
        # ============================================================
        self._progress = QProgressBar()
        self._progress.setFixedHeight(6)
        self._progress.setTextVisible(False)
        self._progress.setRange(0, 0)  # 初始隐藏（最大值 < 最小值 = 不显示进度）
        self._progress.hide()
        content.addWidget(self._progress)

        # ============================================================
        # 卡片 3：运行日志（提前创建，供按钮引用）
        # ============================================================
        self._log = LogViewer()

        log_card = CardWidget()
        log_card_layout = QVBoxLayout(log_card)
        log_card_layout.setContentsMargins(16, 12, 16, 12)
        log_card_layout.setSpacing(8)
        log_card_layout.addWidget(TitleLabel("运行日志"))
        log_card_layout.addWidget(self._log, stretch=1)

        content.addWidget(log_card, stretch=1)

        # ============================================================
        # 操作按钮行
        # ============================================================
        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)

        self._run_btn = PrimaryPushButton(FluentIcon.PLAY, "运行")
        self._run_btn.setMinimumHeight(36)
        self._run_btn.clicked.connect(self._run)

        self._stop_btn = PushButton(FluentIcon.CANCEL, "停止")
        self._stop_btn.setMinimumHeight(36)
        self._stop_btn.clicked.connect(self._stop)
        self._stop_btn.setEnabled(False)

        save_btn = PushButton(FluentIcon.SAVE, "保存预设")
        save_btn.clicked.connect(self._save_preset)

        load_btn = PushButton(FluentIcon.FOLDER, "管理预设")
        load_btn.clicked.connect(self._load_preset)

        clear_btn = PushButton(FluentIcon.DELETE, "清空日志")
        clear_btn.clicked.connect(self._log.clear_log)

        btn_row.addWidget(self._run_btn)
        btn_row.addWidget(self._stop_btn)
        btn_row.addStretch()
        btn_row.addWidget(save_btn)
        btn_row.addWidget(load_btn)
        btn_row.addWidget(clear_btn)
        content.addLayout(btn_row)

        # —— 内容区放入根布局 ——
        root.addLayout(content, stretch=1)

    # ── 动作 ──────────────────────────────────────────────────────

    def _run(self) -> None:
        src = self._src_folder.path().strip()
        dest = self._dest_folder.path().strip()

        if not src or not dest:
            InfoBar.warning(
                "提示",
                "请先选择源文件夹和目标文件夹。",
                position=InfoBarPosition.TOP,
                parent=self,
            ).show()
            return

        self._log.clear_log()
        self._run_btn.setEnabled(False)
        self._stop_btn.setEnabled(True)

        # 启动不确定进度条
        self._progress.show()
        self._progress.setRange(0, 0)

        self._runner.start(src, dest, self._options.to_dict())

    def _stop(self) -> None:
        self._runner.stop()
        self._run_btn.setEnabled(True)
        self._stop_btn.setEnabled(False)
        self._progress.hide()

    def _on_finished(self, exit_code: int) -> None:
        self._run_btn.setEnabled(True)
        self._stop_btn.setEnabled(False)

        # 停止进度条
        self._progress.setRange(0, 100)
        self._progress.setValue(100 if exit_code == 0 else 0)
        self._progress.hide()

        if exit_code == 0:
            InfoBar.success(
                "完成", "RoboCopy 执行成功。", position=InfoBarPosition.TOP, parent=self
            ).show()
        else:
            InfoBar.warning(
                "完成",
                f"RoboCopy 退出码: {exit_code}（非零可能表示有跳过的文件）",
                position=InfoBarPosition.TOP,
                parent=self,
            ).show()

    def _save_preset(self) -> None:
        name, ok = QInputDialog.getText(self, "保存预设", "请输入预设名称：")
        if not ok or not name.strip():
            return

        data = {
            "source": self._src_folder.path(),
            "destination": self._dest_folder.path(),
            "options": self._options.to_dict(),
        }
        self._pm.save_preset(name.strip(), data)

        InfoBar.success(
            "已保存", f"预设「{name.strip()}」已保存。", position=InfoBarPosition.TOP, parent=self
        ).show()

    def _load_preset(self) -> None:
        dlg = PresetDialog(self._pm, self)
        if dlg.exec() != PresetDialog.Accepted:
            return

        name = dlg.selected_name
        data = dlg.selected_data
        if not name or not data:
            return

        self._src_folder.set_path(data.get("source", ""))
        self._dest_folder.set_path(data.get("destination", ""))
        self._options.from_dict(data.get("options", {}))

        InfoBar.success(
            "已加载", f"预设方案「{name}」已加载。", position=InfoBarPosition.TOP, parent=self
        ).show()
